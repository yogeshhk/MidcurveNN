/*******************************************************************************
*       FILENAME :      bspline.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Bspline
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JUN 5, 181995.
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


	block_type	= 	BSPLINE;
    u_order     =   3;
    u_num_pts   =   6;       	//  points are from 0 to 5
	bsp_axis	=	cyl_axis;
    
    /*
    **      Knot vector has multiplicity of 3 at ends
    */


    u_knot_vector[0]   =   1.0;
    u_knot_vector[1]   =   1.0;
    u_knot_vector[7]   =   5.0;
    u_knot_vector[8]   =   5.0;

    for(int j=0;j<5;j++)u_knot_vector[j+2]  =   j+1;

    for(int i=0;i<6;i++){
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
	u_num_pts	=	6	;		//	points are from 0 to 5
	bsp_axis	=	cyl_axis;

	/*
	**		Knot vector has multiplicity of 3 at ends
	*/

    u_knot_vector[0]   =   1.0;
    u_knot_vector[1]   =   1.0;
    u_knot_vector[7]   =   5.0;
    u_knot_vector[8]   =   5.0;

    for(int j=0;j<5;j++)u_knot_vector[j+2]  =   j+1;

	for(int i=0;i<6;i++){

		u_control_pts[i].Set_x(cpts[i].Get_x());
		u_control_pts[i].Set_y(cpts[i].Get_y());
		u_control_pts[i].Set_z(cpts[i].Get_z());
	}

	printf( "Came to Bspline constructor planes %d \n",ax);
}
 
/******************************************************************************
*
*       NAME            :   Bspline..... Constructor
*
*       DESCRIPTION     :   This is second constructor. Gets all the values
*                           reqd. to compute planes etc..Calls constructors of
*                           private members with appropraite values
*
*       INPUT           :
*
*       OUTPUT          :   Undefined by C++
*
*******************************************************************************/

Bspline::Bspline(   char *b,Component *co ,
            double xmn,double xmx,double ymn,double ymx,double zmn,double zmx,
            int ax,
			double x1,double y1,double z1,
			double x2,double y2,double z2,
			double x3,double y3,double z3,
			double x4,double y4,double z4,
			double x5,double y5,double z5,
			double x6,double y6,double z6
			)
            :Prismatic(b,co,xmn,xmx,ymn,ymx,zmn,zmx,ax)

{

    u_order     =   3   ;
    u_num_pts   =   6   ;       //  points are from 0 to 5
    bsp_axis    =   cyl_axis;

    /*
    **      Knot vector has multiplicity of 3 at ends
    */

    u_knot_vector[0]   =   1.0;
    u_knot_vector[1]   =   1.0;
    u_knot_vector[7]   =   5.0;
    u_knot_vector[8]   =   5.0;

    for(int j=0;j<5;j++)u_knot_vector[j+2]  =   j+1;

    u_control_pts[0].Set_x(x1);
    u_control_pts[0].Set_y(y1);
    u_control_pts[0].Set_z(z1);

    u_control_pts[1].Set_x(x2);
    u_control_pts[1].Set_y(y2);
    u_control_pts[1].Set_z(z2);

    u_control_pts[2].Set_x(x3);
    u_control_pts[2].Set_y(y3);
    u_control_pts[2].Set_z(z3);

    u_control_pts[3].Set_x(x4);
    u_control_pts[3].Set_y(y4);
    u_control_pts[3].Set_z(z4);

    u_control_pts[4].Set_x(x5);
    u_control_pts[4].Set_y(y5);
    u_control_pts[4].Set_z(z5);

    u_control_pts[5].Set_x(x6);
    u_control_pts[5].Set_y(y6);
    u_control_pts[5].Set_z(z6);

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
 
		double	pxl		= pxx - pxn;
		double	pyl		= pyx - pyn;
		double	pzl		= pzx - pzn;

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
	**		We will be passing three curves (series) of 6 points each
	*/

	Vertex	min[6];		//	first series
	Vertex	mid[6];		//	second series
	Vertex	max[6];		//	third series

	/*
	**		First I will copy control points to all three curves
	**		then depending on the axis of the block , offset the
	**		dimensions by length/2 ammount so as to get Min,Mid,Max
	**		curve
	*/

	int i;

    for(i=0;i<6;i++){

        min[i].Set_x(u_control_pts[i].Get_x()*pxl + pxn);
        min[i].Set_y(u_control_pts[i].Get_y()*pyl + pyn);
        min[i].Set_z(u_control_pts[i].Get_z()*pzl + pzn);

        mid[i].Set_x(u_control_pts[i].Get_x()*pxl + pxn);
        mid[i].Set_y(u_control_pts[i].Get_y()*pyl + pyn);
        mid[i].Set_z(u_control_pts[i].Get_z()*pzl + pzn);

        max[i].Set_x(u_control_pts[i].Get_x()*pxl + pxn);
        max[i].Set_y(u_control_pts[i].Get_y()*pyl + pyn);
        max[i].Set_z(u_control_pts[i].Get_z()*pzl + pzn);

    }

	Ppoint3     surf_points[18];

	switch(bsp_axis){

		case XAXIS:

			for(i=0;i<6;i++){
				min[i].Set_z(pzn);
				mid[i].Set_z((pzx+pzn)/2.0);
				max[i].Set_z(pzx);
			}
    		for(i=0;i<6;i++){
        		surf_points[i+12].x = (Pfloat)min[i].Get_x();
        		surf_points[i+12].y = (Pfloat)min[i].Get_y();
        		surf_points[i+12].z = (Pfloat)pzn;

				/*
        		printf("[%3.1f %3.1f %3.1f]  ",min[i].Get_x(),
                        		min[i].Get_y(),pzn);
				*/
        		surf_points[i+6].x = (Pfloat)mid[i].Get_x();
        		surf_points[i+6].y = (Pfloat)mid[i].Get_y();
        		surf_points[i+6].z = (Pfloat)((pzx+pzn)/2.0);

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

			for(i=0;i<6;i++){
				min[i].Set_x(pxn);
				mid[i].Set_x((pxx+pxn)/2.0);
				max[i].Set_x(pxx);
			}
    		for(i=0;i<6;i++){
        		surf_points[i+12].x = (Pfloat)pxn;
        		surf_points[i+12].y = (Pfloat)min[i].Get_y();
        		surf_points[i+12].z = (Pfloat)min[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f]  ",pxn,
                        		min[i].Get_y(),min[i].Get_z());
        		*/
        		surf_points[i+6].x = (Pfloat)((pxx+pxn)/2.0);
        		surf_points[i+6].y = (Pfloat)mid[i].Get_y();
        		surf_points[i+6].z = (Pfloat)mid[i].Get_z();

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

		case ZAXIS :

			for(i=0;i<6;i++){
				min[i].Set_y(pyn);
				mid[i].Set_y((pyx+pyn)/2.0);
				max[i].Set_y(pyx);
			}
    		for(i=0;i<6;i++){
        		surf_points[i+12].x = (Pfloat)min[i].Get_x();
        		surf_points[i+12].y = (Pfloat)pyn;
        		surf_points[i+12].z = (Pfloat)min[i].Get_z();

        		/*
        		printf("[%3.1f %3.1f %3.1f]  ",pyn,
                        		min[i].Get_y(),min[i].Get_z());
        		*/
        		surf_points[i+6].x = (Pfloat)mid[i].Get_x();
        		surf_points[i+6].y = (Pfloat)((pyx+pyn)/2.0);
        		surf_points[i+6].z = (Pfloat)mid[i].Get_z();

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

	static  Pfloat      uknots[] = { 0, 0, 0,1,2,3,4,4,4};
	static  Pfloat      vknots[] = { 0, 0, 0, 1, 1, 1 };

    pset_linetype( PLINE_SOLID );
    pset_line_colr_ind( (Pint) 4);
    pset_linewidth((Pfloat) 1.0);

    /* Assign the surface parameters. */
    uorder = 3, vorder = 3;
    grid.num_points.u_dim = 6;
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
    psc.psc_3.u_count = 6;
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
    Face    *f5;

	Face	*fs[4];		//	Dimensioning faces along equal divisions
	Face	*fsy[6];	//	Dimensioning faces along calculated divisions
	double	distances[6];

	Vertex *Vxdim[24];
	Vertex *Vydim[24];
	Vertex *Vzdim[24];

	Vertex *vxdim[16];
	Vertex *vydim[16];
	Vertex *vzdim[16];

    switch(bsp_axis){

        case XAXIS  :

                f1  = new Face(1,XAXIS,v1,v4,v8,v5);
                f2  = new Face(2,YAXIS,v8,v5,v6,v7);
                f3  = new Face(3,YAXIS,v1,v4,v3,v2);
                f4  = new Face(4,ZAXIS,v1,v2,v6,v5);
                f5  = new Face(5,ZAXIS,v3,v4,v8,v7);

                Vertex *vydim[16];

                double  distances[6];

                distances[0]= u_control_pts[0].Get_x()*pxl + pxn;
                distances[1]=Given_X_return_Y(YAXIS,pyn+pyd,    0.2);
                distances[2]=Given_X_return_Y(YAXIS,pyn+2*pyd,  0.4);
                distances[3]=Given_X_return_Y(YAXIS,pyn+3*pyd,  0.6);
                distances[4]=Given_X_return_Y(YAXIS,pyn+4*pyd,  0.8);
                distances[5]= u_control_pts[5].Get_x()*pxl + pxn;

                //  First Y plane is at Ymin and then at Ymin+pyd

                for(int g=0;g<4;g++){
                    vydim[0+g*4]    =new Vertex(9+g*4, pxx,pyn+(g+1)*pyd,pzn);
                    vydim[1+g*4]    =new Vertex(10+g*4,pxn,pyn+(g+1)*pyd,pzn);
                    vydim[2+g*4]    =new Vertex(11+g*4,pxn,pyn+(g+1)*pyd,pzx);
                    vydim[3+g*4]    =new Vertex(12+g*4,pxx,pyn+(g+1)*pyd,pzx);

                    fs[g]           =new Face(6+g,YAXIS,vydim[0+g*4],
                                                        vydim[1+g*4],
                                                        vydim[2+g*4],
                                                        vydim[3+g*4]);
                }

                //  Now we are building 6 X planes

                for(int g=0;g<6;g++){
                    Vxdim[0+g*4]=new Vertex(25+g*4,distances[g],pyn,pzn);
                    Vxdim[1+g*4]=new Vertex(26+g*4,distances[g],pyn,pzx);
                    Vxdim[2+g*4]=new Vertex(27+g*4,distances[g],pyx,pzx);
                    Vxdim[3+g*4]=new Vertex(28+g*4,distances[g],pyx,pzn);

                    fsy[g]          =new Face(10+g,XAXIS,Vxdim[0+g*4],
                                                        Vxdim[1+g*4],
                                                        Vxdim[2+g*4],
                                                        Vxdim[3+g*4]);

                }
                //  Here we are taking 4 planes more between
                //  MIN and MAX along Z axis for dimPlanes.

                f1->Set_nextf(f2);
                f2->Set_nextf(f3);
                f3->Set_nextf(f4);
                f4->Set_nextf(f5);
                f5->Set_nextf(fs[0]);
                (fs[0])->Set_nextf(fs[1]);
                (fs[1])->Set_nextf(fs[2]);
                (fs[2])->Set_nextf(fs[3]);
                (fs[3])->Set_nextf(fsy[0]);
                (fsy[0])->Set_nextf(fsy[1]);
                (fsy[1])->Set_nextf(fsy[2]);
                (fsy[2])->Set_nextf(fsy[3]);
                (fsy[3])->Set_nextf(fsy[4]);
                (fsy[4])->Set_nextf(fsy[5]);
                (fsy[5])->Set_nextf((Face*)NULL);

                break;

        case YAXIS  :

                f1  = new Face(1,XAXIS,v1,v4,v8,v5);
                f2  = new Face(2,XAXIS,v2,v3,v7,v6);
                f3  = new Face(3,YAXIS,v1,v4,v3,v2);
                f4  = new Face(4,ZAXIS,v1,v2,v6,v5);
                f5  = new Face(5,ZAXIS,v3,v4,v8,v7);

				distances[0]= u_control_pts[0].Get_y()*pyl + pyn;
				distances[1]=Given_X_return_Y(ZAXIS,pzn+pzd,	0.2);
				distances[2]=Given_X_return_Y(ZAXIS,pzn+2*pzd,	0.4);
				distances[3]=Given_X_return_Y(ZAXIS,pzn+3*pzd,	0.6);
				distances[4]=Given_X_return_Y(ZAXIS,pzn+4*pzd,	0.8);
				distances[5]= u_control_pts[5].Get_y()*pyl + pyn;

				//	First Z plane is at Zmin and then at Zmin+pzd

				for(int g=0;g<4;g++){
					vzdim[0+g*4]	=new Vertex(9+g*4,pxx,pyn,pzn+(g+1)*pzd);
					vzdim[1+g*4]	=new Vertex(10+g*4,pxn,pyn,pzn+(g+1)*pzd);
					vzdim[2+g*4]	=new Vertex(11+g*4,pxn,pyx,pzn+(g+1)*pzd);
					vzdim[3+g*4]	=new Vertex(12+g*4,pxx,pyx,pzn+(g+1)*pzd);

					fs[g]			=new Face(6+g,ZAXIS,vzdim[0+g*4],
														vzdim[1+g*4],
														vzdim[2+g*4],
														vzdim[3+g*4]);
				}
	
				//	Now we are building 6 Y planes

				for(int g=0;g<6;g++){
					Vydim[0+g*4]=new Vertex(25+g*4,pxx,distances[g],pzn);
					Vydim[1+g*4]=new Vertex(26+g*4,pxn,distances[g],pzx);
					Vydim[2+g*4]=new Vertex(27+g*4,pxn,distances[g],pzx);
					Vydim[3+g*4]=new Vertex(28+g*4,pxx,distances[g],pzn);

					fsy[g]			=new Face(10+g,YAXIS,Vydim[0+g*4],
														Vydim[1+g*4],
														Vydim[2+g*4],
														Vydim[3+g*4]);

				}
				//	Here we are taking 4 planes more between
				//	MIN and MAX along Z axis for dimPlanes.

                f1->Set_nextf(f2);
                f2->Set_nextf(f3);
                f3->Set_nextf(f4);
				f4->Set_nextf(f5);
				f5->Set_nextf(fs[0]);
				(fs[0])->Set_nextf(fs[1]);
				(fs[1])->Set_nextf(fs[2]);
				(fs[2])->Set_nextf(fs[3]);
				(fs[3])->Set_nextf(fsy[0]);
				(fsy[0])->Set_nextf(fsy[1]);
				(fsy[1])->Set_nextf(fsy[2]);
				(fsy[2])->Set_nextf(fsy[3]);
				(fsy[3])->Set_nextf(fsy[4]);
				(fsy[4])->Set_nextf(fsy[5]);
				(fsy[5])->Set_nextf((Face*)NULL);
				printf("Hi1\n");
                break;

        case ZAXIS  :

                f1  = new Face(1,XAXIS,v1,v4,v8,v5);
                f2  = new Face(2,XAXIS,v2,v3,v7,v6);
                f3  = new Face(3,YAXIS,v1,v4,v3,v2);
                f4  = new Face(4,YAXIS,v5,v6,v7,v8);
                f5  = new Face(5,ZAXIS,v3,v4,v8,v7);

                distances[0]= u_control_pts[0].Get_z()*pzl + pzn;
                distances[1]=Given_X_return_Y(XAXIS,pxn+pxd,    0.2);
                distances[2]=Given_X_return_Y(XAXIS,pxn+2*pxd,  0.4);
                distances[3]=Given_X_return_Y(XAXIS,pxn+3*pxd,  0.6);
                distances[4]=Given_X_return_Y(XAXIS,pxn+4*pxd,  0.8);
                distances[5]= u_control_pts[5].Get_z()*pzl + pzn;

                //  First X plane is at Xmin and then at Xmin+pxd

                for(int g=0;g<4;g++){
                    vxdim[0+g*4]    =new Vertex(9+g*4,pxn+(g+1)*pxd,pyn,pzn);
                    vxdim[1+g*4]    =new Vertex(10+g*4,pxn+(g+1)*pxd,pyn,pzx);
                    vxdim[2+g*4]    =new Vertex(11+g*4,pxn+(g+1)*pxd,pyx,pzx);
                    vxdim[3+g*4]    =new Vertex(12+g*4,pxn+(g+1)*pxd,pyx,pzn);

                    fs[g]           =new Face(6+g,XAXIS,vxdim[0+g*4],
                                                        vxdim[1+g*4],
                                                        vxdim[2+g*4],
                                                        vxdim[3+g*4]);
                }

                //  Now we are building 6 Z planes

                for(int g=0;g<6;g++){
                    Vzdim[0+g*4]=new Vertex(25+g*4,pxx,pyn,distances[g]);
                    Vzdim[1+g*4]=new Vertex(26+g*4,pxn,pyn,distances[g]);
                    Vzdim[2+g*4]=new Vertex(27+g*4,pxn,pyx,distances[g]);
                    Vzdim[3+g*4]=new Vertex(28+g*4,pxx,pyx,distances[g]);

                    fsy[g]          =new Face(10+g,ZAXIS,Vzdim[0+g*4],
                                                        Vzdim[1+g*4],
                                                        Vzdim[2+g*4],
                                                        Vzdim[3+g*4]);

                }

                f1->Set_nextf(f2);
                f2->Set_nextf(f3);
                f3->Set_nextf(f4);
                f4->Set_nextf(f5);
                f5->Set_nextf(fs[0]);
                (fs[0])->Set_nextf(fs[1]);
                (fs[1])->Set_nextf(fs[2]);
                (fs[2])->Set_nextf(fs[3]);
                (fs[3])->Set_nextf(fsy[0]);
                (fsy[0])->Set_nextf(fsy[1]);
                (fsy[1])->Set_nextf(fsy[2]);
                (fsy[2])->Set_nextf(fsy[3]);
                (fsy[3])->Set_nextf(fsy[4]);
                (fsy[4])->Set_nextf(fsy[5]);
                (fsy[5])->Set_nextf((Face*)NULL);
                break;


        default     :
                break;

    }


    return f1 ; // return the pointer to the first face of list

}

void   Bspline::Fill_first_order_Ns(double u){

    if(u==0)    N[0]=N[1]=1.0;
    else        N[0]=N[1]=0.0;

    if(u>=0 && u< 1.0)  N[2]=1.0;
    else                N[2]=0.0;

    if(u>=1 && u< 2.0)  N[3]=1.0;
    else                N[3]=0.0;

    if(u>=2 && u< 3.0)  N[4]=1.0;
    else                N[4]=0.0;

    if(u>=3 && u< 4.0)  N[5]=1.0;
    else                N[5]=0.0;


}

double  Bspline::Calculate_Bspline_value(double cpts[],double u){

    double Bspline_value=0.0;

    Fill_first_order_Ns(u);

    Bspline_value   =   cpts[0]*(1 - u)*(1 - u)*N[2]    +
            cpts[1]*(0.5*u*(4 - 3*u)*N[2] + 0.5*(2-u)*(2-u)*N[3]) +
            cpts[2]*(0.5*u*u*N[2] + 0.5*(-2*u*u + 6*u -3)*N[3]+
                    0.5*(3-u)*(3-u)*N[4]) +
            cpts[3]*0.5*((u-1)*(u-1)*N[3] + ( -2*u*u+10*u-11)*N[4] +
            (4-u)*(4-u)*N[5]) +
            cpts[4]*0.5*( (u-2)*(u-2)*N[4] + ( -3*u*u + 20*u - 32)*N[5]) +
            cpts[5]*(u-3)*(u-3)*N[5];

    return Bspline_value ;
}

double  Bspline::f(double cpts[],double u,double Xval){

    double Bspline_value=0.0;

    Fill_first_order_Ns(u);

    Bspline_value  =   cpts[0]*(1 - u)*(1 - u)*N[2]    +
            cpts[1]*(0.5*u*(4 - 3*u)*N[2] + 0.5*(2-u)*(2-u)*N[3]) +
            cpts[2]*(0.5*u*u*N[2] + 0.5*(-2*u*u + 6*u -3)*N[3]+
                    0.5*(3-u)*(3-u)*N[4]) +
            cpts[3]*0.5*((u-1)*(u-1)*N[3] + ( -2*u*u+10*u-11)*N[4] +
            (4-u)*(4-u)*N[5]) +
            cpts[4]*0.5*( (u-2)*(u-2)*N[4] + ( -3*u*u + 20*u - 32)*N[5]) +
            cpts[5]*(u-3)*(u-3)*N[5];

   

    return Bspline_value - Xval;


}

double Bspline::Given_X_return_Y(int axis_of_x,double xval,double bias){

	/*
	**	Bspline function is a summation series of terms containing
	**	control points multiplied to Bspline functions
	**	
	**	Given value of X, we need to find value of U, a parameter in which
	**	Bspline functions are formulated.
	**	This is a non-linear root solving problem
	**	Secant method is used to solve the functions f(x) -X = 0
	*/

	//	bias is the percentage of length at which "xval" lies

    int Num = 50;       // Iteration limit
    double eps=0.001;   // convergence tolerance
	int i;

    double  cptsX[6];
    double  cptsY[6];

    //  We would solve for u with initial guess of Ua and Ub

    double Ua,Ub;

    //  Ua and Ub are the intitial guesses
    //  They can lie between 0 to 4
    //
    //  Plane   Ua  Ub
    //
    //  Lx0     0   0.5
    //  Lx0.25  0.5 1.5
    //  Lx0.5   1.5 2.5
    //  Lx0.75  2.5 3.5
    //  Lx1.0   3.5 4.0

	if(bias>0 && bias <=0.2){	Ua =0.0;Ub=0.5;}
	else if(bias>0.2 && bias <= 0.4){	Ua=0.5;Ub=1.5; }
	else if(bias>0.4 && bias <= 0.6){	Ua=1.5;Ub=2.5; }
	else if(bias>0.6 && bias <= 0.8){	Ua=2.5;Ub=3.5; }
	else {	Ua=3.5;Ub=4; }

    for(i=0;i<6;i++)N[i]=0.0;
    for(i=0;i<6;i++)cptsX[i]=1.0;
    for(i=0;i<6;i++)cptsY[i]=1.0;

    int iter=0;

    double  pxn = Xmin->Get_plane_value();
    double  pxx = Xmax->Get_plane_value();
    double  pyn = Ymin->Get_plane_value();
    double  pyx = Ymax->Get_plane_value();
    double  pzn = Zmin->Get_plane_value();
    double  pzx = Zmax->Get_plane_value();

    double  pxl = pxx -pxn;
    double  pyl = pyx -pyn;
    double  pzl = pzx -pzn;


	switch(axis_of_x){

		case XAXIS:
			for(int w=0;w<6;w++)cptsX[w] = u_control_pts[w].Get_x()*pxl + pxn;
			for(int w=0;w<6;w++)cptsY[w] = u_control_pts[w].Get_z()*pzl + pzn;

			break;

		case YAXIS:
			for(int w=0;w<6;w++)cptsX[w] = u_control_pts[w].Get_y()*pyl + pyn;
			for(int w=0;w<6;w++)cptsY[w] = u_control_pts[w].Get_x()*pxl + pxn;

			break;

		case ZAXIS:

			for(int w=0;w<6;w++)cptsX[w] = u_control_pts[w].Get_z()*pzl + pzn;
			for(int w=0;w<6;w++)cptsY[w] = u_control_pts[w].Get_y()*pyl + pyn;

			break;

		default:
			for(int w=0;w<6;w++)cptsX[w] = u_control_pts[w].Get_z()*pzl + pzn;
			for(int w=0;w<6;w++)cptsY[w] = u_control_pts[w].Get_y()*pyl + pyn;
			
			break;

	}

  	double fb   = f(cptsX,Ub,xval);
    double fa   = f(cptsX,Ua,xval);
    while(iter<Num && fabs(fb) > eps){

        iter++;

        double Uint     = Ub - (fb*(Ub -Ua)/(fb - f(cptsX,Ua,xval)));
        Ua  = Ub;
        Ub  = Uint;
        fb  = f(cptsX,Ub,xval);
    }

    if(fabs(fb) > eps)printf(" Not converged in the given iterations\n");
    else    printf(" Estimated solution U is %f \n",Ub);

    double answer = Calculate_Bspline_value(cptsY,Ub);

    printf("The Y coordinate is %f\n",answer);

	return answer;

}
double Bspline::Volume(){


}
void  Bspline::Write_to_file(FILE* fo){


	for(int w=0;w<6;w++){
		fprintf(fo," %3.2f",u_control_pts[w].Get_x());
		fprintf(fo," %3.2f",u_control_pts[w].Get_y());
		fprintf(fo," %3.2f",u_control_pts[w].Get_z());
	}
	fprintf(fo," \n");
}
