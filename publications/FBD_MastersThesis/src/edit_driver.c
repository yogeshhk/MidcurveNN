/*******************************************************************************
*       FILENAME :      edit_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Edit option on Design_Menubar
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
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"            /* Classes Declarations :header file */
#include <string.h>

/*******************************************************************************
*
*
*       NAME    :       void
*                       edit_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   Depending on the button in Edit,calls the function
*                       Starts editing of current comp ond ptions(switch state
*                       -ment)call function specific to type of editing chosen.
*
*******************************************************************************/
 

void edit_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
        int item_no = (int)client_data;         // which No. button was selected
 
        menu_flag= EDIT;      // user has selected CREATE
        if( comp_flag== OLD_COMP) { 
 
 
                switch(item_no)
                        {
                        case 0 :
							make_length_editing_box();
							printf("Geometric Edit\n");
                            break;
 
                        case 1 :
							printf("Add topolink\n");
                            break;
 
                        case 2 :
							printf("delete topolink\n");
                            break;
 
                        default:
							printf("Bad selection\n");
                            menu_flag  = NO_MENU ;
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
*
*       NAME    :       void
*                       make_length_editing_box()
*
*       DESCRIPTION :Creates a dialog box, presents a block list,new_length
*                    and toggle buttons for length Type selection
*
*******************************************************************************/
 
void make_length_editing_box(){
 
 
        /*
 
                some help for user in terms of message in Message box
 
        */
 
        print_msg("First enter New_length per block",NO_VALUE);
 
 
        Widget shell;   /*  Dialog Shell for this custom dialog */
 
        shell = XmCreateDialogShell(toplevel,"LENGTH_EDITING",NULL,0);
 
 
        Widget rc;      /* rc is RowColumn manager,children in vertical stack */
 
        rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               600,
                        NULL);
 
 
/*--------------------Title of the Dialog Box --------------------------------*/
 
        Widget form_title ;     // form manager for tile bar
 
        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               600,
                NULL);
 
        Widget fram ;           // Frame manager for itched boundary
 
        fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
        Widget nam;             // Label widget for the name plate
 
        nam = XtVaCreateManagedWidget( "Length_Editing",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
/*---------------------- Headings for different fields------------------------*/
 
        Widget form_heading,blkscroll,topos,con_pln;
 
        form_heading = XtVaCreateManagedWidget("heading",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        9,
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
 
        topos = XtVaCreateManagedWidget(" LENGTH_AXIS",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                NULL);
 
        con_pln = XtVaCreateManagedWidget(" CONSTRAIN_PLANE",
                xmLabelGadgetClass,     form_heading,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNtopAttachment,       XmATTACH_FORM,
                NULL);
 
        Widget sep2;
 
        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
 
 
/*------Middle working area contains scrolled window for child blk
        topo_selection radio box, .....         ------------------------*/
 
 

        Widget form_mid ;       // middle form
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        9,
                NULL);
 
 
/*------------------ Scrolled list for block----------------------------------*/
 
 
        Widget form_blk ;       // form for block listing
 
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
 
  XtAddCallback (blk_list, XmNdefaultActionCallback, blk_sel_callback, NULL);
  XtAddCallback (blk_list, XmNbrowseSelectionCallback, blk_sel_callback,NULL);
 
 
        /*----------Radio Box for the selection of the type of length ----*/
 
        Widget form_link;       // form manager for set of toggle buttons
 
        form_link = XtVaCreateManagedWidget("Link_Type",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        4,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       6,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
 
        Widget radio_box,xaxi,yaxi,zaxi;
 
        radio_box = XmCreateRadioBox (form_link, "radio_box", NULL, 0);
 
        xaxi = XtVaCreateManagedWidget ("X_LENGHT",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
        XtAddCallback(xaxi,XmNvalueChangedCallback,len_sel_cb,(XtPointer)XAXIS);
 
 
        yaxi = XtVaCreateManagedWidget ("Y_LENGHT",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
        XtAddCallback(yaxi,XmNvalueChangedCallback,len_sel_cb,(XtPointer)YAXIS);
 
 
        zaxi = XtVaCreateManagedWidget ("Z_LENGHT",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
        XtAddCallback(zaxi,XmNvalueChangedCallback,len_sel_cb,(XtPointer)ZAXIS);
 
 
        XtManageChild (radio_box);
 
        /*----------Radio Box for selection of the type of constrain plane----*/
 
        Widget form_pln;       // form manager for set of toggle buttons
 
        form_pln = XtVaCreateManagedWidget("Link_Type",
                xmFormWidgetClass,      form_mid,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        7,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       9,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
 
        Widget radio,min,mid,max;
 
        radio = XmCreateRadioBox (form_pln, "radio", NULL, 0);
 
        min = XtVaCreateManagedWidget ("MIN_PLANE",
                xmToggleButtonGadgetClass, radio, NULL);
 
        XtAddCallback(min,XmNvalueChangedCallback,con_plane_cb,(XtPointer)MINF);
 
 
        mid = XtVaCreateManagedWidget ("MID_PLANE",
                xmToggleButtonGadgetClass, radio, NULL);
 
        XtAddCallback(mid,XmNvalueChangedCallback,con_plane_cb,(XtPointer)MIDF);
 
 
        max = XtVaCreateManagedWidget ("MAX_PLANE",
                xmToggleButtonGadgetClass, radio, NULL);
 
        XtAddCallback(max,XmNvalueChangedCallback,con_plane_cb,(XtPointer)MAXF);
 
 
        XtManageChild (radio);
 

        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
        Widget  form_l;             // form manager
 
        form_l = XtVaCreateManagedWidget("minimum",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               600,
                XmNfractionBase,        5,
                NULL);
 
 
        Widget  label_length;            // label before text widget
 
        label_length = XtVaCreateManagedWidget("Enter New Length",
                xmLabelGadgetClass,     form_l,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
        edit_length= XtVaCreateManagedWidget("New_length",
                xmTextWidgetClass,      form_l,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       4,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "20",
                NULL);
 

 
        Widget sepa;
 
        sepa =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 

/*-------------------------Control area---------------------------------------*/
 
 
        Widget form_ok;         // OK button
 
        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               600,
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
 
XtAddCallback(ok,XmNactivateCallback,geom_edit_ok,(XtPointer)shell);
 
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        5,
                XmNrightPosition,       6,
                NULL);
 
XtAddCallback(can,XmNactivateCallback,geom_edit_can,(XtPointer)shell);
XtAddCallback(can,XmNactivateCallback,temp_action,(XtPointer)shell);
 
        XtManageChild(rc);
        XtManageChild(shell);
 
 
 
 
}
 

/*****************************************************************************
*
*       NAME    :       len_sel_cb()
*
*       DESCRIPTION :   Called when toggle is pressed in CYL data Entry widget
*
*
******************************************************************************/
 
void len_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
        int i = ( int )client_data;
 
        switch(i){
 
                case XAXIS :
                                len_axis = XAXIS;
                                break;
 
                case YAXIS :
                                len_axis = YAXIS;
                                break;
 
                case ZAXIS :
                                len_axis = ZAXIS;
                                break;
 
                default :
                                len_axis = YAXIS ;
                                break;
        }
}
 
/*****************************************************************************
*
*       NAME    :       con_plane_cb()
*
*       DESCRIPTION :   Called when toggle is pressed in length editing table
*
*
******************************************************************************/
 
void con_plane_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
        int i = ( int )client_data;
 
        switch(i){
 
                case MINF:
                                constrn_pln = MINF;
                                break;
 
                case MIDF:
                                constrn_pln = MIDF;
                                break;
 
                case MAXF:
                                constrn_pln = MAXF;
                                break;
 
                default :
                                constrn_pln = MINF;
                                break;
        }
}


