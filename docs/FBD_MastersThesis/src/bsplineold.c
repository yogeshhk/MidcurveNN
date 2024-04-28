/*******************************************************************************
*       FILENAME :      bspline.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Bspline
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
*       NAME            :   Bspline..... Constructor
*
*       DESCRIPTION     :   
*
*       INPUT           :
*
*       OUTPUT          :   
*
*******************************************************************************/

Bspline::Bspline()
{

    u_order     =   3   ;
    u_num_pts   =   20  ;       //  points are from 0 to 19
    
    /*
    **      Knot vector has multiplicity of 3 at ends
    */

	bsp_axis	=	cyl_axis;

    u_knot_vector[0]    =   1.0;
    u_knot_vector[1]    =   1.0;
    u_knot_vector[21]   =   19.0;
    u_knot_vector[22]   =   19.0;

    for(int j=0;j<19;j++)u_knot_vector[j+2]  =   j+1;

    for(int i=0;i<20;i++){
        u_control_pts[i].Set_x(0.0);
        u_control_pts[i].Set_y(0.0);
        u_control_pts[i].Set_z(0.0);

    }
    printf( "Came to Bspline constructor planes\n");
}

/*******************************************************************************
*
*       NAME            :	Bspline..... Constructor
*
*       DESCRIPTION     :	This is second constructor. Gets all the values
*			 				reqd. to compute planes etc..Calls constructors of
*			 				private members with appropraite values 
*
*       INPUT           : 	
*
*       OUTPUT          : 	Undefined by C++
*
*******************************************************************************/
 
Bspline::Bspline(	char *b,Component *co ,
            double xmn,double xmx,double ymn,double ymx,double zmn,double zmx,
            int ax,Vertex* cpts)
            :Prismatic(b,co,xmn,xmx,ymn,ymx,zmn,zmx,ax)

{

	u_order		=	3	;
	u_num_pts	=	20	;		//	points are from 0 to 19

	/*
	**		Knot vector has multiplicity of 3 at ends
	*/

    u_knot_vector[0]    =   1.0;
    u_knot_vector[1]    =   1.0;
    u_knot_vector[21]   =   19.0;
    u_knot_vector[22]   =   19.0;

    for(int j=0;j<19;j++)u_knot_vector[j+2]  =   j+1;

	bsp_axis	=	cyl_axis;

	for(int i=0;i<20;i++){

		u_control_pts[i].Set_x(cpts[i].Get_x());
		u_control_pts[i].Set_y(cpts[i].Get_y());
		u_control_pts[i].Set_z(cpts[i].Get_z());
	}

	printf( "Came to Bspline constructor planes %d \n",ax);
}
 
/*******************************************************************************
*
*       NAME            :   Bspline..... Destructor
*
*       DESCRIPTION     :   
*
*       INPUT           :
*
*       OUTPUT          :   
*
*******************************************************************************/

Bspline::~Bspline()
{


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
 

void Bspline::Display_by_phigs()
{

        double  pxn     = Xmin->Get_plane_value();
        double  pxx     = Xmax->Get_plane_value();
        double  pyn     = Ymin->Get_plane_value();
        double  pyx     = Ymax->Get_plane_value();
        double  pzn     = Zmin->Get_plane_value();
        double  pzx     = Zmax->Get_plane_value();
 
    Face *tracef = Block::Create_Faces(); 

    Ppoint3         pt[6][4];       // six faces & each has 4 points
    Ppoint_list3    faces[6];       //six faces


    for(int i=0;i<6;i++){

        faces[i].num_points     = 4;
        faces[i].points     = pt[i];
    }


    int j=0;            // temporary counter

    while(tracef){

        Vertex *v1 = tracef->Get_V1();
        Vertex *v2 = tracef->Get_V2();
        Vertex *v3 = tracef->Get_V3();
        Vertex *v4 = tracef->Get_V4();

        pt[j][0].x      = (Pfloat)v1->Get_x();
        pt[j][0].y      = (Pfloat)v1->Get_y();
        pt[j][0].z      = (Pfloat)v1->Get_z();

        pt[j][1].x      = (Pfloat)v2->Get_x();
        pt[j][1].y      = (Pfloat)v2->Get_y();
        pt[j][1].z      = (Pfloat)v2->Get_z();

        pt[j][2].x      = (Pfloat)v3->Get_x();
        pt[j][2].y      = (Pfloat)v3->Get_y();
        pt[j][2].z      = (Pfloat)v3->Get_z();

        pt[j][3].x      = (Pfloat)v4->Get_x();
        pt[j][3].y      = (Pfloat)v4->Get_y();
        pt[j][3].z      = (Pfloat)v4->Get_z();


        pset_linewidth((Pfloat) 2.0);
        pset_line_colr_ind( (Pint) 4);
        ppolyline3( &faces[j]);
        tracef = tracef->Get_nextf();
        j++;
    }


	/*
	**		We will be passing three curves (series) of 20 points each
	*/

	Vertex	min[20];		//	first series
	Vertex	mid[20];		//	second series
	Vertex	max[20];		//	third series

	/*
	**		First I will copy control points to all three curves
	**		then depending on the axis of the block , offset the
	**		dimensions by length/2 ammount so as to get Min,Mid,Max
	**		curve
	*/

	int i;

    for(i=0;i<20;i++){

        min[i].Set_x(u_control_pts[i].Get_x());
        min[i].Set_y(u_control_pts[i].Get_y());
        min[i].Set_z(u_control_pts[i].Get_z());

        mid[i].Set_x(u_control_pts[i].Get_x());
        mid[i].Set_y(u_control_pts[i].Get_y());
        mid[i].Set_z(u_control_pts[i].Get_z());

        max[i].Set_x(u_control_pts[i].Get_x());
        max[i].Set_y(u_control_pts[i].Get_y());
        max[i].Set_z(u_control_pts[i].Get_z());

    }

	Ppoint3     surf_points[60];

	switch(bsp_axis){

		case XAXIS:

			for(i=0;i<20;i++){
				min[i].Set_z(pzn);
				mid[i].Set_z((pzx+pzn)/2.0);
				max[i].Set_z(pzx);
			}
    		for(i=0;i<20;i++){
        		surf_points[i+40].x = (Pfloat)min[i].Get_x();
        		surf_points[i+40].y = (Pfloat)min[i].Get_y();
        		surf_points[i+40].z = (Pfloat)pzn;

				/*
        		printf("[%3.1f %3.1f %3.1f]  ",min[i].Get_x(),
                        		min[i].Get_y(),pzn);
				*/
        		surf_points[i+20].x = (Pfloat)mid[i].Get_x();
        		surf_points[i+20].y = (Pfloat)mid[i].Get_y();
        		surf_points[i+20].z = (Pfloat)((pzx+pzn)/2.0);

				/*
        		printf("[%3.1f %3.1f %3.1f]  ",(pzx+pzn)/2.0,
                        		mid[i].Get_y(),mid[i].Get_z());
				*/

        		surf_points[i].x    = (Pfloat)max[i].Get_x();
        		surf_points[i].y    = (Pfloat)max[i].Get_y();
        		surf_points[i].z    = (Pfloat)pzx;

				/*
        		printf("[%3.1f %3.1f %3.1f] \n ",pzx,
                        		max[i].Get_y(),max[i].Get_z());
				*/
    		}

			break;

		case YAXIS:
			for(i=0;i<20;i++){
				min[i].Set_x(pxn);
				mid[i].Set_x((pxx+pxn)/2.0);
				max[i].Set_x(pxx);
			}
    		for(i=0;i<20;i++){
        		surf_points[i+40].x = (Pfloat)pxn;
        		surf_points[i+40].y = (Pfloat)min[i].Get_y();
        		surf_points[i+40].z = (Pfloat)min[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f]  ",pxn,
                        		min[i].Get_y(),min[i].Get_z());
        		*/
        		surf_points[i+20].x = (Pfloat)((pxx+pxn)/2.0);
        		surf_points[i+20].y = (Pfloat)mid[i].Get_y();
        		surf_points[i+20].z = (Pfloat)mid[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f]  ",(pxx+pxn)/2.0,
                        		mid[i].Get_y(),mid[i].Get_z());
        		*/

        		surf_points[i].x    = (Pfloat)pxx;
        		surf_points[i].y    = (Pfloat)max[i].Get_y();
        		surf_points[i].z    = (Pfloat)max[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f] \n ",pxx,
                        		max[i].Get_y(),max[i].Get_z());
        		*/

    		}

			break;

		case ZAXIS:
			for(i=0;i<20;i++){
				min[i].Set_y(pyn);
				mid[i].Set_y((pyx+pyn)/2.0);
				max[i].Set_y(pyx);
			}
    		for(i=0;i<20;i++){
        		surf_points[i+40].x = (Pfloat)min[i].Get_x();
        		surf_points[i+40].y = (Pfloat)pyn;
        		surf_points[i+40].z = (Pfloat)min[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f]  ",pyn,
                        		min[i].Get_y(),min[i].Get_z());
        		*/
        		surf_points[i+20].x = (Pfloat)mid[i].Get_x();
        		surf_points[i+20].y = (Pfloat)((pyx+pyn)/2.0);
        		surf_points[i+20].z = (Pfloat)mid[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f]  ",(pyx+pyn)/2.0,
                        		mid[i].Get_y(),mid[i].Get_z());
        		*/

        		surf_points[i].x    = (Pfloat)max[i].Get_x();
        		surf_points[i].y    = (Pfloat)pyx;
        		surf_points[i].z    = (Pfloat)max[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f] \n ",pyx,
                        		max[i].Get_y(),max[i].Get_z());
        		*/

    		}

			break;

			}

	/*
	**		Ref : pg 253 PHIGS Programming manual
	*/


	Pfloat_list			uknot_list,vknot_list;
	Ppoint_grid34		grid;
	Ppara_surf_characs  psc;
	Pint	uorder	=	3;		//	stored in class	
	Pint	vorder	=	3;

	static  Pfloat      uknots[] = { 0, 0, 0, 1,2,3,4,5,6,7,8,9,10,
								 	11,12,13,14,15,16,17,18,18,18};
	static  Pfloat      vknots[] = { 0, 0, 0, 1, 1, 1 };

    pset_linetype( PLINE_SOLID );
    pset_line_colr_ind( (Pint) 4);
    pset_linewidth((Pfloat) 1.0);

    /* Assign the surface parameters. */
    uorder = 3, vorder = 3;
    grid.num_points.u_dim = 20;
    grid.num_points.v_dim = 3;
    grid.points.point3d = surf_points;
    uknot_list.num_floats = sizeof(uknots)/sizeof(uknots[0]);
    uknot_list.floats = uknots;
    vknot_list.num_floats = sizeof(vknots)/sizeof(vknots[0]);
    vknot_list.floats = vknots;

    /* Create the structure. */
    pset_view_ind( (Pint) 1 );
    pset_int_style( PSTYLE_EMPTY);

    /* Set the parametric surface characteristics. */
    psc.psc_3.placement = PCP_UNIFORM;
    psc.psc_3.u_count = 20;
    psc.psc_3.v_count = 3;
    pset_para_surf_characs( PSC_ISOPARAMETRIC_CURVES, &psc );

    /* Set the surface approximation criteria. */
    pset_surf_approx( PSURF_CONSTANT_PARAMETRIC_BETWEEN_KNOTS,
        (Pfloat) 10.0, (Pfloat) 10.0 );

	pnuni_bsp_surf( uorder, vorder, &uknot_list, &vknot_list,
        PNON_RATIONAL, &grid, (Pint) 0, (Ptrimcurve_list*) NULL );

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

Face* Bspline::Contribute_dim_Faces(){


    /*
    **      Depending on the axis ,this function returns
    **      two intersecting planes(line of intersection is the central axis)
    **      and also top & bottom planes in the perpendicular direction of
    **      axis
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

	double	pxl	= pxx -pxn;
	double	pyl	= pyx -pyn;
	double	pzl	= pzx -pzn;

	//	divisions
	double	pxd	= pxl/5.0;
	double	pyd	= pyl/5.0;
	double	pzd	= pzl/5.0;

    // Middle plane values

    double  pxm = (pxx -pxn)/2;
    double  pym = (pyx -pyn)/2;
    double  pzm = (pzx -pzn)/2;

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

    /*
    **      Two middle planes and top & bottom planes
    */

    Face    *f1;
    Face    *f2;

    Face    *f3;
    Face    *f4;

    switch(bsp_axis){

        case XAXIS  :

                break;
        case YAXIS  :

                f1  = new Face(1,XAXIS,v1,v4,v8,v5);
                f2  = new Face(2,XAXIS,v2,v3,v7,v6);
                f3  = new Face(3,YAXIS,v1,v4,v3,v2);
                f3  = new Face(4,ZAXIS,v1,v2,v6,v5);
                f4  = new Face(5,ZAXIS,v3,v4,v8,v7);

				Vertex *vzdim[16];

				//	First Z plane is at Zmin and then at Zmin+pzd

				for(int g=0;g<4;g++){
					vzdim[0+g*4]	=new Vertex(9+g*4,pxx,pyn,pzn+(g+1)*pzd);
					vzdim[1+g*4]	=new Vertex(10+g*4,pxn,pyn,pzn+(g+1)*pzd);
					vzdim[2+g*4]	=new Vertex(11+g*4,pxn,pyx,pzn+(g+1)*pzd);
					vzdim[3+g*4]	=new Vertex(12+g*4,pxx,pyx,pzn+(g+1)*pzd);
				}
	

				//	Here we are taking 4 planes more between
				//	MIN and MAX along Z axis for dimPlanes.

                f1->Set_nextf(f2);
                f2->Set_nextf(f3);
                f3->Set_nextf(f4);
                f4->Set_nextf((Face*)NULL);
                break;

        case ZAXIS  :
        default     :
                break;

    }


    return f1 ; // return the pointer to the first face of list

}

double Bspline::Given_X_return_Y(double xval){


}
double Bspline::Volume(){


}

