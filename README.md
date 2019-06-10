# MidcurveNN
Midcurve by Neural Networks

Copyright (C) 2019 Yogesh H Kulkarni

## License:
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or any later version.

## Description
*	Goal: Given a 2D closed shape (closed polygon) find its midcurve (polyline, closed or open)
*	Input: set of points or set of connected lines, non-intersecting, simple, convex, closed polygon 
*	Output: another set of points or set of connected lines, open/branched polygons possible
*	Goal: Like PCA (Principal Component Analysis) or Curve fitting, for given set of points, wish to compute fitting curve (polygon: lines or points)
*   Notes:
	*	This is a translation problem. In 2D, input is the sketch profile, whereas the output is the midcurve. Input points are ordered (mostly forming closed loop, manifold). Output points may not be ordered, and can have branches (non-manifold)
	*	It’s a variable input and variable output problem. For Encoder Decoder like network, padding will be a big issue to make both i/o constant length. Padding value cannot be like 0,0 as it itself would be a valid point. Instead of going to point list as i/o let’s look at well worked format of images. Images are of constant size, say 64x64 pixels. Let’s colour profile in the bitmap (b&w only) similarly midcurve in output bitmap. With this as i/o LSTM encoder decoder seq2seq can be applied. Variety in training data can be populated by shifting/rotating/scaling both i/o. Only 2D sketch profile for now. Only linear segments. Only single simple polygon with no holes.
	*	How to vectorise? Each point as 2 floats/ints. So total input vector is polygon of m points is 2m floats/ints. Closed polygon with repeat the first point as last. Output is vector of 2n points. In case of closed figure, repeat the last point. Prepare training data using data files used in MIDAS. To make 100s, 1000s of input profiles, one can scale both input and output with different factors, and then randomly shuffle the entries. Find max num points of a profile, make that as fixed length for both input and output. Fill with 0,0??? As origin 0,0 could be valid part of profile…any other filler? NULL? Run simple feed forward NN, later RNN, LSTM, Seq2seq
	*	See https://www.tensorflow.org/tutorials/seq2seq, https://www.youtube.com/watch?v=G5RY_SUJih4, A Neural Representation of Sketch Drawings, https://magenta.tensorflow.org/sketch_rnn  https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/README.md 
	*	Add plotting capability, show polygons their midcurves etc, easy to debug and test unseen figures.

## Plan
*	Prep data with transformations
	*	Represent 2D profiles in a file, ideal is vector format like SVG. List of points/lines/curves.
	*	Once one shape is available, both input as well as output midcurve should go through transformations like translation, rotation, scaling, mirror, etc. 
	*	This should be done programmatically to generate huge number of input-output pairs.
	*	Initial polygon profile data should be from PhD .data fies, having similar scheme for closed and open loops
	*	Using these .dat files generate variousl bitmap 100x100 images programmatically, both for input profile as well as midcurve profile.
*	Phase I (Image based, Encoder-Decoder fixed size based)
	*	Img2Img: i/o fixed size 100x100 bitmaps
	*	Populate many by scaling/rotating/translating both io shapes within the fixed size
	*	Use Encode Decode like Semantic Segmentation or Pix2Pix to learn dimension reduction
*	Phase II (Geometric Points based, Variable size sequences i/o, once  such dynamic size encoder-decoder is available)
	*	Ordered sequence of points as io
	*	RNN LSTM like machine translation or summarization
	*	Different sizes of input and output
	*	Closed->closed/open, Manifold->Manifold/Non-manifold

## ToDOs
*	Study Pix2Pix, use its keras implementation (need to prep dataset in specific format)
*	Study other literature, take notes
*	Prepare ODSC presentation using Literature Survey and implementation results
*   Take up Phase II problem of Seq2Seq, do Udemy course https://www.udemy.com/applied-deep-learning-build-a-chatbot-theory-application/learn/lecture/12353012#overview for learning sequence modeling (although its for chatbot, it covers RNNs and LSTMs) 

## Publications/Talks
*	Vixra paper MidcurveNN: Encoder-Decoder Neural Network for Computing Midcurve of a Thin Polygon, viXra.org e-Print archive, viXra:1904.0429 http://vixra.org/abs/1904.0429 
*	ODSC proposal https://confengine.com/odsc-india-2019/proposal/10090/midcurvenn-encoder-decoder-neural-network-for-computing-midcurve-of-a-thin-polygon


## Implementation Notes:
*	Keras
	* DON’T Conda install -c conda-forge keras DIRECTLY
	* Keras installation cribbed that tensorflow is not present
	* Reinstalled tensorflow by pip – U
	* Got error saying not able to load tensorflow. Looking at https://github.com/ContinuumIO/anaconda-issues/issues/10034 installing conda install vs2013_runtime
	* Go to Anaconda prompt and follow https://medium.com/@margaretmz/anaconda-jupyter-notebook-tensorflow-and-keras-b91f381405f8
	* If you get QT error for matplotlib, use “import matplotlib;matplotlib.use('TKAgg')”
	* Using https://blog.keras.io/building-autoencoders-in-keras.html to have a base code
	

## References
* TBD
* TBD


## Disclaimer:
Author (yogeshkulkarni@yahoo.com) gives no guarantee of the results of the program. It is just a fun script. Lot of improvements are still to be made. So, don’t depend on it at all.
	
