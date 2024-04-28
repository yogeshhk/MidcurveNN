/*******************************************************************************
*       FILENAME :      zdata_callbacks.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from zdata_entry Table
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
*                       zmin_data_cb()
*
*
*       DESCRIPTION :   Reads the value,fixes the flag
*
*******************************************************************************/
 
void zmin_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	char 	znc[20];


if(z_minf==NO_VALUE){

 
		char *zmin  = XmTextGetString(z_min);   // read the string
               	float zmn = atof(zmin);                  // convert to value
               	XtFree(zmin);                           // free the string
               	sprintf(znc,"%5.2f",zmn);              	// put value identfy

               	XtVaSetValues (z_min,
               		XmNvalue,          znc,
                       	XmNeditable,       False,        // Locking
                       	NULL);
 
		z_minf = zmn;				// value fixed

        if(z_maxf != NO_VALUE){ 
 
                char *zmax  = XmTextGetString(z_max);   // read the widget
                float zmx = atof(zmax);                 // converts it to value
                XtFree(zmax);                           // frees the character 

		if( zmn >= zmx){

			post_msg("Value must be less than X_MAX");

			z_minf=NO_VALUE;		// reset the flag

                	XtVaSetValues (z_min,
                        	XmNeditable, 	True, 	// Un_Locking
                        	NULL);
 
 
                }
		else{

			print_msg("Correct Value entry !!",NO_VALUE);

			z_minf= zmn;			// fixed the value

                	XtVaSetValues (z_min,
                        	XmNeditable,  	False,	// Locking
                        	NULL);
 
                        if(menu_flag==ADD_BLK){

				z_midf=(z_maxf + z_minf)/2;

				char zdc[10];
                		sprintf(zdc,"%5.2f",z_midf);	
 
                		XtVaSetValues (z_mid,
                        		XmNvalue,          zdc,
                        		XmNeditable,       False,// Locking
                        		NULL);

				z_lenf=(z_maxf - z_minf);

				char zlc[10];
                		sprintf(zlc,"%5.2f",z_lenf);
 
                		XtVaSetValues (z_len,
                        		XmNvalue,          zlc,
                        		XmNeditable,       False,        
                        		NULL);

			}

		}

	}

        if(z_midf != NO_VALUE){
 
                char *zmid  = XmTextGetString(z_mid);   // read the widget
                float zmd = atof(zmid);                 // converts it to value
                XtFree(zmid);                           // frees the character
 
                if( zmn >= zmd){
 
                        post_msg("Value must be less than X_MID");
 
                        z_minf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (z_min,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        z_midf= zmd;                    // fixed the value
                        z_minf= zmn;                    // fixed the value
 
                        XtVaSetValues (z_min,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        z_maxf=(2*z_midf) - z_minf;
 
                        char zxc[10];
                        sprintf(zxc,"%5.2f",z_maxf);    // put value identfy
 
                        XtVaSetValues (z_max,
                                XmNvalue,          zxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        z_lenf=(z_maxf - z_minf);
 
                        char zlc[10];
                        sprintf(zlc,"%5.2f",z_lenf);    // put value identfy
 
                        XtVaSetValues (z_len,
                                XmNvalue,          zlc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

        if(z_lenf != NO_VALUE){
 
                char *zlen  = XmTextGetString(z_len);   // read the widget
                float zln = atof(zlen);                 // converts it to value
                XtFree(zlen);                           // frees the character
 
                if( zln <= 0){
 
                        post_msg("Length must be greater than 0");
 
                        z_minf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (z_min,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        z_minf= zmn;                    // fixed the value
 
                        XtVaSetValues (z_min,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        z_maxf=z_lenf + z_minf;
 
                        char zxc[10];
                        sprintf(zxc,"%5.2f",z_maxf);    // put value identfy
 
                        XtVaSetValues (z_max,
                                XmNvalue,          zxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        z_midf=((z_lenf/2)+  z_minf);
 
                        char zdc[10];
                        sprintf(zdc,"%5.2f",z_midf);    // put value identfy
 
                        XtVaSetValues (z_mid,
                                XmNvalue,          zdc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }


 
}
else{

	print_msg(" Value has been already entered !!",NO_VALUE);

       	XtVaSetValues (z_min,
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
*                       zmax_data_cb()
*
*
*       DESCRIPTION :   Reads the value,fixes the flag
*
*******************************************************************************/
 
void zmax_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        char    zxc[20];
 

if(z_maxf==NO_VALUE){
 
 
                char *zmax  = XmTextGetString(z_max);   // read the string
                float zmx = atof(zmax); 		// convert to value
                XtFree(zmax);                           // free the string
                sprintf(zxc,"%5.2f",zmx);              	// put value identfy
 
                XtVaSetValues (z_max,
                        XmNvalue,          zxc,
                        XmNeditable,       False,        // Locking
                        NULL);
 
                z_maxf = zmx;                             // value fixed
 
 
        if(z_minf != NO_VALUE){
 
                char *zmin  = XmTextGetString(z_min);   // read the widget
                float zmn = atof(zmin);                 // converts it to value
                XtFree(zmin);                           // frees the character
 
                if( zmn >= zmx){
 
                        post_msg("Value must be more than X_MIN");
 
                        z_maxf=NO_VALUE; 		// reset the flag

                        XtVaSetValues (z_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        z_minf= zmn;                       // fixed the value
                        z_maxf= zmx;                       // fixed the value

                        XtVaSetValues (z_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        if(menu_flag==ADD_BLK){

				z_midf=(z_maxf + z_minf)/2;
 
                        	char zdc[10];
                        	sprintf(zdc,"%5.2f",z_midf);    
 
                        	XtVaSetValues (z_mid,
                                	XmNvalue,          zdc,
                                	XmNeditable,       False,// Locking
                                	NULL);
 
                        	z_lenf=(z_maxf - z_minf);
 
                        	char zlc[10];
                        	sprintf(zlc,"%5.2f",z_lenf);    
 
                        	XtVaSetValues (z_len,
                                	XmNvalue,          zlc,
                                	XmNeditable,       False,        
                                	NULL);
			} 

 
                }
 
        }
 
        if(z_midf != NO_VALUE){
 
                char *zmid  = XmTextGetString(z_mid);   // read the widget
                float zmd = atof(zmid);                 // converts it to value
                XtFree(zmid);                           // frees the character
 
                if( zmd >= zmx){
 
                        post_msg("Value must be less than X_MID");
 
                        z_maxf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (z_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        z_maxf= zmx;                    // fixed the value
 
                        XtVaSetValues (z_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        z_minf= (2*z_midf) - z_maxf;
 
                        char znc[10];
                        sprintf(znc,"%5.2f",z_minf);    // put value identfy
 
                        XtVaSetValues (z_min,
                                XmNvalue,          znc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        z_lenf=(z_maxf - z_minf);
 
                        char zlc[10];
                        sprintf(zlc,"%5.2f",z_lenf);    // put value identfy
 
                        XtVaSetValues (z_len,
                                XmNvalue,          zlc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

        if(z_lenf != NO_VALUE){
 
                char *zlen  = XmTextGetString(z_len);   // read the widget
                float zln = atof(zlen);                 // converts it to value
                XtFree(zlen);                           // frees the character
 
                if( zln <= 0){
 
                        post_msg("Length must be greater than 0");
 
                        z_maxf=NO_VALUE;                // reset the flag
 
                        XtVaSetValues (z_max,
                                XmNeditable,    True,   // Un_Locking
                                NULL);
 
 
                }
                else{
 
                        print_msg("Correct Value entry !!",NO_VALUE);
 
                        z_lenf= zln;                    // fixed the value
                        z_maxf= zmx;                    // fixed the value
 
                        XtVaSetValues (z_max,
                                XmNeditable,    False,  // Locking
                                NULL);
 
                        z_minf=z_maxf -  z_lenf;
 
                        char znc[10];
                        sprintf(znc,"%5.2f",z_minf);    // put value identfy
 
                        XtVaSetValues (z_min,
                                XmNvalue,          znc,
                                XmNeditable,       False,// Locking
                                NULL);
 
                        z_midf=((z_lenf/2)+  z_minf);
 
                        char zdc[10];
                        sprintf(zdc,"%5.2f",z_midf);    // put value identfy
 
                        XtVaSetValues (z_mid,
                                XmNvalue,          zdc,
                                XmNeditable,       False,        // Locking
                                NULL);
 
 
 
                }
 
        }

}
else{
 
        print_msg(" Value has been already entered !!",NO_VALUE);
 
        XtVaSetValues (z_max,
                XmNeditable,       False,               // Locking
                NULL);
 
 
 
}
        XmProcessTraversal(widget,XmTRAVERSE_NEXT_TAB_GROUP);
 
                                                // goes to the next tab group
        return;
}


