/*******************************************************************************
*       FILENAME :      topo_selection_callbacks.c DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from topo_selection Table
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
*       NAME            : make_full_data_entry_table()
*
*       DESCRIPTION     : Creates a data enrty table with all the 12 data fields
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void make_full_data_entry_table()
{


        Widget shell ;	/* shell is shell for managing this custom dialog */
 
        shell = XmCreateDialogShell(toplevel,"Data Input",NULL,0);
 
 
		Widget rc; 	/* rc is manager widget.*/
 
        rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation, XmVERTICAL,
                        XmNwidth,       400,
                        NULL);
 
 
 
		/*------------------------------------------------------------------*/
 
		Widget form_title ; 	/* contains title of dialog box */

        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 
		Widget nam;

        nam = XtVaCreateManagedWidget("DATA_ENTRY_TABLE_FOR ",
                xmLabelGadgetClass,     form_title,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                //XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
        Widget  label_block;            // label before text widget
 
        label_block = XtVaCreateManagedWidget("BLK_NAME",
                xmLabelGadgetClass,     form_title,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
                char b_id[20];
                sprintf(b_id,"%d",blk_num);
 
                                        // global text widget for block_id
 
        block_id = XtVaCreateManagedWidget(" BLOCK",
                xmTextWidgetClass,      form_title,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        6,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       8,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               b_id,
                NULL);
 
        Widget sep4;
 
        sep4 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,         rc,
                NULL);
 

		/*------------------------------------------------------------------*/

        /* contains headings for X_data,Y_data,Z_data...*/
 
 
		Widget form_label;

        form_label = XtVaCreateManagedWidget("headings",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 
		Widget labelX;

        labelX = XtVaCreateManagedWidget(" X_DATA ",
                xmLabelGadgetClass,     form_label,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
		Widget labelY;

        labelY = XtVaCreateManagedWidget(" Y_DATA ",
                xmLabelGadgetClass,     form_label,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                NULL);
 
		Widget labelZ;

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
 
 
		Widget form_min;
 
        form_min = XtVaCreateManagedWidget("minimum",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);

		Widget label_min;

        label_min = XtVaCreateManagedWidget(" MIN ",
                xmLabelGadgetClass,     form_min,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

 
        x_min = XtVaCreateManagedWidget(" X_MIN",
                xmTextWidgetClass,      form_min,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
		XtAddCallback(x_min,XmNactivateCallback,
				(XtCallbackProc)xmin_data_cb,NULL);
 

        y_min = XtVaCreateManagedWidget("Y_MIN",
                xmTextWidgetClass,      form_min,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
		XtAddCallback(y_min,XmNactivateCallback,
				(XtCallbackProc)ymin_data_cb,NULL);
 

        z_min = XtVaCreateManagedWidget("Z_MIN",
                xmTextWidgetClass,      form_min,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
		XtAddCallback(z_min,XmNactivateCallback,
				(XtCallbackProc)zmin_data_cb,NULL);

 
		/*------------------------------------------------------------------*/
 
 
		Widget form_max;
 
        form_max = XtVaCreateManagedWidget("maximum",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 

		Widget label_max;

        label_max = XtVaCreateManagedWidget(" MAX ",
                xmLabelGadgetClass,     form_max,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 

        x_max = XtVaCreateManagedWidget(" X_MAX",
                xmTextWidgetClass,      form_max,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
		XtAddCallback(x_max,XmNactivateCallback,
				(XtCallbackProc)xmax_data_cb,NULL);
 

        y_max = XtVaCreateManagedWidget("Y_MAX",
                xmTextWidgetClass,      form_max,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
		XtAddCallback(y_max,XmNactivateCallback,
				(XtCallbackProc)ymax_data_cb,NULL);
 


        z_max = XtVaCreateManagedWidget("Z_MAX",
                xmTextWidgetClass,      form_max,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
 
		XtAddCallback(z_max,XmNactivateCallback,
				(XtCallbackProc)zmax_data_cb,NULL);
 
 
		/*------------------------------------------------------------------*/
 
        Widget sep3;
 
        sep3 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,         rc,
                NULL);
 
        Widget form_mid;
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 
        Widget label_mid;
 
        label_mid = XtVaCreateManagedWidget(" MID ",
                xmLabelGadgetClass,     form_mid,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
        x_mid = XtVaCreateManagedWidget(" X_MID",
                xmTextWidgetClass,      form_mid,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "NO_VALUE",
                XmNeditable,            False,
                NULL);
 
 
        y_mid = XtVaCreateManagedWidget("Y_MID",
                xmTextWidgetClass,      form_mid,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNvalue,               "NO_VALUE",
                XmNeditable,            False,
                NULL);
 
 
        z_mid = XtVaCreateManagedWidget("Z_MID",
                xmTextWidgetClass,      form_mid,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "NO_VALUE",
                XmNeditable,            False,
                NULL);
 

		Widget form_length;
 
        form_length = XtVaCreateManagedWidget("length",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        9,
                NULL);
 

		Widget label_length;

        label_length = XtVaCreateManagedWidget(" LEN ",
                xmLabelGadgetClass,     form_length,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);


        x_len = XtVaCreateManagedWidget(" X_LEN",
                xmTextWidgetClass,      form_length,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       5,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "NO_VALUE",
                XmNeditable,            False,
                NULL);
 
 

        y_len = XtVaCreateManagedWidget("Y_LEN",
                xmTextWidgetClass,      form_length,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNvalue,               "NO_VALUE",
                XmNeditable,            False,
                NULL);
 


        z_len = XtVaCreateManagedWidget("Z_LEN",
                xmTextWidgetClass,      form_length,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "NO_VALUE",
                XmNeditable,            False,
                NULL);
 
        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,         rc,
                NULL);
 
 
		/*--------------Control Area buttons -------------------------------*/

		Widget form_ok;

        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      rc,
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
 
	
		switch(block_flag){

			case BSPLINE:
					XtAddCallback(ok,XmNactivateCallback,
						(XtCallbackProc)make_spl_data_box,
						(XtPointer)shell);

					break;

			default:

					XtAddCallback(ok,XmNactivateCallback,
						(XtCallbackProc)addblk_data_ok,
						(XtPointer)shell);

					break;

		}
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)addblk_data_can,
				(XtPointer)shell);
 
        XtManageChild(rc);
        XtManageChild(shell);
}

/*****************************************************************************
*
*       NAME    :       topo_apply_cb()
*
*       DESCRIPTION : 	Called when APPLY is pressed in Topo_selection widget
*						With the latest values stored in global variables
*						it filles array of topo_info with the index passed
*						through client_data
*
******************************************************************************/
 
void topo_apply_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
	int i = (int)client_data;

	topo_info[i].block_id	= blk_num;	// blk_num is selected block
	topo_info[i].topo_type	= topo_type;	// current topology type
	topo_info[i].Plane1	= temp_planes[1];
	topo_info[i].Plane2	= temp_planes[2];
	topo_info[i].Plane3	= temp_planes[3];
	topo_info[i].Plane4	= temp_planes[4];
	topo_info[i].Plane5	= temp_planes[5];


	int tp1	= temp_planes[1];	// temporary assignments
	int tp2	= temp_planes[2];	// temporary assignments
	int tp3	= temp_planes[3];	// temporary assignments
	int tp4	= temp_planes[4];	// temporary assignments
	int tp5	= temp_planes[5];	// temporary assignments

	/*

		There can not be all six planes constrained by
		any topological link 

	*/


	printf("Topo_link No. %d\n",i);
	printf("BLOCK No. %d\n",topo_info[i].block_id);
	printf("TOPO_TYPE. %d\n",topo_info[i].topo_type);
	printf("Plane1.is  %d\n",topo_info[i].Plane1);
	printf("Plane2.is  %d\n",topo_info[i].Plane2);
	printf("Plane3.is  %d\n",topo_info[i].Plane3);
	printf("Plane4.is  %d\n",topo_info[i].Plane4);
	printf("Plane5.is  %d\n",topo_info[i].Plane5);
 

	// clear all the flags


        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;// X-Data flags   (main_window.h)
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;// Y-Data flags   (main_window.h)
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;// Z-Data flags   (main_window.h)
 

	switch( topo_type){

		case CFM :

			cfm_for_data_table(blk_num,tp1);
			break;

		case CEM :
 
			cem_for_data_table(blk_num,tp1,tp2);
			break;

       	case CM :
 
			cm_for_data_table(blk_num,tp1,tp2,tp3);
			break;

       	case TCM :
 
			tcm_for_data_table(blk_num,tp1,tp2,tp3,tp4);
			break;

        case FCM :
 
			fcm_for_data_table(blk_num,tp1);
			break;
 
        case  SP :
 
			spm_for_data_table(blk_num,tp1);
			break;
		
		default:

			post_msg( " Wrong selection !!");
			break;

	}


	/*

		In the above Switch cases, depending on the
		Topological link some plane values will get assigned
		and those will be written in the Full data entry table
		by the function Write_in_Data_table() coded in
		utility_functions.c


	*/


	Write_in_Data_table();


	/*


		Now depending on the information in this topo_info[i]
		we have to

		get the block and its all plane values
		depending on topotype and planes make assignments
		in the Full_data_entry table and lock them

	*/

}

/*****************************************************************************
*
*       NAME    :       topo_can_cb()
*
*       DESCRIPTION :   Called when CAN is pressed in Topo_selection widget  
*
******************************************************************************/
 
void topo_can_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;

	// clear OFF evrything associated with index i in topo_info array

 
        topo_info[i].block_id   = 0;
        topo_info[i].topo_type  = 0;
        topo_info[i].Plane1     = 0;
        topo_info[i].Plane2     = 0;
        topo_info[i].Plane3     = 0;
        topo_info[i].Plane4     = 0;
        topo_info[i].Plane5     = 0;
 
 
}
 
 

 
