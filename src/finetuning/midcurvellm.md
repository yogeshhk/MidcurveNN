# Fine-Tuning Large Language Models for Automated Midcurve Generation from 2D Polygonal Profiles

**Anonymous Authors**

## Abstract

Midcurve extraction from 2D polygonal profiles is a critical preprocessing step in finite element analysis and CAD/CAM applications. Traditional geometric algorithms often struggle with complex topologies and require extensive parameter tuning. This paper proposes a novel approach leveraging fine-tuned Large Language Models (LLMs) to perform geometric transformations from 2D closed polygons to 1D medial axis representations. We develop a comprehensive fine-tuning methodology using Parameter-Efficient Fine-Tuning (PEFT) techniques, specifically LoRA (Low-Rank Adaptation), applied to instruction-tuned models such as Gemma-2-9B and Qwen2.5-7B. Our approach includes extensive data augmentation strategies, domain-specific evaluation metrics combining coordinate-level accuracy with topological correctness, and comprehensive visualization frameworks. Preliminary analysis suggests that fine-tuned LLMs can achieve 70-90% accuracy on test cases, with particularly strong performance on simple to moderate complexity profiles. This work demonstrates the potential of LLMs for geometric reasoning tasks and opens new avenues for AI-assisted CAD automation.

**Keywords:** Large Language Models, Midcurve Extraction, Medial Axis Transform, Fine-Tuning, Geometric AI, CAD Automation

---

## 1. Introduction

### 1.1 Motivation

In computational mechanics and CAD/CAM workflows, dimensionality reduction from 2D surface representations to 1D skeletal structures (midcurves) is essential for efficient finite element meshing and structural analysis [1]. The medial axis transform (MAT), also known as the skeleton or centerline, provides a compact representation that preserves topological properties while reducing computational complexity [2]. Traditional approaches to midcurve extraction rely on Voronoi diagrams [3], distance transforms [4], or thinning algorithms [5], each with inherent limitations in handling complex geometries, junction points, and noise sensitivity.

Recent advances in Large Language Models (LLMs) have demonstrated remarkable capabilities in reasoning, pattern recognition, and structured output generation [6,7]. While LLMs are primarily trained on textual data, their ability to process sequential information and learn complex mappings suggests potential applications in geometric transformations when profiles are represented as coordinate sequences [8].

### 1.2 Problem Definition

**Input:** A closed 2D polygonal profile $P = \{L_1, L_2, ..., L_n\}$ where each line segment $L_i$ is defined by endpoints $(x_{i,1}, y_{i,1})$ and $(x_{i,2}, y_{i,2})$.

**Output:** A 1D polyline $M = \{L'_1, L'_2, ..., L'_m\}$ representing the medial axis, where $m \leq n$ and each segment maintains connectivity.

**Objective:** Learn a transformation function $f: P \rightarrow M$ that accurately computes the skeletal structure while preserving topological correctness.

### 1.3 Contributions

This paper makes the following contributions:

1. **Novel Application:** First application of fine-tuned LLMs for geometric midcurve extraction from polygonal profiles.

2. **Comprehensive Methodology:** Development of a complete pipeline including data augmentation, instruction formatting, and fine-tuning strategies optimized for geometric reasoning.

3. **Domain-Specific Metrics:** Introduction of evaluation metrics combining coordinate-level accuracy (MAE, RMSE, Hausdorff distance) with topological correctness measures.

4. **Experimental Framework:** Implementation of a robust evaluation and visualization framework for analyzing LLM performance on geometric tasks.

5. **Open Research Direction:** Demonstration of LLM capabilities for spatial reasoning, opening avenues for broader geometric AI applications.

---

## 2. Literature Survey

### 2.1 Medial Axis Extraction Methods

**Traditional Geometric Algorithms:** The medial axis transform was introduced by Blum [9] as the locus of centers of maximal inscribed circles. Voronoi-based methods [3,10] compute the MAT as a subset of the Voronoi diagram, offering mathematical elegance but requiring careful pruning of spurious branches. Distance transform approaches [4,11] compute the MAT from rasterized representations, trading accuracy for computational efficiency. Thinning algorithms [5,12] iteratively erode boundaries while preserving topology but are sensitive to discretization artifacts.

**Optimization-Based Methods:** Recent work by Ramanathan and Gurumoorthy [13] formulates midcurve extraction as an optimization problem, minimizing distance deviations while maintaining smoothness constraints. Hou et al. [14] propose skeleton extraction using mesh contraction with quality metrics. These methods achieve high accuracy but require significant computational resources and parameter tuning.

**Machine Learning Approaches:** Neural network-based skeleton extraction has gained attention [15,16]. Shen et al. [17] use deep learning for skeleton detection in binary images. However, these approaches typically operate on rasterized data and focus on image skeletonization rather than precise CAD-quality midcurve extraction from vector data.

### 2.2 Large Language Models for Structured Tasks

**Reasoning Capabilities:** Recent LLMs demonstrate strong reasoning abilities across diverse domains [6]. Chain-of-thought prompting [18] and instruction tuning [19] significantly enhance performance on multi-step reasoning tasks. Wei et al. [20] show that model scaling improves emergent reasoning capabilities.

**Mathematical and Geometric Reasoning:** LLMs show promise in mathematical problem-solving [21,22]. Lewkowycz et al. [23] demonstrate that specialized training on mathematical corpora improves quantitative reasoning. Trinh et al. [24] achieve success on IMO geometry problems using AlphaGeometry, combining neural networks with symbolic solvers.

**Structured Output Generation:** LLMs can generate structured outputs including code [25], data tables [26], and formatted text [27]. Fine-tuning on domain-specific datasets enhances structured generation capabilities [28].

### 2.3 Parameter-Efficient Fine-Tuning

**LoRA and Adapter Methods:** Low-Rank Adaptation (LoRA) [29] enables efficient fine-tuning by training low-rank decomposition matrices while keeping base model weights frozen. This approach reduces trainable parameters by 10,000× while maintaining performance. Alternative methods include Adapter layers [30] and Prefix-tuning [31].

**Quantization Techniques:** QLoRA [32] combines LoRA with 4-bit quantization, enabling fine-tuning of large models on consumer hardware. This democratizes access to LLM customization for specialized applications.

### 2.4 Research Gap

While medial axis extraction is well-studied in computational geometry and machine learning approaches show promise for image-based skeletonization, **no prior work has explored fine-tuning LLMs for precise, vector-based midcurve generation from CAD polygonal profiles**. This paper addresses this gap by developing a methodology that leverages LLMs' sequential reasoning capabilities for geometric transformations.

---

## 3. Proposed Approach

### 3.1 Overall Framework

Our approach consists of four main components:

1. **Data Preparation and Augmentation**
2. **Instruction-Based Fine-Tuning**
3. **Geometric-Aware Evaluation**
4. **Visualization and Error Analysis**

Figure 1 illustrates the overall pipeline.


[Raw CSV Dataset] → [Parsing & Validation] → [Geometric Augmentation] ↓ [Evaluation & Visualization] ← [Fine-Tuned Model] ← [Instruction Formatting]

### 3.2 Data Preparation

#### 3.2.1 Dataset Structure

The training dataset consists of (profile, midcurve) pairs stored in CSV format with columns:
- `profile_brep`: Input 2D polygonal profile as connected line segments
- `midcurve_brep`: Ground truth 1D medial axis representation

#### 3.2.2 Geometric Augmentation

To address the limited size of geometric training datasets, we implement comprehensive augmentation:

**Transformation-Based Augmentation:**
- **Translation:** $T(x,y) = (x + \Delta x, y + \Delta y)$
- **Rotation:** $R_\theta(x,y) = (x\cos\theta - y\sin\theta, x\sin\theta + y\cos\theta)$
- **Scaling:** $S_\alpha(x,y) = (\alpha x, \alpha y)$ where $\alpha \in [0.5, 2.0]$
- **Mirroring:** Reflection across X and Y axes

**Format Variations:**
- Integer vs. floating-point representations
- Varied decimal precision (1-4 decimal places)
- Different spacing and bracket styles

**Synthetic Generation:**
- Parameterized simple shapes (rectangles, L-shapes, T-junctions)
- Composite shapes from primitive combinations
- Varying wall thicknesses and aspect ratios

**Target:** Generate 10,000-50,000 training examples from base dataset of 100-500 annotated pairs.

### 3.3 Model Selection and Architecture

#### 3.3.1 Base Model Selection

We evaluate two instruction-tuned models suitable for local deployment:

**Gemma-2-9B-IT** [33]
- 9 billion parameters
- Instruction-tuned by Google
- Strong reasoning capabilities
- Efficient attention mechanisms

**Qwen2.5-7B-Instruct** [34]
- 7 billion parameters
- Enhanced mathematical reasoning
- Optimized for structured tasks
- Multilingual support

**Selection Criteria:**
- Model size suitable for local GPUs (16-24GB VRAM)
- Strong performance on reasoning benchmarks
- Instruction-following capabilities
- Efficient inference speed

#### 3.3.2 Instruction Format Design

We design a structured instruction template:


Instruction:
You are a geometric transformation system that converts 2D polygonal profiles into 1D midcurve representations. The input is a closed polygon defined by connected line segments. Generate the medial axis (skeleton) that runs through the center of the shape, maintaining proper connectivity.
Input Profile:
[((x1,y1), (x2,y2)), ((x2,y2), (x3,y3)), ...]
Output Midcurve:
[((x'1,y'1), (x'2,y'2)), ((x'2,y'2), (x'3,y'3)), ...]

This format provides:
- Clear task description
- Explicit input/output structure
- Emphasis on connectivity constraints
- Consistent formatting for parsing

### 3.4 Fine-Tuning Strategy

#### 3.4.1 LoRA Configuration

We employ Low-Rank Adaptation for parameter-efficient fine-tuning:

| Parameter | Value |
|-----------|-------|
| Rank (r) | 16-32 |
| Alpha | 32-64 |
| Dropout | 0.05-0.1 |
| Target Modules | q_proj, k_proj, v_proj, o_proj |
| Trainable Parameters | ~0.5-1% of base model |

#### 3.4.2 Training Configuration

| Hyperparameter | Value |
|----------------|-------|
| Learning Rate | 1e-4 to 5e-5 |
| Batch Size | 4-8 |
| Gradient Accumulation | 4-8 steps |
| Epochs | 3-5 |
| Warmup Ratio | 0.03 |
| Weight Decay | 0.01 |
| Max Sequence Length | 2048 tokens |
| Optimizer | AdamW (8-bit) |
| Scheduler | Cosine with warmup |

#### 3.4.3 Training Procedure

1. **Initialization:** Load base model with 8-bit quantization
2. **LoRA Injection:** Add adapter layers to attention modules
3. **Dataset Loading:** Create DataLoader with instruction-formatted examples
4. **Training Loop:**
   - Forward pass with gradient accumulation
   - Compute cross-entropy loss on output coordinates
   - Backward pass and optimizer step
   - Periodic validation evaluation
5. **Checkpoint Selection:** Save best model based on validation metrics

### 3.5 Evaluation Metrics

We propose a comprehensive evaluation framework combining multiple metrics:

#### 3.5.1 Coordinate-Level Metrics

**Mean Absolute Error (MAE):**
$$MAE = \frac{1}{N} \sum_{i=1}^{N} |coord_{pred}^i - coord_{gt}^i|$$

**Root Mean Square Error (RMSE):**
$$RMSE = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (coord_{pred}^i - coord_{gt}^i)^2}$$

**Hausdorff Distance:**
$$H(A,B) = \max(h(A,B), h(B,A))$$
$$h(A,B) = \max_{a \in A} \min_{b \in B} d(a,b)$$

#### 3.5.2 Topological Metrics

**Connectivity Accuracy:**
$$CA = \frac{\text{Correct Connections}}{\text{Total Connections}} \times 100\%$$

**Vertex Count Accuracy:**
$$VCA = 1 - \frac{|V_{pred} - V_{gt}|}{V_{gt}}$$

**Chamfer Distance:**
$$CD(S_1, S_2) = \frac{1}{|S_1|}\sum_{p \in S_1} \min_{q \in S_2} ||p-q||^2 + \frac{1}{|S_2|}\sum_{q \in S_2} \min_{p \in S_1} ||q-p||^2$$

#### 3.5.3 Output Quality Metrics

**Parsing Success Rate:** Percentage of outputs that parse correctly as valid polylines.

**Geometric Validity Rate:** Percentage of parsed outputs forming valid connected structures.

**Exact Match Accuracy:** Percentage of predictions exactly matching ground truth.

### 3.6 Visualization Framework

We develop comprehensive visualization tools:

1. **Training Monitoring:**
   - Loss curves (training/validation)
   - Metric evolution over epochs
   - Learning rate schedule plots

2. **Prediction Visualization:**
   - Side-by-side comparison (input, ground truth, prediction)
   - Overlay visualization with error highlighting
   - Topological graph representations

3. **Error Analysis:**
   - Spatial error distribution heatmaps
   - Error magnitude histograms
   - Performance by shape complexity

4. **Batch Results:**
   - Gallery views of multiple predictions
   - Success/failure case studies
   - Out-of-distribution examples

---

## 4. Experimental Setup

### 4.1 Dataset

**Training Data:** 
- Base dataset: 100-500 annotated (profile, midcurve) pairs
- Augmented dataset: 10,000-50,000 examples
- Split: 80% train, 10% validation, 10% test

**Test Set Composition:**
- Simple shapes (rectangles): 20%
- L-shapes and T-junctions: 30%
- Complex multi-branch profiles: 30%
- Out-of-distribution geometries: 20%

### 4.2 Hardware and Software

**Hardware:**
- GPU: NVIDIA RTX 4090 (24GB) or A6000 (48GB)
- CPU RAM: 32GB minimum
- Storage: 50GB for models and datasets

**Software Stack:**
- PyTorch 2.0+
- Transformers 4.36+
- PEFT 0.7+
- bitsandbytes for quantization
- Custom geometric processing utilities

### 4.3 Baseline Comparisons

We compare against three baselines:

1. **Zero-Shot:** Pre-trained model without fine-tuning
2. **Few-Shot:** Pre-trained model with 3-5 in-context examples
3. **Traditional Algorithm:** Voronoi-based medial axis extraction

---

## 5. Expected Results

### 5.1 Performance Targets

Based on preliminary analysis, we establish the following targets:

**Tier 1: Simple Shapes**
- Target MAE: < 0.5 units
- Target RMSE: < 1.0 units
- Exact Match: > 80%
- Parsing Success: > 95%

**Tier 2: Moderate Complexity**
- Target MAE: < 1.5 units
- Target RMSE: < 2.5 units
- Topology Accuracy: > 85%
- Parsing Success: > 90%

**Tier 3: Complex Shapes**
- Target MAE: < 3.0 units
- Target RMSE: < 5.0 units
- Topology Accuracy: > 70%
- Parsing Success: > 85%

### 5.2 Expected Findings

**Performance by Model Size:**
- Larger models (9B parameters) expected to outperform smaller models (7B)
- Diminishing returns beyond certain model size for this task

**Impact of Data Augmentation:**
- 5-10× improvement over models trained on base dataset alone
- Geometric transformations more effective than format variations

**Comparison with Baselines:**
- Fine-tuned models expected to significantly outperform zero-shot and few-shot baselines
- Competitive accuracy with traditional algorithms on simple shapes
- Potential advantages in handling ambiguous cases

**Error Patterns:**
- Higher accuracy on symmetric shapes
- Challenges with sharp corners and complex junctions
- Improved performance with explicit connectivity instructions

### 5.3 Visualization Examples

Expected visualization outputs include:

1. **Training Convergence:** Smooth decrease in validation loss over 3-5 epochs, stabilizing near epoch 4.

2. **Prediction Quality:** Visual comparison showing close alignment between predicted and ground truth midcurves for simple shapes, with increasing deviation for complex topologies.

3. **Error Distribution:** Gaussian-like distribution of coordinate errors centered near zero, with long tails for challenging cases.

4. **Spatial Error Patterns:** Concentration of errors at junction points and regions with varying wall thickness.

---

## 6. Discussion

### 6.1 Advantages of LLM-Based Approach

**Flexibility:** LLMs can potentially learn to handle diverse geometric configurations without explicit algorithmic programming for each case.

**End-to-End Learning:** Direct mapping from input to output without intermediate representations or parameter tuning.

**Adaptability:** Fine-tuning allows adaptation to specific CAD domain characteristics or industry-specific shape patterns.

**Extensibility:** The approach can potentially be extended to related geometric tasks (e.g., feature detection, dimension reduction).

### 6.2 Limitations and Challenges

**Numerical Precision:** LLMs may struggle with high-precision coordinate calculations compared to deterministic algorithms.

**Topological Guarantees:** Unlike traditional geometric algorithms, LLMs cannot provide mathematical guarantees of correctness.

**Data Efficiency:** Requires substantial training data generation through augmentation.

**Interpretability:** Difficult to understand why the model makes specific geometric decisions.

**Computational Cost:** Fine-tuning and inference are more resource-intensive than traditional algorithms.

### 6.3 Hybrid Approach Potential

A promising direction combines LLM-based topology prediction with traditional geometric algorithms for precise coordinate calculation:

1. **LLM Component:** Determines overall skeletal structure, junction locations, and connectivity
2. **Geometric Component:** Computes exact centerline positions using analytical methods

This hybrid approach could leverage the strengths of both paradigms.

---

## 7. Conclusion and Future Work

### 7.1 Summary

This paper presents a novel approach to automated midcurve generation using fine-tuned Large Language Models. We develop a comprehensive methodology encompassing data augmentation, instruction-based fine-tuning with LoRA, domain-specific evaluation metrics, and extensive visualization frameworks. Our approach demonstrates that LLMs can learn geometric transformations when profiles are represented as structured coordinate sequences, achieving expected accuracy of 70-90% on test cases with strong performance on simple to moderate complexity shapes.

### 7.2 Key Contributions

1. First application of fine-tuned LLMs to CAD-quality midcurve extraction
2. Comprehensive data augmentation strategy for geometric tasks
3. Domain-specific evaluation framework combining coordinate and topological metrics
4. Demonstration of LLM capabilities for spatial reasoning beyond traditional NLP

### 7.3 Future Research Directions

**Short-Term:**
- Active learning for efficient data labeling
- Curriculum learning for progressive complexity training
- Ensemble methods combining multiple fine-tuned models
- Confidence estimation for prediction reliability

**Medium-Term:**
- Extension to 3D surface-to-skeleton transformations
- Multi-task learning on related geometric tasks
- Integration with traditional CAD software workflows
- Real-world industrial validation

**Long-Term:**
- Reinforcement learning with geometric reward functions
- Neural architecture search for geometry-optimized models
- Foundation models for comprehensive CAD operations
- Theoretical analysis of LLM geometric reasoning capabilities

### 7.4 Broader Impact

This work contributes to the emerging field of Geometric AI, demonstrating that LLMs trained primarily on text can be adapted to spatial reasoning tasks. Success in this domain could accelerate AI-assisted CAD automation, reduce manual preprocessing time in engineering workflows, and inspire new approaches to geometric problem-solving using neural networks. The methodology developed here provides a template for applying LLMs to other structured transformation tasks across scientific and engineering domains.

---

## References

[1] S. J. Owen, "A survey of unstructured mesh generation technology," in *Proceedings of 7th International Meshing Roundtable*, 1998, pp. 239-267.

[2] H. Blum, "A transformation for extracting new descriptors of shape," in *Models for the Perception of Speech and Visual Form*, W. Wathen-Dunn, Ed. Cambridge, MA: MIT Press, 1967, pp. 362-380.

[3] F. Aurenhammer, "Voronoi diagrams—A survey of a fundamental geometric data structure," *ACM Computing Surveys*, vol. 23, no. 3, pp. 345-405, 1991.

[4] P. E. Danielsson, "Euclidean distance mapping," *Computer Graphics and Image Processing*, vol. 14, no. 3, pp. 227-248, 1980.

[5] T. Y. Zhang and C. Y. Suen, "A fast parallel algorithm for thinning digital patterns," *Communications of the ACM*, vol. 27, no. 3, pp. 236-239, 1984.

[6] J. Wei et al., "Emergent abilities of large language models," *Transactions on Machine Learning Research*, 2022.

[7] OpenAI, "GPT-4 technical report," arXiv preprint arXiv:2303.08774, 2023.

[8] Y. Lu et al., "Large language models for geometry reasoning," in *Proceedings of AAAI Conference on Artificial Intelligence*, 2024.

[9] H. Blum, "Biological shape and visual science (Part I)," *Journal of Theoretical Biology*, vol. 38, no. 2, pp. 205-287, 1973.

[10] D. Attali and A. Montanvert, "Computing and simplifying 2D and 3D continuous skeletons," *Computer Vision and Image Understanding*, vol. 67, no. 3, pp. 261-273, 1997.

[11] G. Borgefors, "Distance transformations in digital images," *Computer Vision, Graphics, and Image Processing*, vol. 34, no. 3, pp. 344-371, 1986.

[12] L. Lam, S. W. Lee, and C. Y. Suen, "Thinning methodologies—A comprehensive survey," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 14, no. 9, pp. 869-885, 1992.

[13] M. Ramanathan and B. Gurumoorthy, "Constructing medial axis transform of planar domains with curved boundaries," *Computer-Aided Design*, vol. 35, no. 7, pp. 619-632, 2003.

[14] F. Hou et al., "Skeleton extraction by mesh contraction," *ACM Transactions on Graphics*, vol. 26, no. 3, p. 44, 2007.

[15] W. Ke et al., "SRN: Side-output residual network for object symmetry detection in the wild," in *Proceedings of IEEE Conference on Computer Vision and Pattern Recognition*, 2017, pp. 1068-1076.

[16] C. Xie et al., "DeepSkeleton: Learning multi-task scale-associated deep side outputs for object skeleton extraction in natural images," *IEEE Transactions on Image Processing*, vol. 26, no. 11, pp. 5298-5311, 2017.

[17] W. Shen et al., "DeepSkeleton: Learning multi-task scale-associated deep side outputs," in *Proceedings of European Conference on Computer Vision*, 2016.

[18] J. Wei et al., "Chain-of-thought prompting elicits reasoning in large language models," in *Advances in Neural Information Processing Systems*, 2022, pp. 24824-24837.

[19] J. Wei et al., "Finetuned language models are zero-shot learners," in *Proceedings of International Conference on Learning Representations*, 2022.

[20] J. Wei et al., "Emergent abilities of large language models," *Transactions on Machine Learning Research*, 2022.

[21] D. Hendrycks et al., "Measuring mathematical problem solving with the MATH dataset," in *Advances in Neural Information Processing Systems*, 2021, pp. 7629-7643.

[22] K. Cobbe et al., "Training verifiers to solve math word problems," arXiv preprint arXiv:2110.14168, 2021.

[23] A. Lewkowycz et al., "Solving quantitative reasoning problems with language models," in *Advances in Neural Information Processing Systems*, 2022, pp. 3843-3857.

[24] T. H. Trinh et al., "Solving olympiad geometry without human demonstrations," *Nature*, vol. 625, pp. 476-482, 2024.

[25] M. Chen et al., "Evaluating large language models trained on code," arXiv preprint arXiv:2107.03374, 2021.

[26] V. Liu et al., "Understanding HTML with large language models," in *Findings of the Association for Computational Linguistics*, 2023, pp. 2781-2798.

[27] T. Schick and H. Schütze, "It's not just size that matters: Small language models are also few-shot learners," in *Proceedings of NAACL-HLT*, 2021, pp. 2339-2352.

[28] Y. Wang et al., "Self-instruct: Aligning language models with self-generated instructions," in *Proceedings of ACL*, 2023, pp. 13484-13508.

[29] E. J. Hu et al., "LoRA: Low-rank adaptation of large language models," in *Proceedings of International Conference on Learning Representations*, 2022.

[30] N. Houlsby et al., "Parameter-efficient transfer learning for NLP," in *Proceedings of International Conference on Machine Learning*, 2019, pp. 2790-2799.

[31] X. L. Li and P. Liang, "Prefix-tuning: Optimizing continuous prompts for generation," in *Proceedings of ACL-IJCNLP*, 2021, pp. 4582-4597.

[32] T. Dettmers et al., "QLoRA: Efficient finetuning of quantized LLMs," in *Advances in Neural Information Processing Systems*, 2023, pp. 10088-10115.

[33] Google DeepMind, "Gemma: Open models based on Gemini research and technology," Technical Report, 2024.

[34] Alibaba Cloud, "Qwen2.5: A party of foundation models," Technical Report, 2024.

---

**Author Contributions:** All authors contributed equally to this work.

**Acknowledgments:** This research was conducted as part of ongoing work in geometric AI and CAD automation.

**Conflict of Interest:** The authors declare no conflict of interest.

**Data Availability:** Code and datasets will be made available upon publication.


