/*******************************************************************************
*       FILENAME :    polygonh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Polygon
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       OCT 27, 1995.
*
*******************************************************************************/
#ifndef _POLYGON_H_
#define _POLYGON_H_

/******************************************************************************
*                       INCLUDE FILES
******************************************************************************/
 
#include "vertexh.h"

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class Polygon{

	protected :

        /*
        **      Plane Identification
        */
		int		polygon_id ;			// Polygon number
		int		polygon_axis;			// face type
		int		block_type;				//	ADDT or SUBT block
		Vector  *normal;				// normal to the surface

		/*
		**		Counters
		*/
		int 	num_of_points;

        /*
        **      Information Representation
        */
		double	polygon_value;			// positional value on the axis

        /*
        **      Link List members
        */
		Vertex	*V_list_head;			// circular doubly linked list
		Polygon *nextp;					// next polygon in the list
		Polygon *prevp;					// previous	polygon in the list

	public :
		
        /*
        **      Constructors
        */
		Polygon();				
		Polygon(Face *ff);	
		Polygon(int ,int ,int pv,Vertex *v1,Vertex *v2,Vertex *v3,Vertex *v4);

        /*
        **      Destructor
        */
		~Polygon(){}	

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrictions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		int			Get_polygon_id(){return polygon_id; }
		void		Set_polygon_id(int fi){ polygon_id = fi ;}

		int			Get_block_type(){return block_type; }
		void		Set_block_type(int fi){ block_type = fi ;}

		int			Get_num_of_points(){return num_of_points; }
		void		Set_num_of_points(int fi){ num_of_points= fi ;}

		int			Get_polygon_axis(){return polygon_axis; }
		double		Get_polygon_value(){return polygon_value; }

		Vertex*		Get_V_list_head(){ return V_list_head;}
		void		Set_V_list_head(Vertex *vv){ V_list_head = vv;}

		Polygon*	Get_nextp(){	return nextp;}
		void		Set_nextp(Polygon *fn){ nextp = fn ; }

		Polygon*	Get_prevp(){	return prevp;}
		void		Set_prevp(Polygon *fn){ prevp = fn ; }

		Vector*		Get_normal(){	return normal;}
		void		Set_normal(Vector *nn){	normal = nn;}

		/*
		**			Display operations
		*/
        void    	Display_by_phigs();

		/*			
		**			Link List Operations
		*/
		void		Add_to_the_V_list(Vertex* vv);
		void		Insert_before(Vertex *before,Vertex *vv);
		void		Insert_after(Vertex *after,Vertex *vv);
		void		Insert_between(Vertex *left,Vertex *self,Vertex *right);
		void		Remove_duplicate_Vertices();
		int			Remove(Vertex *de);

		/*
		**			Applcation specific
		*/
		Polygon*	Split();

		/*
		**			Utility functions
		*/
		void 		Print_list();

}; 

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/


class PolygonSet{

	protected :

        /*
        **      Plane Identification
        */
		int			polygonset_id;
		Vertex		*plane_normal;

		// Normal has three direction cosines ,Rightnow I dont have
		// any special class called class Normal,and its really
		// nothing different than class Vertex in terms of members

		/*
		**		Counters
		*/	
		int		num_polygons;

        /*
        **      Information Representation
        */
		double		plane_value;	// of this polygon set

        /*
        **      Link List members
        */
		Polygon 	*poly_list_head;// list of polygons
		PolygonSet	*nextps;	// next polygon Set

	public :

        /*
        **      Constructors
        */
		PolygonSet();

        /*
        **      Destructor
        */
		~PolygonSet(){}

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrictions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		int			Get_polygonset_id(){ return polygonset_id;}
		void		Set_polygonset_id(int ii){ polygonset_id = ii;}

        double		Get_polygon_value(){return plane_value; }
		Polygon*	Get_poly_list_head(){ return poly_list_head;}

        PolygonSet *Get_nextps(){   return nextps;}
        void    Set_nextps(PolygonSet *fn){ nextps = fn ; }

		/*
		**		List Operations
		*/
		void	Add_to_poly_list(Polygon *pp);

		/*
		**		Utility functions
		*/
		void	Print(); 

		/*
		**		Application Specific
		*/
		int		Join_if_touching(Polygon *pp,Polygon *pq);
		void 	Merge_the_polygons();


		/*
		**		Display functions
		*/
		void	Display_by_phigs();


};

 
#endif
