/*******************************************************************************
*       FILENAME :      dimension_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Display option on Parent_Menubar
*
*       FUNCTIONS   :   
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
#include "classes.h"            /* Classes Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
 

/******************************************************************************
                        GLOBAL DECLARATIONS(INTERFACE)
******************************************************************************/

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void    dimension_cb(Widget wi, XtPointer client_d, XtPointer call_data){
 
    printf("Came ****************************************\n");
 
        int item_no = (int)client_d;     // which No. button was selected
 
        menu_flag	= DIMENSION;      	// user has selected CREATE
 
        if( comp_flag== OLD_COMP) {
 
                switch(item_no)
                        {
                        case 0 :
						
                            printf("Option 1 of dimension menu\n");
							if(currc)currc->Create_default_dim_graphs();
                            break;
 
                        case 1 :
							menu_flag	= SPECIFY_DIM;
                            printf("Specifying Dimensions \n");
							select_dim_axis();
                            break;
 
                        case 2 :
							menu_flag	= CHG_DATUM;
							select_dim_axis();
                            printf("Change of Datum\n");
                            break;

						case 3 :
							menu_flag	= QUERY_DIM;
							select_dim_axis();
							printf("Make query box\n");
							break;
 
                        default:
                            menu_flag  = NO_MENU ;
                            printf("Bad selection\n");
                            post_msg("Error !!!");
                            break;
                        }
        }
        else{
 
            print_msg("Component has not been created",NO_VALUE);
            return;
        }
}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/

void make_change_datum_box(){

        /*
        **  Here I am doing little saving of memory and code.
        **  I have already set global "menu_flag" depending on the
        **  chioce in the menu item
        **  The initial dialog boxes are same as "sepcify dim scheme"
        **  so I will call the same function here.
        **  But the callback at which they are changing I will differentiate
        **  them with help of "menu_flag"
        */

}
/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void    make_query_box(){

		/*
		**	Here I am doing little saving of memory and code.
		**	I have already set global "menu_flag" depending on the
		**	chioce in the menu item
		**  The initial dialog boxes are same as "sepcify dim scheme"
		**	so I will call the same function here.
		**	But the callback at which they are changing I will differentiate
		**  them with help of "menu_flag"
		*/

}
/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void    select_dim_axis(){


	if(comp_flag != NO_COMP){
 
        Widget data_shell ;             // dialog shell : managing custom dialog
 
        data_shell = XmCreateDialogShell(toplevel,
					"Dim Axis Selection",NULL,0);
 
        Widget data_rc ;                // Keeps childer one bellow another
 
        data_rc = XtVaCreateWidget("row_col",
						xmRowColumnWidgetClass,	data_shell,
                        XmNorientation, 		XmVERTICAL,
                        XmNwidth,       		400,
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
 
        nam = XtVaCreateManagedWidget("DIM AXIS SEL",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
/*----------------------------------------------------------------------------*/
 
 
        /*----------Radio Box for the selection of the type of topo_link ----*/
 
        Widget form_axis;       // form manager for set of toggle buttons
 
        form_axis = XtVaCreateManagedWidget("AXIS",
                xmFormWidgetClass,      data_rc,
                XmNheight,              200,
                XmNwidth,               100,
                NULL);
 
 
 
        Widget radio_box,xaxis , yaxis,zaxis,oaxis;
 
        radio_box = XmCreateRadioBox (form_axis, 
						"radio_box", NULL, 0);
 
        xaxis = XtVaCreateManagedWidget ("X_AXIS",
                		xmToggleButtonGadgetClass, radio_box, 
						NULL);
 
		XtAddCallback (xaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)XAXIS);
 
 
        yaxis = XtVaCreateManagedWidget ("Y_AXIS",
                		xmToggleButtonGadgetClass, radio_box, 
						NULL);
 
 
		XtAddCallback (yaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)YAXIS);
 
        zaxis = XtVaCreateManagedWidget ("Z_AXIS",
                		xmToggleButtonGadgetClass, radio_box, 
						NULL);
 
		XtAddCallback (zaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)ZAXIS);
 
        oaxis = XtVaCreateManagedWidget ("Other",
                		xmToggleButtonGadgetClass, radio_box, 
						NULL);
 
		XtAddCallback (oaxis, XmNvalueChangedCallback,
						cyl_axis_sel_cb,(XtPointer)OAXIS);


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
 
		printf("Menu %d\n",menu_flag);

		if(menu_flag==CHG_DATUM)
		XtAddCallback(ok,XmNactivateCallback,
				(XtCallbackProc)chg_datum_axis_ok_cb,(XtPointer)data_shell);
		else
		XtAddCallback(ok,XmNactivateCallback,
				(XtCallbackProc)dim_axis_ok_cb,(XtPointer)data_shell);

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

/*****************************************************************************
*
*       NAME    :       chg_datum_axis_ok_cb()
*
*       DESCRIPTION :   Called when OK is pressed in Dim axis Entry widget
*
*
******************************************************************************/

void chg_datum_axis_ok_cb(Widget wi,XtPointer client_data,XtPointer call_data)
{
    Widget is= (Widget)client_data; // shell which we have to destroy afterwards

    printf("IN CHG_DATUM - Cylindrical Axis selected is %d\n",cyl_axis);

    Widget shell;   /*  Dialog Shell for this custom dialog */

    shell = XmCreateDialogShell(toplevel,"PLANES_SELECTION",NULL,0);

    Widget rc;  /* rc is RowColumn manager,children in vertical stack */

    rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               200,
                        NULL);

/*--------------------Title of the Dialog Box --------------------------------*/

    Widget form_title ; // form manager for tile bar
    form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               200,
                NULL);

    Widget fram ;       // Frame manager for itched boundary
    fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);


    Widget nam;     // Label widget for the name plate

    nam = XtVaCreateManagedWidget( "Datum Plane Selection",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);


/*---------------------- Headings for different fields------------------------*/

        Widget form_heading,blkscroll1;

        form_heading = XtVaCreateManagedWidget("heading",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        3,
                NULL);

        blkscroll1 = XtVaCreateManagedWidget(" Plane_IDs ",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

        Widget sep2;

        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);



/*------Middle working area contains scrolled window for child blk
    topo_selection radio box, .....         ------------------------*/

    Widget form_mid ;   // middle form

        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        3,
                NULL);


/*------------------ Scrolled list for block----------------------------------*/


    Widget form_blk1 ;   // form for plane1 listing

        form_blk1 = XtVaCreateManagedWidget("Parent_Block",
                xmFormWidgetClass,      form_mid,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

        Widget scroll_list1;

        scroll_list1 = XtVaCreateManagedWidget("scroll_list",
                xmScrolledWindowWidgetClass,    form_blk1,
                XmNscrollingPolicy,             XmAUTOMATIC,
                XmNbottomAttachment,            XmATTACH_FORM,
                XmNtopAttachment,               XmATTACH_FORM,
                XmNrightAttachment,             XmATTACH_FORM,
                XmNleftAttachment,              XmATTACH_FORM,
                NULL);

        Widget blk_list1;
        int i;

        blk_list1 = XtVaCreateManagedWidget("Plane1",
                xmListWidgetClass,              scroll_list1,
                XmNwidth,                       100,
                XmNheight,                      300,
                NULL);


    /*
    **      Here we present plane ids along the axis selected by
    **      user. cyl_axis ( global) is already set in the previous
    **      dialog box
    **      we ask ids along that list to spec_dim_graph
    */

                int     n=0;
                char    blkid[20];
                Arg     args[5];
                XmString strn, str_list;

                DimensionGraph  *tempn;
                i = 1;
                if (currc == NULL)
                       return;


                tempn = currc->Get_spec_dim_graph();

                DimNode* tra;
                int id=0;


                switch(cyl_axis){

                    case XAXIS :
                        tra =   tempn->Get_X_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case YAXIS :
                        tra =   tempn->Get_Y_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case ZAXIS :
                        tra =   tempn->Get_Z_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case OAXIS :
                        tra =   tempn->Get_O_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                }

                XtManageChild (blk_list1);

        /*
        **  When user selects Plane1 , both ids should be passed
        **  to OK callback. I will use "Topo_info" structure(defined in
        **  application.h) for this purpose.only p1 and fields will
        **  used.
        */

    Topo_info* info = new Topo_info;



        XtAddCallback(blk_list1,XmNdefaultActionCallback,
                        p1_sel_callback,(XtPointer)info);
        XtAddCallback(blk_list1,XmNbrowseSelectionCallback,
                        p1_sel_callback,(XtPointer)info);

        Widget sep1;

        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);


/*-------------------------Control area---------------------------------------*/


    Widget form_ok;     // OK button

        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               200,
                XmNfractionBase,        6,
                NULL);

        Widget ok,can;

        ok = XtVaCreateManagedWidget("APPLY",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightPosition,       2,
                XmNalignment,           XmALIGNMENT_END,
                NULL);

        XtAddCallback(ok,XmNactivateCallback,
                chg_datum_callback,(XtPointer)info);
        XtAddCallback(ok,XmNactivateCallback,
                temp_action,(XtPointer)shell);


        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);


        XtAddCallback(can,XmNactivateCallback,
                (XtCallbackProc)temp_action,(XtPointer)shell);

    XtManageChild(rc);
    XtManageChild(shell);
    XtPopdown(is);
}

/*****************************************************************************
*
*       NAME    :       dim_axis_ok_cb()
*
*       DESCRIPTION :   Called when OK is pressed in Dim axis Entry widget
*
*
******************************************************************************/
 
void dim_axis_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
	Widget is= (Widget)client_data; // shell which we have to destroy afterwards
 
 	printf("Cylindrical Axis selected is %d\n",cyl_axis);

    Widget shell;   /*  Dialog Shell for this custom dialog */
 
    shell = XmCreateDialogShell(toplevel,"PLANES_SELECTION",NULL,0);
 
	Widget rc;  /* rc is RowColumn manager,children in vertical stack */
 
   	rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               400,
                        NULL);
 
/*--------------------Title of the Dialog Box --------------------------------*/
 
    Widget form_title ; // form manager for tile bar
	form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                NULL);
 
    Widget fram ;       // Frame manager for itched boundary
    fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
    Widget nam;     // Label widget for the name plate
 
    nam = XtVaCreateManagedWidget( "Dim Plane Selection",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
/*---------------------- Headings for different fields------------------------*/
 
        Widget form_heading,blkscroll1,blkscroll2;
 
        form_heading = XtVaCreateManagedWidget("heading",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        6,
                NULL);
 
        blkscroll1 = XtVaCreateManagedWidget(" Plane1_IDs ",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        blkscroll2	= XtVaCreateManagedWidget("Plane2_IDs",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                NULL);
 
        Widget sep2;
 
        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
 
 
/*------Middle working area contains scrolled window for child blk
    topo_selection radio box, .....         ------------------------*/
 
    Widget form_mid ;   // middle form
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        6,
                NULL);
 
 
/*------------------ Scrolled list for block----------------------------------*/
 
 
    Widget form_blk1 ;   // form for plane1 listing
    Widget form_blk2 ;   // form for plane2	listing
 
        form_blk1 = XtVaCreateManagedWidget("Parent_Block",
                xmFormWidgetClass,      form_mid,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        Widget scroll_list1;
 
        scroll_list1 = XtVaCreateManagedWidget("scroll_list",
                xmScrolledWindowWidgetClass,    form_blk1,
                XmNscrollingPolicy,             XmAUTOMATIC,
                XmNbottomAttachment,            XmATTACH_FORM,
                XmNtopAttachment,               XmATTACH_FORM,
                XmNrightAttachment,             XmATTACH_FORM,
                XmNleftAttachment,              XmATTACH_FORM,
                NULL);
 
        form_blk2 = XtVaCreateManagedWidget("Parent_Block",
                xmFormWidgetClass,      form_mid,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        Widget scroll_list2;
 
        scroll_list2 = XtVaCreateManagedWidget("scroll_list",
                xmScrolledWindowWidgetClass,    form_blk2,
                XmNscrollingPolicy,             XmAUTOMATIC,
                XmNbottomAttachment,            XmATTACH_FORM,
                XmNtopAttachment,               XmATTACH_FORM,
                XmNrightAttachment,             XmATTACH_FORM,
                XmNleftAttachment,              XmATTACH_FORM,
                NULL);
 
 
 
        Widget blk_list1;
        int i;
 
        blk_list1 = XtVaCreateManagedWidget("Plane1",
                xmListWidgetClass,              scroll_list1,
                XmNwidth,                       100,
                XmNheight,                      300,
                NULL);
 
 
        Widget blk_list2;
 
        blk_list2 = XtVaCreateManagedWidget("Plane2",
                xmListWidgetClass,              scroll_list2,
                XmNwidth,                       100,
                XmNheight,                      300,
                NULL);
 
 
 
 
    /*
	**		Here we present plane ids along the axis selected by
	**		user. cyl_axis ( global) is already set in the previous
	**		dialog box
	**		we ask ids along that list to spec_dim_graph 
    */
 
                int     n=0;
                char    blkid[20];
                Arg     args[5];
                XmString strn, str_list;
 
                DimensionGraph	*tempn;
                i = 1;
                if (currc == NULL)
                       return;
 

                tempn = currc->Get_spec_dim_graph();
 
    			DimNode* tra;
    			int id=0;
 
 
    			switch(cyl_axis){
 
        			case XAXIS :
                		tra =   tempn->Get_X_DimList();
                		while(tra){
                        	sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                        	strn = XmStringCreateLocalized (blkid);
                        	XmListAddItem (blk_list1, strn, i);
                        	XmListAddItem (blk_list2, strn, i);
                        	XmStringFree (strn);
                        	i++;
                    		if(tra)tra = tra->Get_nextdn();
                		}
                		break;
 
                    case YAXIS :
                        tra =   tempn->Get_Y_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmListAddItem (blk_list2, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case ZAXIS :
                        tra =   tempn->Get_Z_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmListAddItem (blk_list2, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case OAXIS :
                        tra =   tempn->Get_O_DimList();
                        while(tra){
                            sprintf(blkid,"  %d       ",tra->Get_dim_node_id());
                            strn = XmStringCreateLocalized (blkid);
                            XmListAddItem (blk_list1, strn, i);
                            XmListAddItem (blk_list2, strn, i);
                            XmStringFree (strn);
                            i++;
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

    			}

                XtManageChild (blk_list1);
                XtManageChild (blk_list2);
 
		/*
		**	When user selects Plane1 and Plane 2, both ids should be passed
		**	to OK callback. I will use "Topo_info" structure(defined in
		**	application.h) for this purpose.only p1 and p2 fields will
		**	used.
		*/

	Topo_info* info	= new Topo_info;

	

		XtAddCallback(blk_list1,XmNdefaultActionCallback,
						p1_sel_callback,(XtPointer)info);
		XtAddCallback(blk_list1,XmNbrowseSelectionCallback, 
						p1_sel_callback,(XtPointer)info);
		XtAddCallback(blk_list2,XmNdefaultActionCallback, 
						p2_sel_callback,(XtPointer)info);
		XtAddCallback(blk_list2,XmNbrowseSelectionCallback, 
						p2_sel_callback,(XtPointer)info);
 
 
        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
/*-------------------------Control area---------------------------------------*/
 
 
    Widget form_ok;     // OK button
 
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        6,
                NULL);
 
        Widget ok,can;
 
        ok = XtVaCreateManagedWidget("APPLY",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightPosition,       2,
                XmNalignment,           XmALIGNMENT_END,
                NULL);
 
			XtAddCallback(ok,XmNactivateCallback,
				display_path_callback,(XtPointer)info);
			XtAddCallback(ok,XmNactivateCallback,
				temp_action,(XtPointer)shell);
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);
 
 
		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)temp_action,(XtPointer)shell);

	XtManageChild(rc);
    XtManageChild(shell);
    XtPopdown(is);
}

void chg_datum_callback(Widget wi, XtPointer cl_d, XtPointer call_data){

	printf(" yet to define\n");

	/*
		Delete all the arcs from all the nodes.
		Get the NewDatum node
		Build all the arcs (symm) from that node to all others
	*/
	DimensionGraph  *tempn;
    if (currc == NULL) return;


    Topo_info* info = (Topo_info*)cl_d;

    int datum_plane  =   info->Plane1 ;

    tempn = currc->Get_spec_dim_graph();

    DimNode* tra;
    int id=0;


    switch(cyl_axis){

    				case XAXIS :
                        tra =   tempn->Get_X_DimList();
                        while(tra){
							tra->Remove_all_Arcs();
                            if(tra)tra = tra->Get_nextdn();
                        }
                        tra =   tempn->Get_X_DimList();
                        while(tra){
                            int id = tra->Get_dim_node_id();
                            if(id != datum_plane){
                                tempn->BuildArc(datum_plane,id);
                            }
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case YAXIS :
                        tra =   tempn->Get_Y_DimList();
                        while(tra){
							tra->Remove_all_Arcs();
                            if(tra)tra = tra->Get_nextdn();
                        }
                        tra =   tempn->Get_Y_DimList();
                        while(tra){
							int id = tra->Get_dim_node_id();
							if(id != datum_plane){
								tempn->BuildArc(datum_plane,id);
							}
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case ZAXIS :
                        tra =   tempn->Get_Z_DimList();
                        while(tra){
							tra->Remove_all_Arcs();
                            if(tra)tra = tra->Get_nextdn();
                        }
                        tra =   tempn->Get_Z_DimList();
                        while(tra){
                            int id = tra->Get_dim_node_id();
                            if(id != datum_plane){
                                tempn->BuildArc(datum_plane,id);
                            }
                            if(tra)tra = tra->Get_nextdn();
                        }
                        break;

                    case OAXIS :
                        tra =   tempn->Get_O_DimList();
                        while(tra){
							tra->Remove_all_Arcs();
                            if(tra)tra = tra->Get_nextdn();
						}
                        tra =   tempn->Get_O_DimList();
                        while(tra){
                            int id = tra->Get_dim_node_id();
                            if(id != datum_plane){
                                tempn->BuildArc(datum_plane,id);
                            }
                            if(tra)tra = tra->Get_nextdn();
                        }
						break;
					default:
						break;

			}

	tempn->PrintYourself(stdout);
}
/*****************************************************************************
*
*       NAME    :       p1_sel_callback()
*
*       DESCRIPTION :   
*
******************************************************************************/
 
 
void
p1_sel_callback(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
 
	Topo_info* info	= (Topo_info*)client_data;
    char        *str;
    int s                       = (int) client_data;
    XmListCallbackStruct *cbs   = (XmListCallbackStruct *) call_data;
    XmStringGetLtoR (cbs->item, XmFONTLIST_DEFAULT_TAG, &str);
 
    int nn          = atoi(str);    // converts string got from list
                                        // to integer
    info->Plane1	= nn;
	printf("Dimension Plane 1 = %d\n",nn);
}
 
/*****************************************************************************
*
*       NAME    :       p2_sel_callback()
*
*       DESCRIPTION :
*
******************************************************************************/
 
 
void
p2_sel_callback(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
 
	Topo_info* info	= (Topo_info*)client_data;
    char        *str;
    int s                       = (int) client_data;
    XmListCallbackStruct *cbs   = (XmListCallbackStruct *) call_data;
    XmStringGetLtoR (cbs->item, XmFONTLIST_DEFAULT_TAG, &str);
 
    int nn          = atoi(str);    // converts string got from list
                                        // to integer
    info->Plane2	= nn;
	printf("Dimension Plane 2 = %d\n",nn);
}

/*****************************************************************************
*
*       NAME    :       arc_sel_callback()
*
*       DESCRIPTION :
*
******************************************************************************/
 
 
void
arc_sel_callback(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
	printf("AAAAAAAAAAAA\n");
 
    char        *str;
    int s                       = (int) client_data;
    XmListCallbackStruct *cbs   = (XmListCallbackStruct *) call_data;
    XmStringGetLtoR (cbs->item, XmFONTLIST_DEFAULT_TAG, &str);
 
    int nn          = atoi(str);    // converts string got from list
                                        // to integer
    cyl_axis = nn;
    printf("Deleted Arc Id = %d\n",nn);
}

/*****************************************************************************
*
*       NAME    :       display_path_callback()
*
*       DESCRIPTION :
*
******************************************************************************/
 
 
void
display_path_callback(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
 
    Topo_info* info = (Topo_info*)client_data;

    int	plane1	=	info->Plane1 ;
    int	plane2	=	info->Plane2 ;
    printf("After OK Dimension Plane 1 = %d\n",plane1);
    printf("After OK Dimension Plane 2 = %d\n",plane2);

	/*
	**		Creation of the dialog box
	*/

	
    Widget shell;   /*  Dialog Shell for this custom dialog */
 
    shell = XmCreateDialogShell(toplevel,"PLANES_SELECTION",NULL,0);
 
    Widget rc;  /* rc is RowColumn manager,children in vertical stack */
 
    rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               400,
                        NULL);
 
/*--------------------Title of the Dialog Box --------------------------------*/
 
    Widget form_title ; // form manager for tile bar
    form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                NULL);
 
    Widget fram ;       // Frame manager for itched boundary
    fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
    Widget nam;     // Label widget for the name plate
 
    nam = XtVaCreateManagedWidget( "Delete Arc Selection",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
/*---------------------- Headings for different fields------------------------*/
 
        Widget form_heading,blkscroll1;
 
        form_heading = XtVaCreateManagedWidget("heading",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        6,
                NULL);
 
        blkscroll1 = XtVaCreateManagedWidget(" Arc_IDs ",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        Widget sep2;
 
        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
 
 
/*------Middle working area contains scrolled window for child blk
    topo_selection radio box, .....         ------------------------*/
 
    Widget form_mid ;   // middle form
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        6,
                NULL);
 
 
/*------------------ Scrolled list for block----------------------------------*/
 
 
    Widget form_blk1 ;   // form for plane1 listing
 
        form_blk1 = XtVaCreateManagedWidget("Parent_Block",
                xmFormWidgetClass,      form_mid,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        Widget scroll_list1;
 
        scroll_list1 = XtVaCreateManagedWidget("scroll_list",
                xmScrolledWindowWidgetClass,    form_blk1,
                XmNscrollingPolicy,             XmAUTOMATIC,
                XmNbottomAttachment,            XmATTACH_FORM,
                XmNtopAttachment,               XmATTACH_FORM,
                XmNrightAttachment,             XmATTACH_FORM,
                XmNleftAttachment,              XmATTACH_FORM,
                NULL);
 
        Widget blk_list1;
        int i;
 
        blk_list1 = XtVaCreateManagedWidget("Plane1",
                xmListWidgetClass,              scroll_list1,
                XmNwidth,                       100,
                XmNheight,                      300,
                NULL);
 
 
    /*
    **      Here we present arc ids to the 
    **      user. cyl_axis ( global) is used temporarily to store the
	**		selection.
    */
 
	DimensionGraph*	G = currc->Get_spec_dim_graph();

	DimArc *firstarc = 	G->ComputePath(plane1,plane2);
						G->BuildArc(plane1,plane2);

	/*
	**		Now we have two plane ids between which dimension has to be 
	**		specified.We will check if they are diffent or not.
	**		Passing these to ids to "spec_dim_graph" in component
	**		we will get list of DimArcs and present them to user
	**		User will select one to delete
	**	
	**		Interface at this stage is crude but works..
	**		If time permites, I may make it more user friendly
	**		ArcId - Node 1 - Node 2
	**		is shown in the message window while only Arc Ids are
	**		put for selection.
	*/

	/*
	**		Compute number of arcs
	*/
	int 	num_arcs=0;

	DimArc* arc	=firstarc;

	double tol	= 0.0;
	double dim	=0.0;
	Topo_info* delarc	= new Topo_info;

	while(arc){
		tol += arc->Get_tolerance();
		dim += arc->Get_dim_value();
		num_arcs++;
		arc = arc->Get_nextda();
	}

	printf("Number of arcs are = %d\n",num_arcs);

	Topo_info*	pass	= new Topo_info[num_arcs];

	if(menu_flag == SPECIFY_DIM){


	/*
	**	The above array will store the information temporarily
	**	and will be used to pass between callbacks
	*/

	int k;
	arc	= firstarc;

	for(k =0;(k<num_arcs)||(arc);k++){

		pass[k].topo_type	= arc->Get_dim_arc_id();
		pass[k].Plane1	= arc->Get_nodeA()->Get_dim_node_id();
		pass[k].Plane2	= arc->Get_nodeB()->Get_dim_node_id();
		
		arc = arc->Get_nextda();
	}

    int     n=0;
	char	arc_info[200];
	char	message[200];
    char    blkid[20];
    Arg     args[5];
    XmString strn, str_list;

	strcpy(message,"Arc Info :");

	for(k =0;(k<num_arcs);k++){

		int aid	= pass[k].topo_type;
		int p1	= pass[k].Plane1  ;
		int p2	= pass[k].Plane2  ;
		sprintf(arc_info,"Arc %d [%d , %d]\t",aid,p1,p2);
		strcat(message,arc_info);
		printf("Message is %s\n",arc_info);
	}
		
	printf("Finnaly Message is %s\n",message);

	print_msg(message,NO_VALUE);	// Prints in Message window

    i = 1;
    int id=0;
 
    for(k =0;(k<num_arcs);k++){
 
        int aid = pass[k].topo_type;
        sprintf(blkid,"  %d       ",aid);
        printf("  %d       ",aid);
        strn = XmStringCreateLocalized (blkid);
        XmListAddItem (blk_list1, strn, i);
        XmStringFree (strn);
        i++;
    }
 
    XtManageChild (blk_list1);
 
	XtAddCallback(blk_list1,XmNdefaultActionCallback,arc_sel_callback,NULL);
	XtAddCallback(blk_list1,XmNbrowseSelectionCallback, arc_sel_callback,NULL);
 
 
	/*
	**		After the above callbacks are executed
	**		global "cyl_axis" will have the arc_id
	**		Get the Topo_info structure corresponding to it
	**		pass it to further callbacks
	*/

	delarc->topo_type	= pass[cyl_axis-1].topo_type;
	delarc->Plane1		= pass[cyl_axis-1].Plane1;
	delarc->Plane2		= pass[cyl_axis-1].Plane2;

        Widget sep1;
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
	printf("Test Arc is %d\n",delarc->topo_type);
	printf("Test Plane 1 is %d\n",delarc->Plane1);
	printf("Test Plane 2 is %d\n",delarc->Plane2);

	}
/*-------------------------Control area---------------------------------------*/
 
 
    Widget form_ok;     // OK button
 
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                XmNfractionBase,        6,
                NULL);
 
        Widget ok,can;
 
        ok = XtVaCreateManagedWidget("APPLY",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightPosition,       2,
                XmNalignment,           XmALIGNMENT_END,
                NULL);
 
		if(menu_flag == SPECIFY_DIM){
			XtAddCallback(ok,XmNactivateCallback,
					del_dim_arc_cb,(XtPointer)delarc);
	//		XtAddCallback(can,XmNactivateCallback,
	//			(XtCallbackProc)temp_action,(XtPointer)shell);
		}
		else{
			char message[100];
			sprintf(message,"The dimension is %f to %f ",dim -tol,dim+tol);
			post_msg(message);	

		}

		XtAddCallback(ok,XmNactivateCallback,
			temp_action,(XtPointer)shell);
 
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);
 
 
		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)temp_action,(XtPointer)shell);

    XtManageChild(rc);
    XtManageChild(shell);
}

/*****************************************************************************
*
*       NAME    :       del_dim_arc_cb()
*
*       DESCRIPTION :
*
******************************************************************************/
 
 
void
del_dim_arc_cb(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
 
    Topo_info* info = (Topo_info*)client_data;
 
    int plane1  =   info->Plane1 ;
    int plane2  =   info->Plane2 ;
    printf("OK Dimension Plane 1 = %d\n",plane1);
    printf("OK Dimension Plane 2 = %d\n",plane2);
 
	DimensionGraph* G= currc->Get_spec_dim_graph();
	if(G)G->DeleteArc(plane1,plane2);

	G->PrintYourself(stdout);

}

