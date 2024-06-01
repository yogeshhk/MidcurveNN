/*******************************************************************************
*       FILENAME :      addblk_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Add_Block option on CREATE
*
*       FUNCTIONS   :	addblk_cb(Widget..)   
*						addblk_cb()
*						no_links_cb()
*						make_topo_selection_box()
*						blk_sel_callback()
*						cfm_sel_cb()
*						cm_sel_cb()
*						cem_sel_cb()
*						tcm_sel_cb()
*						fcm_sel_cb()
*						spm_sel_cb()
*						Select_Plane()
*						plane_sel_cb()
*						sel_plane_ok_cb()
*						sel_plane_can_cb()
*						
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 4, 1995.
*
*******************************************************************************/

/*******************************************************************************
                       INCLUDE FILES
*******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"			/* Class definitions */

/********************************************************************************
*
*       NAME    :       void
*                       addblk_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Depending on the button pressed in PullrightaddBlock,
*						calls the function Add the block to the existing 
*						component/block.Dependng on the type of the block 
*						calls the functions(coded in create_menu.c)
*
*******************************************************************************/
 
void addblk_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int item_no = (int)client_data;
 
        menu_flag	= CREATE;      				// user has selected CREATE
 
        if(comp_flag== OLD_COMP){				// atleast component is present        
                switch(item_no)
                        {
                        case 0 :
                                addblk_cb();
								block_flag = BLOC;
                                break;
 
                        case 1 :
                                addblk_cb();
								block_flag = SBLOC;
                                break;
 
                        case 2 :
                                addblk_cb();
								cyl_axis_selection();
								block_flag = CYLINDR;
                                break;
 
                        case 3 :
                                addblk_cb();
								cyl_axis_selection();
								block_flag = SCYLINDR;
                                break;
 
                        case 4 :
 
                                addblk_cb();
								wedge_axis_selection();
								block_flag = WEDGE;
                                break;

						case 5 :
								addblk_cb();
								wedge_axis_selection();
								block_flag = SWEDGE;
								break;

						case 6:
								addblk_cb();
								cyl_axis_selection();
								block_flag = BSPLINE;
								break;
 
                        }
        }
        else{
                post_msg("No component(BLOCK) present ");
                return;
        }
}
/*******************************************************************************
*
*       NAME    :       void
*                       addblk_cb()
*
*
*       DESCRIPTION :   Adding any type of block ,calls for number of topo_links
*                       to be added.
*
*******************************************************************************/
 
 
void addblk_cb()
{
        menu_flag	=	ADD_BLK;

        Widget data_shell ;             // dialog shell : managing custom dialog
        data_shell = XmCreateDialogShell(toplevel,"Links Specification",NULL,0);
 
 
        Widget data_rc ;                // Keeps childer one bellow another
        data_rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,data_shell,
                        XmNorientation, XmVERTICAL,
                        XmNwidth,       350,
                        NULL);
 
		/*------------------------------------------------------------------*/
 
        Widget  form_title ;            // contains name of dialog box
        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               350,
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
        nam = XtVaCreateManagedWidget("Linking Specifications",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);

	
 
        Widget  form_link;             // form manager
        form_link = XtVaCreateManagedWidget("minimum",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               350,
                XmNfractionBase,        9,
                NULL);
 
 
        Widget  label_link;            // label before text widget
        label_link= XtVaCreateManagedWidget(" TOPO_LINKS",
                xmLabelGadgetClass,     form_link,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
		/* 
		**	num_links is declared global : can be found in main_window.h
		*/
 
        num_links= XtVaCreateManagedWidget("COMP_ID",
                xmTextWidgetClass,      form_link,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "1",
                NULL);
 
 
        Widget  label_block;            // label before text widget
        label_block = XtVaCreateManagedWidget("  LEN_LINKS",
                xmLabelGadgetClass,     form_link,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
		/* 
		**	len_links is declared global : can be found in main_window.h
		*/

        len_links= XtVaCreateManagedWidget(" BLOCK",
                xmTextWidgetClass,      form_link,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "0",
                NULL);
 
        Widget sep;
        sep =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,  data_rc,
                NULL);
 
		/*----------Control Area buttons -----------------------------------*/
 
        Widget  form_ok ;
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               350,
                XmNfractionBase,        6,
                NULL);
 
        Widget ok,can;
        ok = XtVaCreateManagedWidget("  OK  ",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        1,
                XmNrightPosition,       3,
                XmNalignment,           XmALIGNMENT_END,
                NULL);
 
		XtAddCallback(ok,XmNactivateCallback,
				(XtCallbackProc)no_links_cb,
				(XtPointer)data_shell);
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightPosition,       6,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)temp_action,
				(XtPointer)data_shell);
 
        XtManageChild(data_rc);
        XtManageChild(data_shell);
 
		/*
		**		Importatnt Message
		**		Following function is declared in utility_functions.c
		*/
		print_msg("Length linking is not supported now !!!",NO_VALUE);

}
 
/********************************************************************************
*
*       NAME    :       void
*                       no_links_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Depending on the number entered in abve dialog,following
*                       functions are repeated.
*
*******************************************************************************/
 
 
void no_links_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
       	Widget a=(Widget)client_data;   // shell to destroy data_entry table
 
			// both num_links and len_links are global text widgets

        char *numlink	= XmTextGetString(num_links);
        char *lenlink	= XmTextGetString(len_links);

		int nos = atoi(numlink);
		int nol = atoi(lenlink);	// number of length linkings
 
        XtFree(lenlink);
        XtFree(numlink);

		make_full_data_entry_table();

        for(int j=1;j<= nos;j++){
   
			make_topo_selection_box(j);	// creates j topo_link boxes
			printf("Topolink No %d\n",j); 
      	}
 
	XtPopdown(a);		// destroy the widget 
}
 
 
/*******************************************************************************
*
*
*       NAME    :       void
*						make_topo_selection_box(int number)
*
*       DESCRIPTION :	Creates a dialog box, presents Link number, a block list
*		     			and toggle buttons for Topolink Type selection
*
*******************************************************************************/
 
void make_topo_selection_box(int number){


	/*

		some help for user in terms of message in Message box

	*/

	print_msg("First select block and one topolink per block",NO_VALUE);


        Widget shell;	/*  Dialog Shell for this custom dialog */
 
        shell = XmCreateDialogShell(toplevel,"TOPO_SELECTION",NULL,0);
 
 
        Widget rc;	/* rc is RowColumn manager,children in vertical stack */
 
        rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               400,
                        NULL);
 
 
/*--------------------Title of the Dialog Box --------------------------------*/

	Widget form_title ;	// form manager for tile bar 
 
        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               400,
                NULL);
 
	Widget fram ;		// Frame manager for itched boundary

        fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 

	char name[30];		// stores Link num got for above function

	sprintf(name,"TOPO_SELECTION for LINK No.%d",number);

		Widget nam;		// Label widget for the name plate
 
        nam = XtVaCreateManagedWidget( name ,
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
		/*------------ Headings for different fields------------------------*/
 
        Widget form_heading,blkscroll,topos;
 
        form_heading = XtVaCreateManagedWidget("heading",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        6,
                NULL);
 
        blkscroll = XtVaCreateManagedWidget(" Block_IDs ",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        topos = XtVaCreateManagedWidget(" TOPO_TYPES ",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                NULL);

        Widget sep2;
 
        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 

 
		Widget form_mid ;	// middle form
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        6,
                NULL);
 
 
		/*-------- Scrolled list for block----------------------------------*/
 
 
		Widget form_blk ;	// form for block listing

        form_blk = XtVaCreateManagedWidget("Parent_Block",
                xmFormWidgetClass,      form_mid,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        Widget scroll_list;
 
        scroll_list = XtVaCreateManagedWidget("scroll_list",
                xmScrolledWindowWidgetClass,    form_blk,
                XmNscrollingPolicy,             XmAUTOMATIC,
                XmNbottomAttachment,            XmATTACH_FORM,
                XmNtopAttachment,               XmATTACH_FORM,
                XmNrightAttachment,             XmATTACH_FORM,
                XmNleftAttachment,              XmATTACH_FORM,
                NULL);
 
 
 
        Widget blk_list;
        int i;
 
        blk_list = XtVaCreateManagedWidget("Parent_block",
                xmListWidgetClass,              scroll_list,
                XmNwidth,                       100,
                XmNheight,                      300,
                NULL);
 
 

	/*
		Here we have to present block ids of the current
		component. Thus nodelist in the current block is
		traversed and nodeids are collectd. Node Ids are
		same as Block ids.And presented in the form of list

	*/

                int     n=0;
                char    blkid[20];
                Arg     args[5];
                Node    *tempn;
                XmString strn, str_list;
 
                i = 1;
                if (currc == NULL)
                       return;
 
                tempn = currc->Get_comp_graph()->Get_graph_node();
 
                while (tempn != NULL) {
 
                        sprintf(blkid,"  %d           ",tempn->Get_node_id());
                        strn = XmStringCreateLocalized (blkid);
                        XmListAddItem (blk_list, strn, i);
                        XmStringFree (strn);
                        tempn = tempn->Get_nextn();
                        i++;
                }
                XtManageChild (blk_list);
 
  		XtAddCallback (blk_list, XmNdefaultActionCallback, 
				blk_sel_callback, 
				NULL);
  		XtAddCallback (blk_list, XmNbrowseSelectionCallback, 
				blk_sel_callback,
				NULL);
 
 
        /*----------Radio Box for the selection of the type of topo_link ----*/
 
		Widget form_link;	// form manager for set of toggle buttons

        form_link = XtVaCreateManagedWidget("Link_Type",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
 
        Widget radio_box,cfm,cem,cm,tcm,fcm,spm;
 
        radio_box = XmCreateRadioBox (form_link, "radio_box", NULL, 0);
 
        cfm = XtVaCreateManagedWidget ("CFM",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (cfm, XmNvalueChangedCallback,
				cfm_sel_cb,(XtPointer)CFM);

        cem = XtVaCreateManagedWidget ("CEM",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (cem,XmNvalueChangedCallback,
				cem_sel_cb,(XtPointer)CEM );
 
 
        cm = XtVaCreateManagedWidget ("CM",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (cm, XmNvalueChangedCallback, 
				cm_sel_cb, (XtPointer)CM);
 
        tcm = XtVaCreateManagedWidget ("TCM",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (tcm,XmNvalueChangedCallback,
				tcm_sel_cb,(XtPointer)TCM);
 
        fcm = XtVaCreateManagedWidget ("FCM",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (fcm,XmNvalueChangedCallback,
				fcm_sel_cb,(XtPointer)FCM);
 
        spm = XtVaCreateManagedWidget ("SPM",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
		XtAddCallback (spm,XmNvalueChangedCallback,
				spm_sel_cb,(XtPointer)SP);
 
        XtManageChild (radio_box);
 
        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
		/*---------------Control area---------------------------------------*/
 

		Widget form_ok;		// OK button

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
 
		XtAddCallback(ok, XmNactivateCallback,
				(XtCallbackProc)topo_apply_cb, 
				(XtPointer)number);

		XtAddCallback(ok,XmNactivateCallback,
				temp_action,
				(XtPointer)shell);
 
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback, 
				(XtCallbackProc)topo_can_cb,  
				(XtPointer)number);

		XtAddCallback(can,XmNactivateCallback,
				(XtCallbackProc)temp_action,
				(XtPointer)shell);
 
        XtManageChild(rc);
        XtManageChild(shell);
 
} 
 
/*****************************************************************************
*
*       NAME    :       blk_sel_callback()
*
*       DESCRIPTION :   This is called when block is selected from the list
*                       widget in the TOPOSELECTION widget.
*
******************************************************************************/
 
 
void
blk_sel_callback(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
 
    char        *str;
    int s                       = (int) client_data;
    XmListCallbackStruct *cbs   = (XmListCallbackStruct *) call_data;
    XmStringGetLtoR (cbs->item, XmFONTLIST_DEFAULT_TAG, &str);
 
   	int nn   	= atoi(str);    
	blk_num		= nn; 
}


/*****************************************************************************
*
*       NAME    :       cfm_sel_cb() : Center Face Match
*
*       DESCRIPTION :   This is called when CFM is selected from the radio
*                       buttons in the TOPOSELECTION widget.
*
******************************************************************************/
 
void cfm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
        int i = (int)client_data;       // not really necessary
 
		make_temp_planes_null();		// clears array of temporary planes

        if(i==1){
                topo_type=CFM;          // sets global variable to CFM(macro)
                Select_Plane(FIRST);    // requires only one plane
        }
 
		print_msg("Select 1st as resting plane ",NO_VALUE);

}
/*****************************************************************************
*
*       NAME    :       cm_sel_cb(): One Corner match
*
*       DESCRIPTION :   This is called when CM is selected from the radio
*                       buttons in the TOPOSELECTION widget.
*
******************************************************************************/
 
void cm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;
 
		make_temp_planes_null();	// clears array of temporary planes

        if(i==3){
                topo_type=CM;
                Select_Plane(THIRD);
                Select_Plane(SECOND);
                Select_Plane(FIRST);
 
        }
 
       print_msg("Select 2nd and 3rd plane as MIN_MIN or MAX_MAX",NO_VALUE);
}
 
/*****************************************************************************
*
*       NAME    :       cem_sel_cb(): Center Edge match
*
*       DESCRIPTION :   This is called when CEM is selected from the radio
*                       buttons in the TOPOSELECTION widget.
*
******************************************************************************/
 
 
void cem_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;

        make_temp_planes_null();        // clears array of temporary planes

 
        if(i==2){
                topo_type=CEM;
                Select_Plane(SECOND);
                Select_Plane(FIRST);
 
        }
 
 
		print_msg("Select 1st as resting plane and 2nd as center edge plane",
					NO_VALUE);
 
}
 
/*****************************************************************************
*
*       NAME    :       tcm_sel_cb(): Two Corner match
*
*       DESCRIPTION :   This is called when TCM is selected from the radio
*                       buttons in the TOPOSELECTION widget.
*
******************************************************************************/
 
void tcm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;
 
        make_temp_planes_null();        // clears array of temporary planes

        if(i==4){
                topo_type=TCM;
                Select_Plane(FOURTH);
                Select_Plane(THIRD);
                Select_Plane(SECOND);
                Select_Plane(FIRST);
 
        }
 
		print_msg("Select 2nd & 3rd MIN_MIN / MAX_MAX & 4th is oppos. of 2nd",
					NO_VALUE);
 
}
 
/*****************************************************************************
*
*       NAME    :       fcm_sel_cb(): Four corner Match
*
*       DESCRIPTION :   This is called when FCM is selected from the radio
*                       buttons in the TOPOSELECTION widget.
*
******************************************************************************/
 
void fcm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;

        make_temp_planes_null();        // clears array of temporary planes
 
        if(i==5){
                topo_type=FCM;
                Select_Plane(FIRST);
        }
 
		print_msg("Select 1st as resting plane ",NO_VALUE);
 
}
 
/*****************************************************************************
*
*       NAME    :       spm_sel_cb():Shared plane Match
*
*       DESCRIPTION :   This is called when SP is selected from the radio
 
*                       buttons in the TOPOSELECTION widget.
*
******************************************************************************/
 
 
void spm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;

        make_temp_planes_null();        // clears array of temporary planes
 
        if(i==6){
                topo_type=SP;
                Select_Plane(FIRST);
        }

		print_msg("Select 1st as resting plane ",NO_VALUE);
 
}
 
 
/*****************************************************************************
*
*       NAME    :       Select_Plane()
*
*       DESCRIPTION :   This is called when any plane needs to be specified,
*                       Called in (cfm-cem-...)_sel_cb for number of times
*
******************************************************************************/
 
void Select_Plane(int num)
{
 
        Widget sh,rc,form_title,fram,nam,form_dir,form_ok;
        Widget form_mid,form_plane;
 
        static Position x,y;            // positioning of the total widget
        Dimension w,h;                  // window dimensions
 
 
        /*  Dialog Shell for this custom dialog,behaves as manager ... */
 
        sh = XmCreateDialogShell(toplevel,"TOPO_SELECTION",NULL,0);
 
        XtVaGetValues(sh,
                        XmNwidth,       &w,
                        XmNheight,      &h,
                        NULL);
 
        if( (x+w) >= WidthOfScreen(XtScreen (sh))) x= 0; // out of Screen or not
        if( (y+h) >= HeightOfScreen(XtScreen (sh))) y= 0;// out of screen or not
 
        x =(num*250)- 100;   
		// this is a trick every widget is displaced by plane no. into 250

        y = 0;          // Vertically all are at top
 
        XtVaSetValues(sh,
                        XmNx,   x,
                        XmNy,   y,
                        NULL);
 
 
        /* rc is RowColumn manager widget-arranges children in vertical stack */
 
        rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,sh,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               225,
                        NULL);
 
/*---------------------------Title of the Dialog Box ------------------------*/
 
 
 
        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               225,
                NULL);
 
        fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        char pp[20];
 
        sprintf(pp,"Plane No.%d",num);
 
 
        nam = XtVaCreateManagedWidget(pp,
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        4,
                NULL);
 
 
        /*--------Radio Box for the selection of X-Y-Z direction ---------*/
 
		Widget form_dir1;

        form_dir1 = XtVaCreateManagedWidget("Direction",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                NULL);
 
        Widget xminmin,xminmax;
        Widget yminmin,yminmax;
        Widget zminmin,zminmax;

        Widget radio_dir1;
 
        radio_dir1 = XmCreateRadioBox (form_dir1, "Direction", NULL, 0);
 

	/*

		number got from above is passed to the following call backs
		so that they are assigned to proper array index in the
		array of temp_planes,( defined global in application.h)

	*/

        xminmin = XtVaCreateManagedWidget ("X MIN_MIN",
                xmToggleButtonGadgetClass, radio_dir1, NULL);
 
		XtAddCallback(xminmin,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)XMIN_MIN);
 
 
        xminmax = XtVaCreateManagedWidget ("X MIN_MAX",
                xmToggleButtonGadgetClass, radio_dir1, NULL);
 
		XtAddCallback(xminmax,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)XMIN_MAX);
 
        yminmin = XtVaCreateManagedWidget ("Y MIN_MIN",
                xmToggleButtonGadgetClass, radio_dir1, NULL);
 
		XtAddCallback(yminmin,XmNvalueChangedCallback,				
				plane_sel_cb,(XtPointer)YMIN_MIN);
 
        yminmax = XtVaCreateManagedWidget ("Y MIN_MAX",
                xmToggleButtonGadgetClass, radio_dir1, NULL);
 
		XtAddCallback(yminmax,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)YMIN_MAX);
 
        zminmin = XtVaCreateManagedWidget ("Z MIN_MIN",
                xmToggleButtonGadgetClass, radio_dir1, NULL);
 
		XtAddCallback(zminmin,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)ZMIN_MIN);
 
        zminmax = XtVaCreateManagedWidget ("Z MIN_MAX",
                xmToggleButtonGadgetClass, radio_dir1, NULL);
 
		XtAddCallback(zminmax,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)ZMIN_MAX);
 

        XtManageChild (radio_dir1);

		Widget form_dir2;

        form_dir2 = XtVaCreateManagedWidget("Dirtion",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                NULL);
 
 
        Widget xmaxmin,xmaxmax;
        Widget ymaxmin,ymaxmax;
        Widget zmaxmin,zmaxmax;
 
        Widget radio_dir2;

        radio_dir2 = XmCreateRadioBox (form_dir2, "Direction", NULL, 0);
 
 
        /*
 
                number got from above is passed to the following call backs
                so that they are assigned to proper array index in the
                array of temp_planes,( defined global in application.h)
 
        */
 
 
        xmaxmin = XtVaCreateManagedWidget ("X MAX_MIN",
                xmToggleButtonGadgetClass, radio_dir2, NULL);
 
		XtAddCallback(xmaxmin,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)XMAX_MIN);
 
        xmaxmax = XtVaCreateManagedWidget ("X MAX_MAX",
                xmToggleButtonGadgetClass, radio_dir2, NULL);
 
		XtAddCallback(xmaxmax,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)XMAX_MAX);
 
        ymaxmin = XtVaCreateManagedWidget ("Y MAX_MIN",
                xmToggleButtonGadgetClass, radio_dir2, NULL);
 
		XtAddCallback(ymaxmin,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)YMAX_MIN);
 
        ymaxmax = XtVaCreateManagedWidget ("Y MAX_MAX",
                xmToggleButtonGadgetClass, radio_dir2, NULL);
 
		XtAddCallback(ymaxmax,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)YMAX_MAX);
 
        zmaxmin = XtVaCreateManagedWidget ("Z MAX_MIN",
                xmToggleButtonGadgetClass, radio_dir2, NULL);
 
		XtAddCallback(zmaxmin,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)ZMAX_MIN);
 
        zmaxmax = XtVaCreateManagedWidget ("Z MAX_MAX",
                xmToggleButtonGadgetClass, radio_dir2, NULL);
 
		XtAddCallback(zmaxmax,XmNvalueChangedCallback,
				plane_sel_cb,(XtPointer)ZMAX_MAX);
 
 
        XtManageChild (radio_dir2);

        Widget sep2;
 
        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
 
		/*-------------Control area-----------------------------------------*/
 
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               225,
                XmNfractionBase,        4,
                NULL);
 
        Widget ok,can;
 
        ok = XtVaCreateManagedWidget(" OK ",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightPosition,       2,
                XmNalignment,           XmALIGNMENT_END,
                NULL);
 
		XtAddCallback(ok,XmNactivateCallback,
				sel_plane_ok_cb,(XtPointer)num);

		XtAddCallback(ok,XmNactivateCallback,
				(XtCallbackProc)temp_action,(XtPointer)sh);
 
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightPosition,       4,
                NULL);
 
		XtAddCallback(can,XmNactivateCallback,
				sel_plane_can_cb,(XtPointer)sh);
 
        XtManageChild(rc);
        XtManageChild(sh);
 
 
 
 
}
 
/*****************************************************************************
*
*       NAME    :       plane_sel_cb()
*
*       DESCRIPTION :   This is called when any plane is selected from radio
 
*                       buttons in the SELECT_PLANE widget.
*
******************************************************************************/
 
 
void plane_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;

	switch(i){

		case XMIN_MIN :

			plane_type = XMIN_MIN;
			break;

		case XMIN_MAX :

			plane_type = XMIN_MAX;
			break;

        case XMAX_MIN :
 
       		plane_type = XMAX_MIN;
            break;

        case XMAX_MAX :
 
        	plane_type = XMAX_MAX;
            break;

        case YMIN_MIN :
 
            plane_type = YMIN_MIN;
            break;
 
        case YMIN_MAX :
 
            plane_type = YMIN_MAX;
			break;
 
        case YMAX_MIN :
 
           plane_type = YMAX_MIN;
           break;
 
        case YMAX_MAX :
 
           plane_type = YMAX_MAX;
           break;

        case ZMIN_MIN :
 
           plane_type = ZMIN_MIN;
           break;
 
        case ZMIN_MAX :
 
           plane_type = ZMIN_MAX;
           break;
 
        case ZMAX_MIN :
 
           plane_type = ZMAX_MIN;
           break;
 
        case ZMAX_MAX :
 
           plane_type = ZMAX_MAX;
           break;

	}
 
 
}

/*****************************************************************************
*
*       NAME    :       sel_plane_ok_cb()
*
*       DESCRIPTION :   This is called when OK is selected from radio
 
*                       buttons in the SELECT_PLANE widget.
*
******************************************************************************/
void sel_plane_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int i = (int)client_data;
 

	/*

		this client_data is the number of plane required
		in a topolink.Accordingly we will index the array
		of temp_planes and assign the latest selected plane
		to it. plane_type is global and thus stores the latest
		value assigned to it

	*/

	temp_planes[i]= plane_type;

	printf("Plane no.%d and type %d \n", i,plane_type);
}
 
/*****************************************************************************
*
*       NAME    :       sel_plane_can_cb()
*
*       DESCRIPTION :   This is called when CANCEL is selected from radio
 
*                       buttons in the SELECT_PLANE widget.
*
******************************************************************************/
void sel_plane_can_cb(Widget wid, XtPointer client_data, XtPointer call_data) 
{
        Widget i = (Widget)client_data;


	make_temp_planes_null();

	// here we should NULL all the planes because if we nullify
	// only this plane then there is no meaning to the remaining
	// planes and thus Topo_link information may be wierd.

	XtPopdown(i);		// destroy the widget
 
}

