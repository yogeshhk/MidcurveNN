# MidcurveNN
Midcurve by Neural Networks

![Midcurve](https://github.com/yogeshhk/MidcurveNN/blob/master/TalksPublications/images/midcurvenn_simpleencoderdecoder.jpg)

<!---
Copyright (C) 2019 Yogesh H Kulkarni

## License
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or any later version.
-->

## Description
- Goal: Given a 2D closed shape (closed polygon) find its midcurve (polyline, closed or open)
- Input: set of points or set of connected lines, non-intersecting, simple, convex, closed polygon 
- Output: another set of points or set of connected lines, open/branched polygons possible

## Instructions to Run

```
cd src
conda env create -f environment.yml
activate midcurvenn
python simpleencoderdecoder\main_simple_encoderdecoder.py
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
  - It is a dimension-reduction problem. In 2D, input is the sketch profile (parametrically 2D), whereas the output is the midcurve (parametrically 1D). Input points are ordered (mostly forming closed loop, manifold). Output points may not be ordered, and can have branches (non-manifold)
  - It is a variable input and variable output problem as number of points and lines are different in input and output.
  - It is a network 2 network problem (not Sequence to Sequence) with variable size inputs and outputs
  - For Encoder Decoder like network, libraries like Tensorflow need fixed length inputs. If input has variable lengths then padding is done with some unused value. But the padding will be a big issue here as the padding value cannot be like 0,0 as it itself would be a valid point. 
  - The problem of using seq2seq is that both input polygons and output branched midcurves are not linearly connected, they may have loops, or branches. Need to think more. (more details in LIMITATIONS below)
  - Instead of going to point list as i/o let’s look at well worked format of images. Images are of constant size, say 64x64 pixels. Let’s colour profile in the bitmap (b&w only) similarly midcurve in output bitmap. With this as i/o LSTM encoder decoder seq2seq can be applied. Variety in training data can be populated by shifting/rotating/scaling both i/o. Only 2D sketch profile for now. Only linear segments. Only single simple polygon with no holes.
  - How to vectorise? Each point as 2 floats/ints. So total input vector is polygon of m points is 2m floats/ints. Closed polygon with repeat the first point as last. Output is vector of 2n points. In case of closed figure, repeat the last point. Prepare training data using data files used in MIDAS. To make 100s, 1000s of input profiles, one can scale both input and output with different factors, and then randomly shuffle the entries. Find max num points of a profile, make that as fixed length for both input and output. Fill with 0,0??? As origin 0,0 could be valid part of profile…any other filler? NULL? Run simple feed forward NN, later RNN, LSTM, Seq2seq
  - See https://www.tensorflow.org/tutorials/seq2seq, https://www.youtube.com/watch?v=G5RY_SUJih4, A Neural Representation of Sketch Drawings, https://magenta.tensorflow.org/sketch_rnn  https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/README.md 
  - Add plotting capability, show polygons their midcurves etc, easy to debug and test unseen figures.

### Dilution to Images
- Images of geometric shapes address both, representation as well as variable-size issue. Big dilution is that, true geometric shapes are like Vector images, whereas images used here would be of Raster type. Approximation has crept in.
- Even after modeling, the predicted output needs to be post-processed to bring to geometric form. Challenging again.
- Thus, this project is divided into two phases:
	- Phase I: Image to Image transformation learning
		- Img2Img: i/o fixed size 100x100 bitmaps
		- Populate many by scaling/rotating/translating both io shapes within the fixed size
		- Use Encoder Decoder like Semantic Segmentation or Pix2Pix of IMages to learn dimension reduction
	- Phase II: Geometry to Geometry transformation learning
		- Build both, input and output polyline graphs with (x,y) coordinates as node features and edges with node id pairs mentioned. For poly-lines, edges being lines, no need to store geometric intermediate points as features, else for curves, store say, sampled fixed 'n' points.
		- Build Image-Segmentation like Encoder-Decoder network, given Graph Convolution Layers from DGL in place of usual Image-based 2D convolution layer, in the usual pytorch encoder-decoder model.
		- Generate variety of input-output polyline pairs, by using geometric transformations (and not image transformations as done in Phase I).
		- See if Variational Graph Auto-Encoders https://github.com/dmlc/dgl/tree/master/examples/pytorch/vgae can help.

- Phase I has been implemented in a simplistic manner. 
- Phase II is trying to look for a good representation to store geometry/graph/network as text so that NLP (Natural Language Techniques) can be applied. [Paper: "Talk like a graph: encoding graphs for large language models"](https://arxiv.org/pdf/2310.04560.pdf) surveys many such representations and benchmarks them, but none of them looked appropriate for geometry. So, here we leverage a geometry representation similar to that found in 3D B-rep (Boundary representation), but in 2D. It can be shown as:
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
	
