/*******************************************************************************
*       FILENAME :      create_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Create option on Design_Menubar
*
*       FUNCTIONS   :   
*			create_newcomp_cb(Widget , XtPointer , XtPointer )
*			create_addtopo_cb(Widget , XtPointer , XtPointer )
*			make_data_entry_table(int blk_type)
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
#include "graphics_phigs.h"     /* Phigs Declarations :header file */

/********************************************************************************
*
*       NAME    :       void
*                       create_newcomp_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Depending on the button in PullCreate,calls the function
*                       Starts the of the new Component and options(switch state
*                       -ment)cll function specific to the type of block chosen.
*
*******************************************************************************/
 
void create_newcomp_cb(Widget widget,XtPointer client_data,XtPointer call_data)
{
        int item_no = (int)client_data;		// which No. button was selected
 
        menu_flag= CREATE;      // user has selected CREATE
        comp_flag= NEW_COMP;    // user has selected New_comp button
 
 
                switch(item_no)
                        {
                        case 0 :
                                block_flag = BLOC;
								make_data_entry_table(BLOC);
                                break;
 
                        case 1 :
                                block_flag = CYLINDR;
								post_msg(" Not implementd yet !!!");
                                break;
 
                        case 2 :
                                block_flag = PBLOCK;
								post_msg(" Not implementd yet !!!");
                                break;
 
                        default:
                                block_flag = NO_BLOCK;
								menu_flag  = NO_MENU ;
								comp_flag  = NO_COMP ;
								post_msg("Error !!!");
								break;
 
                        }
 
}


/********************************************************************************
*
*       NAME    :       void
*                       create_addtopo_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Depending on the button PullrightaddBlock,calls function
*                       Adds topological link between two existing blocks.
*
*******************************************************************************/
 
void create_addtopo_cb(Widget w, XtPointer client_data, XtPointer call_data)
{
        int item_no = (int)client_data;
        block_flag = NO_BLOCK;
        menu_flag  = NO_MENU ;
        comp_flag  = NO_COMP ;
		post_msg(" Not implementd yet !!!");
 
}
 
/*******************************************************************************
*
*       NAME    :       void
*						make_data_entry_table(int blk_type)
*
*
*       DESCRIPTION :   Creates DATA ENTRY dialog box for entering data .
*
*******************************************************************************/
 
void make_data_entry_table(int blk_type)
{
 
 
 
	if(comp_flag != NO_COMP){
 
        Widget data_shell ;		// dialog shell : managing custom dialog
        data_shell = XmCreateDialogShell(toplevel,"Data Input",NULL,0);

        Widget data_rc ;		// Keeps childer one bellow another
        data_rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,data_shell,
                        XmNorientation, XmVERTICAL,
                        XmNwidth,       400,
                        NULL);
 
 
 
		/*------------------------------------------------------------------*/
 

		Widget	form_title ;		// contains name of dialog box

        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                NULL);
 
		Widget	fram ;			// gives itched border to widget

        fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
		Widget	nam ;			// label widget with name

        nam = XtVaCreateManagedWidget("DATA_ENTRY_TABLE",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
		/*------------------------------------------------------------------*/
 

		Widget	form_comp ;		// form manager

        form_comp = XtVaCreateManagedWidget("minimum",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 

		Widget	label_comp ;		// label before text widget

        label_comp = XtVaCreateManagedWidget("COMP_NAME",
                xmLabelGadgetClass,     form_comp,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
                char c_id[20];
                sprintf(c_id,"%d",comp_num);// next asking component no.

					// global text widget for to get comp_id

        comp_id = XtVaCreateManagedWidget("COMP_ID",
                xmTextWidgetClass,      form_comp,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               c_id,
                NULL);
 
 
		Widget	label_block;		// label before text widget

        label_block = XtVaCreateManagedWidget("BLK_NAME",
                xmLabelGadgetClass,     form_comp,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
                char b_id[20];
                sprintf(b_id,"%d",blk_num);

					// global text widget for block_id
 
        block_id = XtVaCreateManagedWidget(" BLOCK",
                xmTextWidgetClass,      form_comp,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               b_id,
                NULL);
 
        Widget sep;
 
        sep =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,  data_rc,
                NULL);
 
	/*------------------------------------------------------------------*/
 

		Widget	form_label ;	// contains headings for x_data ,y_data..

       	form_label = XtVaCreateManagedWidget("headings",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);

		Widget	labelX ;
 
        labelX = XtVaCreateManagedWidget(" X_DATA ",
                xmLabelGadgetClass,     form_label,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
		Widget	labelY ;

        labelY = XtVaCreateManagedWidget(" Y_DATA ",
                xmLabelGadgetClass,     form_label,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                NULL);
 
		Widget	labelZ ;

        labelZ = XtVaCreateManagedWidget(" Z_DATA",
                xmLabelGadgetClass,     form_label,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       8,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
		/*------------------------------------------------------------------*/
 
		Widget	form_min ;	// contains label and 3 text widgets for MIN 
 
        form_min = XtVaCreateManagedWidget("minimum",
 
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);

		Widget	label_min ;
 
        label_min = XtVaCreateManagedWidget(" MIN ",
                xmLabelGadgetClass,     form_min,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        1,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);


	/* x_min widget is made global so as to get & set data from anywhere */ 

        x_min = XtVaCreateManagedWidget(" X_MIN",
                xmTextWidgetClass,      form_min,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "10",
                NULL);
 
		XtAddCallback(x_min,XmNactivateCallback,
				(XtCallbackProc)xmin_data_cb,
				NULL);
 
	/* y_min widget is made global so as to get & set data from anywhere */ 

        y_min = XtVaCreateManagedWidget("Y_MIN",
                xmTextWidgetClass,      form_min,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNvalue,               "10",
                NULL);
 
		XtAddCallback(y_min,XmNactivateCallback,
				(XtCallbackProc)ymin_data_cb,
				NULL);
 

	/* z_min widget is made global so as to get & set data from anywhere */ 

        z_min = XtVaCreateManagedWidget("Z_MIN",
                xmTextWidgetClass,      form_min,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "10",
                NULL);
 
		XtAddCallback(z_min,XmNactivateCallback,
				(XtCallbackProc)zmin_data_cb,
				NULL);
 
 
		/*------------------------------------------------------------------*/
 
		Widget	form_max ;		// contains label and 3 text widgets 
 
        form_max = XtVaCreateManagedWidget("maximum",
 
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 

		Widget	label_max ;


        label_max = XtVaCreateManagedWidget(" MAX ",
                xmLabelGadgetClass,     form_max,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        1,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
	/* x_max widget is made global so as to get & set data from anywhere */ 

        x_max = XtVaCreateManagedWidget(" X_MAX",
                xmTextWidgetClass,      form_max,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "30",
                NULL);
 
		XtAddCallback(x_max,XmNactivateCallback,
				(XtCallbackProc)xmax_data_cb,
				NULL);
 
 
	/* y_max widget is made global so as to get & set data from anywhere */ 

        y_max = XtVaCreateManagedWidget("Y_MAX",
                xmTextWidgetClass,      form_max,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNvalue,               "30",
                NULL);
 
 
	/* z_max widget is made global so as to get & set data from anywhere */ 
 
		XtAddCallback(y_max,XmNactivateCallback,
				(XtCallbackProc)ymax_data_cb,
				NULL);
 
        z_max = XtVaCreateManagedWidget("Z_MAX",
                xmTextWidgetClass,      form_max,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "30",
                NULL);
 
 
		XtAddCallback(z_max,XmNactivateCallback,
				(XtCallbackProc)zmax_data_cb,
				NULL);
 
 
		/*------------------------------------------------------------------*/
 
        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,         data_rc,
                NULL);
 
 
		/*----------Control Area buttons -----------------------------------*/

		Widget	form_ok ;
 
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        6,
                NULL);
 
        Widget ok,can;
 
        ok = XtVaCreateManagedWidget("  OK  ",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightPosition,       2,
                XmNalignment,           XmALIGNMENT_END,
                NULL);
 
		XtAddCallback(ok,XmNactivateCallback,
				(XtCallbackProc)data_entry_ok,
				(XtPointer)data_shell);

        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)data_entry_can,
				(XtPointer)data_shell);
 
        XtManageChild(data_rc);
        XtManageChild(data_shell);
 
 
	}			// end of comp_flag if
	else{

        post_msg("Create has not been selected");
		block_flag = NO_BLOCK ;
		menu_flag  = NO_MENU ;
        return;
	}
 
}
 
 
 

