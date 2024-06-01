/*******************************************************************************
*       FILENAME :      subcylinder.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class SubCylinder
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 4, 1995.
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
*       NAME            :SubCylinder...Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*			 reqd. to compute planes etc..Calls constructors of
*			 private members with appropraite values 
*
*       INPUT           : id , parent component and plane values
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
 
SubCylinder::SubCylinder(	char *blkid,Component *co ,
							double xmn,double xmx,
							double ymn, double ymx , 
							double zmn , double zmx)
{
	
	strcpy(block_name , blkid);			// copies block name
										// block_id gets assigned in the
										// Link_block in Component

	block_type	= block_flag;
	block_type	= SCYLINDR;


	int temp ;
	temp = co->Get_block_id_counter();// get maximum no. of blocks
	block_id = ++temp ;		// assignened the incremented value
	co->Set_block_id_counter(temp);	// reset block_id_counter in Component ;

	nextb	= NULL ;		// next block is NULL
	prevb	= NULL ;		// previous block is NULL

	block_comp = co;		// parent component

	double	xmd = (xmn+xmx)/2 ;	// calculating X mid plane value
	double	ymd = (ymn+ymx)/2 ;	// calculating Y mid plane value
	double	zmd = (zmn+zmx)/2 ;	// calculating Z mid plane value


	double	xln = (xmx - xmn );	// calculating X length
	double	yln = (ymx - ymn );	// calculating Y length
	double	zln = (zmx - zmn );	// calculating Z length

	/*

		Plane ids are assignend explicitely with numbers
		because for sure there are 9 planes only and naming
		can be made consistant

	*/

	Xmin	= new Plane(1,XMIN,xmn);// Plane( id ,type, value)
	Xmid	= new Plane(2,XMID,xmd);
	Xmax	= new Plane(3,XMAX,xmx);

	Ymin	= new Plane(4,YMIN,ymn);
	Ymid	= new Plane(5,YMID,ymd);
	Ymax	= new Plane(6,YMAX,ymx);

	Zmin	= new Plane(7,ZMIN,zmn);
	Zmid	= new Plane(8,ZMID,zmd);
	Zmax	= new Plane(9,ZMAX,zmx);

	/*

        Naming convention for lengths :
 
                Its a four bit string out of which second 2 are of block_ids
                (thus restricting no. of blocks to 99) and the forth bit is for
                axis. X=1, Y=2 and Z=3 ;
                The first digit could be used for comp num
 
                Lenght_List just concatenates these length_names whenever
                they are linked to this specific Length_list
 

	*/

	char	lx[4];
	sprintf(lx,"%1d%2d",co->Get_component_id(),block_id);	
	strcat(lx,"1");				// concatenate with 1 for X

	Xlen	= new Length(lx);

        char    ly[4];
	sprintf(ly,"%1d%2d",co->Get_component_id(),block_id);	
        strcat(ly,"2");				// 2 for Y

	Ylen	= new Length(ly);

        char    lz[4];	
	sprintf(lz,"%1d%2d",co->Get_component_id(),block_id);	
        strcat(lz,"3");				// 3 for Z

	Zlen	= new Length(lz);


	/*

		Now we have to prepare list of global Length_List
		It will be local declaration because they are not
		in the private of the Block
		Same length_name is passed for this also

	*/

	Length_List *xll = new Length_List(lx,xln,Xlen);
	Link_Length_List(xll);		// adding to the global list

	Length_List *yll = new Length_List(ly,yln,Ylen);
	Link_Length_List(yll);

	Length_List *zll = new Length_List(lz,zln,Zlen);
	Link_Length_List(zll);


	//Display_by_phigs();

        // cyl_axis is global variable
 
        switch(cyl_axis){
 
                case XAXIS:
                                axis            = XAXIS;
                                height          = xln;
                                major_radius    = yln/2;
                                minor_radius    = zln/2;
                                break;
                case YAXIS:
 
                                axis            = YAXIS;
                                height          = yln;
                                major_radius    = zln/2;
                                minor_radius    = xln/2;
                                break;
 
                case ZAXIS:
 
                                axis            = ZAXIS;
                                height          = zln;
                                major_radius    = xln/2;
                                minor_radius    = yln/2;
                                break;
 
                default :
                                axis            = YAXIS;
                                height          = yln;
                                major_radius    = zln/2;
                                minor_radius    = xln/2;
                                break;
 
        }

	printf( "Came to SuBCYLINDER constructor with no. %s \n",block_name);
} 




/*******************************************************************************
*
*       NAME            :Display_by_phigs()
*
*       DESCRIPTION     :Temporarily creates list of faces and then
*			 traverses each face to get the vertices
*			 Uses PHIGS calls to display
*
*       INPUT           : Nothing
*
*       OUTPUT          : Creation of structure in phigs
*
******************************************************************************/
 

void SubCylinder::Display_by_phigs()
{

        double  pxn     = Xmin->Get_plane_value();
        double  pxx     = Xmax->Get_plane_value();
        double  pyn     = Ymin->Get_plane_value();
        double  pyx     = Ymax->Get_plane_value();
        double  pzn     = Zmin->Get_plane_value();
        double  pzx     = Zmax->Get_plane_value();
 

	//Face *tracef = Create_Faces();	

	Ppoint3		pt[12][4];	// 12 side faces with 4 points
	Ppoint3		ptb[2][12];	// 2 top and bottom faces with 12 points
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
        pset_line_colr_ind( (Pint) 6);
 
	double theta = 3.142/6;	// 30 degrees in radiance

        double bcx;     // bottom center
        double bcy;
        double bcz;
 
        double tcx;     // top center
        double tcy;
        double tcz;
 

	switch(axis){

		case XAXIS :

			bcx = pxn;
			bcy = ( pyx + pyn )/2;
			bcz = ( pzx + pzn )/2;

			tcx = pxx;
			tcy = bcy;
			tcz = bcz;

			for(i=0;i<12;i++){

				ptb[0][i].x= pxn;
				ptb[0][i].y= bcy + ( major_radius*cos(i*theta));
				ptb[0][i].z= bcz - ( minor_radius*sin(i*theta));

				ptb[1][i].x= pxx;
				ptb[1][i].y= tcy + ( major_radius*cos(i*theta));
				ptb[1][i].z= tcz - ( minor_radius*sin(i*theta));

			}

			for(j=0;j<12;j++){
			
				int k = (j+1)%12;	// next point

				pt[j][0].x= pxx;
				pt[j][0].y= tcy + ( major_radius*cos(j*theta));
				pt[j][0].z= tcz + ( minor_radius*sin(j*theta));

				pt[j][1].x= pxn;
				pt[j][1].y= tcy + ( major_radius*cos(j*theta));
				pt[j][1].z= tcz + ( minor_radius*sin(j*theta));

				pt[j][2].x= pxn;
				pt[j][2].y= tcy + ( major_radius*cos(k*theta));
				pt[j][2].z= tcz + ( minor_radius*sin(k*theta));

				pt[j][3].x= pxx;
				pt[j][3].y= tcy + ( major_radius*cos(k*theta));
				pt[j][3].z= tcz + ( minor_radius*sin(k*theta));

			
			}

			for(j=0;j<14;j++){

                		ppolyline3( &faces[j]);
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
 
                                ptb[0][i].x= bcx - ( minor_radius*sin(i*theta));
                                ptb[0][i].y= pyn ;
                                ptb[0][i].z= bcz + ( major_radius*cos(i*theta));

 
                                ptb[1][i].x= tcx - ( minor_radius*sin(i*theta));
                                ptb[1][i].y= pyx ;
                                ptb[1][i].z= tcz + ( major_radius*cos(i*theta));

 
                        }
 
                        for(j=0;j<12;j++){
 
                                int k = (j+1)%12;       // next point
 
                                pt[j][0].x= tcx + ( minor_radius*sin(j*theta));
                                pt[j][0].y= pyx;
                                pt[j][0].z= tcz + ( major_radius*cos(j*theta));
 
                                pt[j][1].x= tcx + ( minor_radius*sin(j*theta));
                                pt[j][1].y= pyn;
                                pt[j][1].z= tcz + ( major_radius*cos(j*theta));

                                pt[j][2].x= tcx + ( minor_radius*sin(k*theta));
                                pt[j][2].y= pyn;
                                pt[j][2].z= tcz + ( major_radius*cos(k*theta));
 
                                pt[j][3].x= tcx + ( minor_radius*sin(k*theta));
                                pt[j][3].y= pyx;
                                pt[j][3].z= tcz + ( major_radius*cos(k*theta));
 
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
 
                                ptb[0][i].x= bcx + ( major_radius*cos(i*theta));
                                ptb[0][i].y= bcy - ( minor_radius*sin(i*theta));
                                ptb[0][i].z= pzn ;
 
 
                                ptb[1][i].x= tcx + ( major_radius*cos(i*theta));
                                ptb[1][i].y= tcy - ( minor_radius*sin(i*theta));
                                ptb[1][i].z= pzx ;
 
 
                        }
 
                        for(j=0;j<12;j++){
 
                                int k = (j+1)%12;       // next point
 
                                pt[j][0].x= tcx + ( major_radius*cos(j*theta));
                                pt[j][0].y= tcy + ( minor_radius*sin(j*theta));
                                pt[j][0].z= pzx;
 
                                pt[j][1].x= tcx + ( major_radius*cos(j*theta));
                                pt[j][1].y= tcy + ( minor_radius*sin(j*theta));
                                pt[j][1].z= pzn;

                                pt[j][2].x= tcx + ( major_radius*cos(k*theta));
                                pt[j][2].y= tcy + ( minor_radius*sin(k*theta));
                                pt[j][2].z= pzn;
 
                                pt[j][3].x= tcx + ( major_radius*cos(k*theta));
                                pt[j][3].y= tcy + ( minor_radius*sin(k*theta));
                                pt[j][3].z= pzx;
 
                        }
 
                        for(j=0;j<14;j++){
 
                                ppolyline3( &faces[j]);
                        }
 
                        break;

	}

		//DrawAxes(display_max);

}

double SubCylinder::Volume(){


}
