# MidcurveNN
Midcurve by Neural Networks

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
## Links
*	Vixra paper MidcurveNN: Encoder-Decoder Neural Network for Computing Midcurve of a Thin Polygon, viXra.org e-Print archive, viXra:1904.0429 http://vixra.org/abs/1904.0429 
*	ODSC proposal https://confengine.com/odsc-india-2019/proposal/10090/midcurvenn-encoder-decoder-neural-network-for-computing-midcurve-of-a-thin-polygon


## Implementation:
*	Keras
	* DON’T Conda install -c conda-forge keras DIRECTLY
	* Keras installation cribbed that tensorflow is not present
	* Reinstalled tensorflow by pip – U
	* Got error saying not able to load tensorflow. Looking at https://github.com/ContinuumIO/anaconda-issues/issues/10034 installing conda install vs2013_runtime
	* Go to Anaconda prompt and follow https://medium.com/@margaretmz/anaconda-jupyter-notebook-tensorflow-and-keras-b91f381405f8
	* If you get QT error for matplotlib, use “import matplotlib;matplotlib.use('TKAgg')”
	* Using https://blog.keras.io/building-autoencoders-in-keras.html to have a base code
		
		
# A wider research domain: CAD with Deep Learning

## Notes

Vectorization is a must for preparing input for Machine/Deep Learning

Comparison of NLP and CAD wrt vectorization:

|    NLP                                 |    CAD                              | 
|----------------------------------------|-------------------------------------|
|    Words                               |    Entities                         | 
|    Sentences composed of words         |    Features composed of entities    | 
|    Paragraphs composed of sentences    |    Bodies composed of features      | 
|    Document composed of sentences      |    Assemblies composed of bodies    | 

## References
*	Geometric Deep Learning http://geometricdeeplearning.com/ 
*	3D Machine Learning https://github.com/timzhang642/3D-Machine-Learning/blob/master/README.md
*	Pointer Networks https://pdfs.semanticscholar.org/eb5c/1ce6818333560d0d3247c0c74985ef295d9d.pdf
*	Feature Recognition
		* 	https://ai.stackexchange.com/questions/5011/using-machine-learning-to-identify-cad-model-features
		* 	https://orca.cf.ac.uk/86873/1/2016niuzphd.pdf
*	Shape2vec:
		* 	A neural network is trained to generate shape descriptors that lie close to a vector representation of the shape class, given a vector space of words. This method is easily extendable to range scans, hand-drawn sketches and images. This makes cross-modal retrieval possible, without a need to design different methods depending on the query type. We show that sketch-based shape retrieval using semantic-based descriptors outperforms the state-of-the-art by large margins, and mesh-based retrieval generates results of higher relevance to the query, than current deep shape descriptors.  https://github.com/ftasse/Shape2Vec https://www.cl.cam.ac.uk/research/rainbow/projects/shape2vec/ 
		*	Shape2vec: Understanding 3D Shapes With AI | Two Minute Papers #138 https://www.youtube.com/watch?v=bB54Wz4kq0E
*	Courses
		*	https://www.cse.iitb.ac.in/~cs749/spr2017/
		*	Machine Learning on Geometrical Data https://cse291-i.github.io/index.html
		*	Machine Learning for 3D Data http://graphics.stanford.edu/courses/cs468-17-spring/ 
		*	Geometric Modeling and Analysis CS597D https://www.cs.princeton.edu/courses/archive/fall03/cs597D/ 
*	People
		*	https://www.cse.iitb.ac.in/~sidch/ 
		*	Hao Li http://www.hao-li.com/Hao_Li/Hao_Li_-_about_me.html Human Digitization
		*	Hao Su Stanford http://3ddl.cs.princeton.edu/2016/slides/su.pdf haosu@ucsd.edu
* Applications of Machine Learning in CAD/PLM
http://ndesign.co/2017/03/09/applications-of-machine-learning-in-cadplm/
Common applications
	*	Categorize parts across libraries by their shapes and parameters.
	*	Parametrize STL and IGES, using geometry parsers and library of standard parameters for the parts and assemblies.
	*	Interaction with CAD systems using text or voice conversation in natural language: review the model (pan, rotate, zoom, comments, etc.), call common commands and perform input.
	*	Improving the behavior of wizards and generators according to standards and technical specification of overall project.
	*	Fasteners generator
	*	Frame generator
	*	Mold-base generator for casting and molding
	*	Hole generator
	*	Thread generator
	*	Design check of performed design operations according to standards and technical specifications.

