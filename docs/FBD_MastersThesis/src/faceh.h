/*******************************************************************************
*       FILENAME :    faceh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Face
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
#ifndef _FACEH_H_
#define _FACEH_H_

/******************************************************************************
*                       INCLUDE FILES
******************************************************************************/
 
#include "vertexh.h"

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class Face {

	protected :

		/*
		**		Face Identification
		*/
		int			face_id ;				// face number
		int			face_type ;				// face type
	
		/*
		**		Geometric Representation
		*/
		Vertex	*V1 , *V2 , *V3 , *V4 ;		// real ( encapsulated )block faces 

		/*
		**		Link List Data Members
		*/
		Face	*nextf ;					// netx face pointer


	public :
		
		/*
		**			Constructor
		*/
		Face(){}		
		Face(int fid ,int fit,Vertex *v1,Vertex *v2,Vertex *v3,Vertex *v4);

		/*
		**			Destructor
		*/
		~Face(){delete V1; delete V2;delete V3;delete V4;}

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
		int		Get_face_id()		{ return face_id ; }
		void	Set_face_id(int fi)	{ face_id = fi ;}

		int		Get_face_type()		{ return face_type ; }

		Vertex	*Get_V1()			{ return V1;}
		Vertex	*Get_V2()			{ return V2;}
		Vertex	*Get_V3()			{ return V3;}
		Vertex	*Get_V4()			{ return V4;}

		Face	*Get_nextf()		{ return nextf ;}
		void	Set_nextf(Face *fn)	{ nextf = fn ; }


}; 

#endif
 
 

