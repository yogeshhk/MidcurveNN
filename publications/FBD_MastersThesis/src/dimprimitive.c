/*******************************************************************************
*       FILENAME :      dimprimitive.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class DimPrimitive
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
 

DimPrimitive::DimPrimitive(){

	nextdp	= NULL;

}
/*******************************************************************************
*
*       NAME            :DimPlane..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to compute dimplanes etc..Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : DimPlane id ,type and dimplane value
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
DimPlane::DimPlane(Face* ff,int blk_id)
{

	dimplane_id 	=	ff->Get_face_id();      // dimplane number
	block_id		=	blk_id;               	// the parent block
	dimplane_type 	=	ff->Get_face_type(); 	// type along which dimplane is

	Vertex *v1	= ff->Get_V1();
	Vertex *v2	= ff->Get_V2();
	Vertex *v3	= ff->Get_V3();

	switch(dimplane_type){

		case XAXIS:

			dimplane_value 	=	v1->Get_x();	// numerical value of dimplane
			break;

		case YAXIS:

			dimplane_value 	=	v1->Get_y();	// numerical value of dimplane
			break;

		case ZAXIS:

			dimplane_value 	=	v1->Get_z();	// numerical value of dimplane
			break;

		default:

			// Need to code for other category
			// We need to find out distance of the plane from origin and
			// with directional sense(+/-)

			break;
	}

    double dx1 = v1->Get_x() - v2->Get_x();
    double dy1 = v1->Get_y() - v2->Get_y();
    double dz1 = v1->Get_z() - v2->Get_z();
 
    double dx2 = v3->Get_x() - v2->Get_x();
    double dy2 = v3->Get_y() - v2->Get_y();
    double dz2 = v3->Get_z() - v2->Get_z();
 
    /*
        Now we need to take cross product of these two "difference vectors"
 
        A X B = (aybz - azby)i - (axbz -bxaz)j + (axby -bxay)k
 
    */
 
    double ix = (dy1*dz2) -(dz1*dy2);
    double iy = (dx2*dz1) -(dx1*dz2);
    double iz = (dx1*dy2) -(dx2*dy1);
 
    normal = new Vector(ix,iy,iz);

	// printf("DimPlane constructor with value %f\n",dimplane_value);
} 
 
 

