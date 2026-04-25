import numpy as np
import json
import ast
from typing import Dict, List
import pandas as pd
from config_enhanced import Config

class GeometricAugmentation:
    """Advanced geometric augmentation for training data"""
    
    @staticmethod
    def parse_brep(json_str):
        """Parse B-Rep JSON"""
        try:
            if isinstance(json_str, str):
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return ast.literal_eval(json_str)
            return json_str
        except:
            return None
    
    @staticmethod
    def to_brep_string(data: Dict) -> str:
        """Convert to JSON string"""
        return json.dumps(data)
    
    @staticmethod
    def add_noise(data: Dict, noise_level: float = 0.01) -> Dict:
        """Add Gaussian noise to coordinates"""
        augmented = data.copy()
        points = np.array(augmented["Points"])
        
        # Calculate noise scale based on coordinate range
        coord_range = points.max(axis=0) - points.min(axis=0)
        noise_scale = coord_range * noise_level
        
        # Add noise
        noise = np.random.normal(0, noise_scale, points.shape)
        noisy_points = points + noise
        
        augmented["Points"] = noisy_points.tolist()
        return augmented
    
    @staticmethod
    def non_uniform_scale(data: Dict, scale_x: float, scale_y: float) -> Dict:
        """Apply non-uniform scaling"""
        augmented = data.copy()
        points = np.array(augmented["Points"])
        
        # Apply scaling
        points[:, 0] *= scale_x
        points[:, 1] *= scale_y
        
        augmented["Points"] = points.tolist()
        return augmented
    
    @staticmethod
    def vary_precision(data: Dict, decimals: int) -> Dict:
        """Vary floating point precision"""
        augmented = data.copy()
        points = np.array(augmented["Points"])
        
        # Round to specified decimals
        points = np.round(points, decimals)
        
        augmented["Points"] = points.tolist()
        return augmented
    
    @staticmethod
    def create_thin_variant(data: Dict, thickness_factor: float = 0.5) -> Dict:
        """Create thinner version (for profiles with thickness)"""
        # This is a simplified approach - real implementation would need
        # geometric analysis to identify and modify wall thickness
        augmented = data.copy()
        points = np.array(augmented["Points"])
        
        # Move points slightly toward centroid
        centroid = points.mean(axis=0)
        points = centroid + (points - centroid) * thickness_factor
        
        augmented["Points"] = points.tolist()
        return augmented
    
    @staticmethod
    def augment_pair(profile_str: str, midcurve_str: str, 
                     augmentation_type: str = "noise") -> tuple:
        """Augment a profile-midcurve pair consistently"""
        profile_data = GeometricAugmentation.parse_brep(profile_str)
        midcurve_data = GeometricAugmentation.parse_brep(midcurve_str)
        
        if not profile_data or not midcurve_data:
            return None, None
        
        if augmentation_type == "noise":
            profile_aug = GeometricAugmentation.add_noise(
                profile_data, Config.AUGMENTATION_NOISE_LEVEL)
            midcurve_aug = GeometricAugmentation.add_noise(
                midcurve_data, Config.AUGMENTATION_NOISE_LEVEL)
        
        elif augmentation_type == "non_uniform_scale":
            scale_x = np.random.uniform(0.7, 1.3)
            scale_y = np.random.uniform(0.7, 1.3)
            profile_aug = GeometricAugmentation.non_uniform_scale(
                profile_data, scale_x, scale_y)
            midcurve_aug = GeometricAugmentation.non_uniform_scale(
                midcurve_data, scale_x, scale_y)
        
        elif augmentation_type == "precision":
            decimals = np.random.choice([1, 2, 3, 4])
            profile_aug = GeometricAugmentation.vary_precision(
                profile_data, decimals)
            midcurve_aug = GeometricAugmentation.vary_precision(
                midcurve_data, decimals)
        
        else:
            return profile_str, midcurve_str
        
        return (GeometricAugmentation.to_brep_string(profile_aug),
                GeometricAugmentation.to_brep_string(midcurve_aug))
    
    @staticmethod
    def augment_dataset(input_file: str, output_file: str, 
                       multiplier: int = 5):
        """Augment entire dataset"""
        df = pd.read_csv(input_file)
        augmented_rows = []
        
        augmentation_types = ["noise", "non_uniform_scale", "precision"]
        
        for idx, row in df.iterrows():
            # Keep original
            augmented_rows.append(row)
            
            # Generate augmented versions
            for i in range(multiplier - 1):
                aug_type = np.random.choice(augmentation_types)
                profile_aug, midcurve_aug = GeometricAugmentation.augment_pair(
                    row['Profile_brep'], row['Midcurve_brep'], aug_type)
                
                if profile_aug and midcurve_aug:
                    new_row = row.copy()
                    new_row['Profile_brep'] = profile_aug
                    new_row['Midcurve_brep'] = midcurve_aug
                    new_row['ShapeName'] = f"{row['ShapeName']}_aug{i}"
                    augmented_rows.append(new_row)
        
        augmented_df = pd.DataFrame(augmented_rows)
        augmented_df.to_csv(output_file, index=False)
        
        print(f"Augmented dataset: {len(df)} -> {len(augmented_df)} samples")
        return augmented_df

if __name__ == "__main__":
    # Example usage
    print("Augmenting training data...")
    GeometricAugmentation.augment_dataset(
        Config.TRAIN_FILE,
        Config.TRAIN_FILE.replace(".csv", "_augmented.csv"),
        Config.AUGMENTATION_MULTIPLIER
    )
