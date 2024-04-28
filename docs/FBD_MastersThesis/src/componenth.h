/*******************************************************************************
*       FILENAME :    componenth.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Component 
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _COMPONENTH_H
#define  _COMPONENTH_H
 
/******************************************************************************
*                       INCLUDE FILES
******************************************************************************/
 
#include "blockh.h"
#include "graphh.h"

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 

class Component {

        /*
        **      Component Identification
        */
		int		component_id ;			// component number
		char	component_name[20] ;	// Component name (string)

		/*
		**		Counters
		*/
		int		block_id_counter ;		// for id assignment of blocks
		int		num_polygonsets;		// Num of polysets attched to firstset

        /*
        **      Link List members
        */
		Component	*nextc;				// 	next component
		Block		*comp_block ;		// 	to the first block of block list
		PolygonSet	*firstset;			// 	head of the list of polygon sets

		/*
		**		Graph Representation
		*/
		Graph			*comp_graph ;	// 	graph which represents this comp
		DimensionGraph	*ref_dim_graph;	//	Reference Dimension Graph
		DimensionGraph	*spec_dim_graph;//	Specified Dimension Graph

		void		Scale(int side,double);


	public :

	
        /*
        **      Constructors
        */
		Component(){}	
		Component(char*,char*,double,double,double,double,double,double);

        /*
        **      Destructor
        */
		~Component(){}		

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrucutions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		int			Get_component_id()			{ return component_id ; }
		void		Set_component_id(int id )	{ component_id = id ; }

		char*		Get_component_name();
		void		Set_comp_name(char te[])	{ strcpy( component_name,te);} 


		int			Get_block_id_counter()		{ return block_id_counter ;}
		void		Set_block_id_counter(int bn){ block_id_counter = bn ;}

		Graph*		Get_comp_graph()			{ return comp_graph;}
		void		Set_comp_graph( Graph *gr)	{ comp_graph = gr ;}

		Component*	Get_nextc()					{ return nextc ;}
		void		Set_nextc(Component *co)	{ nextc = co ;}
 
		Block*		Get_comp_block()			{ return comp_block ;}
		void		Set_comp_block(Block *bb)	{ comp_block = bb ;}		
		Block*		Get_block(int blockid);

		PolygonSet*	Get_first_polygon_set()		{ return firstset;}
		DimensionGraph*	Get_spec_dim_graph()	{ return spec_dim_graph;}

		/*
		**			Link List functionality
		*/
		void		Link_Blocks( Block *cb);
		void		Link_PolygonSets(PolygonSet* pp);

		/*
		**			Transformations
		*/
		void		ScaleX(double val){	Scale(XAXIS,val);}
		void		ScaleY(double val){	Scale(YAXIS,val);}
		void		ScaleZ(double val){	Scale(ZAXIS,val);}
		void		Scale(double val){
						ScaleX(val);
						ScaleY(val);
						ScaleZ(val);
					}
		/*
		**			Display functionality
		*/
		virtual	double		Get_max_dimension();
		virtual	void		Display_by_phigs(int type);
		virtual int			Check_coplanarity(Polygon* ,Polygon*);
		virtual	void		PolygonSet_Display();
		virtual	void		Solid_Display();

		/*
		**			Dimensioning functionality
		*/
		virtual	void		Create_default_dim_graphs();

		/*
		**			Editing functions
		*/
		virtual void		Copy_for_Edit( Component* co);

		/*
		**			File operations
		*/
		virtual void		Write_to_file( FILE *fp);
		virtual void		Write_to_Venkys_file( FILE *fp);

}; 

#endif
 
 

