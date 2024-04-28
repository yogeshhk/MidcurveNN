/*******************************************************************************
*       FILENAME :      addwedge_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Add_Block(CYL) option on CREATE
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 3, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"		/* Class definitions */

/******************************************************************************
                        GLOBAL DECLARATIONS(INTERFACE)
******************************************************************************/

/*******************************************************************************
*
*       NAME    :       void
*                       wedge_axis_selection()
*
*
*       DESCRIPTION :   Creates DATA ENTRY dialog box for entering data .
*
*******************************************************************************/
 
void wedge_axis_selection()
{
 
if(comp_flag != NO_COMP){
 
        Widget data_shell ;             // dialog shell : managing custom dialog
 
        data_shell = XmCreateDialogShell(toplevel,"Data Input",NULL,0);
 
 
        Widget data_rc ;                // Keeps childer one bellow another
 
        data_rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,data_shell,
                        XmNorientation, XmVERTICAL,
                        XmNwidth,       400,
                        NULL);
 
/*----------------------------------------------------------------------------*/
 
 
        Widget  form_title ;            // contains name of dialog box
 
        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               400,
                NULL);
 
        Widget  fram ;                  // gives itched border to widget
 
        fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
        Widget  nam ;                   // label widget with name
 
        nam = XtVaCreateManagedWidget("AXIS SEL",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
	
        Widget form_mid;       // form manager for set of toggle buttons
 
        form_mid = XtVaCreateManagedWidget("MID",
                xmFormWidgetClass,      data_rc,
				 XmNfractionBase,        4,
                NULL);
 


/*----------------------------------------------------------------------------*/
 
 
        /*----------Radio Box for the selection of the type of topo_link ----*/
 
        Widget form_axis;       // form manager for set of toggle buttons
 
        form_axis = XtVaCreateManagedWidget("AXIS",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                NULL);
 
 
 
        Widget radio_box,xaxis , yaxis,zaxis;
 
        radio_box = XmCreateRadioBox (form_axis, "radio_box", 
				NULL, 0);
 
        xaxis = XtVaCreateManagedWidget ("X_AXIS",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (xaxis, XmNvalueChangedCallback,
						wedge_axis_sel_cb,(XtPointer)XAXIS);
 
 
        yaxis = XtVaCreateManagedWidget ("Y_AXIS",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (yaxis, XmNvalueChangedCallback,
						wedge_axis_sel_cb,(XtPointer)YAXIS);
 
        zaxis = XtVaCreateManagedWidget ("Z_AXIS",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (zaxis, XmNvalueChangedCallback,
				wedge_axis_sel_cb,(XtPointer)ZAXIS);
 
        XtManageChild (radio_box);


        /*----------Radio Box for the selection of the Butting Plane ----*/
 
        Widget form_plane;       // form manager for set of toggle buttons
 
        form_plane = XtVaCreateManagedWidget("PLANE",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightAttachment,     XmATTACH_FORM,
                NULL);
 
 
 
        Widget radio_box2,minmin,minmax,maxmin,maxmax;
 
        radio_box2 = XmCreateRadioBox (form_plane, "radio_box",
                NULL, 0);
 
        minmin = XtVaCreateManagedWidget ("MINMIN",
                xmToggleButtonGadgetClass, radio_box2, NULL);
 
		XtAddCallback (minmin,XmNvalueChangedCallback,
				wedge_pl_sel_cb,(XtPointer)MIN_MIN);
 
 
        minmax = XtVaCreateManagedWidget ("MINMAX",
                xmToggleButtonGadgetClass, radio_box2, NULL);
 
		XtAddCallback (minmax,XmNvalueChangedCallback,
				wedge_pl_sel_cb,(XtPointer)MIN_MAX);

        maxmin = XtVaCreateManagedWidget ("MAXMIN",
                xmToggleButtonGadgetClass, radio_box2, NULL);
 
		XtAddCallback (maxmin,XmNvalueChangedCallback,
				wedge_pl_sel_cb,(XtPointer)MAX_MIN);
        maxmax = XtVaCreateManagedWidget ("MAXMAX",
                xmToggleButtonGadgetClass, radio_box2, NULL);
 
		XtAddCallback (maxmax,XmNvalueChangedCallback,
				wedge_pl_sel_cb,(XtPointer)MAX_MAX);

        XtManageChild (radio_box2);

        Widget sep;
 
        sep =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,  data_rc,
                NULL);
 


/*--------------------Control Area buttons -----------------------------------*/
 
        Widget  form_ok ;
 
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               100,
                XmNfractionBase,        4,
                NULL);
 
        Widget ok,can;
 
        ok = XtVaCreateManagedWidget("  OK  ",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightPosition,       1,
                XmNalignment,           XmALIGNMENT_END,
                NULL);
 
		XtAddCallback(ok,XmNactivateCallback,
					(XtCallbackProc)wedge_data_ok_cb,(XtPointer)data_shell);

        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightPosition,       4,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)wedge_data_can_cb,(XtPointer)data_shell);
 
        XtManageChild(data_rc);
 
        XtManageChild(data_shell);
 
 
}                       // end of comp_flag if
else{
        post_msg("Create has not been selected");
        block_flag = NO_BLOCK ;
        menu_flag  = NO_MENU ;
        return;
}

}
