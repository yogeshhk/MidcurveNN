/*******************************************************************************
*       FILENAME :      main_window.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   "main" function(Interface Structure with Motif)
*
*       FUNCTIONS   :   main
*                       BuildPullDownMenu()
*			redraw_all()
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
#include "classes.h"     		/* class Declarations :header file */

/******************************************************************************
                        GLOBAL DECLARATIONS(INTERFACE)
******************************************************************************/

double drawing_width;                   /* Drawing Area width*/
double drawing_height;                  /* Drawing Area height */

XGCValues gcv;
GC gc;                          /* Graphics Context */

Widget toplevel;                /* main application shell */
Widget main_w;                  /* main window as overall manager */
Widget drawing_a;               /* Drawind area widget */
Widget rc;                      /* manager for parent and child menu */
Widget parent_menubar;          /* Parent menubar for common menu */
Widget hwidget;                 /* Help widget,set from any where */
Widget parent_menu;             /* common men manager */
Widget child_menu;              /* mode : design or Manufacturing menu*/
Widget design_menubar;          /* Design menu options */
Widget mfg_menubar;             /* Manufacturing menu options */
Widget rc2;                     /* Status area manager */
Widget name;                    /* Logo label widget */
Widget comp_btn;                /* componet button at status area */
Widget block_btn;               /* block button at status area */
Widget lab;                     /* text widget for messages at bottom */
Widget comp_label;				/* Status comp_btn's label */
Widget block_label;				/* Status block_btn's label */

Widget comp_id;					/* comp_id in data entry*/
Widget block_id;				/* block_id in data entry*/
Widget num_links;               /* Number of topo links*/
Widget len_links;               /* Number of length links*/
Widget edit_length;             /* New length for modification*/
Widget modf_node;             	/* modification Node for cycle*/


Widget major_rad;               /* Major radius of Cylinder*/
Widget minor_rad;               /* Minor radius of Cylinder*/
Widget cylinder_base;           /* Base Plane of Cylinder*/


Widget x_min,x_max,x_mid,x_len; /* X-Data entry widgets */
Widget y_min,y_max,y_mid,y_len; /* Y-Data entry widgets */
Widget z_min,z_max,z_mid,z_len; /* Z-Data entry widgets */

Widget spl_x[20];       		/* Spline data X coordinates    */
Widget spl_y[20];       		/* Spline data Y coordinates    */
Widget spl_z[20];       		/* Spline data Z coordinates    */

int comp_flag;                  /* Status of component NO/OLD */       
int block_flag;                 /* Status of block NO/ADD_BLK.. */
int menu_flag;                  /* Which menu is selected */            

double	x_minf,x_maxf,x_midf,x_lenf;/* X-Data entry flags */
double	y_minf,y_maxf,y_midf,y_lenf;/* Y-Data entry flags */
double	z_minf,z_maxf,z_midf,z_lenf;/* Z-Data entry flags */
 

/*****************************************************************************
*
*       NAME    :       main(int argc, char *argv[])
*
*       DESCRIPTION :   Creates Interface structure containing main window,
*                       menubar,scrolled drawing area,message area,list buttons
*
******************************************************************************/


main(int argc, char *argv[])
{


	Init_App();	/* Initializes application variables and flags */


    	XtAppContext 		app;                      /* Application Context */
    	XtWidgetGeometry 	size;


        String fallbacks[]={
		"Demos*background :gray70",
        NULL};

        /* Arrays Defined bellow form pulldown menues on the menu bar.
           These MenuItem(s) are used in the function BuilPulldownMenu() 
           This function is taken from Motif programming manual */


        MenuItem save_menu[] = {
                { "Yogesh", &xmPushButtonGadgetClass, 'Y', NULL, NULL,
                filename_save, (XtPointer) 3, (MenuItem *) NULL },
                { "Venky", &xmPushButtonGadgetClass, 'V', NULL, NULL,
                Venkys_save, (XtPointer) 3, (MenuItem *) NULL },
                { "DXF...", &xmPushButtonGadgetClass, 'D', NULL, NULL,
                        NULL, (XtPointer) 6, (MenuItem *) NULL },
                NULL,
                };

		MenuItem file_menu[] = {
    		{ "New", &xmPushButtonGadgetClass, 'N', NULL, NULL,
        	file_new_cb, (XtPointer) 1, (MenuItem *) NULL },
    		{ "Retrieve", &xmPushButtonGadgetClass, 'R', NULL, NULL,
       		filename_retrieve, (XtPointer) 2, (MenuItem *) NULL },
    		{ "Save...", &xmCascadeButtonGadgetClass, 'S', NULL, NULL,
        		NULL, (XtPointer) 3, save_menu},
    		{ "Exit ", &xmPushButtonGadgetClass, 'x', NULL, NULL,
        	file_quit_cb, (XtPointer) 4,(MenuItem *)NULL },
    		NULL,
		};

        MenuItem mode_menu[] = {
                { "Design", &xmPushButtonGadgetClass, 'D', NULL, NULL,
                mode_design_cb, (XtPointer) 1, (MenuItem *)NULL },
                { "Manufacturing ", &xmPushButtonGadgetClass, 'M', NULL, NULL,
                mode_mfg_cb   , (XtPointer) 3, (MenuItem *)NULL },
                NULL,
                };

        MenuItem scale_menu[] = {
                { "ScaleX", &xmPushButtonGadgetClass, 'X', NULL, NULL,
                NULL, (XtPointer) 1, (MenuItem *) NULL },
                { "ScaleY", &xmPushButtonGadgetClass, 'Y', NULL, NULL,
                NULL, (XtPointer) 2, (MenuItem *) NULL },
                { "ScaleZ", &xmPushButtonGadgetClass, 'Z', NULL, NULL,
                NULL, (XtPointer) 3, (MenuItem *) NULL },
                { "ScaleAll", &xmPushButtonGadgetClass, 'A', NULL, NULL,
                NULL, (XtPointer) 4, (MenuItem *) NULL },
                NULL,
                };

        MenuItem display_typemenu[] = {
                { "PolygonSet", &xmPushButtonGadgetClass, 'P', NULL, NULL,
                display_pset_cb, (XtPointer) 1, (MenuItem *) NULL },
                { "Solid", &xmPushButtonGadgetClass, 'S', NULL, NULL,
                  display_truewire_cb, (XtPointer) 2, (MenuItem *) NULL},
                { "Wireframe", &xmPushButtonGadgetClass, 'W', NULL, NULL,
                        display_blkwise_cb, (XtPointer) 3, (MenuItem *) NULL },
                NULL,
                };


        MenuItem display_menu[] = {
                { "Display_Type", &xmPushButtonGadgetClass, 'D', NULL, NULL,
                NULL, (XtPointer) 1, display_typemenu},
                { "Scale", &xmPushButtonGadgetClass, 'P', NULL, NULL,
                        NULL, (XtPointer) 2, scale_menu },
                { "Rotation", &xmPushButtonGadgetClass, 'R', NULL, NULL,
                        NULL, (XtPointer) 3, (MenuItem *) NULL },
                NULL,
                };

        MenuItem query_menu[] = {
                { "Geo_Query", &xmPushButtonGadgetClass, 'G', NULL, NULL,
                        NULL, (XtPointer) 3, (MenuItem *)NULL },
                { "Topo_Query", &xmPushButtonGadgetClass, 'T', NULL, NULL,
                        NULL, (XtPointer) 4, (MenuItem *)NULL },
                NULL,
                };

        MenuItem window_menu[] = {
                { "Auto", &xmPushButtonGadgetClass, 'A', NULL, NULL,
                        NULL, (XtPointer) 3, (MenuItem *)NULL },
                { "User_Defined", &xmPushButtonGadgetClass, 'U', NULL, NULL,
                        NULL, (XtPointer) 4, (MenuItem *)NULL },
                NULL,
                };

        MenuItem util_menu[] = {
                { "Query...", &xmPushButtonGadgetClass, 'Q', NULL, NULL,
                        NULL, (XtPointer) 1, query_menu },
                { "Mesh", &xmPushButtonGadgetClass, 'M', NULL, NULL,
                        NULL, (XtPointer) 2, (MenuItem *) NULL },
                { "Win_Resize", &xmPushButtonGadgetClass, 'W', NULL, NULL,
                        NULL, (XtPointer) 3, window_menu },
                { "Volume", &xmPushButtonGadgetClass, 'V', NULL, NULL,
                        NULL, (XtPointer) 4, (MenuItem *) NULL },
                { "Geo_Consistancy", &xmPushButtonGadgetClass, 'G', NULL, NULL,
                        NULL, (XtPointer) 2, (MenuItem *) NULL },
                NULL,
                };

        MenuItem settings_menu[] = {
                { "Window", &xmPushButtonGadgetClass, 'W', NULL, NULL,
                        NULL, (XtPointer) 1, (MenuItem *) NULL },
                NULL,
                };

        MenuItem help_menu[] = {
                { "Help", &xmPushButtonGadgetClass, 'H', NULL, NULL,
                        NULL, (XtPointer) 1, (MenuItem *) NULL },
                NULL,
                };




    XtSetLanguageProc (NULL, NULL, NULL);

    toplevel = XtVaAppInitialize (&app, "Demos", NULL, 0,
        	&argc, argv, fallbacks, NULL);  	/* Application Initialization */	


    main_w = XtVaCreateManagedWidget ("main_w",          
        	xmMainWindowWidgetClass, 	toplevel,
        	NULL);				/* main_window (manager) */


    rc = XtVaCreateWidget("rc",
			xmRowColumnWidgetClass, 	main_w,
        	XmNorientation, 		XmVERTICAL,
        	NULL);				/* Rowcolumn: geometry mangmt */

    parent_menu = XtVaCreateManagedWidget ("parent_menu",
        	xmFormWidgetClass, 		rc, 
			NULL);				


        /* Menu Bar Creation : Convinience Routine is used to create menu bar.
           BuildPulldownMenu() is used to create individual menu items */


    parent_menubar = XmCreateMenuBar(main_w, "parent_menubar", NULL, 0);

    BuildPulldownMenu (parent_menubar, "File", 		'F', 	file_menu);
    BuildPulldownMenu (parent_menubar, "Mode", 		'M', 	mode_menu);
    BuildPulldownMenu (parent_menubar, "Display", 	'D', 	display_menu);
    BuildPulldownMenu (parent_menubar, "Utilities", 'Q', 	util_menu);
    BuildPulldownMenu (parent_menubar, "Settings", 	'S', 	settings_menu);



        /* 	Help Widget is declared differently so as to take it to the 
	   		right most position ( as suggested in Motif Style guide ) 
		*/

   hwidget = BuildPulldownMenu (parent_menubar, "Help", 'H', help_menu);

   XtVaSetValues(parent_menubar, 
		XmNmenuHelpWidget, 	hwidget, 
		NULL);

    XtManageChild (parent_menubar);



        /* child_menu is manager capable of having Design & mfg menubars */ 

    child_menu = XtVaCreateManagedWidget ("child_menu",
        	xmFormWidgetClass,              rc, 
            XmNheight,                      25,
        	NULL);


	Create_design_menubar();	/* At start Design sub_menu will come */



        /* middle_form contains drawing area and status bar at the right side */ 
	Widget middle_form ;

    middle_form = XtVaCreateManagedWidget ("middle_form",
        	xmFormWidgetClass,              rc, 
        	NULL);



        /* form_drawing contains drawing area  */

	Widget	form_drawing ;

    form_drawing = XtVaCreateManagedWidget ("form_drawing",
                xmFormWidgetClass,      middle_form,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                NULL);



        /* form_status contains status area  */

	Widget 	form_status ;

    form_status = XtVaCreateManagedWidget ("form_status",
                xmFormWidgetClass,      middle_form,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_WIDGET,
                XmNleftWidget,          form_drawing,
                XmNtopAttachment,    	XmATTACH_FORM,
                NULL);


    	/* Scrolled Window for drawing */

	Widget	scroll_drawing ;


    scroll_drawing = XtVaCreateManagedWidget("scroll_drawing", 
                xmScrolledWindowWidgetClass,    form_drawing,
                XmNwidth,                       500,
                XmNheight,                      500,
                XmNscrollingPolicy,             XmAUTOMATIC,
                NULL);

    drawing_a = XtVaCreateManagedWidget ("drawing_a",
                xmDrawingAreaWidgetClass,       scroll_drawing,
                XmNwidth,                       (int)drawing_width,
                XmNheight,                      (int)drawing_height,
                NULL);


    XtAddCallback(drawing_a,XmNexposeCallback,(XtCallbackProc)redraw_all,NULL);

    gcv.foreground = BlackPixelOfScreen(XtScreen(drawing_a));

    gc = XCreateGC (XtDisplay (drawing_a),             
                RootWindowOfScreen (XtScreen (drawing_a)), GCForeground,&gcv);

    XtVaSetValues (drawing_a, XmNuserData, gc, NULL);

    XSetForeground (XtDisplay (drawing_a), gc,
                WhitePixelOfScreen (XtScreen (drawing_a)));

	XSetFunction(XtDisplay (drawing_a), gc,GXxor);	// Adding Ex-or mode
													// does not have any effect
													// on display

        /* Interface having logo , list Buttons are under rc2 */

    rc2 = XtVaCreateManagedWidget("rowcol",
        	xmRowColumnWidgetClass, 	form_status,
        	XmNorientation,			XmVERTICAL,
        	NULL);

	Widget frame ;

    frame = XtVaCreateManagedWidget("frame",
        	xmFrameWidgetClass,		rc2,
        	NULL);



        Widget icon,rowcol,rowc;
        Pixel fg,bg,fg1,bg1;

    rowc = XtVaCreateManagedWidget("Demos",
                xmRowColumnWidgetClass, 	frame,
                XmNorientation, 		XmHORIZONTAL,
                NULL);

    	XtVaGetValues(rowc,
        	XmNforeground, 	&fg1,
        	XmNbackground, 	&bg1,
        	NULL);

    Pixmap pixmapy = XmGetPixmap(XtScreen(rowc),"yogya",fg1,bg1);

    name = XtVaCreateManagedWidget("yogesh",        	/* Logo on label */
        	xmLabelGadgetClass,		rowc,
        	XmNlabelType, 			XmPIXMAP,
        	XmNlabelPixmap, 		pixmapy,
        	XmNalignment, 			XmALIGNMENT_CENTER,
        	NULL);



        Widget sep;

        sep =XtVaCreateManagedWidget("seperator",      /* Seperator line */
                xmSeparatorGadgetClass, 	rc2,
                NULL);

	Widget	form_sel ;


    form_sel = XtVaCreateManagedWidget ("form_sel",    /* List btns */
        	xmFormWidgetClass, 		rc2,
        	XmNfractionBase,    		7,
        	NULL);



        Widget sep1;

        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, 	rc2,
                NULL);


    comp_label = XtVaCreateManagedWidget ("COMPONENT LIST ",
                xmLabelGadgetClass,     	form_sel,
                XmNleftAttachment,      	XmATTACH_POSITION,
                XmNleftPosition,        	0,
                XmNtopAttachment,       	XmATTACH_POSITION,
                XmNtopPosition,         	2,
                XmNbottomAttachment,    	XmATTACH_POSITION,
                XmNbottomPosition,      	3,
                XmNrightAttachment,     	XmATTACH_POSITION,
                XmNrightPosition,       	3,
                NULL);

    comp_btn = XtVaCreateManagedWidget("Comp Id",
                xmPushButtonGadgetClass, 	form_sel,
                XmNrightAttachment,     	XmATTACH_FORM,
                XmNleftAttachment,      	XmATTACH_POSITION,
                XmNleftPosition,        	4,
                XmNtopAttachment,       	XmATTACH_POSITION,
                XmNtopPosition,         	2,
                XmNbottomAttachment,    	XmATTACH_POSITION,
                XmNbottomPosition,      	3,
                NULL);

	//#################### Need to Put a callback down or post an
	//#################### Error dialog,or lese it will core dump


    XtAddCallback (comp_btn, XmNactivateCallback, 
                        comp_btn_callback, NULL);



    block_label = XtVaCreateManagedWidget ("BLOCK LIST",
                xmLabelGadgetClass,     	form_sel,
                XmNleftAttachment,      	XmATTACH_POSITION,
                XmNleftPosition,        	0,
                XmNtopAttachment,       	XmATTACH_POSITION,
                XmNtopPosition,         	4,
                XmNbottomAttachment,    	XmATTACH_POSITION,
                XmNbottomPosition,      	5,
                XmNrightAttachment,     	XmATTACH_POSITION,
                XmNrightPosition,       	3,
                NULL);

    block_btn = XtVaCreateManagedWidget("block id",
                xmPushButtonGadgetClass,    	form_sel,
                XmNrightAttachment,         	XmATTACH_FORM,
                XmNleftAttachment,          	XmATTACH_POSITION,
                XmNleftPosition,            	4,
                XmNtopAttachment,           	XmATTACH_POSITION,
                XmNtopPosition,             	4,
                XmNbottomAttachment,        	XmATTACH_POSITION,
                XmNbottomPosition,          	5,
                NULL);

    XtAddCallback (block_btn, XmNactivateCallback,   
                        block_btn_callback, NULL);

	
	Widget	form_message ;	/* form_message contains message area  */
	
	
    form_message = XtVaCreateManagedWidget ("form_message",
                xmFormWidgetClass,      	rc,
                NULL);

	Widget	pane ;

    pane = XtVaCreateWidget ("pane", 		/* Manager for Message window */
                xmPanedWindowWidgetClass,       form_message,
                XmNrightAttachment,     	XmATTACH_FORM,
                XmNbottomAttachment,    	XmATTACH_FORM,
                XmNtopAttachment,       	XmATTACH_FORM,
                XmNleftAttachment,       	XmATTACH_FORM,
                NULL);


	Widget	label ;

    label = XtVaCreateManagedWidget ("Message",
                xmLabelWidgetClass,             pane,
                NULL);

    size.request_mode = CWHeight;
    XtQueryGeometry (label, NULL, &size);

    XtVaSetValues (label,
                XmNpaneMaximum,         size.height,
                XmNpaneMinimum,         size.height,
                NULL);



   lab = XtVaCreateManagedWidget ("text", xmTextWidgetClass, pane,
                XmNrows,           	5,
                XmNcolumns,        	80,
                XmNresizeWidth,    	False,
                XmNresizeHeight,   	False,
                XmNpaneMinimum,    	35,
                XmNeditMode,       	XmMULTI_LINE_EDIT,
                XmNvalue,          	"New Fbd.......",
                NULL);

    XtVaSetValues (lab,
        XmNvalue,       " Welcome to New Feature based design !!",
        NULL);

    XtManageChild (pane);
    XtManageChild(rc);
    XtRealizeWidget (toplevel);


	Init_Phigs();						// Phigs Initialization
    XtAppMainLoop (app);                /* Setting the Event loop running */

}



/************************** End of Main ***************************************/



/*******************************************************************************
*
*       NAME    :       Widget
*                       BuildPulldownMenu(Widget parent, char *menu_title,
*                                       char menu_mnemonic, MenuItem *items)
*
*
*       DESCRIPTION :   Creates Menu  structure containing Menu-Items defined
*                       as an array in the function main.This function has been
*						copied from Motif Programming manual.
*
*       INPUT       :   parent = menubar
*                       menu_title = Label that appeares on the menu bar
*                       menu_mnemonic = Mnemonic key sequence
*                       MenuItem = array of structure
*
*       OUTPUT      :   cascade Button (widget)
*
******************************************************************************/


Widget
BuildPulldownMenu(Widget parent, char *menu_title, char menu_mnemonic, MenuItem *items)
{
    Widget PullDown, cascade, widget;
    int i;
    XmString str;



    PullDown = XmCreatePulldownMenu (parent, "_pulldown", NULL, 0);
    str = XmStringCreateLocalized (menu_title);

    cascade = XtVaCreateManagedWidget (menu_title,
        xmCascadeButtonGadgetClass, parent,
        XmNsubMenuId,   PullDown,
        XmNlabelString, str,
        XmNmnemonic,    menu_mnemonic,
        NULL);
    XmStringFree (str);



    for (i = 0; items[i].label != NULL; i++) {
        if (items[i].subitems)
            widget = BuildPulldownMenu (PullDown, items[i].label,
                items[i].mnemonic, items[i].subitems);
        else
            widget = XtVaCreateManagedWidget (items[i].label,
                *items[i].class1, PullDown,
                NULL);
        if (items[i].mnemonic)
            XtVaSetValues (widget, XmNmnemonic, items[i].mnemonic, NULL);
        if (items[i].accelerator) {
            str = XmStringCreateLocalized (items[i].accel_text);
            XtVaSetValues (widget,
                XmNaccelerator, items[i].accelerator,
                XmNacceleratorText, str,
                NULL);
            XmStringFree (str);
        }
        if (items[i].callback)
            XtAddCallback(widget,
                (items[i].class1 == &xmToggleButtonWidgetClass ||
                items[i].class1 == &xmToggleButtonGadgetClass) ?
                    XmNvalueChangedCallback : /* ToggleButton class */
                    XmNactivateCallback,      /* PushButton class */
                items[i].callback, items[i].callback_data);
    }
    return cascade;
}

/*******************************************************************************
*
*       NAME            :redraw_all()
*
*       DESCRIPTION     :Whenever any exposure occurs over drawing area widget
*			 			this callback is invoked. The main function is to
*			 			repaint the picture.Its in programmers hand ,what
*			 			to display at every exposure. Here repainting of
*			 			current component ( along with its blocks) is done.
*
*       INPUT           : Exposure event
*
*       OUTPUT          : Repainting of the current component
*
******************************************************************************/
 
void redraw_all(Widget widget, XtPointer client_data, XtPointer call_data)
{
        predraw_all_structs(WS_ID,PFLAG_ALWAYS);

        if(currc != NULL){
 
         	pdel_all_structs();							// clear everything
            currc->Display_by_phigs(display_type);
			
						// display_type is global in
						// graphics_phigs.h It can be
						// set to various types such as
						// wirefram,blockwise etc.

						// See also display_driver.c for
						// Polygon set display

            // ppost_struct(WS_ID,(Pint)currc->Get_component_id(),0);

						// struct_id is same as comp_id
						// with casting of Pint

            // predraw_all_structs(WS_ID,PFLAG_ALWAYS);
            }
 
}
