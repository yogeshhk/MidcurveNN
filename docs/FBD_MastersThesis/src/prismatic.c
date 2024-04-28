/*******************************************************************************
*       FILENAME :      prismatic.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Prismatic
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
*       NAME            :	Prismatic..... Constructor
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
 
 
Prismatic::Prismatic(char *blkid,Component *co ,double xmn,double xmx,
				double ymn,double ymx,double zmn,double zmx,int axis)
				:Block(blkid,co,xmn,xmx,ymn,ymx,zmn,zmx)
{
	
	prism_axis	=	axis;
	printf( "Came to Prismatic constructor with no. %d \n",prism_axis);
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
 

void Prismatic::Display_by_phigs()
{

        double  pxn     = Xmin->Get_plane_value();
        double  pxx     = Xmax->Get_plane_value();
        double  pyn     = Ymin->Get_plane_value();
        double  pyx     = Ymax->Get_plane_value();
        double  pzn     = Zmin->Get_plane_value();
        double  pzx     = Zmax->Get_plane_value();
 

	//Face *tracef = Create_Faces();	

	Ppoint3			pt[12][4];	// 12 side faces with 4 points
	Ppoint3			ptb[2][12];	// 2 top and bottom faces with 12 points
	Ppoint_list3	faces[14];	// total 14 faces


	int i,j;

	for(i=0;i<12;i++){

		faces[i].num_points 	= 4;
		faces[i].points		= pt[i];
	}

	faces[12].num_points	= 12;		// bottom face
	faces[12].points	= ptb[0];


	faces[13].num_points	= 12;		// top face
	faces[13].points	= ptb[1];


    pset_linetype( PLINE_SOLID );
	pset_linewidth((Pfloat) 2.0);
    pset_line_colr_ind( (Pint) 5);

	double theta = 3.142/6;				// 30 degrees in radiance

	double bcx;							// bottom center
    double bcy;
    double bcz;
 
    double tcx;							// top center
    double tcy;
    double tcz;


	switch(prism_axis){

		case XAXIS :

			bcx = pxn;
			bcy = ( pyx + pyn )/2;
			bcz = ( pzx + pzn )/2;

			tcx = pxx;
			tcy = bcy;
			tcz = bcz;

			for(i=0;i<12;i++){

				ptb[0][i].x= pxn;


				ptb[1][i].x= pxx;

			}

			for(j=0;j<12;j++){
			
				int k = (j+1)%12;	// next point

				pt[j][0].x= pxx;

				pt[j][1].x= pxx;

				pt[j][2].x= pxn;

				pt[j][3].x= pxn;

			
			}

			for(int m=0;m<14;m++){

                		ppolyline3( &faces[m]);
			}

			break;

                case YAXIS :
 
                        bcy = pyn;
                        bcz = ( pzx + pzn )/2;
                        bcx = ( pxx + pxn )/2;
 
                        tcy = pyx;
                        tcz = bcz;
                        tcx = bcx;
 
                        for(i=0;i<12;i++){
 
                                ptb[1][i].y= pyx ;
 
                        }
 
                        for(j=0;j<12;j++){
 
                                int k = (j+1)%12;       // next point
 
                                pt[j][0].y= pyx;
 
                                pt[j][1].y= pyx;
 
                                pt[j][2].y= pyn;
 
                                pt[j][3].y= pyn;
 
 
                        }
 
                        for(j=0;j<14;j++){
 
                                ppolyline3( &faces[j]);
                        }
 
                        break;

                case ZAXIS :
 
                        bcz = pzn;
                        bcx = ( pxx + pxn )/2;
                        bcy = ( pyx + pyn )/2;
 
                        tcz = pzx;
                        tcx = bcx;
                        tcy = bcy;
 
                        for(i=0;i<12;i++){
 
                                ptb[0][i].z= pzn ;
 
 
                                ptb[1][i].z= pzx ;
 
 
                        }
 
                        for(j=0;j<12;j++){
 
                                int k = (j+1)%12;       // next point
 
                                pt[j][0].z= pzx;
 
                                pt[j][1].z= pzx;
 
                                pt[j][2].z= pzn;
 
                                pt[j][3].z= pzn;
 
 
                        }
 
                        for(j=0;j<14;j++){
 
                                ppolyline3( &faces[j]);
                        }
 
                        break;

	}

		//DrawAxes(display_max);

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
 
Polygon* Prismatic::Create_Polygons(){

	// Need to make two polygons , one for top of the
	// prismatic and one for the bottom.It may have about 12 vertices each
	// so as to approximate circle

}

/*******************************************************************************
*
*       NAME            :   Contribute_dim_Faces()
*
*       DESCRIPTION     :
*
*       INPUT           : Nothing
*
*       OUTPUT          :
*
******************************************************************************/

Face* Prismatic::Contribute_dim_Faces(){


	/*
	**		Depending on the axis ,this function returns
	**		two intersecting planes(line of intersection is the central axis)
	**		and also top & bottom planes in the perpendicular direction of
	**		axis
	*/

    /*
 
        Values of Min_Max planes are sufficient to calculate
        all the 8 vertices and 6 faces with values
        Verices are oriented such that by right hand rule
        the direction of thumb is away from the material
 
    */
 
 
    // lets get values from planes and store them temporarily
 
    double  pxn = Xmin->Get_plane_value();
    double  pxx = Xmax->Get_plane_value();
    double  pyn = Ymin->Get_plane_value();
    double  pyx = Ymax->Get_plane_value();
    double  pzn = Zmin->Get_plane_value();
    double  pzx = Zmax->Get_plane_value();
 
	// Middle plane values

	double 	pxm	= (pxx -pxn)/2;
	double 	pym	= (pyx -pyn)/2;
	double 	pzm	= (pzx -pzn)/2;

    // bottom four vertices
 
    Vertex *v1  = new Vertex(1,pxn,pyn,pzx);
    Vertex *v2  = new Vertex(2,pxx,pyn,pzx);
    Vertex *v3  = new Vertex(3,pxx,pyn,pzn);
    Vertex *v4  = new Vertex(4,pxn,pyn,pzn);
 
    // top four vertices
 
    Vertex *v5  = new Vertex(5,pxn,pyx,pzx);
    Vertex *v6  = new Vertex(6,pxx,pyx,pzx);
    Vertex *v7  = new Vertex(7,pxx,pyx,pzn);
    Vertex *v8  = new Vertex(8,pxn,pyx,pzn);

	// Middle x face

    Vertex *v9  = new Vertex(9, pxm,pyx,pzx);
    Vertex *v10 = new Vertex(10,pxm,pyx,pzn);
    Vertex *v11 = new Vertex(11,pxm,pyn,pzx);
    Vertex *v12 = new Vertex(12,pxm,pyn,pzn);

	// Middle y face

    Vertex *v13 = new Vertex(13,pxn,pym,pzx);
    Vertex *v14 = new Vertex(14,pxm,pym,pzx);
    Vertex *v15 = new Vertex(15,pxm,pym,pzn);
    Vertex *v16 = new Vertex(16,pxn,pym,pzn);

	// Middle z face

    Vertex *v17 = new Vertex(17,pxn,pyn,pzm);
    Vertex *v18 = new Vertex(18,pxn,pym,pzm);
    Vertex *v19 = new Vertex(19,pxm,pym,pzm);
    Vertex *v20 = new Vertex(20,pxm,pyn,pzm);

	/*
	**		Two middle planes and top & bottom planes
	*/

	Face	*f1;
	Face	*f2;
	Face	*f3;
	Face	*f4;

	switch(prism_axis){

		case XAXIS 	:

        		f1 	= new Face(1,XAXIS,v2,v3,v7,v6);
        		f2  = new Face(2,XAXIS,v4,v1,v5,v8);
        		f3  = new Face(3,YAXIS,v13,v14,v15,v16);
        		f4  = new Face(4,ZAXIS,v17,v18,v19,v20);
        		f1->Set_nextf(f2);
        		f2->Set_nextf(f3);
        		f3->Set_nextf(f4);
        		f4->Set_nextf((Face*)NULL);
				break;

		case YAXIS 	:

        		f1 	= new Face(1,YAXIS,v1,v4,v3,v2);
        		f2  = new Face(2,YAXIS,v5,v6,v7,v8);
        		f3  = new Face(3,XAXIS,v9,v10,v11,v12);
        		f4  = new Face(4,ZAXIS,v17,v18,v19,v20);
        		f1->Set_nextf(f2);
        		f2->Set_nextf(f3);
        		f3->Set_nextf(f4);
        		f4->Set_nextf((Face*)NULL);
				break;

		case ZAXIS 	:
		default		:
        		f1 	= new Face(1,ZAXIS,v3,v4,v8,v7);
        		f2  = new Face(2,ZAXIS,v1,v2,v6,v5);
        		f3  = new Face(3,YAXIS,v13,v14,v15,v16);
        		f4  = new Face(4,XAXIS,v9,v10,v11,v12);
        		f1->Set_nextf(f2);
        		f2->Set_nextf(f3);
        		f3->Set_nextf(f4);
        		f4->Set_nextf((Face*)NULL);
				break;

	}


    return f1 ; // return the pointer to the first face of list
 
}

