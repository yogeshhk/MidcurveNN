/*******************************************************************************
*       FILENAME :      display_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Display option on Parent_Menubar
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   MAY 27, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "classes.h"            /* Classes Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
 

/******************************************************************************
                        GLOBAL DECLARATIONS(INTERFACE)
******************************************************************************/

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
 
void    display_pset_cb(Widget wi, XtPointer client_d, XtPointer call_data){

	printf("Came ****************************************\n");

	display_type = POLYSET;
    if(currc){

        currc->PolygonSet_Display();
		// Here only creation of the Polygon Sets takes place
		// Actalyy traversal and displaying of Polygon is done in 
		// component::Display_by_Phigs()
    }

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

void   display_truewire_cb(Widget wi, XtPointer client_d, XtPointer call_data){

    display_type = SOLID;

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

void  display_blkwise_cb(Widget wi, XtPointer client_d, XtPointer call_data){

		display_type =WIREFRAME;
}
