# Notes o Geometry to Vector

## A wider research domain: CAD with Deep Learning

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

