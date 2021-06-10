# MidcurveNN
Midcurve by Neural Networks

![Midcurve](https://github.com/yogeshhk/MidcurveNN/blob/master/TalksPublications/images/IMG-20191008-WA0001.jpg)

<!---
Copyright (C) 2019 Yogesh H Kulkarni

## License:
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or any later version.
-->

## Description
- Goal: Given a 2D closed shape (closed polygon) find its midcurve (polyline, closed or open)
- Input: set of points or set of connected lines, non-intersecting, simple, convex, closed polygon 
- Output: another set of points or set of connected lines, open/branched polygons possible

## Thoughts

### Representation Issue
- Shapes can not be modeled as sequences. Although polygon shape L may appear as sequence of points, it is not. 
- All shapes can not be drawn without lifting a pencil, which is possible for sequences. Say, Shapes like Y or concentric O, cannot be modeled as sequences. So, Midcurve transformation cannot be modeled as Sequence 2 Sequence network.
- How to represent a geometric figure to feed to any Machine/Deep Learning problem, as they need numeric data in vector form?
- How to convert geometric shapes (even after restricting the domain to 2D linear profile shapes) to vectors?
- Closest data structure is graph, but thats predominantly topological and not geometrical. Meaning, graphs represent only connectivity and not spatial positions. Here, nodes would have coordinates and arcs would have curved-linear shape. So, even Graph Neural Networks, which convolute neighbors around a node and pool the output to generate vectors, are not suitable.
- Need RnD to come up with a way to generate geometric-graph embedding that will convolute at nodes (having coordinates) around arcs (having geometry, say, a set of point coordinates), then pool them to form a meaningful representation.

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
	- Phase II: Geometry to Geometry transformation learning
- Currently Phase I is under implementation. Phase II can start only after suitable geometric-graph embedding representation becomes available.


## Publications/Talks
- Vixra paper MidcurveNN: Encoder-Decoder Neural Network for Computing Midcurve of a Thin Polygon, viXra.org e-Print archive, viXra:1904.0429 http://vixra.org/abs/1904.0429 
- ODSC proposal https://confengine.com/odsc-india-2019/proposal/10090/midcurvenn-encoder-decoder-neural-network-for-computing-midcurve-of-a-thin-polygon
- CAD Conference 2021, Barcelona, pages 223-225 http://www.cad-conference.net/files/CAD21/CAD21_223-225.pdf
- Google Developers Dev Library https://devlibrary.withgoogle.com/products/ml/repos/yogeshhk-MidcurveNN
<!-- 
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
 -->
## Disclaimer:
Author (yogeshkulkarni@yahoo.com) gives no guarantee of the results of the program. It is just a fun script. Lot of improvements are still to be made. So, don’t depend on it at all.
	
