/*******************************************************************************
*       FILENAME :      xdata_callbacks.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from xdata_entry Table
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   June 17, 1995.
*
*******************************************************************************/
 
 
/******************************************************************************
                       INCLUDE FILES
******************************************************************************/
 
#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "classes.h"        	/* Classes Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
 
/*******************************************************************************
*
*       NAME    :       void
*                       xmin_data_cb()
*
*
*       DESCRIPTION :   Reads the value,fixes the flag
*
*******************************************************************************/
 
void xmin_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	char 	xnc[20];


if(x_minf==NO_VALUE){

 
		char *xmin  = XmTextGetString(x_min);   // read the string
               	float xmn = atof(xmin);                  // convert to value
               	XtFree(xmin);                           // free the string
               	sprintf(xnc,"%5.2f",xmn);              	// put value identfy

               	XtVaSetValues (x_min,
               		XmNvalue,          xnc,
                       	XmNeditable,       False,        // Locking
                       	NULL);
 
		x_minf = xmn;				// value fixed

        if(x_maxf != NO_VALUE){ 
 
                char *xmax  = XmTextGetString(x_max);   // read the widget
                float xmx = atof(xmax);                 // converts it to value
                XtFree(xmax);                           // frees the character 

		if( xmn >= xmx){

			post_msg("Value must be less than X_MAX");

			x_minf=NO_VALUE;		// reset the flag

                	XtVaSetValues (x_min,
                        	XmNeditable, 	True, 	// Un_Locking
                        	NULL);
 
 
                }
		else{

			print_msg("Correct Value entry !!",NO_VALUE);

			x_minf= xmn;			// fixed the value

                	XtVaSetValues (x_min,
                        	XmNeditable,  	False,	// Locking
                        	NULL);
 
                        if(menu_flag==ADD_BLK){

				x_midf=(x_maxf + x_minf)/2;

				char xdc[10];
                		sprintf(xdc,"%5.2f",x_midf);
 
                		XtVaSetValues (x_mid,
                        		XmNvalue,          xdc,
                        		XmNeditable,       False,// Locking
                        		NULL);

				x_lenf=(x_maxf - x_minf);

				char xlc[10];
                		sprintf(xlc,"%5.2f",x_lenf);
 
                		XtVaSetValues (x_len,
                        		XmNvalue,          xlc,
                        		XmNeditable,       False, 
                        		NULL);

			}

		}

	}

        if(x_midf != NO_VALUE){
 
                char *xmid  = XmTextGetString(x_mid);   // read the widget
                float xmd = atof(xmid);                 // converts it to value
                XtFree(xmid);                           // frees the character
 
                if( xmn >= xmd){
 
                        post_msg("Value must be less than X_MID");
 
                        x_minf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (x_min,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        x_midf= xmd;                    // fixed the value
                        x_minf= xmn;                    // fixed the value
 
                        XtVaSetValues (x_min,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        x_maxf=(2*x_midf) - x_minf;
 
                        char xxc[10];
                        sprintf(xxc,"%5.2f",x_maxf);    // put value identfy
 
                        XtVaSetValues (x_max,
                                XmNvalue,          xxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        x_lenf=(x_maxf - x_minf);
 
                        char xlc[10];
                        sprintf(xlc,"%5.2f",x_lenf);    // put value identfy
 
                        XtVaSetValues (x_len,
                                XmNvalue,          xlc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

        if(x_lenf != NO_VALUE){
 
                char *xlen  = XmTextGetString(x_len);   // read the widget
                float xln = atof(xlen);                 // converts it to value
                XtFree(xlen);                           // frees the character
 
                if( xln <= 0){
 
                        post_msg("Length must be greater than 0");
 
                        x_minf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (x_min,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        x_minf= xmn;                    // fixed the value
 
                        XtVaSetValues (x_min,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        x_maxf=x_lenf + x_minf;
 
                        char xxc[10];
                        sprintf(xxc,"%5.2f",x_maxf);    // put value identfy
 
                        XtVaSetValues (x_max,
                                XmNvalue,          xxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        x_midf=((x_lenf/2)+  x_minf);
 
                        char xdc[10];
                        sprintf(xdc,"%5.2f",x_midf);    // put value identfy
 
                        XtVaSetValues (x_mid,
                                XmNvalue,          xdc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }


 
}
else{

	print_msg(" Value has been already entered !!",NO_VALUE);

       	XtVaSetValues (x_min,
       		XmNeditable,       False,        	// Locking
               	NULL);
 


} 
        XmProcessTraversal(widget,XmTRAVERSE_NEXT_TAB_GROUP);   

						// goes to the next tab group
        return ;
}

/*******************************************************************************
*
*       NAME    :       void
*                       xmax_data_cb()
*
*
*       DESCRIPTION :   Reads the value,fixes the flag
*
*******************************************************************************/
 
void xmax_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        char    xxc[20];
 

if(x_maxf==NO_VALUE){
 
 
                char *xmax  = XmTextGetString(x_max);   // read the string
                float xmx = atof(xmax); 		// convert to value
                XtFree(xmax);                           // free the string
                sprintf(xxc,"%5.2f",xmx);              	// put value identfy
 
                XtVaSetValues (x_max,
                        XmNvalue,          xxc,
                        XmNeditable,       False,        // Locking
                        NULL);
 
                x_maxf = xmx;                             // value fixed
 
 
        if(x_minf != NO_VALUE){
 
                char *xmin  = XmTextGetString(x_min);   // read the widget
                float xmn = atof(xmin);                 // converts it to value
                XtFree(xmin);                           // frees the character
 
                if( xmn >= xmx){
 
                        post_msg("Value must be more than X_MIN");
 
                        x_maxf=NO_VALUE; 		// reset the flag

                        XtVaSetValues (x_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        x_minf= xmn;                       // fixed the value
                        x_maxf= xmx;                       // fixed the value

                        XtVaSetValues (x_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
			if(menu_flag==ADD_BLK){

				x_midf=(x_maxf + x_minf)/2;
 
                        	char xdc[10];
                        	sprintf(xdc,"%5.2f",x_midf);
 
                        	XtVaSetValues (x_mid,
                                	XmNvalue,          xdc,
                                	XmNeditable,       False,// Locking
                                	NULL);
 
                        	x_lenf=(x_maxf - x_minf);
 
                        	char xlc[10];
                        	sprintf(xlc,"%5.2f",x_lenf);
 
                        	XtVaSetValues (x_len,
                                	XmNvalue,          xlc,
                                	XmNeditable,       False,  
                                	NULL);
			} 

 
                }
 
        }
 
        if(x_midf != NO_VALUE){
 
                char *xmid  = XmTextGetString(x_mid);   // read the widget
                float xmd = atof(xmid);                 // converts it to value
                XtFree(xmid);                           // frees the character
 
                if( xmd >= xmx){
 
                        post_msg("Value must be less than X_MID");
 
                        x_maxf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (x_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        x_maxf= xmx;                    // fixed the value
 
                        XtVaSetValues (x_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        x_minf= (2*x_midf) - x_maxf;
 
                        char xnc[10];
                        sprintf(xnc,"%5.2f",x_minf);    // put value identfy
 
                        XtVaSetValues (x_min,
                                XmNvalue,          xnc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        x_lenf=(x_maxf - x_minf);
 
                        char xlc[10];
                        sprintf(xlc,"%5.2f",x_lenf);    // put value identfy
 
                        XtVaSetValues (x_len,
                                XmNvalue,          xlc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

        if(x_lenf != NO_VALUE){
 
                char *xlen  = XmTextGetString(x_len);   // read the widget
                float xln = atof(xlen);                 // converts it to value
                XtFree(xlen);                           // frees the character
 
                if( xln <= 0){
 
                        post_msg("Length must be greater than 0");
 
                        x_maxf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (x_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        x_lenf= xln;                    // fixed the value
                        x_maxf= xmx;                    // fixed the value
 
                        XtVaSetValues (x_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        x_minf=x_maxf -  x_lenf;
 
                        char xnc[10];
                        sprintf(xnc,"%5.2f",x_minf);    // put value identfy
 
                        XtVaSetValues (x_min,
                                XmNvalue,          xnc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        x_midf=((x_lenf/2)+  x_minf);
 
                        char xdc[10];
                        sprintf(xdc,"%5.2f",x_midf);    // put value identfy
 
                        XtVaSetValues (x_mid,
                                XmNvalue,          xdc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

}
else{
 
        print_msg(" Value has been already entered !!",NO_VALUE);
 
        XtVaSetValues (x_max,
                XmNeditable,       False,               // Locking
                NULL);
 
 
 
}
        XmProcessTraversal(widget,XmTRAVERSE_NEXT_TAB_GROUP);
 
                                                // goes to the next tab group
        return;
}


