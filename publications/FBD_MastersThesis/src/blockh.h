/*******************************************************************************
*       FILENAME :    blockh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Block and their children
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _BLOCKH_H_
#define _BLOCKH_H_

/******************************************************************************
*                       INCLUDE FILES
******************************************************************************/

#include "application.h"
#include "lengthh.h"
#include "nodeh.h"
#include "componenth.h"
#include "planeh.h"

/******************************************************************************

		CLASS HEIRARCHY



			Block
			 |
		-----------------------------
		|			|				|
	SubBlock	Cylinder		Prismatic
				   	|				|
					|				---------
				SubCylinder		  Wedge	  Bspline	
									|
								SubWedge


*******************************************************************************/

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class Block {


	protected :							// Because children need these variables

		/*
		**		Block Identification
		*/
		int		block_id ;				// block number
		int		block_type;				// Block type
		char	block_name[20];			// block name

		/*
		**		Link List members
		*/
		Block	*nextb ;				// next block in link list of blocks
		Block	*prevb ;				// previous block in link list of blocks

		/*
		**		Graph(Node) Representation
		*/
		Node	*block_node ;			// Node which represents this block

		/*	
		**		Geometric Representation
		*/
		Plane	*Xmin , *Xmid , *Xmax ;	// Planes along X axis
		Plane	*Ymin , *Ymid , *Ymax ;	// Planes along Y axis
		Plane	*Zmin , *Zmid , *Zmax ;	// Planes along Z axis
		Length	*Xlen , *Ylen , *Zlen ;	// Lengths along 3 axes

		/*
		**		Connection to Component of which it is a part
		*/
		Component	*block_comp ;		// parent component


		void        Scale(int side,double);

	public :

		/*
		**		Constructors
		*/
		Block(){}			
		Block(char*,Component*,double,double,double,double,double,double);		

		/*
		**		Destructor
		*/
		~Block(){}				

		/*
		**		Following functions are specific to this class
		**		and are not translated differently by the subclasses
		**		thats why they are not virtual
		**
		**		GET and SET functions are normally avoided in Object oriented
		**		Programming but some restrictions posed by Motif and to
		**		continue the method adopted by earlier programs those functions
		**		are still used.
		*/
		int		Get_block_id()				{ return block_id ; }
		void	Set_block_id( int bi )		{ block_id = bi ;}

		int		Get_block_type()			{ return block_type ; }
		void	Set_block_type( int bt )	{ block_type = bt ;}

		char*	Get_block_name()			{ return block_name;}
		void	Set_block_name( char te[])	{ strcpy(block_name,te);}

		Block*	Get_nextb()					{ return nextb ; }
		void	Set_nextb(Block *b)			{ nextb = b ;}

		Node*	Get_block_node()			{ return block_node; }
		void	Set_block_node(Node *bn)	{ block_node = bn ;}

		Block*	Get_prevb()					{ return prevb ; }
		void	Set_prevb(Block *b)			{ prevb = b ;}
	
		int		Get_flags_sum(int axi);

		/*
		**		Following functions are used to some extent because
		**		they were used by previous students.There could be
		**		another way of designing things better than this
		*/
		void	fix_xmin(int boo){ Xmin->Set_fixed(boo);}
		void	fix_xmid(int boo){ Xmid->Set_fixed(boo);}
		void	fix_xmax(int boo){ Xmax->Set_fixed(boo);}
		void	fix_xlen(int boo){ Xlen->Set_fixed(boo);}

		int		fix_xmin(int b,double d){return Xmin->Set_fixed(b,d);}
		int		fix_xmid(int b,double d){return Xmin->Set_fixed(b,d);}
		int		fix_xmax(int b,double d){return Xmin->Set_fixed(b,d);}

		void	fix_ymin(int boo){ Ymin->Set_fixed(boo);}
		void	fix_ymid(int boo){ Ymid->Set_fixed(boo);}
		void	fix_ymax(int boo){ Ymax->Set_fixed(boo);}
		void	fix_ylen(int boo){ Ylen->Set_fixed(boo);}

		int		fix_ymin(int b,double d){return Xmin->Set_fixed(b,d);}
		int		fix_ymid(int b,double d){return Xmin->Set_fixed(b,d);}
		int		fix_ymax(int b,double d){return Xmin->Set_fixed(b,d);}

        void    fix_zmin(int boo){ Zmin->Set_fixed(boo);}
        void    fix_zmid(int boo){ Zmid->Set_fixed(boo);}
        void    fix_zmax(int boo){ Zmax->Set_fixed(boo);}
        void    fix_zlen(int boo){ Zlen->Set_fixed(boo);}
 
		int		fix_zmin(int b,double d){return Xmin->Set_fixed(b,d);}
		int		fix_zmid(int b,double d){return Xmin->Set_fixed(b,d);}
		int		fix_zmax(int b,double d){return Xmin->Set_fixed(b,d);}

        int		Get_fix_xmin(){ return Xmin->Get_fixed();}
        int		Get_fix_xmid(){ return Xmid->Get_fixed();}
        int		Get_fix_xmax(){ return Xmax->Get_fixed();}
        int		Get_fix_xlen(){ return Xlen->Get_fixed();}
 
        int		Get_fix_ymin(){ return Ymin->Get_fixed();}
        int		Get_fix_ymid(){ return Ymid->Get_fixed();}
        int		Get_fix_ymax(){ return Ymax->Get_fixed();}
        int		Get_fix_ylen(){ return Ylen->Get_fixed();}
 
		int		Get_fix_zmin(){ return Zmin->Get_fixed();}
		int		Get_fix_zmid(){ return Zmid->Get_fixed();}
		int		Get_fix_zmax(){ return Zmax->Get_fixed();}
		int		Get_fix_zlen(){ return Zlen->Get_fixed();}
 
 
        double      Get_Xmin(){ return  Xmin->Get_plane_value();}
        double      Get_Xmid(){ return  Xmid->Get_plane_value();}
        double      Get_Xmax(){ return  Xmax->Get_plane_value();}
 
        double      Get_Ymin(){ return  Ymin->Get_plane_value();}
        double      Get_Ymid(){ return  Ymid->Get_plane_value();}
        double      Get_Ymax(){ return  Ymax->Get_plane_value();}
 
        double      Get_Zmin(){ return  Zmin->Get_plane_value();}
        double      Get_Zmid(){ return  Zmid->Get_plane_value();}
        double      Get_Zmax(){ return  Zmax->Get_plane_value();}
 
        void        Set_Xmin(double v){ Xmin->Set_plane_value(v);}
        void        Set_Xmid(double v){ Xmid->Set_plane_value(v);}
        void        Set_Xmax(double v){ Xmax->Set_plane_value(v);}
 
        void        Set_Ymin(double v){ Ymin->Set_plane_value(v);}
        void        Set_Ymid(double v){ Ymid->Set_plane_value(v);}
        void        Set_Ymax(double v){ Ymax->Set_plane_value(v);}
 
        void        Set_Zmin(double v){ Zmin->Set_plane_value(v);}
        void        Set_Zmid(double v){ Zmid->Set_plane_value(v);}
        void        Set_Zmax(double v){ Zmax->Set_plane_value(v);}
 
        Length*     Get_Xlen(){ return Xlen ;}
        Length*     Get_Ylen(){ return Ylen ;}
        Length*     Get_Zlen(){ return Zlen ;}
 


		/*
		**		All the Shape classes will be derived from
		**		"this" class only. Lot of functionality is
		**		class specific and gets translated differently by
		**		each class.Power of inheritance can be achieved by
		**		Mechanism of virtual functions
		*/
		virtual int			Get_axis(){}
		virtual	int			Get_butting_plane1(){}
		virtual	int			Get_butting_plane2(){}

		virtual void		Initialize_flags(int boo);
		virtual double		Get_max_dimension();
		virtual void		Update(int axis);

		virtual	void		Write_to_file(FILE*){}
        virtual Face*       Create_Faces();
        virtual Polygon*    Create_Polygons(){return NULL;}
        virtual void        Display_by_phigs();
        virtual void        Solid_Display_by_phigs();

		virtual double		Volume();
		/*
		**		Dimensioning Functionality
		*/
        virtual Face*       Contribute_dim_Faces(){return Create_Faces();}

        /*
        **          Transformations
        */
        void        ScaleX(double val){ Scale(XAXIS,val);}
        void        ScaleY(double val){ Scale(YAXIS,val);}
        void        ScaleZ(double val){ Scale(ZAXIS,val);}
        void        Scale(double val){
                        ScaleX(val);
                        ScaleY(val);
                        ScaleZ(val);
                    }

}; 

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class SubBlock : public Block
{

	public:

		/*
		**		Constructors
		*/
		SubBlock(){}				
		SubBlock(char*,Component*,double,double,double,double,double,double);

		/*
		**		Destructor
		*/
		~SubBlock(){}			

		/*
		**		Faces returned by this function are of reverse orientation
		**		than the superclass Block.	
		*/
		virtual	Face*		Create_Faces();
		virtual double		Volume();
        virtual void        Display_by_phigs();
		virtual	void		Write_to_file(FILE*){}
		/*
		**		Dimensioning Functionality
		*/
        virtual Face*       Contribute_dim_Faces(){return Create_Faces();}
};


/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class Cylinder: public Block
{
 
	protected :
		
		int			axis ;						// height axis
		double		major_radius ;				// Major radius
		double		minor_radius ;				// Minjor radius
		double		height ;					// height along axis

	public:
 
		/*
		**		Constructors
		*/
        Cylinder(){}                   
        Cylinder(char*,Component*,double,double,double,double,double,double);

		/*
		**		Destructor
		*/
        ~Cylinder(){}                           
 
		/*
		**		Get data functions
		*/
		virtual int			Get_axis(){ return axis ;}
		virtual double		Volume();
		virtual	void		Write_to_file(FILE*){}

		/*
		**		Display functionality
		*/
		virtual Polygon* 	Create_Polygons();
		virtual	void		Display_by_phigs();

		/*
		**		Dimensioning Functionality
		*/
        virtual Face*       Contribute_dim_Faces();
};

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class SubCylinder: public Cylinder
{
 
    public:
 
        /*
        **      Constructors
        */
    	SubCylinder(){}                            
        SubCylinder(char*,Component*,double,double,double,double,double,double);
                    
        /*
        **      Destructor
        */
        ~SubCylinder(){}                  
		virtual	void		Write_to_file(FILE*){}
 
        /*
        **      Display functionality
        */
		virtual	void		Display_by_phigs();
		virtual double		Volume();



};

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 

	/*
	**		The main theme of Prismatic block is based on Extrusion
	**		All the subclasses of this class will be the extuded shapes
	**		Thus this has a member "prism_axis" which corresponds to
	**		the axis of extrusion
	*/
class Prismatic:public Block
{
	protected :

		int			prism_axis;				//		Axis

	public:

		Prismatic(){}
		Prismatic(	char*,Component*,
					double,double,double,double,double,double,
					int);

		~Prismatic(){}

        /*
        **      Get data functions
        */
        virtual int         Get_axis(){ return prism_axis;}
		virtual	int			Get_butting_plane1(){}
		virtual	int			Get_butting_plane2(){}
 
        /*
        **      Display functionality
        */
        virtual Polygon*    Create_Polygons();
        virtual void        Display_by_phigs();
 
        /*
        **      Dimensioning Functionality
        */
        virtual Face*       Contribute_dim_Faces();

};

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class Wedge:public Prismatic
{

	protected :

		/*
		**		The super class "Prismatic" defines axis 
		**		that matches with the Encapsulating blocks plane
		**		in the direction other than axis direction
		**		
		**		Wedge is the prism in which two planes match with the
		**		two adjacent planes of the encapsulating block
		*/

		int			butting_plane1;			//		Plane matching with Block
		int			butting_plane2;			//		Plane matching with Block

	public:

		Wedge(){}
        Wedge(	char*,Component*,
				double,double,double,double,double,double,
				int,int,int);

		~Wedge(){}

        /*
        **      Get data functions
        */
		virtual	int			Get_butting_plane1(){	return	butting_plane1;} 
		virtual	int			Get_butting_plane2(){	return	butting_plane2;} 
		virtual	void		Write_to_file(FILE*){}

        /*
        **      Display functionality
        */
        virtual Polygon*    Create_Polygons();
        virtual void        Display_by_phigs();
 
};

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/

class SubWedge:public Wedge
{

    public:

        SubWedge(){}
        SubWedge(  	char*,Component*,
                	double,double,double,double,double,double,
                	int,int,int);

        ~SubWedge(){}
		virtual	void		Write_to_file(FILE*){}

        /*
        **      Display functionality
        */
        virtual Polygon*    Create_Polygons();
        virtual void        Display_by_phigs();

};


/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/

class Bspline:public Prismatic
{

	/*
	**			This is extruded Bspline surface.ie. in U direction
	**			it is Bspline but in V direction its a straight line
	**			Later if we would like to have Bspline in Both direction
	**			we will derive such class from it and add attributes
	**			for that direction
	**		
	**			Pl. read 244 PHIGS programming manual
	**
	*/

	private :

			/*
			**		Follwoing are the spline functions
			**		wrt num_points = 5 and order 3
			*/

			double	N[6];		//	Refere pp. 130
								//	Geometric Modeling - Mortenson

			void	Fill_first_order_Ns(double u);
			double  f(double cpts[],double u, double xval);
			double	Calculate_Bspline_value(double cpts[],double u);

    protected :

        /*
        **      The super class "Prismatic" defines axis
        **      that matches with the Encapsulating blocks plane
        **      in the direction other than axis direction
        */

		/*
		**		Right now we have decided to have array of control
		**		points and also we will hard code order and knot
		**		vectors
		*/

		int		u_order;			//	Order in U direction = 3
		int		u_num_pts;			//	Number of points in U direction

		float	u_knot_vector[9];	//	Ends with multiplicity 3
		Vertex	u_control_pts[6];	//	Control points

		int		bsp_axis;			//	Bspline prism axis

    public:

        Bspline();
        Bspline(  	char*,Component*,
                	double,double,double,double,double,double,
                	int ax,Vertex*);
        Bspline(  	char*,Component*,
                	double,double,double,double,double,double,
                	int ax,
					double, double,double,
					double, double,double,
					double, double,double,
					double, double,double,
					double, double,double,
					double, double,double
					);
        ~Bspline();

        virtual double      Volume();
		virtual	void		Write_to_file(FILE*);

        /*
        **      Display functionality
        */
        virtual void        Display_by_phigs();

        /*
        **      Dimensioning Functionality
        */
		virtual	double		Given_X_return_Y(int,double,double);
        virtual Face*       Contribute_dim_Faces();

};
#endif
 
 

