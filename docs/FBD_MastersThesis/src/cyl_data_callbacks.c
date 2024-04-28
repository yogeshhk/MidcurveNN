/*******************************************************************************
*       FILENAME :      cyl_data_callbacks.c DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains the callbacks from Cylinder data Entry Table
*
*       FUNCTIONS   :   
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
#include "classes.h"        	/* Classes Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
 
/*****************************************************************************
*
*       NAME    :       cyl_axis_sel_cb()
*
*       DESCRIPTION :   Called when toggle is pressed in CYL data Entry widget
*
*
******************************************************************************/
 
void cyl_axis_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	int i = ( int )client_data;

	switch(i){

		case XAXIS :
				cyl_axis = XAXIS;
				break;

		case YAXIS :
				cyl_axis = YAXIS;
				break;

		case ZAXIS :
				cyl_axis = ZAXIS;
				break;

		case OAXIS :
				cyl_axis = OAXIS;
                break;
		default :	
				cyl_axis = YAXIS ;
				break;
	}
}





/*****************************************************************************
*
*       NAME    :       cyl_data_ok_cb()
*
*       DESCRIPTION : 	Called when OK is pressed in CYL data Entry widget
*		     
*
******************************************************************************/
 
void cyl_data_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        Widget i = (Widget)client_data;

	print_msg("Cylindrical Axis selected is ",cyl_axis);

	XtPopdown(i);
}

/*****************************************************************************
*
*       NAME    :       cyl_data_can_cb()
*
*       DESCRIPTION :   Called when CANCEL is pressed in Cyl_data_entry widget  
*                       
*
******************************************************************************/
 
void cyl_data_can_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        Widget i = (Widget)client_data;

	// clear OFF evrything

        cyl_axis        = 0 ;           // cylinder axis        (application.h)
 
	XtPopdown(i);
}
 
 

 
