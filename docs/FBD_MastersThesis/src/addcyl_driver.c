/*******************************************************************************
*       FILENAME :      addcyl_driver.c      DESIGN REF :  FBD(CAD/CAPP)
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
*                       cyl_axis_selection()
*
*
*       DESCRIPTION :   Creates DATA ENTRY dialog box for entering data .
*
*******************************************************************************/
 
void cyl_axis_selection()
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
                XmNwidth,               100,
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
 

/*----------------------------------------------------------------------------*/
 
 
        /*----------Radio Box for the selection of the type of topo_link ----*/
 
        Widget form_axis;       // form manager for set of toggle buttons
 
        form_axis = XtVaCreateManagedWidget("AXIS",
                xmFormWidgetClass,      data_rc,
                XmNheight,              100,
                XmNwidth,               100,
                NULL);
 
 
 
        Widget radio_box,xaxis , yaxis,zaxis;
 
        radio_box = XmCreateRadioBox (form_axis, "radio_box", NULL, 0);
 
        xaxis = XtVaCreateManagedWidget ("X_AXIS",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (xaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)XAXIS);
 
 
        yaxis = XtVaCreateManagedWidget ("Y_AXIS",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (yaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)YAXIS);
 
        zaxis = XtVaCreateManagedWidget ("Z_AXIS",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (zaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)ZAXIS);
 
        XtManageChild (radio_box);


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
						(XtCallbackProc)cyl_data_ok_cb,(XtPointer)data_shell);

        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightPosition,       4,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback,
						(XtCallbackProc)cyl_data_can_cb,(XtPointer)data_shell);
 
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
