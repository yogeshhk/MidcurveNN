/*******************************************************************************
*       FILENAME :    planeh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Plane
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _PLANEH_H
#define    _PLANEH_H
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "application.h"
 
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Plane {

	protected:

        /*
        **      Plane Identification
        */
		int		plane_id ;			// plane number
		int		plane_type ;		// type along which this plane is
		int		fixed ;				// flag to see whether value is fixed or not
									// TRUE means no modification allowed
									// FALSE means modification is allowed
		/*
		**		Information Representation
		*/
		double	plane_value ;		// numerical value of plane


	public :

		/*
        **      Constructors
        */
		Plane(){}	// Constructor
		Plane(int planeid,int planetype,double planevalue);

        /*
        **      Destructor
        */
		~Plane(){}

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
		int		Get_plane_id(){ return plane_id ; }
		void	Set_plane_id(int pid){ plane_id = pid ;}

		int		Get_plane_type(){ return plane_type; }
		void	Set_plane_type(int pty){ plane_type = pty ;}

		int		Get_fixed(){ return fixed ;}
		void	Set_fixed(int fx){ fixed = fx ;}
		int		Set_fixed(int fx,double d);

		double	Get_plane_value(){ return plane_value ;}
		void	Set_plane_value(double pval){ plane_value = pval;}

        /*
        **          Transformations
        */
        void        Scale(double val){ plane_value *= val;}

}; 
#endif
 
 

