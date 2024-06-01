/*******************************************************************************
*       FILENAME :      subwedge.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class SubWedge
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JUN 5, 1995.
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
*       NAME            :	SubWedge..... Constructor
*
*       DESCRIPTION     :	This is second constructor. Gets all the values
*			 				reqd. to compute planes etc..Calls constructors of
*			 				private members with appropraite values 
*
*       INPUT           : 	id , parent component and plane values
*
*       OUTPUT          : 	Undefined by C++
*
*******************************************************************************/
 
 
SubWedge::SubWedge(char *b,Component *co ,
			double xmn,double xmx,double ymn,double ymx,double zmn,double zmx,
			int ax,int p1,int p2)
			:Wedge(b,co,xmn,xmx,ymn,ymx,zmn,zmx,ax,p1,p2)
{

	block_type	=	SWEDGE;

	printf( "Came to SubWedge constructor planes %d %d %d  \n",ax,p1,p2);
} 


/*******************************************************************************
*
*       NAME            :	Display_by_phigs()
*
*       DESCRIPTION     :	Temporarily creates list of faces and then
*			 				traverses each face to get the vertices
*			 				Uses PHIGS calls to display
*
*       INPUT           : 	Nothing
*
*       OUTPUT          : 	Creation of structure in phigs
*
******************************************************************************/
 

void SubWedge::Display_by_phigs()
{

        double  pxn     = Xmin->Get_plane_value();
        double  pxx     = Xmax->Get_plane_value();
        double  pyn     = Ymin->Get_plane_value();
        double  pyx     = Ymax->Get_plane_value();
        double  pzn     = Zmin->Get_plane_value();
        double  pzx     = Zmax->Get_plane_value();
 

	Ppoint3			pt[3][4];	// 3 side faces with 4 points each 
	Ppoint3			ptb[2][3];	// 2 top and bottom faces with 3 points
	Ppoint_list3	faces[5];	// total 14 faces


	int i,j;

	for(i=0;i<3;i++){

		faces[i].num_points 	= 4;
		faces[i].points		= pt[i];
	}

	faces[3].num_points	= 3;		// bottom face
	faces[3].points	= ptb[0];


	faces[4].num_points	= 3;		// top face
	faces[4].points	= ptb[1];


    pset_linetype( PLINE_SOLID );
	pset_linewidth((Pfloat) 2.0);
    pset_line_colr_ind( (Pint) 7);


	/*
	**		The data of ButtingPlane1 and 2 are enough to draw them
	**		independant of other information
	**		
	**		pt[0] is buttingplane1
	**		pt[1] is buttingpalne2
	**
	**		I have not tested following functions for all combinations
	**		of butting planes. I should find (later) a method that is
	**		consize, and simple to understand. I will leave that for now.
	**
	*/

	switch(butting_plane1){

		case XMIN:
			for(i=0;i<4;i++)pt[0][i].x	=	(Pfloat)pxn;
			pt[0][3].y	=	(Pfloat)pyn;
			pt[0][3].z	=	(Pfloat)pzn;
			pt[0][2].y	=	(Pfloat)pyn;
			pt[0][2].z	=	(Pfloat)pzx;
			pt[0][1].y	=	(Pfloat)pyx;
			pt[0][1].z	=	(Pfloat)pzx;
			pt[0][0].y	=	(Pfloat)pyx;
			pt[0][0].z	=	(Pfloat)pzn;
			break;

        case XMAX:
            for(i=0;i<4;i++)pt[0][i].x  =   (Pfloat)pxx;
            pt[0][3].y  =   (Pfloat)pyn;
            pt[0][3].z  =   (Pfloat)pzn;
            pt[0][2].y  =   (Pfloat)pyx;
            pt[0][2].z  =   (Pfloat)pzn;
            pt[0][1].y  =   (Pfloat)pyx;
            pt[0][1].z  =   (Pfloat)pzx;
            pt[0][0].y  =   (Pfloat)pyn;
            pt[0][0].z  =   (Pfloat)pzx;
            break;

        case YMIN:
            for(i=0;i<4;i++)pt[0][i].y  =   (Pfloat)pyn;
            pt[0][3].z  =   (Pfloat)pzn;
            pt[0][3].x  =   (Pfloat)pxn;
            pt[0][2].z  =   (Pfloat)pzn;
            pt[0][2].x  =   (Pfloat)pxx;
            pt[0][1].z  =   (Pfloat)pzx;
            pt[0][1].x  =   (Pfloat)pxx;
            pt[0][0].z  =   (Pfloat)pzx;
            pt[0][0].x  =   (Pfloat)pxn;
            break;
 
        case YMAX:
            for(i=0;i<4;i++)pt[0][i].y  =   (Pfloat)pyx;
            pt[0][3].z  =   (Pfloat)pzn;
            pt[0][3].x  =   (Pfloat)pxn;
            pt[0][2].z  =   (Pfloat)pzx;
            pt[0][2].x  =   (Pfloat)pxn;
            pt[0][1].z  =   (Pfloat)pzx;
            pt[0][1].x  =   (Pfloat)pxx;
            pt[0][0].z  =   (Pfloat)pzn;
            pt[0][0].x  =   (Pfloat)pxx;
            break;
 
		case ZMIN:
            for(i=0;i<4;i++)pt[0][i].z  =   (Pfloat)pzn;
            pt[0][3].x  =   (Pfloat)pxn;
            pt[0][3].y  =   (Pfloat)pyn;
            pt[0][2].x  =   (Pfloat)pxn;
            pt[0][2].y  =   (Pfloat)pyx;
            pt[0][1].x  =   (Pfloat)pxx;
            pt[0][1].y  =   (Pfloat)pyx;
            pt[0][0].x  =   (Pfloat)pxx;
            pt[0][0].y  =   (Pfloat)pyn;
            break;

        case ZMAX:
            for(i=0;i<4;i++)pt[0][i].z  =   (Pfloat)pzx;
            pt[0][3].x  =   (Pfloat)pxn;
            pt[0][3].y  =   (Pfloat)pyn;
            pt[0][2].x  =   (Pfloat)pxx;
            pt[0][2].y  =   (Pfloat)pyn;
            pt[0][1].x  =   (Pfloat)pxx;
            pt[0][1].y  =   (Pfloat)pyx;
            pt[0][0].x  =   (Pfloat)pxn;
            pt[0][0].y  =   (Pfloat)pyx;
            break;

		default:
			printf("Bad choice\n");
			break;

	}

	switch(butting_plane2){

        case XMIN:
            for(i=0;i<4;i++)pt[1][i].x  =   (Pfloat)pxn;
            pt[1][3].y  =   (Pfloat)pyn;
            pt[1][3].z  =   (Pfloat)pzn;
            pt[1][2].y  =   (Pfloat)pyn;
            pt[1][2].z  =   (Pfloat)pzx;
            pt[1][1].y  =   (Pfloat)pyx;
            pt[1][1].z  =   (Pfloat)pzx;
            pt[1][0].y  =   (Pfloat)pyx;
            pt[1][0].z  =   (Pfloat)pzn;
            break;
 
        case XMAX:
            for(i=0;i<4;i++)pt[1][i].x  =   (Pfloat)pxx;
            pt[1][3].y  =   (Pfloat)pyn;
            pt[1][3].z  =   (Pfloat)pzn;
            pt[1][2].y  =   (Pfloat)pyx;
            pt[1][2].z  =   (Pfloat)pzn;
            pt[1][1].y  =   (Pfloat)pyx;
            pt[1][1].z  =   (Pfloat)pzx;
            pt[1][0].y  =   (Pfloat)pyn;
            pt[1][0].z  =   (Pfloat)pzx;
            break;
 
        case YMIN:
            for(i=0;i<4;i++)pt[1][i].y  =   (Pfloat)pyn;
            pt[1][3].z  =   (Pfloat)pzn;
            pt[1][3].x  =   (Pfloat)pxn;
            pt[1][2].z  =   (Pfloat)pzn;
            pt[1][2].x  =   (Pfloat)pxx;
            pt[1][1].z  =   (Pfloat)pzx;
            pt[1][1].x  =   (Pfloat)pxx;
            pt[1][0].z  =   (Pfloat)pzx;
            pt[1][0].x  =   (Pfloat)pxn;
            break;
 
        case YMAX:
            for(i=0;i<4;i++)pt[1][i].y  =   (Pfloat)pyx;
            pt[1][3].z  =   (Pfloat)pzn;
            pt[1][3].x  =   (Pfloat)pxn;
            pt[1][2].z  =   (Pfloat)pzx;
            pt[1][2].x  =   (Pfloat)pxn;
            pt[1][1].z  =   (Pfloat)pzx;
            pt[1][1].x  =   (Pfloat)pxx;
            pt[1][0].z  =   (Pfloat)pzn;
            pt[1][0].x  =   (Pfloat)pxx;
            break;
 
        case ZMIN:
            for(i=0;i<4;i++)pt[1][i].z  =   (Pfloat)pzn;
            pt[1][3].x  =   (Pfloat)pxn;
            pt[1][3].y  =   (Pfloat)pyn;
            pt[1][2].x  =   (Pfloat)pxn;
            pt[1][2].y  =   (Pfloat)pyx;
            pt[1][1].x  =   (Pfloat)pxx;
            pt[1][1].y  =   (Pfloat)pyx;
            pt[1][0].x  =   (Pfloat)pxx;
            pt[1][0].y  =   (Pfloat)pyn;
            break;
 
		case ZMAX:
            for(i=0;i<4;i++)pt[1][i].z  =   (Pfloat)pzx;
            pt[1][3].x  =   (Pfloat)pxn;
            pt[1][3].y  =   (Pfloat)pyn;
            pt[1][2].x  =   (Pfloat)pxx;
            pt[1][2].y  =   (Pfloat)pyn;
            pt[1][1].x  =   (Pfloat)pxx;
            pt[1][1].y  =   (Pfloat)pyx;
            pt[1][0].x  =   (Pfloat)pxn;
            pt[1][0].y  =   (Pfloat)pyx;
            break;
 
        default:
            printf("Bad choice\n");
            break;
 
	}


	/*
	**		Now formulating the third rectangle
	**		in terms of known points
	*/

	pt[2][3].x	=	pt[1][1].x;
	pt[2][3].y	=	pt[1][1].y;
	pt[2][3].z	=	pt[1][1].z;

	pt[2][2].x	=	pt[0][3].x;
	pt[2][2].y	=	pt[0][3].y;
	pt[2][2].z	=	pt[0][3].z;

	pt[2][1].x	=	pt[0][2].x;
	pt[2][1].y	=	pt[0][2].y;
	pt[2][1].z	=	pt[0][2].z;

	pt[2][0].x	=	pt[1][2].x;
	pt[2][0].y	=	pt[1][2].y;
	pt[2][0].z	=	pt[1][2].z;


	/*
	**		Top Triangle
	*/

    ptb[0][2].x  =   pt[0][1].x;
    ptb[0][2].y  =   pt[0][1].y;
    ptb[0][2].z  =   pt[0][1].z;

    ptb[0][1].x  =   pt[1][2].x;
    ptb[0][1].y  =   pt[1][2].y;
    ptb[0][1].z  =   pt[1][2].z;
 
    ptb[0][0].x  =   pt[0][2].x;
    ptb[0][0].y  =   pt[0][2].y;
    ptb[0][0].z  =   pt[0][2].z;
 

	/*
	**		Bottom Triangle
	*/

    ptb[1][2].x  =   pt[1][0].x;
    ptb[1][2].y  =   pt[1][0].y;
    ptb[1][2].z  =   pt[1][0].z;
 
    ptb[1][1].x  =   pt[0][3].x;
    ptb[1][1].y  =   pt[0][3].y;
    ptb[1][1].z  =   pt[0][3].z;
 
    ptb[1][0].x  =   pt[1][1].x;
    ptb[1][0].y  =   pt[1][1].y;
    ptb[1][0].z  =   pt[1][1].z;
 
	/*
	**		Drawing
	*/

	for(j=0;j<5;j++)ppolyline3( &faces[j]);
 
}
/*******************************************************************************
*
*       NAME            :	Create_Polygons()
*
*       DESCRIPTION     :
*
*       INPUT           : Nothing
*
*       OUTPUT          :
*
******************************************************************************/
 
Polygon* SubWedge::Create_Polygons(){

	// Need to make two polygons , one for top of the
	// subwedge and one for the bottom.

}

