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

	int	polygon_id ;		// Polygon number
	int	polygon_axis;		// face type
	int num_of_points;
	Vector  *normal;		// normal to the surface
	double	polygon_value;		// positional value on the axis
	
	Vertex	*V_list_head;		// circular doubly linked list

	Polygon *nextp;			// next polygon in the list
	Polygon *prevp;			// previous	polygon in the list

	public :
		
		Polygon(){}		// constructor
		Polygon(Face *ff);		// constructor

		Polygon(int pid ,int pa,int pv ,Vertex *v1,Vertex *v2,Vertex *v3,Vertex *v4);

		~Polygon(){}		// destructor

		int	Get_polygon_id(){return polygon_id; }
		void	Set_polygon_id(int fi){ polygon_id = fi ;}

		int	Get_num_of_points(){return num_of_points; }
		void	Set_num_of_points(int fi){ num_of_points= fi ;}

		int	Get_polygon_axis(){return polygon_axis; }
		double	Get_polygon_value(){return polygon_value; }

		Vertex	*Get_V_list_head(){ return V_list_head;}
		void	Set_V_list_head(Vertex *vv){ V_list_head = vv;}

		Polygon	*Get_nextp(){	return nextp;}
		void	Set_nextp(Polygon *fn){ nextp = fn ; }
		Polygon	*Get_prevp(){	return prevp;}
		void	Set_prevp(Polygon *fn){ prevp = fn ; }

        void    Display_by_phigs();

		Vector*	Get_normal(){	return normal;}
		void	Add_to_the_V_list(Vertex* vv);
		void	Insert_before(Vertex *before,Vertex *vv);
		void	Insert_after(Vertex *after,Vertex *vv);
		void 	Print_list();

}; 

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/


class PolygonSet{

	protected :

		int		polygonset_id;
		int		num_polygons;
		Vertex		*plane_normal;

		// Normal has three direction cosines ,Rightnow I dont have
		// any special class called class Normal,and its really
		// nothing different than class Vertex in terms of members

		double		plane_value;	// of this polygon set
		Polygon 	*poly_list_head;// list of polygons

		PolygonSet	*nextps;	// next polygon Set

	public :

		PolygonSet();
		~PolygonSet(){}
		int		Get_polygonset_id(){ return polygonset_id;}
		void	Set_polygonset_id(int ii){ polygonset_id = ii;}

        double	Get_polygon_value(){return plane_value; }
		Polygon *Get_poly_list_head(){ return poly_list_head;}
		void	Add_to_poly_list(Polygon *pp);
		void	Print(); 
		int		Join_if_touching(Polygon *pp,Polygon *pq);
		void 	Merge_the_polygons();
		void	Display_by_phigs();

        PolygonSet *Get_nextps(){   return nextps;}
        void    Set_nextps(PolygonSet *fn){ nextps = fn ; }
 

};

 
#endif
