from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json
import ast
import numpy as np
from datetime import datetime
import uvicorn
from config_enhanced import Config
from metrics_enhanced import GeometricMetrics

# Initialize FastAPI app
app = FastAPI(
    title="Midcurve Generation API",
    description="API for generating midcurves from 2D polygonal profiles using LLMs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variables
model = None
tokenizer = None
device = None

# Request/Response models
class ProfileInput(BaseModel):
    points: List[List[float]] = Field(..., description="List of 2D coordinates")
    lines: List[List[int]] = Field(..., description="Line connectivity (point indices)")
    segments: List[List[int]] = Field(..., description="Segment groupings")
    
    class Config:
        schema_extra = {
            "example": {
                "points": [[0.0, 0.0], [10.0, 0.0], [10.0, 25.0], [35.0, 25.0], [35.0, 30.0], [0.0, 30.0]],
                "lines": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
                "segments": [[0, 1, 2, 3, 4, 5]]
            }
        }

class PredictionRequest(BaseModel):
    profile: ProfileInput
    validate_input: bool = Field(True, description="Whether to validate input geometry")
    return_confidence: bool = Field(True, description="Whether to return confidence scores")
    
class MidcurveOutput(BaseModel):
    points: List[List[float]]
    lines: List[List[int]]
    segments: List[List[int]]

class PredictionResponse(BaseModel):
    success: bool
    midcurve: Optional[MidcurveOutput] = None
    confidence_score: Optional[float] = None
    metrics: Optional[Dict] = None
    error: Optional[str] = None
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]

# Validation functions
def validate_profile_geometry(profile: ProfileInput) -> ValidationResult:
    """Validate input profile geometry"""
    issues = []
    
    # Check if points array is not empty
    if not profile.points:
        issues.append("Points array is empty")
    
    # Check if all points are 2D
    for i, point in enumerate(profile.points):
        if len(point) != 2:
            issues.append(f"Point {i} is not 2D: {point}")
    
    # Check if line indices are valid
    max_index = len(profile.points) - 1
    for i, line in enumerate(profile.lines):
        if len(line) != 2:
            issues.append(f"Line {i} does not have exactly 2 endpoints: {line}")
        for idx in line:
            if idx < 0 or idx > max_index:
                issues.append(f"Line {i} has invalid point index: {idx}")
    
    # Check if profile is closed (each point connects to exactly 2 lines)
    point_connections = {}
    for line in profile.lines:
        for pt in line:
            point_connections[pt] = point_connections.get(pt, 0) + 1
    
    unclosed_points = [pt for pt, count in point_connections.items() if count != 2]
    if unclosed_points:
        issues.append(f"Profile is not closed. Points with != 2 connections: {unclosed_points}")
    
    # Check coordinate ranges
    points_array = np.array(profile.points)
    if np.any(np.isnan(points_array)) or np.any(np.isinf(points_array)):
        issues.append("Points contain NaN or Inf values")
    
    coord_range = points_array.max(axis=0) - points_array.min(axis=0)
    if np.any(coord_range == 0):
        issues.append("Profile has zero range in one or more dimensions")
    
    return ValidationResult(is_valid=len(issues) == 0, issues=issues)

def validate_and_correct_output(generated_json: dict, input_profile: ProfileInput) -> tuple:
    """Validate and potentially correct generated output"""
    issues = []
    
    # Check required keys
    if not all(k in generated_json for k in ["Points", "Lines", "Segments"]):
        return None, ["Missing required keys (Points, Lines, Segments)"]
    
    # Check connectivity
    lines = generated_json.get("Lines", [])
    points = generated_json.get("Points", [])
    
    if len(lines) == 0:
        return None, ["No lines in output"]
    
    if len(points) == 0:
        return None, ["No points in output"]
    
    # Build adjacency graph
    adj = {i: [] for i in range(len(points))}
    for line in lines:
        if len(line) >= 2:
            p1, p2 = line[0], line[1]
            if p1 < len(points) and p2 < len(points):
                adj[p1].append(p2)
                adj[p2].append(p1)
    
    # Check connectivity via BFS
    visited = set()
    queue = [0]
    visited.add(0)
    
    while queue:
        node = queue.pop(0)
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    if len(visited) < len(points):
        issues.append(f"Output graph is not fully connected ({len(visited)}/{len(points)} points reachable)")
    
    # Check coordinate range
    output_points = np.array(points)
    input_points = np.array(input_profile.points)
    
    input_min = input_points.min(axis=0)
    input_max = input_points.max(axis=0)
    output_min = output_points.min(axis=0)
    output_max = output_points.max(axis=0)
    
    input_range = input_max - input_min
    buffer = input_range * 0.5
    
    if not (np.all(output_min >= input_min - buffer) and np.all(output_max <= input_max + buffer)):
        issues.append("Output coordinates outside reasonable range")
    
    if len(issues) > 0:
        return generated_json, issues
    
    return generated_json, None

def compute_confidence_score(prediction_json: dict, input_profile: ProfileInput) -> float:
    """Compute confidence score for prediction"""
    try:
        # Check basic validity
        if not all(k in prediction_json for k in ["Points", "Lines", "Segments"]):
            return 0.0
        
        # Connectivity score
        connectivity = GeometricMetrics.connectivity_score(json.dumps(prediction_json))
        
        # Coordinate range score
        points = np.array(prediction_json["Points"])
        input_points = np.array(input_profile.points)
        
        input_center = input_points.mean(axis=0)
        pred_center = points.mean(axis=0)
        
        center_distance = np.linalg.norm(pred_center - input_center)
        input_scale = np.linalg.norm(input_points.max(axis=0) - input_points.min(axis=0))
        
        center_score = np.exp(-center_distance / input_scale)
        
        # Vertex count reasonableness (midcurve should have fewer vertices)
        vertex_ratio = len(prediction_json["Points"]) / len(input_profile.points)
        vertex_score = 1.0 if vertex_ratio < 1.0 else 1.0 / vertex_ratio
        
        # Combined confidence
        confidence = 0.5 * connectivity + 0.3 * center_score + 0.2 * vertex_score
        
        return float(confidence)
    
    except:
        return 0.0

# API endpoints
@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global model, tokenizer, device
    
    print("Loading model...")
    try:
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            Config.MODEL_ID,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_ID)
        
        # Load fine-tuned adapters
        model = PeftModel.from_pretrained(base_model, Config.NEW_MODEL_NAME)
        model = model.merge_and_unload()
        model.eval()
        
        device = next(model.parameters()).device
        
        print(f"Model loaded successfully on {device}")
    
    except Exception as e:
        print(f"Error loading model: {e}")
        print("API will run but predictions will fail")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="running",
        model_loaded=model is not None,
        device=str(device) if device else "unknown"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy" if model is not None else "model_not_loaded",
        model_loaded=model is not None,
        device=str(device) if device else "unknown"
    )

@app.post("/validate", response_model=ValidationResult)
async def validate_profile(profile: ProfileInput):
    """Validate input profile geometry"""
    return validate_profile_geometry(profile)

@app.post("/predict", response_model=PredictionResponse)
async def predict_midcurve(request: PredictionRequest):
    """Generate midcurve prediction"""
    start_time = datetime.now()
    
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Validate input if requested
        if request.validate_input:
            validation = validate_profile_geometry(request.profile)
            if not validation.is_valid:
                return PredictionResponse(
                    success=False,
                    error=f"Invalid input: {', '.join(validation.issues)}",
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
        
        # Convert profile to B-Rep format
        profile_brep = {
            "Points": request.profile.points,
            "Lines": request.profile.lines,
            "Segments": request.profile.segments
        }
        profile_str = json.dumps(profile_brep)
        
        # Generate prediction
        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": profile_str}
        ]
        
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        
        inputs = tokenizer([text], return_tensors="pt").to(device)
        
        with torch.no_grad():
            generated_ids = model.generate(
                inputs.input_ids,
                max_new_tokens=Config.MAX_NEW_TOKENS,
                do_sample=Config.DO_SAMPLE,
                temperature=Config.TEMPERATURE
            )
        
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        response_text = tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True)[0].strip()
        
        # Parse response
        try:
            # Try to extract JSON from response
            if '{' in response_text and '}' in response_text:
                start_idx = response_text.index('{')
                end_idx = response_text.rindex('}') + 1
                json_str = response_text[start_idx:end_idx]
                prediction_json = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        
        except:
            try:
                prediction_json = ast.literal_eval(response_text)
            except:
                return PredictionResponse(
                    success=False,
                    error="Could not parse model output as JSON",
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
        
        # Validate output
        validated_json, validation_issues = validate_and_correct_output(
            prediction_json, request.profile)
        
        if validated_json is None:
            return PredictionResponse(
                success=False,
                error=f"Invalid output: {', '.join(validation_issues)}",
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        
        # Compute confidence if requested
        confidence = None
        if request.return_confidence:
            confidence = compute_confidence_score(validated_json, request.profile)
        
        # Compute additional metrics if ground truth provided
        metrics = None
        
        # Prepare response
        midcurve_output = MidcurveOutput(
            points=validated_json["Points"],
            lines=validated_json["Lines"],
            segments=validated_json["Segments"]
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return PredictionResponse(
            success=True,
            midcurve=midcurve_output,
            confidence_score=confidence,
            metrics=metrics,
            error=None,
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        return PredictionResponse(
            success=False,
            error=str(e),
            processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
        )

@app.post("/batch_predict")
async def batch_predict(profiles: List[ProfileInput], background_tasks: BackgroundTasks):
    """Batch prediction endpoint"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    
    for profile in profiles:
        request = PredictionRequest(
            profile=profile,
            validate_input=True,
            return_confidence=True
        )
        result = await predict_midcurve(request)
        results.append(result)
    
    return {"results": results, "total": len(results)}

# Run server
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Midcurve Generation API Server')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Host address')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port number')
    parser.add_argument('--reload', action='store_true',
                       help='Enable auto-reload')
    
    args = parser.parse_args()
    
    uvicorn.run(
        "model_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
