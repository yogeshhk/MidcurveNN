# MidcurveNN
Midcurve by Neural Networks

[![CI](https://github.com/yogeshhk/MidcurveNN/actions/workflows/ci.yml/badge.svg)](https://github.com/yogeshhk/MidcurveNN/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)

MidcurveNN is a project aimed at solving the challenging problem of finding the midcurve of a 2D closed shape using neural networks. The primary goal is to transform a closed polygon, represented by a set of points or connected lines, into another set of points or connected lines, allowing for the possibility of open or branched polygons in the output. To run the project, follow the provided instructions in the "Instructions to Run" section.

![Midcurve](https://github.com/yogeshhk/MidcurveNN/blob/master/publications/Midcurve_LaTeX/images/midcurvenn_simpleencoderdecoder.jpg)


- *Goal*: Given a 2D closed shape (closed polygon), find its midcurve (polyline, closed or open).
- *Input*: Set of points or set of connected lines, non-intersecting, simple, convex, closed polygon.
- *Output*: Another set of points or set of connected lines, open/branched polygons possible.

If you are interested in working/contributing to this project voluntarily, do have a look at the [issues](https://github.com/yogeshhk/MidcurveNN/issues)

<!---
Copyright (C) 2019 Yogesh H Kulkarni

## License
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or any later version.
-->


## Repository Structure

```
src/
├── config.py                         # Global configuration
├── data/raw/                         # Raw .dat/.mid coordinate files (shared by all)
├── utils/                            # Shared data prep, plotting, metrics
│
├── image_based/                      # Phase I — raster/bitmap approaches
│   ├── data/                         # Shared generated image data (one copy, no duplication)
│   │   ├── image-pairs/              # PNG pairs — used by simple/cnn/dense/denoiser
│   │   ├── unet-splits/train|test/   # UNet split PNGs
│   │   └── images-combo/train|val|test/  # Side-by-side JPGs for pix2pix/img2img
│   ├── simpleencoderdecoder/         # Dense baseline
│   ├── cnnencoderdecoder/            # CNN encoder-decoder
│   ├── denseencoderdecoder/          # Fully connected
│   ├── denoiserencoderdecoder/       # Denoising autoencoder
│   ├── unet/                         # UNet 2-stage (best image model)
│   ├── pix2pix/                      # Pix2Pix GAN (Keras)
│   ├── img2img/                      # Pix2Pix (PyTorch)
│   └── kaggle/                       # Kaggle notebooks
│
├── geometry_based/                   # Phase III — graph/geometric approaches
│   ├── graph_transformer/            # Non-auto-regressive Graph Transformer ← primary
│   ├── finetuned_graph_transformer/  # Pretrained Graphormer fine-tuned on midcurves
│   └── gnnencoderdecoder/            # Legacy GNN stub (reference)
│
├── text_based/                       # Phase II — LLM/seq2seq (implemented)
│   ├── data/brep/                    # 4 base BRep JSON shapes (I, L, T, Plus)
│   ├── data/csvs/                    # CSV train/test/val splits (993 rows)
│   ├── utils/                        # BRep data pipeline (generate CSVs, visualize)
│   ├── finetuning/                   # QLoRA fine-tuning pipeline (Qwen/Gemma/Mistral)
│   ├── codeT5/                       # CodeT5 notebooks
│   ├── ludwig/                       # Ludwig framework notebooks
│   └── prompt/                       # Few-shot prompting + LLM comparison
│
├── image_based/testing/              # Phase I tests
│   └── test_image_based.py
├── geometry_based/testing/           # Phase III tests
│   └── test_geometry_based.py
├── text_based/testing/               # Phase II tests
│   └── test_text_based.py
└── testing/                          # Cross-approach benchmark
    └── benchmark.py
```

## Instructions to Run

```bash
cd src
conda env create -f environment.yml
conda activate midcurvenn

# Generate training data for all approaches
# Outputs: image_based/data/image-pairs/, unet-splits/, images-combo/, text_based/data/sequences.json
python utils/prepare_data.py

# --- Image-based (Phase I) ---
python image_based/simpleencoderdecoder/main_simple_encoderdecoder.py

# Best image model (UNet)
cd image_based/unet && python train.py && python test.py
# Each approach saves a results/results_grid.png (5-sample Input|GT|Predicted grid)

# --- Geometry-based (Phase III) ---
cd geometry_based/graph_transformer
python main_graph_transformer.py

# Fine-tune pretrained Graphormer (Phase III-b)
cd geometry_based/finetuned_graph_transformer
pip install transformers>=4.35
python train.py

# --- Text-based / LLM (Phase II) ---
cd text_based/utils
python create_brep_csvs.py          # regenerate CSV dataset from base shapes

cd ../finetuning
python data_validator.py            # validate CSV data
python train.py                     # QLoRA fine-tune Qwen/Gemma/Mistral
python run_pipeline.py --full       # full pipeline in one command
python model_server.py --port 8000  # serve via FastAPI

# --- Tests & Benchmark ---
cd src
python -m pytest                                              # all 3 approach suites (via pytest.ini)
python -m pytest image_based/testing/test_image_based.py -v  # Phase I only
python -m pytest geometry_based/testing/test_geometry_based.py -v  # Phase III only
python -m pytest text_based/testing/test_text_based.py -v    # Phase II only
python testing/benchmark.py                                   # cross-approach benchmark
```

## Thoughts

### What is it?
Graph Summarization/Dimension-Reduction/Compression: Reducing a large graph to a smaller graph preserving its underlying structure, similar to text summarization, which attempts to keep the essence.

### Representation Issue
- Shapes can not be modeled as sequences. Although polygon shape L may appear as sequence of points, it is not. 
- All shapes can not be drawn without lifting a pencil, which is possible for sequences. Say, Shapes like Y or concentric O, cannot be modeled as sequences. So, Midcurve transformation cannot be modeled as Sequence 2 Sequence network.
- How to represent a geometric figure to feed to any Machine/Deep Learning problem, as they need numeric data in vector form?
- How to convert geometric shapes (even after restricting the domain to 2D linear profile shapes) to vectors?
- Closest data structure is graph, but thats predominantly topological and not geometrical. Meaning, graphs represent only connectivity and not spatial positions. Here, nodes would have coordinates and arcs would have curved-linear shape. So, even Graph Neural Networks, which convolute neighbors around a node and pool the output to generate vectors, are not suitable.
- Need RnD to come up with a way to generate geometric-graph embedding that will convolute at nodes (having coordinates) around arcs (having geometry, say, a set of point coordinates), then pool them to form a meaningful representation. Real crux would be how to formulate pooling to aggregate all incident curves info plus node coordinates info into a single number!!

### Variable Lengths Issue
- This is a dimension-reduction problem wherein, in 2D, the input constitutes the sketch profile (parametrically 2D), while the output represents the midcurve (parametrically 1D). Input points are ordered, mostly forming a closed loop known as a manifold. Conversely, output points may lack a defined order and can exhibit branches, referred to as non-manifold structures.
- It poses a variable input and variable output challenge, given that the number of points and lines differs in the input and output.
- This presents a network 2 network problem (not Sequence to Sequence) with variable-sized inputs and outputs.
- For Encoder-Decoder networks like those in Tensorflow, fixed-length inputs are necessary. Introducing variable lengths poses a significant hurdle as padding with a distinct unused value, such as 0,0, is not feasible, considering it could represent a valid point.
- The limitation with Seq2Seq models is notable; the input polygons and output branched midcurves are not linearly connected. They may exhibit loops or branches, necessitating further consideration for a more suitable solution. (More details on limitations below)
- Instead of adopting a point list as input/output, let's consider the well-worked format of images. These images are standardized to a constant size, say 64x64 pixels. The sketch profile is represented as a color profile in a bitmap (black and white only), and similarly, the midcurve appears in the output bitmap. This image-based format allows for the application of LSTM encoder-decoder Seq2Seq models. To diversify training data, one can introduce variations by shifting, rotating, and scaling both input and output. The current focus is on 2D sketch profiles, limited to linear segments within a single, simple polygon without holes.
- The vectorization process involves representing each point as 2 floats/ints. Consequently, the total input vector for a polygon with 'm' points is 2m floats/ints. For closed polygons, the first point is repeated as the last one. The output is a vector of 2n points, repeating the last point in the case of a closed figure. Preparing training data involves using data files from MIDAS. For scalability, input and output can be scaled with different factors, and entries can be randomly shuffled. Determining the maximum number of points in a profile establishes a fixed length for both input and output.
- Resources and further exploration for Seq2Seq models can be found at [Tensorflow Seq2Seq Tutorial]( https://www.tensorflow.org/tutorials/seq2seq), [Seq2Seq Video Tutorial](https://www.youtube.com/watch?v=G5RY_SUJih4), [A Neural Representation of Sketch Drawings](https://magenta.tensorflow.org/sketch_rnn), and [Sketch RNN GitHub Repository](https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/README.md ).
- Additionally, consider incorporating plotting capabilities to visualize polygons and their midcurves, facilitating easy debugging and testing of unseen figures.

### Dilution to Images
- Images of geometric shapes address both, representation as well as variable-size issue. Big dilution is that, true geometric shapes are like Vector images, whereas images used here would be of Raster type. Approximation has crept in.
- Even after modeling, the predicted output needs to be post-processed to bring to geometric form. Challenging again.
- Thus, this project is divided into three phases:
	- Phase I: Image to Image transformation learning
		- Img2Img: i/o fixed size 100x100 bitmaps
		- Populate many by scaling/rotating/translating both io shapes within the fixed size
		- Use Encoder Decoder like Semantic Segmentation or Pix2Pix of IMages to learn dimension reduction
	- Phase III: Geometry to Geometry transformation learning
		- Build both, input and output polyline graphs with (x,y) coordinates as node features and edges with node id pairs mentioned. For poly-lines, edges being lines, no need to store geometric intermediate points as features, else for curves, store say, sampled fixed 'n' points.
		- Build Image-Segmentation like Encoder-Decoder network, given Graph Convolution Layers from DGL in place of usual Image-based 2D convolution layer, in the usual pytorch encoder-decoder model.
		- Generate variety of input-output polyline pairs, by using geometric transformations (and not image transformations as done in Phase I).
		- See if Variational Graph Auto-Encoders https://github.com/dmlc/dgl/tree/master/examples/pytorch/vgae can help.
	- Phase II: Using Large Language Models (LLMs)
		- With representation of Profile and Midcurve in form of text, json-brep, so that LLMs can be leveraged
		- Prepapre instruct-based fine-tuning [dataset](https://www.kaggle.com/datasets/yogeshkulkarni/midcurvellm) which can be used using [Ludwig](https://www.kaggle.com/code/yogeshkulkarni/midcurvellm-finetune-ludwig) or classical Hugging Face way of fine-tuning

- **Phase I** is fully implemented with 7 encoder-decoder variants. UNet (2-stage, CoordConv, weighted BCE) is the strongest.
- **Phase III** is implemented as a **non-auto-regressive Graph Transformer** trained from scratch (`geometry_based/graph_transformer/`), and a second variant **fine-tunes a pretrained Graphormer** HuggingFace model (`geometry_based/finetuned_graph_transformer/`).
- **Phase II** is **implemented** (`text_based/`) — QLoRA fine-tuning pipeline (Qwen/Gemma/Mistral 7B), CodeT5 and Ludwig notebooks, few-shot prompt scripts, and a FastAPI inference server. BRep JSON with explicit `Lines`/`Segments` topology solves the branching serialization problem.

[Paper: "Talk like a graph: encoding graphs for large language models"](https://arxiv.org/pdf/2310.04560.pdf) surveys graph-to-text representations. We leverage a geometry representation similar to 3D B-rep (Boundary representation), in 2D:
```
{
	'ShapeName': 'I',
	'Profile': [(5.0, 5.0), (10.0, 5.0), (10.0, 20.0), (5.0, 20.0)],
	'Midcurve': [(7.5, 5.0), (7.5, 20.0)],
	'Profile_brep': {
				'Points': [(5.0, 5.0), (10.0, 5.0), (10.0, 20.0),(5.0, 20.0)], # list of (x,y) coordinates
				'Lines': [[0, 1], [1, 2], [2, 3], [3, 0]], # list of point ids (ie index in the Points list)
                'Segments': [[0, 1, 2, 3]] # list of line ids (ie index in Lines list)
				},
	'Midcurve_brep': {
				'Points': [(7.5, 5.0), (7.5, 20.0)],
				'Lines': [[0, 1]],
                'Segments': [[0]]
				},				
}
```

Column information is as below:
- **ShapeName** (text): name of the shape. Just for visualization/reports.
- **Profile**(text): List of Points coordinates (x,y) representing outer profile shape, typically closed.
- **Midcurve**(text): List of Points coordinates (x,y) representing inner midcurve shape, typically open.
- **Profile_brep**(text): Dictionary in Brep format representing outer profile shape, typically closed.
- **Midcurve_brep**(text): Dictionary in Brep format representing inner midcurve shape, typically open.

Each Segment is a continuous list of lines. In case of, say `Midcurve-T`, as there is a intersection, we can treat each line in a separate segment. In case of 'Profile O', there will be two segments, one for outer lines and another for inner lines. Each line is list of points, for now, linear. Points is list of coordinates (x,y), later can be (x,y,z).

Once we have this brep representations of both, profile and the corresponding midcurve, in the text form, then we can try various machine translation approaches or LLM based fine tuning or few-shots prompt engineering.

One major advantage of text based method over image based method is that image output still has stray pixels, cleaning which will be a complex task. But text method has exact points. It may just give odd lines, which can be removed easily.

For a wider discussion on Use of Deep Learning in CAD (Computer-aided Design), refer [Notes](./Notes.md)

## Publications/Talks
- Vixra paper MidcurveNN: Encoder-Decoder Neural Network for Computing Midcurve of a Thin Polygon, viXra.org e-Print archive, viXra:1904.0429 http://vixra.org/abs/1904.0429 
- ODSC proposal https://confengine.com/odsc-india-2019/proposal/10090/midcurvenn-encoder-decoder-neural-network-for-computing-midcurve-of-a-thin-polygon
- CAD Conference 2021, Barcelona, pages 223-225 http://www.cad-conference.net/files/CAD21/CAD21_223-225.pdf
- CAD & Applications 2022 Journal paper 19(6) http://www.cad-journal.net/files/vol_19/CAD_19(6)_2022_1154-1161.pdf
- Google Developers Dev Library https://devlibrary.withgoogle.com/products/ml/repos/yogeshhk-MidcurveNN
- Medium story [Geometry, Graphs and GPT](https://medium.com/technology-hits/geometry-graphs-and-gpt-2862d6d24866) talks about using LLMs (Large Language Models) to see if geometry serialized as line-list can predict the midcurve. An [extended abstract](https://github.com/yogeshhk/MidcurveNN/blob/master/TalksPublications/MidcurveLLM/MidcurveLLM_content.md) on the same topic.
- Kaggle [LLM-dataset](https://www.kaggle.com/datasets/yogeshkulkarni/midcurvellm) and its Ludwig fine-tuning [Notebook](https://www.kaggle.com/code/yogeshkulkarni/midcurvellm-finetune-ludwig). The [Image-dataset](https://www.kaggle.com/datasets/yogeshkulkarni/midcurvenn) and its [Simple Encode Decoder](https://www.kaggle.com/code/yogeshkulkarni/simple-encode-decoder-for-midcurvenn)
- ICONIEA 2024 (IIT Kharagpur) extended abstract: "Midcurve Computation using Large Language Models" — presented at International Conference on Intelligent and Innovative Endeavors in Applied Research, 2024
- ICCCIT 2025: "Computing Midcurve with Multi-Layer and Convolutional Neural Networks" — published in IEEE Xplore (`publications/MidcurveNN_ICCCIT2025/`)

## Citations
- [Boussuge, Flavien, & Marc, Raphaël. (2021, October 9). Mid-Curve Completion Using Convolutional Neural Network. 29th International Meshing Roundtable (IMR), Virtual Conference.](https://doi.org/10.5281/zenodo.5559223)

```
Regarding the state of the art, the closest work related to this paper is   from   Kulkarni[28].   
Kulkarni   proposed MidcurveNN, an encoder-decoder neural network to extract mid-curves from 
polygonal 2D shapes. The principle is to train the network with both a pixel image of the 
polygonal shape and of the final desired mid-curves. Although in an early  stage  of  research,  
the  network  is  able  to  produce reasonably  well  the mid-curves  of  simple  L-shaped polygons.  
The  limitations  of  this  work  remain  in  the noisiness of the produced results. 
It has not been tested on a large diversity of shapes and is performed on the full shape 
globally potentially requiring a high-resolution pixel grid for large models.

[28]Y.H. Kulkarni, MIDCURVENN: Encoder-decoder neural network for computing midcurve of a thin polygon, 
in: Open Data Sci. Conf.,2019
```


<!-- 

## Prep training data with transformations
- Represent 2D profiles in a file, ideal is vector format like SVG. List of points/lines/curves.
- Once one shape is available, both input as well as output midcurve should go through transformations like translation, rotation, scaling, mirror, etc.
- This should be done programmatic-ally to generate huge number of input-output pairs.
- Initial polygon profile data should be from PhD .data fies, having similar scheme for closed and open loops
- Using these .dat files generate vagarious bitmap 100x100 images programmatic-ally, both for input profile as well as midcurve profile. DrawSVG library can be used to rasterize the vector images
- Manually: Plot the points of profile and/or midcurve in Excel as scatter line plot. Remove all background grid legends, etc. Copy and paste as image in Powerpoint. Resize it.
- DrawSVG method is preferred as it puts lots of blank space around the object, which is needed in case of transformations.

## Implementation Notes:
- Keras (TBD: Moving from independant Keras to Tensorflow.Keras, so wait for update here)
	- DON’T Conda install -c conda-forge keras DIRECTLY
	- Keras installation cribbed that tensorflow is not present
	- Reinstalled tensorflow by pip – U
	- Got error saying not able to load tensorflow. Looking at https://github.com/ContinuumIO/anaconda-issues/issues/10034 installing conda install vs2013_runtime
	- Go to Anaconda prompt and follow https://medium.com/@margaretmz/anaconda-jupyter-notebook-tensorflow-and-keras-b91f381405f8
	- If you get QT error for matplotlib, use “import matplotlib;matplotlib.use('TKAgg')”
	- Using https://blog.keras.io/building-autoencoders-in-keras.html to have a base code
	
- Pix2Pix
	- Github Keras-GAN code https://github.com/eriklindernoren/Keras-GAN/tree/master/pix2pix
	- Same Keras-GAN code in notebook format https://www.kaggle.com/vikramtiwari/pix-2-pix-model-using-tensorflow-and-keras/notebook
	- Google Colab based code (different from Keras-GAN) https://colab.research.google.com/github/tensorflow/docs/blob/master/site/en/r2/tutorials/generative/pix2pix.ipynb

## Why Pix2Pix may not be good
- In midcurveNN problem, both input and output are black and white images with with pixel width. 
- For given input image, exact and only one possible output is there. No other output would be correct.
- So, Loss function of such learning systems would be exact and can be specified by simple distance formulas like L1, L2, etc.
- Simple/Dense/CNN based Encoder Decoder have exact loss function.
- In case of GANs, like conditional GAN or Pix2Pix, the purpose of Discriminator is actually to learn the Cost Function itself. (Ref: Phillip pod cast video regarding Pix2Pix). There "goodness" of the output is learnt in the Cost Function, and not the Exactness as specified in the examples above.
- Thus, theoretically, GANs are not suitable for MidcurveNN problem. Comments?


## Errors and Solutions
- no library called "libcairo-2" was found
  https://stackoverflow.com/questions/28211418/python-oserror-cannot-load-library-libcairo-so-2
  Install GTK 3 runtime https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer and add to path
- Failed to create a directory: models/autoencoder_model.pkl\variables; No such file or directory
  use a forward slash with the checkpoint directory or os.paths.join("models","modelname")
- If using Keras pass *_constraint arguments to layers.
- Cuda lib error, https://www.joe0.com/2019/10/19/how-resolve-tensorflow-2-0-error-could-not-load-dynamic-library-cudart64_100-dll-dlerror-cudart64_100-dll-not-found/

## Pending
- Network 2 Network Encode Decoder (not graph, as graph is topological-connectivity based, and not spatial)
- Different sizes of input and output
- Closed->closed/open, Manifold->Manifold/Non-manifold

## Why Me?
- Directly matching MidcurveNN, my PhD topic, own work in image domain, already an own paper, IKIGAI and Specific Knowledge (actually no one else knows!!)
- Favorite Graph algorithms from masters, Data Science (encoder-decoder), need in large graph databases (neo4j) or knowledge graphs
- Pytorch Geometric, Geometric Deep Learning, enormous collaboration-research publications potential.
- MidcurveNN brings geometric view of applying Skeletonization to profile or even solid geometry, into graph data science, real Geometric Deep Learning
 -->
## Disclaimer:
Author (yogeshkulkarni@yahoo.com) gives no guarantee of the results of the program. It is just a fun script. Lot of improvements are still to be made. So, don’t depend on it at all.
	
