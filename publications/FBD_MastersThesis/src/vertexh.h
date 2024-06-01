/*******************************************************************************
*       FILENAME :    vertexh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Vertex
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _VERTEX_H_
#define _VERTEX_H_
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "application.h"
 
#define 	ZERO 0.0001

/*******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Vertex {

        /*
        **      Vertex Identification
        */
		int	vertex_id ;	// vertex number

        /*
        **      Information Representation
        */
		double	x ;		// numerical value of x_coordinate 
		double	y ;		// numerical value of y_coordinate 
		double	z ;		// numerical value of z_coordinate 

		int		rem_flag;

        /*
        **      Link List members
        */
		Vertex*	nextv;		// next vertex
		Vertex*	prevv;		// previous vertex


	public :

        /*
        **      Constructors
        */
		Vertex(){rem_flag = 0;nextv = prevv = NULL; x= y=z=0.0;vertex_id = 0;}
		Vertex(int vid ,double vx,double vy,double vz);

        /*
        **      Destructor
        */
		~Vertex(){}

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
		int		Get_vertex_id(){ return vertex_id ; }
		int		Get_rem_flag(){ return rem_flag;}
		void	Set_rem_flag(int jj){rem_flag = jj;}

		double	Get_x(){ return x;}
		double	Get_y(){ return y;}
		double	Get_z(){ return z;}

		void	Set_x(double vx){x = vx ;}
		void	Set_y(double vy){y = vy ;}
		void	Set_z(double vz){z = vz ;}

		Vertex*	Get_nextv(){ return nextv;}
		Vertex*	Get_prevv(){ return prevv;}

		void	Set_nextv(Vertex* vv){ nextv = vv;}
		void	Set_prevv(Vertex* vv){ prevv = vv;}

        /*
        **      Utility functions
        */
		void	Print();

        /*
        **      Application Specific
        */
		double	distance();
		double	distance(Vertex *v);
		double	angle_xy();
		double	angle_yz();
		double	angle_zx();

		Vertex*  	operator=(Vertex *rv);
		Vertex*		operator+(Vertex* vv);
		Vertex*		operator-(Vertex* vv);
		Vertex*		operator+();	// just like saying +4
		Vertex*		operator-();	// just like saying -4
		Vertex* 	operator*(double f);
		Vertex* 	operator/(double f);
		Vertex* 	operator+=(Vertex *v);
		Vertex* 	operator-=(Vertex *v);
		Vertex* 	operator*=(Vertex *v);
		Vertex* 	operator/=(Vertex *v);
		Vertex* 	operator++();
		Vertex* 	operator--();
		int			operator>(Vertex* v);
		int			operator<(Vertex* v);
		int			operator>=(Vertex* v);
		int			operator<=(Vertex* v);
		int			operator==(Vertex* v);
		int			operator!=(Vertex* v);
		
}; 
#endif
 
 

