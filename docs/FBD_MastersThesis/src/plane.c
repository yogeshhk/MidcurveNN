/*******************************************************************************
*       FILENAME :      plane.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Plane
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
*       NAME            :Plane..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to compute planes etc..Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Plane id ,type and plane value
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Plane::Plane(int pid, int ptype ,double pvalue)
{

	plane_id 	= pid ;					// plane number
	plane_type 	= ptype ;				// plane type XMAX, ZMIN etc.
	fixed 		= TRUE;					// now value can not be modified
	plane_value = pvalue ;				// actual position value

	printf("came to Plane %d with value %f \n",plane_type,plane_value);

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

int Plane::Set_fixed(int fx,double n_val){

	int sucsess = 1;

	if( fixed == TRUE){

		if(fx == TRUE){
			if( plane_value == n_val){ // ignore
				sucsess = TRUE;
			}
			else{				// its an error
				print_msg("ERRROR in Setting Plane",NO_VALUE);
				sucsess = FALSE;
			}
		}
		else{
			fixed = fx;

		}
	}
	else{
		if(fx == TRUE){

			fixed = fx;
			plane_value = n_val;
			sucsess = TRUE;
		}
	}

	printf("FIXING PLANE returning %d\n",sucsess);
	return sucsess;
}
 


