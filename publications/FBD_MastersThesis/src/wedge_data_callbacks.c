/*******************************************************************************
*       FILENAME :      wedge_data_callbacks.c DESIGN REF :  FBD(CAD/CAPP)
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
*       NAME    :       wedge_axis_sel_cb()
*
*       DESCRIPTION :   Called when toggle is pressed in CYL data Entry widget
*
*
******************************************************************************/
 
void wedge_axis_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	int i = ( int )client_data;

	switch(i){

		case XAXIS :
				wedge_axis = XAXIS;
				break;

		case YAXIS :
				wedge_axis = YAXIS;
				break;

		case ZAXIS :
				wedge_axis = ZAXIS;
				break;

		case OAXIS :
				wedge_axis = OAXIS;
                break;
		default :	
				wedge_axis = YAXIS ;
				break;
	}
}



/*****************************************************************************
*
*       NAME    :       wedge_pl_sel_cb()
*
*       DESCRIPTION :   Called when toggle is pressed in CYL data Entry widget
*
*
******************************************************************************/
 
void wedge_pl_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data
)
{
 
    int i = ( int )client_data;
 
	switch(wedge_axis){

		case XAXIS:

				printf("Wedge axis is X axis\n");
				switch(i){

					case MIN_MIN:
						wedge_planes[0]	= YMIN;
						wedge_planes[1]	= ZMIN;
						break;

					case MIN_MAX:
						wedge_planes[0]	= YMIN;
						wedge_planes[1]	= ZMAX;
						break;

                    case MAX_MIN:
                        wedge_planes[0]  = YMAX;
                        wedge_planes[1]  = ZMIN;
                        break;
 
                    case MAX_MAX:
                        wedge_planes[0]  = YMAX;
                        wedge_planes[1]  = ZMAX;
                        break;

					default:
                        wedge_planes[0]  = YMAX;
                        wedge_planes[1]  = ZMAX;
                        break;
						
				}
                break;

        case YAXIS:
 
                printf("Wedge axis is Y axis\n");
                switch(i){
 
                    case MIN_MIN:
                        wedge_planes[0]  = ZMIN;
                        wedge_planes[1]  = XMIN;
                        break;
 
                    case MIN_MAX:
                        wedge_planes[0]  = ZMIN;
                        wedge_planes[1]  = XMAX;
                        break;
 
                    case MAX_MIN:
                        wedge_planes[0]  = ZMAX;
                        wedge_planes[1]  = XMIN;
                        break;
 
                    case MAX_MAX:
                        wedge_planes[0]  = ZMAX;
                        wedge_planes[1]  = XMAX;
                        break;
 
                    default:
                        wedge_planes[0]  = ZMAX;
                        wedge_planes[1]  = XMAX;
                        break;
 
                }
                break;

        case ZAXIS:
 
                printf("Wedge axis is Z axis\n");
                switch(i){
 
                    case MIN_MIN:
                        wedge_planes[0]  = XMIN;
                        wedge_planes[1]  = YMIN;
                        break;
 
                    case MIN_MAX:
                        wedge_planes[0]  = XMIN;
                        wedge_planes[1]  = YMAX;
                        break;
 
                    case MAX_MIN:
                        wedge_planes[0]  = XMAX;
                        wedge_planes[1]  = YMIN;
                        break;
 
                    case MAX_MAX:
                        wedge_planes[0]  = XMAX;
                        wedge_planes[1]  = YMAX;
                        break;
 
                    default:
                        wedge_planes[0]  = XMAX;
                        wedge_planes[1]  = YMAX;
                        break;
 
                }
                break;

    }
}

/*****************************************************************************
*
*       NAME    :       wedge_data_ok_cb()
*
*       DESCRIPTION : 	Called when OK is pressed in CYL data Entry widget
*		     
*
******************************************************************************/
 
void wedge_data_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        Widget i = (Widget)client_data;
		print_msg("Cylindrical Axis selected is ",wedge_axis);
		XtPopdown(i);
}

/*****************************************************************************
*
*       NAME    :       wedge_data_can_cb()
*
*       DESCRIPTION :   Called when CANCEL is pressed in Cyl_data_entry widget  
*                       
*
******************************************************************************/
 
void wedge_data_can_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        Widget i = (Widget)client_data;
        wedge_axis        = 0 ;           // wedgeinder axis   (application.h)
		XtPopdown(i);
}
 
 

 
