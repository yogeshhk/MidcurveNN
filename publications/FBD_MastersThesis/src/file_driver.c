/*******************************************************************************
*       FILENAME :      file_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to File option on Parent_Menubar
*
*       FUNCTIONS   :   
*                       file_quit_cb()
*                       file_quit_ok_cb()
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   APR 12, 1995.
*
*******************************************************************************/

/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"     	/* Class Declarations :header file */
#include<string.h>

/*******************************************************************************
*
*       NAME    :       void
*                       file_new_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   
*
*******************************************************************************/
 
void
file_new_cb(Widget button, XtPointer client_data, XtPointer call_data)
{

    topo_type   = 0 ;       // No topo_links    			(application.h)
    plane_type  = 0 ;       // No plane selected    		(application.h)

    cyl_axis        = 0 ;           // cylinder axis        (application.h)
    wedge_axis      = 0 ;           // wedge axis           (application.h)
    len_axis        = 0 ;           // length axis          (application.h)
    constrn_pln     = 0 ;           // constrain plane  	(application.h)

    make_Topo_info_null();      	// No topo_info     	(application.h)
    make_temp_planes_null();    	// No planes selection  (application.h)

    comp_flag       = NO_COMP ;     // closing      		(main_window.h)
    block_flag      = NO_BLOCK ;    // closing      		(main_window.h)
    menu_flag       = NO_MENU ;     // closing      		(main_window.h)

    x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;// X-Data flags   (main_window.h)
    y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;// Y-Data flags   (main_window.h)
    z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;// Z-Data flags   (main_window.h)

    drawing_width   = 500;          // equal to 500         (main_window.h)
    drawing_height  = 500;          // equal to 500         (main_window.h)

}

/*******************************************************************************
*
*       NAME    :       void
*                       file_quit_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Creates a Question Dialog asking "Do you want to quit?"
*
*******************************************************************************/
 
void
file_quit_cb(Widget button, XtPointer client_data, XtPointer call_data)
{
    Widget      dialog;
    XmString    msg, yes, no;
 
    dialog      = XmCreateQuestionDialog (toplevel, "dialog", NULL, 0);
 
    yes         = XmStringCreateLocalized ("Yes");
    no          = XmStringCreateLocalized ("No");
    msg         = XmStringCreateLocalized ("Do you want to quit?");
 
 
    XtVaSetValues(dialog,
                XmNmessageString,       msg,
                XmNokLabelString,       yes,
                XmNcancelLabelString,   no,
                XmNdefaultButtonType,   XmDIALOG_CANCEL_BUTTON,
                NULL);
 
    XtUnmanageChild(XmMessageBoxGetChild(dialog, XmDIALOG_HELP_BUTTON));
    XtAddCallback(dialog, XmNokCallback, (XtCallbackProc)file_quit_ok_cb, NULL);
 
    XmStringFree(msg);
    XmStringFree(yes);
    XmStringFree(no);
 
    XtManageChild (dialog);
    XtPopup (XtParent (dialog), XtGrabNone);
}
 
/********************************************************************************
*
*       NAME    :       void
*                       file_quit_ok_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Call back for Exit
*
*******************************************************************************/
 
 
void
file_quit_ok_cb(Widget button, XtPointer client_data, XtPointer call_data)
{
 
        Close_Phigs();			// coded in graphics_phigs.c
        Close_App();			// coded in application.c
        exit(0);
}


/*******************************************************************************
*
*
*       NAME    :       void
*                       filename_save(Widget w, XtPointer c, XtPointer cal)
*
*
*       DESCRIPTION :   Call back for opening file selection Dialog
*
*******************************************************************************/

void filename_save(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
	if(comp_flag==OLD_COMP){
 
		menu_flag	=SAVE;
    	Widget 		dial;
    	Arg 		args[5];
    	int 		n = 0;
 
    	dial = XmCreateFileSelectionDialog (toplevel, "Files", args, n);

    	XtSetSensitive (
        		XmFileSelectionBoxGetChild (dial, XmDIALOG_HELP_BUTTON), 
				False);

    /* if user presses OK button, call new_file_cb() */

		XtAddCallback (dial, 
				XmNokCallback, new_file_cb, 
				NULL);
		XtAddCallback (dial,
				XmNokCallback,temp_action,
				(XtPointer)(XtParent(dial)));

    /* if user presses Cancel button, exit program */

		XtAddCallback(dial,
				XmNcancelCallback,temp_action,
				(XtPointer)(XtParent(dial)));
 
    	XtManageChild (dial);
	}
	else{
        print_msg("No component present",NO_VALUE);
        return;
	}
 
}
 

/*******************************************************************************
*
*
*       NAME    :       void
*                       new_file_cb(Widget w, XtPointer c, XtPointer cal)
*
*
*       DESCRIPTION :   Call back for checking opening of the file
*
*******************************************************************************/
 

void new_file_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	if(menu_flag==SAVE){
 
    	char *file;
    	XmFileSelectionBoxCallbackStruct *cbs =
        	(XmFileSelectionBoxCallbackStruct *) call_data;
 
    /* get the string typed in the text field in char * format */

    	if (!XmStringGetLtoR (cbs->value, XmFONTLIST_DEFAULT_TAG, &file))
        return;

    	if (*file != '/') {

        	/* if it's not a directory, determine the full pathname
         	** of the selection by concatenating it to the "dir" part
         	*/


        char *dir, *newfile;

        	if (XmStringGetLtoR (cbs->dir, XmFONTLIST_DEFAULT_TAG, &dir)) {
            	newfile = XtMalloc (strlen (dir) + 1 + strlen (file) + 1);
            	sprintf (newfile, "%s/%s", dir, file);
            	XtFree( file);
            	XtFree (dir);
            	file = newfile;
        	}
    	}
 
    	if(!*file){
                printf("Nofile selected");
                XtFree (file);
                return;
    	}
    	else{
                FILE *fr = fopen(file,"w");
                compid_save(fr);
                XtFree(file);
    	}
 
	}
	else print_msg("No proper selection",NO_VALUE);
}

/*******************************************************************************
*
*
*       NAME    :       void
*                       compid_save()
*
*
*       DESCRIPTION :   Call back for asking the component to be saved
*
*******************************************************************************/
 

void compid_save(FILE *fp)
{
 
	if(menu_flag==SAVE){
 
 
   		Widget pdial;
 
        XmString t = XmStringCreateLocalized("Enter the Comp. ID");
        Arg args[5];
        int n =0;
 
        XtSetArg(args[n],XmNselectionLabelString,t);n++;
        XtSetArg(args[n],XmNautoUnmanage,False);n++;
 
        pdial = XmCreatePromptDialog(main_w,"SAVE",args,n);
 
        XmStringFree(t);
 
		XtAddCallback(pdial,
			XmNokCallback, 	write_file,
			(XtPointer)fp);

		XtAddCallback(pdial,
			XmNokCallback,	temp_action,
			(XtPointer)(XtParent(pdial)));

		XtAddCallback(pdial,
			XmNcancelCallback,	temp_action,
			(XtPointer)(XtParent(pdial)));
 
		XtSetSensitive(XmSelectionBoxGetChild(pdial,XmDIALOG_HELP_BUTTON),
			False);
 
        XtManageChild(pdial);
        XtPopup(XtParent(pdial),XtGrabNone);
 
	}
    else{
    	print_msg("SAVE was not selected",NO_VALUE);
        return;
    }
 
}

/*******************************************************************************
*
*
*       NAME    :       void
*                       write_file()
*
*
*       DESCRIPTION :   Call back for saving the component to be selected
*
*******************************************************************************/
 
void write_file(Widget widget, XtPointer client_data, XtPointer call_data)
{

	FILE *fp = (FILE *)client_data;

    if(menu_flag==SAVE){
 
    	print_msg("came to write SAVE",NO_VALUE);
		char *val;
		XmSelectionBoxCallbackStruct *cbs ;
		cbs = (XmSelectionBoxCallbackStruct *)call_data;

       	XmStringGetLtoR(cbs->value,XmFONTLIST_DEFAULT_TAG,&val);

       	int comp = atoi(val);
       	Component *tracer;
       	tracer = Get_Comp(comp);
 
       	if(tracer != NULL){
           	tracer->Write_to_file(fp);
			printf("Comp to save %d\n",tracer->Get_component_id());
       	}
       	else print_msg("Cannot write for SAVE ",NO_VALUE);
    }
    else{
    	print_msg(" SAVE was not selected",NO_VALUE);
        return;
    }
}

/*******************************************************************************
*
*
*       NAME    :       void
*                       filename_retrieve()
*
*
*       DESCRIPTION :   Call back for file-opening for retrieving
*
*******************************************************************************/
 
void filename_retrieve(Widget wi, XtPointer client_data, XtPointer call_data)
{
 
    Widget 	dial;
    Arg 	args[5];
    int 	n = 0;
 
    dial = XmCreateFileSelectionDialog (toplevel, "Files", args, n);

    XtSetSensitive (
        XmFileSelectionBoxGetChild (dial, XmDIALOG_HELP_BUTTON), False);

    /* if user presses OK button, call new_file_cb() */

	XtAddCallback (dial, 
		XmNokCallback, open_file_cb, 
		NULL);

	XtAddCallback (dial, 
		XmNokCallback,	temp_action,
		(XtPointer)(XtParent(dial)));

    /* if user presses Cancel button, exit program */

	XtAddCallback(dial,
		XmNcancelCallback,	temp_action,
		(XtPointer)(XtParent(dial)));
 
    XtManageChild (dial);
 
}
 
/*******************************************************************************
*
*
*       NAME    :       void
*                       open_file_cb()
*
*
*       DESCRIPTION :   Call back for file-opening for retrieving
*
*******************************************************************************/
 

void open_file_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

    char *file;
    XmFileSelectionBoxCallbackStruct *cbs =
        (XmFileSelectionBoxCallbackStruct *) call_data;
 


    // get the string typed in the text field in char * format 

    if (!XmStringGetLtoR (cbs->value, XmFONTLIST_DEFAULT_TAG, &file))
        return;

	FILE *fp;

    if( (fp = fopen(file,"r")) == NULL )
    {
        puts("Nofile selected\n");
        XtFree (file);
        return;
    }
    else{
        fp = fopen(file,"r");
		printf("File opened %s\n",file);
		Read_from_file(fp);
		fclose(fp);
        XtFree(file);
    }
 
}


/*******************************************************************************
*
*
*       NAME    :       void
*                       Venkys_save(Widget w, XtPointer c, XtPointer cal)
*
*
*       DESCRIPTION :   Call back for opening file selection Dialog
*
*******************************************************************************/
 
void Venkys_save(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
	if(comp_flag==OLD_COMP){
 
        menu_flag=SAVE;
 
        Widget dial;
        Arg args[5];
        int n = 0;
 
        dial = XmCreateFileSelectionDialog (toplevel, "Files", args, n);
        XtSetSensitive (
                XmFileSelectionBoxGetChild (dial, XmDIALOG_HELP_BUTTON), False);
 
    /* if user presses OK button, call new_file_cb() */
 
		XtAddCallback (dial, 
			XmNokCallback, 	Venkys_file_cb, 
			NULL);
		XtAddCallback (dial,
			XmNokCallback,	temp_action,
			(XtPointer)(XtParent(dial)));
 
    /* if user presses Cancel button, exit program */
 
		XtAddCallback(dial,
			XmNcancelCallback,temp_action,
			(XtPointer)(XtParent(dial)));
 
        XtManageChild (dial);
	}
	else{
        print_msg("No component present",NO_VALUE);
        return;
	}
}
 
/*******************************************************************************
*
*
*       NAME    :       void
*                       Venkys_file_cb(Widget w, XtPointer c, XtPointer cal)
*
*
*       DESCRIPTION :   Call back for checking opening of the file
*
*******************************************************************************/
 
 
void Venkys_file_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
	if(menu_flag==SAVE){
 
    	char *file;
    	XmFileSelectionBoxCallbackStruct *cbs =
        (XmFileSelectionBoxCallbackStruct *) call_data;
 
    /* get the string typed in the text field in char * format */
 
    	if (!XmStringGetLtoR (cbs->value, XmFONTLIST_DEFAULT_TAG, &file))
        return;
 
    	if (*file != '/') {
 
        	/* if it's not a directory, determine the full pathname
         	** of the selection by concatenating it to the "dir" part
         	*/
 
 
        	char *dir, *newfile;
 
        	if (XmStringGetLtoR (cbs->dir, XmFONTLIST_DEFAULT_TAG, &dir)) {
            	newfile = XtMalloc (strlen (dir) + 1 + strlen (file) + 1);
            	sprintf (newfile, "%s/%s", dir, file);
            	XtFree( file);
            	XtFree (dir);
            	file = newfile;
        	}
    	}
 
    	if(!*file){
        	printf("Nofile selected");
            XtFree (file);
            return;
    	}
    	else{
                FILE *fr = fopen(file,"w");
                Venkys_compid_save(fr);
                XtFree(file);
    	}
 
	}
	else print_msg("No proper selection",NO_VALUE);
}

/*******************************************************************************
*
*
*       NAME    :       void
*                       Venkys_compid_save()
*
*
*       DESCRIPTION :   Call back for asking the component to be saved
*
*******************************************************************************/
 
 
void Venkys_compid_save(FILE *fp)
{
 
	if(menu_flag==SAVE){
 
 
    	Widget pdial;
 
        XmString t = XmStringCreateLocalized("Enter the Comp. ID");
        Arg args[5];
        int n =0;
 
        XtSetArg(args[n],XmNselectionLabelString,t);n++;
        XtSetArg(args[n],XmNautoUnmanage,False);n++;
 
        pdial = XmCreatePromptDialog(main_w,"SAVE",args,n);
 
        XmStringFree(t);
 
		XtAddCallback(pdial,
			XmNokCallback, Venkys_write_file,
			(XtPointer)fp);

		XtAddCallback(pdial,
			XmNokCallback,temp_action,
			(XtPointer)(XtParent(pdial)));

		XtAddCallback(pdial,
			XmNcancelCallback,temp_action,
			(XtPointer)(XtParent(pdial)));
 
		XtSetSensitive(XmSelectionBoxGetChild(pdial,XmDIALOG_HELP_BUTTON),
			False);
 
        XtManageChild(pdial);

        XtPopup(XtParent(pdial),XtGrabNone);
 
	}
    else{
    	print_msg("SAVE was not selected",NO_VALUE);
        return;
    }
 
}

/*******************************************************************************
*
*
*       NAME    :       void
*                       Venkys_write_file()
*
*
*       DESCRIPTION :   Call back for saving the component to be selected
*
*******************************************************************************/
 
void Venkys_write_file(Widget wid, XtPointer client_data, XtPointer call_data)
{
 
        FILE *fp = (FILE *)client_data;
 
        if(menu_flag==SAVE){
 
                print_msg("came to write SAVE",NO_VALUE);
 
                char *val;
 
                XmSelectionBoxCallbackStruct *cbs ;
                cbs = (XmSelectionBoxCallbackStruct *)call_data;
 
                XmStringGetLtoR(cbs->value,XmFONTLIST_DEFAULT_TAG,&val);
 
                int comp = atoi(val);
 
                Component *tracer;
 
                tracer = Get_Comp(comp);
 
                if(tracer != NULL){
                        tracer->Write_to_Venkys_file(fp);
                        printf("Comp to save %d\n",tracer->Get_component_id());
                }
                else{
 
                        print_msg("Cannot write for SAVE ",NO_VALUE);
 
                }
 
        }
        else{
                print_msg(" SAVE was not selected",NO_VALUE);
                return;
        }
 
 
}

