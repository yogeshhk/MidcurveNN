/*******************************************************************************
*       FILENAME :    vector.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Vector
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _VECTOR_H_
#define _VECTOR_H_
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "application.h"
 
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Vector{

        /*
        **      Information Representation
        */
		double	dx ;		// directional cosine X component
		double	dy ;		// directional cosine Y component
		double	dz ;		// directional cosine Z component
		double	dist;		// distance of this vector from origin

	public :

	
        /*
        **      Constructors
        */
		Vector(){}
		Vector(double xx,double yy,double zz);

        /*
        **      Destructor
        */
		~Vector(){}

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
		double	Get_dcx(){ return dx;}
		double	Get_dcy(){ return dy;}
		double	Get_dcz(){ return dz;}


		/*
		**		Utility functions
		*/
        void    Print();
 
		/*
		**		Application Specific
		*/
        double  distance();
        double  distance(Vector *v);
        double  angle_xy();
        double  angle_yz();
        double  angle_zx();
 
		/*
		**		Operator Overloading
		*/
        Vector*  	operator=(Vector *rv);
        Vector* 	operator+(Vector* vv);
        Vector* 	operator-(Vector* vv);
        Vector* 	operator+();    // just like saying +4
        Vector* 	operator-();    // just like saying -4
        Vector* 	operator*(double f);
        Vector* 	operator/(double f);
        Vector* 	operator+=(Vector *v);
        Vector* 	operator-=(Vector *v);
        Vector* 	operator*=(Vector *v);
        Vector* 	operator/=(Vector *v);
        Vector* 	operator++();
        Vector* 	operator--();
        int     	operator>(Vector* v);
        int     	operator<(Vector* v);
        int     	operator>=(Vector* v);
        int     	operator<=(Vector* v);
        int     	operator==(Vector* v);
        int     	operator!=(Vector* v);

}; 
#endif
 
 

