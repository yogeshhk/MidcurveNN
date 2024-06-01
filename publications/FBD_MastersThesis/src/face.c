/*******************************************************************************
*       FILENAME :      face.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Face
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   MAY 29, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"            /* Classes Declarations :header file */
#include <string.h>
 

/*******************************************************************************
*
*       NAME            :Face..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to set vertices etc..
*
*       INPUT           : id , and four vertices
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Face::Face(int fid=1 ,int fit=0,Vertex *v1=NULL,Vertex *v2=NULL,Vertex *v3=NULL,Vertex *v4=NULL) 
{

	face_id = fid ;
	face_type= fit;

	V1 = v1;
	V2 = v2;
	V3 = v3;
	V4 = v4;

	nextf = NULL;

}
 

