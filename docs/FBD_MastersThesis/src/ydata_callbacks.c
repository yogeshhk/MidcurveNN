/*******************************************************************************
*       FILENAME :      ydata_callbacks.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from ydata_entry Table
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
*                       ymin_data_cb()
*
*
*       DESCRIPTION :   Reads the value,fixes the flag
*
*******************************************************************************/
 
void ymin_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	char 	ync[20];


if(y_minf==NO_VALUE){

 
		char *ymin  = XmTextGetString(y_min);   // read the string
               	float ymn = atof(ymin);                  // convert to value
               	XtFree(ymin);                           // free the string
               	sprintf(ync,"%5.2f",ymn);              	// put value identfy

               	XtVaSetValues (y_min,
               		XmNvalue,          ync,
                       	XmNeditable,       False,        // Locking
                       	NULL);
 
		y_minf = ymn;				// value fixed

        if(y_maxf != NO_VALUE){ 
 
                char *ymax  = XmTextGetString(y_max);   // read the widget
                float ymx = atof(ymax);                 // converts it to value
                XtFree(ymax);                           // frees the character 

		if( ymn >= ymx){

			post_msg("Value must be less than X_MAX");

			y_minf=NO_VALUE;		// reset the flag

                	XtVaSetValues (y_min,
                        	XmNeditable, 	True, 	// Un_Locking
                        	NULL);
 
 
                }
		else{

			print_msg("Correct Value entry !!",NO_VALUE);

			y_minf= ymn;			// fixed the value

                	XtVaSetValues (y_min,
                        	XmNeditable,  	False,	// Locking
                        	NULL);
 
                        if(menu_flag==ADD_BLK){

				y_midf=(y_maxf + y_minf)/2;

				char ydc[10];
                		sprintf(ydc,"%5.2f",y_midf);
 
                		XtVaSetValues (y_mid,
                        		XmNvalue,          ydc,
                        		XmNeditable,       False,// Locking
                        		NULL);

				y_lenf=(y_maxf - y_minf);

				char ylc[10];
                		sprintf(ylc,"%5.2f",y_lenf);
 
                		XtVaSetValues (y_len,
                        		XmNvalue,          ylc,
                        		XmNeditable,       False,        
                        		NULL);

			}

		}

	}

        if(y_midf != NO_VALUE){
 
                char *ymid  = XmTextGetString(y_mid);   // read the widget
                float ymd = atof(ymid);                 // converts it to value
                XtFree(ymid);                           // frees the character
 
                if( ymn >= ymd){
 
                        post_msg("Value must be less than X_MID");
 
                        y_minf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (y_min,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        y_midf= ymd;                    // fixed the value
                        y_minf= ymn;                    // fixed the value
 
                        XtVaSetValues (y_min,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        y_maxf=(2*y_midf) - y_minf;
 
                        char yxc[10];
                        sprintf(yxc,"%5.2f",y_maxf);    // put value identfy
 
                        XtVaSetValues (y_max,
                                XmNvalue,          yxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        y_lenf=(y_maxf - y_minf);
 
                        char ylc[10];
                        sprintf(ylc,"%5.2f",y_lenf);    // put value identfy
 
                        XtVaSetValues (y_len,
                                XmNvalue,          ylc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

        if(y_lenf != NO_VALUE){
 
                char *ylen  = XmTextGetString(y_len);   // read the widget
                float yln = atof(ylen);                 // converts it to value
                XtFree(ylen);                           // frees the character
 
                if( yln <= 0){
 
                        post_msg("Length must be greater than 0");
 
                        y_minf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (y_min,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        y_minf= ymn;                    // fixed the value
 
                        XtVaSetValues (y_min,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        y_maxf=y_lenf + y_minf;
 
                        char yxc[10];
                        sprintf(yxc,"%5.2f",y_maxf);    // put value identfy
 
                        XtVaSetValues (y_max,
                                XmNvalue,          yxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        y_midf=((y_lenf/2)+  y_minf);
 
                        char ydc[10];
                        sprintf(ydc,"%5.2f",y_midf);    // put value identfy
 
                        XtVaSetValues (y_mid,
                                XmNvalue,          ydc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }


 
}
else{

	print_msg(" Value has been already entered !!",NO_VALUE);

       	XtVaSetValues (y_min,
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
*                       ymax_data_cb()
*
*
*       DESCRIPTION :   Reads the value,fixes the flag
*
*******************************************************************************/
 
void ymax_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        char    yxc[20];
 

if(y_maxf==NO_VALUE){
 
 
                char *ymax  = XmTextGetString(y_max);   // read the string
                float ymx = atof(ymax); 		// convert to value
                XtFree(ymax);                           // free the string
                sprintf(yxc,"%5.2f",ymx);              	// put value identfy
 
                XtVaSetValues (y_max,
                        XmNvalue,          yxc,
                        XmNeditable,       False,        // Locking
                        NULL);
 
                y_maxf = ymx;                             // value fixed
 
 
        if(y_minf != NO_VALUE){
 
                char *ymin  = XmTextGetString(y_min);   // read the widget
                float ymn = atof(ymin);                 // converts it to value
                XtFree(ymin);                           // frees the character
 
                if( ymn >= ymx){
 
                        post_msg("Value must be more than X_MIN");
 
                        y_maxf=NO_VALUE; 		// reset the flag

                        XtVaSetValues (y_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        y_minf= ymn;                       // fixed the value
                        y_maxf= ymx;                       // fixed the value

                        XtVaSetValues (y_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        if(menu_flag==ADD_BLK){

				y_midf=(y_maxf + y_minf)/2;
 
                        	char ydc[10];
                        	sprintf(ydc,"%5.2f",y_midf);
 
                        	XtVaSetValues (y_mid,
                                	XmNvalue,          ydc,
                                	XmNeditable,       False,// Locking
                                	NULL);
 
                        	y_lenf=(y_maxf - y_minf);
 
                        	char ylc[10];
                        	sprintf(ylc,"%5.2f",y_lenf);    
 
                        	XtVaSetValues (y_len,
                                	XmNvalue,          ylc,
                                	XmNeditable,       False,        
                                	NULL);

			}

 
                }
 
        }
 
        if(y_midf != NO_VALUE){
 
                char *ymid  = XmTextGetString(y_mid);   // read the widget
                float ymd = atof(ymid);                 // converts it to value
                XtFree(ymid);                           // frees the character
 
                if( ymd >= ymx){
 
                        post_msg("Value must be less than X_MID");
 
                        y_maxf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (y_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        y_midf= ymd;                    // fixed the value
                        y_maxf= ymx;                    // fixed the value
 
                        XtVaSetValues (y_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        y_minf=(2*y_midf) - y_maxf;
 
                        char ync[10];
                        sprintf(ync,"%5.2f",y_minf);    // put value identfy
 
                        XtVaSetValues (y_min,
                                XmNvalue,          ync,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        y_lenf=(y_maxf - y_minf);
 
                        char ylc[10];
                        sprintf(ylc,"%5.2f",y_lenf);    // put value identfy
 
                        XtVaSetValues (y_len,
                                XmNvalue,          ylc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

        if(y_lenf != NO_VALUE){
 
                char *ylen  = XmTextGetString(y_len);   // read the widget
                float yln = atof(ylen);                 // converts it to value
                XtFree(ylen);                           // frees the character
 
                if( yln <= 0){
 
                        post_msg("Length must be greater than 0");
 
                        y_maxf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (y_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        y_lenf= yln;                    // fixed the value
                        y_maxf= ymx;                    // fixed the value
 
                        XtVaSetValues (y_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        y_minf=y_maxf -  y_lenf;
 
                        char ync[10];
                        sprintf(ync,"%5.2f",y_minf);    // put value identfy
 
                        XtVaSetValues (y_min,
                                XmNvalue,          ync,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        y_midf=((y_lenf/2)+  y_minf);
 
                        char ydc[10];
                        sprintf(ydc,"%5.2f",y_midf);    // put value identfy
 
                        XtVaSetValues (y_mid,
                                XmNvalue,          ydc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
                }
 
        }

}
else{
 
        print_msg(" Value has been already entered !!",NO_VALUE);
 
        XtVaSetValues (y_max,
                XmNeditable,       False,               // Locking
                NULL);
 
 
 
}
        XmProcessTraversal(widget,XmTRAVERSE_NEXT_TAB_GROUP);
 
                                                // goes to the next tab group
        return;
}


