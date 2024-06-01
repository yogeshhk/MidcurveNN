/*******************************************************************************
*       FILENAME :      dimarc.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class DimArc
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JUN 22, 1995.
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
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
DimArc::DimArc(int id,DimNode* A,DimNode* B,double dimension,double tol){

	start	=	A;
	end		=	B;
	nextda	= NULL;
	
	dim_arc_id	= 	id;	
	dim_value	= 	dimension;
	tolerance	=   tol;
}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/

void DimArc::PrintYourself(FILE* fp){

	int id1	= start->Get_dim_node_id();
	int id2	= end->Get_dim_node_id();

	fprintf(fp,"\t Arc %d %d ",id1,id2);
	fprintf(fp,"\t%f\t %f\n",dim_value,tolerance);

}
