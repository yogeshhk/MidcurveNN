# Describing 2D Geometry as text

## Prompt

```
You are an expert in computational geometry and generative AI. Here is a deep research problem of describing 2D geometry as text so that it becomes amenable to vectoization, retrieval augmented generation and fine-tuning, similar to standard LLM ways.

Please list out results of research in this domain where 2D geomtey with examples such as Mechanical design (2D sketches in CAD modeling), or architecture (floor plans) or Electronic engineering (circuit design), etc are described in plain text and then LLM based ways are used to access this information in search or creation/modeling copilot or chatbot like query applications.

Be very specific and output only very relevant work.
```
## Perplexity

## Research on 2D Geometry Text Description for LLM-based Applications

Based on my comprehensive search across research domains, here are the key findings on 2D geometry text description systems that enable vectorization, retrieval augmented generation, and fine-tuning approaches similar to standard LLM methodologies:

### **Parametric CAD and Sketch Systems**

**SketchGraphs Dataset and Models**[1][2][3][4]
- **Dataset**: 15 million parametric CAD sketches represented as geometric constraint graphs where nodes are primitives (lines, arcs) and edges denote geometric relationships (coincidence, perpendicularity)
- **Text Representation**: Each sketch encoded as sequences of primitives with explicit constraints, enabling natural language-like processing
- **LLM Application**: Vitruvion model uses autoregressive synthesis of sketches as sequences of primitives and constraints, trained on real-world designs

**Text2CAD Framework**[5][6]
- **Approach**: First AI framework generating parametric CAD models from text descriptions using transformer-based architecture
- **Text Integration**: Multi-level text prompts from abstract ("rectangular shape") to specific parametric instructions ("draw rectangle from (x1,y1) to (x2,y2)")
- **Applications**: Direct integration with CAD software for design workflows

**CAD-LLM and CadVLM**[7][8]
- **Architecture**: Large language models fine-tuned on engineering sketches, leveraging pre-trained foundation models
- **Text Processing**: Manipulates 2D sketches through natural language commands for CAD autocompletion, constraint inference, and conditional generation

**HPSketch Dataset**[9][10]
- **Innovation**: History-based parametric CAD sketch dataset with advanced engineering commands (parabola, hyperbola, rotation, fillet, chamfer)
- **Text Structure**: Command sequence structure inherently integrating primitives, operations, and constraints for natural language processing compatibility

### **Architectural Design and Floor Plans**

**Tell2Design (T2D) Dataset**[11][12]
- **Dataset**: 80,000+ floor plans with natural language instructions describing semantics, geometry, and topology
- **Text Description**: Document-level descriptions averaging 256 words per floor plan, covering room functionality, spatial relationships, and geometric constraints
- **LLM Integration**: Sequence-to-sequence models for language-guided floor plan generation

**Text2Scene and RoomDreamer**[13][14][15]
- **Applications**: Text-driven indoor scene synthesis with geometric and texture consistency
- **Text Processing**: Natural language prompts for room styling, furniture arrangement, and architectural modifications

### **Circuit Design and Electronic Engineering**

**Schemato System**[16]
- **Purpose**: LLM for netlist-to-schematic conversion, translating circuit descriptions into visual diagrams
- **Text Representation**: Conversion between textual netlists and structured circuit layouts for LTSpice and LaTeX formats
- **Applications**: 93% compilation success rate for netlist-to-LaTeX conversion tasks

**Circuit Analysis Benchmarks**[17]
- **Dataset**: CIRCUIT benchmark with 510 question-answer pairs for analog circuit reasoning
- **Text Integration**: Natural language queries about circuit topology, component relationships, and functionality

### **Vector Graphics and SVG Generation**

**Text-to-Vector Neural Path Systems**[18][19][20][21]
- **StarVector**: Multimodal LLM generating SVG code directly from text prompts using semantic understanding of vector primitives
- **DeepSVG**: Hierarchical generative network for SVG icon generation with text conditioning
- **Neural Path Representation**: Dual-branch VAE learning latent representations of vector paths for text-guided optimization

### **3D Object and Scene Understanding**

**Text2Shape and Shape-Language Datasets**[22][23]
- **Integration**: Joint embeddings of text descriptions and 3D shapes for cross-modal retrieval and generation
- **Applications**: Natural language querying of 3D model databases

**PartNet and Hierarchical Part Understanding**[24][25][26]
- **Dataset**: 573,585 part instances across 26,671 3D models with fine-grained hierarchical annotations
- **Text Applications**: Part-level object understanding through natural language descriptions of geometric components

### **Key Technical Approaches**

**Spatial Retrieval Augmented Generation**[27]
- **Innovation**: Extends traditional RAG to spatial reasoning, combining text-based inference with geometric computations
- **Applications**: Spatial question answering using hybrid spatial-semantic ranking strategies

**Multimodal Text-Geometry Processing**[28][29]
- **CADLLM Dataset**: CAD models paired with textual descriptions and command sequences
- **Applications**: Automated CAD modeling sequence generation from text descriptions using transformer-based LLMs

### **Research Implications**

These systems demonstrate successful integration of 2D geometric information with LLM-based approaches through:

1. **Structured Text Representations**: Converting geometric primitives and constraints into sequence-based formats amenable to transformer architectures
2. **Multimodal Embeddings**: Joint learning of text and geometric features for cross-modal retrieval and generation
3. **Hierarchical Descriptions**: Multi-level text annotations from abstract concepts to detailed parametric specifications
4. **Domain-Specific Languages**: Developing text formats that preserve geometric relationships while enabling natural language processing

The research shows particularly strong results in parametric CAD (SketchGraphs, Text2CAD), architectural design (Tell2Design), and vector graphics (StarVector, DeepSVG), establishing clear pathways for applying LLM methodologies to 2D geometric understanding and generation tasks.

[1](https://developer.nvidia.com/blog/ai-helps-predict-and-sketch-computer-aided-design-models/)
[2](https://arxiv.org/pdf/2007.08506.pdf)
[3](https://arxiv.org/abs/2109.14124)
[4](https://arxiv.org/abs/2007.08506)
[5](https://arxiv.org/html/2411.06206v1)
[6](https://arxiv.org/html/2409.17106v1)
[7](https://www.research.autodesk.com/publications/ai-lab-cad-llm/)
[8](https://arxiv.org/abs/2409.17457)
[9](https://www.sciencedirect.com/science/article/abs/pii/S0010448525000107)
[10](https://openreview.net/forum?id=cMUarIxUty)
[11](https://aclanthology.org/2023.acl-long.820.pdf)
[12](https://arxiv.org/html/2311.15941)
[13](https://arxiv.org/html/2509.00543v1)
[14](https://machinelearning.apple.com/research/roomdreamer)
[15](https://arxiv.org/abs/2308.16880)
[16](https://arxiv.org/html/2411.13899v1)
[17](https://arxiv.org/html/2502.07980v1)
[18](https://arxiv.org/html/2405.10317v1)
[19](https://arxiv.org/html/2312.11556v4)
[20](https://arxiv.org/abs/2007.11301)
[21](https://arxiv.org/html/2501.03992v1)
[22](http://text2shape.stanford.edu)
[23](https://oar.princeton.edu/bitstream/88435/pr1982p/1/Text2ShapeNaturalLanguageJointEmbeddings.pdf)
[24](https://github.com/daerduoCarey/partnet_dataset)
[25](https://cs.stanford.edu/~kaichun/partnet/partnet_main_paper_high_res.pdf)
[26](https://arxiv.org/abs/1812.02713)
[27](https://arxiv.org/html/2502.18470v3)
[28](https://huggingface.co/datasets/lanlanguai/CADLLM)
[29](https://wandb.ai/byyoung3/ml-news/reports/Text2CAD-Generating-CAD-Models-from-Text-Descriptions--Vmlldzo5NjAwMTk3)
[30](https://pub.towardsai.net/beyond-training-data-how-rag-lets-llms-retrieve-not-guess-25934b8579d8)
[31](https://zoo.dev/text-to-cad)
[32](https://blog.gopenai.com/day-9-retrieval-augmented-generation-rag-f2e628b6d7cd)
[33](https://sourcecad.com/standard-text-sizes-in-technical-drawing/)
[34](https://www.maket.ai)
[35](https://dev.to/kuldeep_paul/understanding-the-latent-space-in-llms-a-deep-dive-7e5)
[36](https://mechanomy.substack.com/p/text-to-cad)
[37](https://ideal.house/ai-floor-plan-generator)
[38](https://arxiv.org/html/2504.05786v1)
[39](https://help.autodesk.com/view/AMECH_PP/2025/ENU/?guid=GUID-E2794A6D-B52B-444E-B176-3E3948FC7DE4)
[40](https://www.sciencedirect.com/science/article/abs/pii/S0926580525005527)
[41](https://dl.acm.org/doi/10.1145/3637528.3671470)
[42](https://www.youtube.com/watch?v=AEdWElFMXt8)
[43](https://www.linkedin.com/pulse/ai-revolutionizes-architecture-fusion-nlp-computer-vision-sierra-tdulc)
[44](https://www.zenml.io/llmops-database/text-to-floor-plan-generation-using-llms-with-prompt-engineering-and-fine-tuning)
[45](https://arxiv.org/html/2410.11908v1)
[46](https://forums.fast.ai/t/describing-an-electronic-circuit-diagram/106316)
[47](https://shelf.io/blog/text-becomes-insight-with-vectorization/)
[48](https://blog.jitx.com/jitx-corporate-blog/testing-generative-ai-for-circuit-board-design)
[49](https://machinelearningmastery.com/a-gentle-introduction-to-word-embedding-and-text-vectorization/)
[50](https://diagrammergpt.github.io)
[51](https://www.umake.com/blog/natural-language-in-cad-how-it-works)
[52](https://pub.towardsai.net/text-vectorization-de690f5edb5e)
[53](https://www.deepset.ai/blog/what-is-text-vectorization-in-nlp)
[54](https://arxiv.org/abs/2401.05476)
[55](https://neptune.ai/blog/vectorization-techniques-in-nlp-guide)
[56](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
[57](https://www.sciencedirect.com/science/article/abs/pii/S0010448525000879)
[58](https://www.geeksforgeeks.org/nlp/vectorization-techniques-in-nlp/)
[59](https://www.reddit.com/r/LangChain/comments/1bp914d/help_with_llm_to_design_circuits/)
[60](https://www.cecmohali.org/public/documents/applied/material/ppt/1.%20EGD%20Introduction%20Lecture.pdf)
[61](https://www.catalyzex.com/s/Sketchgraphs)
[62](https://github.com/AutodeskAILab/Fusion360GalleryDataset)
[63](https://www.makeuk.org/insights/blogs/how-to-read-engineering-drawings-a-simple-guide)
[64](https://journals.sagepub.com/doi/full/10.3233/ICA-240744)
[65](https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/Engineering+Working+Drawing+Basics.pdf)
[66](https://www.sciencedirect.com/science/article/pii/S0010448525000107)
[67](https://en.wikipedia.org/wiki/Engineering_drawing)
[68](https://github.com/PrincetonLIPS/SketchGraphs)
[69](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5268323)
[70](https://www.mcgill.ca/engineeringdesign/step-step-design-process/basics-graphics-communication/drawing-format-and-elements)
[71](https://www.youtube.com/watch?v=ki784S3wjqw)
[72](https://powerdrill.ai/discover/discover-CadVLM-Bridging-Language-cm1l7nb9o2pig013wv4s63bc0)
[73](https://www.scribd.com/document/901899639/BRepNet-A-Topological-Message-Passing-System-for-Solid-Models)
[74](https://www.research.autodesk.com/publications/brep-net/)
[75](https://openaccess.thecvf.com/content/CVPR2021/papers/Lambourne_BRepNet_A_Topological_Message_Passing_System_for_Solid_Models_CVPR_2021_paper.pdf)
[76](https://github.com/AutodeskAILab/BRepNet)
[77](https://openaccess.thecvf.com/content/ICCV2021/papers/Wu_DeepCAD_A_Deep_Generative_Network_for_Computer-Aided_Design_Models_ICCV_2021_paper.pdf)
[78](https://arxiv.org/html/2508.14006v1)
[79](https://www.linkedin.com/posts/neeraj-yadav-50b572198_deeplearning-cad-brep-activity-7374035059454070784-f1pu)
[80](https://www.cs.columbia.edu/cg/deepcad/)
[81](https://www.sciencedirect.com/science/article/abs/pii/S0926580525004480)
[82](https://www.emergentmind.com/articles/2104.00706)
[83](https://arxiv.org/html/2411.04954)
[84](https://aclanthology.org/2025.acl-long.331.pdf)
[85](https://www.semanticscholar.org/paper/BRepNet:-A-topological-message-passing-system-for-Lambourne-Willis/5eab9f408700c95438c18f458c48b6c16175f49d)
[86](https://www.deeplearning.ai/resources/natural-language-processing/)
[87](https://www.themoonlight.io/en/review/text-to-vector-generation-with-neural-path-representation)
[88](https://www.ibm.com/think/topics/natural-language-processing)
[89](https://journals.sagepub.com/doi/full/10.1177/03064190231166665)
[90](https://www.reddit.com/r/MachineLearning/comments/hw6u23/r_deepsvg_a_hierarchical_generative_network_for/)
[91](https://intchous.github.io/T2V-NPR/)
[92](https://journals.sagepub.com/doi/abs/10.1177/03064190231166665)
[93](https://openaccess.thecvf.com/content/CVPR2025/papers/Rodriguez_StarVector_Generating_Scalable_Vector_Graphics_Code_from_Images_and_Text_CVPR_2025_paper.pdf)
[94](https://github.com/ximinng/PyTorch-SVGRender)
[95](https://www.sciencedirect.com/science/article/pii/S1877050924002060)
[96](https://richradke.github.io/computationalcreativity/lectures/lec22/)
[97](https://dl.acm.org/doi/10.1145/3658204)
[98](https://www.geeksforgeeks.org/nlp/natural-language-processing-nlp-tutorial/)
[99](https://www.semanticscholar.org/paper/DeepSVG:-A-Hierarchical-Generative-Network-for-Carlier-Danelljan/2c5dba61816bc607a91fa44da7407620561cd985)
[100](https://webdesignerdepot.com/neuralsvg-revolutionizing-vector-graphics-with-ai/)
[101](https://dspace.mit.edu/handle/1721.1/144555)
[102](https://3dvision.princeton.edu/projects/2015/ShapeNet/paper.pdf)
[103](https://arxiv.org/abs/2009.09633)
[104](https://proceedings.mlr.press/v164/thomason22a/thomason22a.pdf)
[105](https://www.linkedin.com/posts/isaac-solomon-686b4731_techartist-technicalart-gamedev-activity-7364105070075940864-mLq8)
[106](https://openreview.net/forum?id=L4yLhMjCOR&noteId=tI1de2cOBf)
[107](https://shapenet.org/publications)
[108](https://arxiv.org/html/2310.03602v5)
[109](https://shapenet.org/annotations)
[110](https://dl.acm.org/doi/10.1007/s11263-021-01534-z)
[111](https://partnet.cs.stanford.edu)
[112](https://www.sciencedirect.com/science/article/pii/S1524070325000402)
[113](https://www.sciencedirect.com/science/article/pii/S0168169925008038)
[114](https://cgifurniture.com/blog/furniture-render-ways-to-fresh-up-marketing/)
[115](https://openaccess.thecvf.com/content_CVPR_2019/papers/Yu_PartNet_A_Recursive_Part_Decomposition_Network_for_Fine-Grained_and_Hierarchical_CVPR_2019_paper.pdf)
[116](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123630171.pdf)
[117](https://arxiv.org/html/2508.15769v1)
[118](https://openaccess.thecvf.com/content/ICCV2021/papers/Selvaraju_BuildingNet_Learning_To_Label_3D_Buildings_ICCV_2021_paper.pdf)
[119](https://openaccess.thecvf.com/content/CVPR2025/papers/Huang_RoomPainter_View-Integrated_Diffusion_for_Consistent_Indoor_Scene_Texturing_CVPR_2025_paper.pdf)
[120](https://www.youtube.com/watch?v=53B_vXNApdA)
[121](https://www.nature.com/articles/s41597-024-03946-1)
[122](https://mengmouxu.github.io/SceneGen/)
[123](https://arxiv.org/abs/2110.04955)
[124](https://openaccess.thecvf.com/content_ICCV_2017/papers/Lee_RoomNet_End-To-End_Room_ICCV_2017_paper.pdf)
[125](https://openaccess.thecvf.com/content/CVPR2021/papers/Tan_SceneGen_Learning_To_Generate_Realistic_Traffic_Scenes_CVPR_2021_paper.pdf)
[126](https://buildingnet.org)
[127](https://arxiv.org/abs/2211.11350)
[128](https://arxiv.org/pdf/2508.15769.pdf)
[129](https://arxiv.org/html/2306.10146)
[130](https://www.amazon.science/publications/rooms-with-text-a-dataset-for-overlaying-text-detection)
[131](https://www.sciencedirect.com/science/article/pii/S0926580525001694)
[132](https://github.com/buildingnet/buildingnet_dataset)
[133](https://www.sciencedirect.com/science/article/abs/pii/S0925231219314419)
[134](https://dl.acm.org/doi/10.1145/3314221.3314633)