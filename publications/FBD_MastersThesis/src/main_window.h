/*******************************************************************************
*       FILENAME :      main_window.h      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Motif Declarations 
*
*	USAGE :		Wherever motif calls are made,mainly for files having
*			"_"in their name.These are basically Interface files.
*
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE   	:   	MAY 27, 1995.
*
*******************************************************************************/


/******************************************************************************
*                       INCLUDE FILES
******************************************************************************/

#ifndef _main_window_h
#define  _main_window_h

#include <Xm/RowColumn.h>
#include <Xm/LabelG.h>
#include <Xm/TextF.h>
#include <Xm/Label.h>
#include <Xm/PanedW.h>
#include <Xm/Text.h>
#include <Xm/List.h>
#include <Xm/ScrolledW.h>
#include <Xm/Form.h>
#include <Xm/Frame.h>
#include <Xm/MainW.h>
#include <Xm/Scale.h>
#include <Xm/DrawingA.h>
#include <Xm/CascadeBG.h>
#include <Xm/SeparatoG.h>
#include <Xm/PushB.h>
#include <Xm/PushBG.h>
#include <Xm/ToggleB.h>
#include <Xm/ToggleBG.h>
#include <Xm/FileSB.h>
#include <Xm/MessageB.h>
#include <Xm/SelectioB.h>
#include <Xm/DialogS.h>

#include <X11/Xos.h>

#include <stdio.h>
#include <stdlib.h>

/*******************************************************************************
                MACRO DEFINITIONS
*******************************************************************************/
 
 
    /*
    **      Note:
    **
    **      Normally macros are not handled by compiler .Preprocessers
    **      substitutes them with constant value. Thats why they are type-unsafe
    **      and may cause problems if not handled properly.
    **      "enumeration" is a better way to handle such declarations.
    **      Following thing is done at very begining of the coding stage
    **      at that time I followed the method used in previous programs.
    **      and now it will be time consuming to change all those places
    **      Its definitely a better programming practice to code that way.
    */

/* For OK_APPLY_CANCEL buttons to be passed as client_data through callback */

#define OK 	1
#define APPLY 	2
#define CANCEL 	3

/* following things are values of comp_flag  */

#define NO_COMP		0
#define NEW_COMP	1 
#define OLD_COMP	2

/* following things are values of menu_flag  */

#define NO_MENU			0	
#define CREATE			1	
#define EDIT			2	
#define DISPLAY			3	
#define QUERY			4	
#define ROTATION		5	
#define SCALING			6	
#define DXF				7	
#define SAVE			8	
#define RETRIEVE		9		
#define NEWCOMPONENT	10		
#define ADD_TOPO		11		
#define ADD_BLK			12		
#define DIMENSION		13		
#define QUERY_DIM		14		
#define REDIMENSION		15		
#define CHG_DATUM		16		
#define SPECIFY_DIM		17		

#define NO_VALUE	-99999		/* reqiured for fn. print_msg() */


#define WIDTH 	500               	/* Drawing Area width 	*/
#define HEIGHT 	500              	/* Drawing Area height 	*/

    /*
    **      Following structure is used only to facillitate
    **      transfer of information from Motif to Applications
    **      Similar structures could be defined for rest of the
    **      Callbacks for cleaner and readable program design
    **      rather than declaring globals for every information
    **      needed( currently there are some such globals still present)
    */

/********This structure is required in the Buildpulldownmenu routine *******/

typedef struct _menu_item {
    char        *label;
    WidgetClass *class1;
    char         mnemonic;
    char        *accelerator;
    char        *accel_text;
    void       (*callback)(Widget,XtPointer,XtPointer);
    XtPointer    callback_data;
    struct _menu_item *subitems;
} MenuItem;

/******************************************************************************
                        GLOBAL DECLARATIONS(INTERFACE)
******************************************************************************/

    /*
    **      Declaring globals is normally a BAD programming practice,
    **      especially in a project of this or bigger size.
    **      Following GLOBALS are declared mainly because of Motif.
    **      There is definitely scope for minimizing these GLOBALS
    **      by better program and class design.
    */
 
extern	double drawing_width;                   /* Drawing Area width*/
extern	double drawing_height;                  /* Drawing Area height */

extern  XGCValues gcv;
extern  GC gc;                 	/* Graphics Context */

extern 	Widget toplevel;		/* main application shell */
extern  Widget main_w;			/* main window as overall manager */
extern  Widget drawing_a;		/* Drawind area widget */
extern  Widget rc;				/* manager for parent and child menu */
extern  Widget parent_menubar;	/* Parent menubar for common menu */
extern  Widget hwidget;			/* Help widget,set from any where */
extern  Widget child_menu;		/* mode : design or Manufacturing menu*/
extern  Widget design_menubar;	/* Design menu options */
extern  Widget mfg_menubar;		/* Manufacturing menu options */
extern  Widget rc2;				/* Status area manager */
extern  Widget name;			/* Logo label widget */
extern  Widget comp_btn;		/* componet button at status area */
extern  Widget block_btn;		/* block button at status area */
extern  Widget lab;				/* text widget for messages at bottom */
extern  Widget comp_label;     	/* Status comp_btn's label */
extern  Widget block_label;     /* Status block_btn's label */

extern  Widget comp_id;         /* comp_id in data entry*/
extern  Widget block_id;        /* block_id in data entry*/
extern  Widget num_links;       /* Number of topo links*/
extern  Widget len_links;       /* Number of length links*/
extern  Widget edit_length;     /* New length for modification*/
extern  Widget modf_node;       /* modification Node in cycle*/
extern  Widget major_rad;       /* Major radius of Cylinder*/
extern  Widget minor_rad;       /* Minor radius of Cylinder*/
extern  Widget cylinder_base;   /* Base Plane of Cylinder*/

extern  Widget x_min,x_max,x_mid,x_len;	/* X-Data entry widgets */
extern  Widget y_min,y_max,y_mid,y_len;	/* Y-Data entry widgets */
extern  Widget z_min,z_max,z_mid,z_len;	/* Z-Data entry widgets */

extern	Widget spl_x[20];		/* Spline data X coordinates	*/
extern	Widget spl_y[20];		/* Spline data Y coordinates	*/
extern	Widget spl_z[20];		/* Spline data Z coordinates	*/

extern	int comp_flag;			/* Status of component NO/OLD */	
extern	int block_flag;			/* Status of block NO/ADD_BLK.. */
extern	int menu_flag;			/* Which menu is selected */		

extern  double 	x_minf,x_maxf,x_midf,x_lenf;/* X-Data entry flags */
extern  double	y_minf,y_maxf,y_midf,y_lenf;/* Y-Data entry flags */
extern  double	z_minf,z_maxf,z_midf,z_lenf;/* Z-Datanentry flags */


/******************************************************************************
                        FUNCTIONS PROTOTYPE  DECLARATIONS
******************************************************************************/

/*	Functions coded in the file : main_window.c		*/

Widget
BuildPulldownMenu(Widget parent, char *menu_title, char menu_mnemonic, MenuItem *items);

void redraw_all(Widget widget, XtPointer client_data, XtPointer call_data);

/*	Functions coded in the file : file_driver.c		*/

void file_new_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void file_quit_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void file_quit_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data);

void filename_save(Widget widget, XtPointer client_data, XtPointer call_data);
void new_file_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void compid_save(FILE *f);
void write_file(Widget widget, XtPointer client_data, XtPointer call_data);

void filename_retrieve(Widget wi, XtPointer client_data, XtPointer call_data);
void open_file_cb(Widget widget, XtPointer client_data, XtPointer call_data);
 

void Venkys_save(Widget widget, XtPointer client_data, XtPointer call_data);
void Venkys_file_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void Venkys_compid_save(FILE *f);
void Venkys_write_file(Widget wi, XtPointer client_data, XtPointer call_data);

/*	Functions coded in the file : mode_driver.c		*/

void mode_design_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void mode_mfg_cb(Widget widget, XtPointer client_data, XtPointer call_data);

void Create_design_menubar();	
void Create_mfg_menubar();

/*	Functions coded in the file : create_driver.c		*/

void create_newcomp_cb(Widget widget,XtPointer client_data,XtPointer call_data);
void create_addtopo_cb(Widget widget,XtPointer client_data,XtPointer call_data);

void make_data_entry_table(int blk_type);

/*	Functions coded in the file : edit_driver.c		*/


void edit_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void make_length_editing_box();
void len_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void con_plane_cb(Widget widget, XtPointer client_data, XtPointer call_data);

/*	Functions coded in the file : geom_edit_callbacks.c		*/

void geom_edit_ok(Widget widget, XtPointer client_data, XtPointer call_data);
void geom_edit_can(Widget widget, XtPointer client_data, XtPointer call_data);
void select_cycle_ok(Widget widget, XtPointer client_data, XtPointer call_data);
void Create_Cycle_Selection_box();
void cycle_sel_callback(Widget w, XtPointer client_data, XtPointer call_data);
void cyl_sel_cb(Widget w, XtPointer client_data, XtPointer call_data);

/*	Functions coded in the file : addblk_driver.c		*/

void addblk_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void addblk_cb();
void no_links_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void make_topo_selection_box(int number);
void blk_sel_callback(Widget w, XtPointer client_data, XtPointer call_data);
void cfm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void cm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void cem_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void tcm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void fcm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void spm_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void Select_Plane(int num);
void plane_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void sel_plane_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void sel_plane_can_cb(Widget wi, XtPointer client_data, XtPointer call_data);

/*	Functions coded in the file : addcyl_driver.c		*/

void cyl_axis_selection();

/*  Functions coded in the file : addwedge_driver.c       */
 
void wedge_axis_selection();


/*	Functions coded in the file : topo_selection_callbacks.c	*/

void make_full_data_entry_table();
void topo_apply_cb(Widget wi, XtPointer client_data, XtPointer call_data);
void topo_can_cb(Widget wi, XtPointer client_data, XtPointer call_data);


/*	Functions coded in the file : topo_data_assignments.c	*/

void cfm_for_data_table(int ,int);
void cm_for_data_table(int ,int,int,int);
void cem_for_data_table(int ,int,int);
void tcm_for_data_table(int ,int,int,int,int);
void fcm_for_data_table(int ,int);
void spm_for_data_table(int ,int);

/*	Functions coded in the file : cyl_data_callbacks.c		*/

void cyl_axis_sel_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void cyl_data_ok_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void cyl_data_can_cb(Widget widget, XtPointer client_data, XtPointer call_data);

/*  Functions coded in the file : wedge_data_callbacks.c      */
 
void wedge_axis_sel_cb(Widget wid, XtPointer client_data, XtPointer call_data);
void wedge_pl_sel_cb(Widget wid, XtPointer client_data, XtPointer call_data);
void wedge_data_ok_cb(Widget wid, XtPointer client_data, XtPointer call_data);
void wedge_data_can_cb(Widget wi,XtPointer clit_data, XtPointer call_data);
 

/*	Functions coded in the file : data_entry_callbacks.c		*/

void 	data_entry_ok(Widget widget,XtPointer client_data,XtPointer call_data);
void 	data_entry_can(Widget widget,XtPointer client_data,XtPointer call_data);

void 	compid_data_cb(Widget widget,XtPointer client_data,XtPointer call_data);
void 	blkid_data_cb(Widget widget,XtPointer client_data,XtPointer call_data);

void 	addblk_data_ok(Widget w,XtPointer client_data,XtPointer call_data);
void 	addblk_data_can(Widget w,XtPointer client_data,XtPointer call_data);

/*	Functions coded in the file : bspline_driver.c		*/
void 	make_spl_data_box(Widget w,XtPointer client_data,XtPointer call_data);
void 	addspl_data_ok(Widget w,XtPointer client_data,XtPointer call_data);
void 	addspl_data_apply(Widget w,XtPointer client_data,XtPointer call_data);

/*	Functions coded in the file : xdata_callbacks.c		*/

void 	xmin_data_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void 	xmax_data_cb(Widget widget, XtPointer client_data, XtPointer call_data);

/*	Functions coded in the file : ydata_callbacks.c		*/

void    ymin_data_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void    ymax_data_cb(Widget widget, XtPointer client_data, XtPointer call_data);
 
/*	Functions coded in the file : zdata_callbacks.c		*/

void    zmin_data_cb(Widget widget, XtPointer client_data, XtPointer call_data);
void    zmax_data_cb(Widget widget, XtPointer client_data, XtPointer call_data);
 
/*	Functions coded in the file : util_driver.c		*/
void 	comp_btn_callback(Widget wi, XtPointer client_d, XtPointer call_data);
void 	block_btn_callback(Widget wi, XtPointer client_d, XtPointer call_data);


/*	Functions coded in the file : utility_functions.c		*/

void 	print_msg(char text[],float value);
Widget 	PostDialog(Widget parent,int dialog_type,char *msg);
void 	post_msg(char *prompt);
void 	temp_action(Widget widget, XtPointer client_data, XtPointer call_data);
void	Write_in_Data_table();
void	print_graph();

/*	Functions coded in the file : display_driver.c		*/

void 	display_pset_cb(Widget wi, XtPointer client_d, XtPointer call_data);
void 	display_truewire_cb(Widget wi, XtPointer client_d, XtPointer call_data);
void 	display_blkwise_cb(Widget wi, XtPointer client_d, XtPointer call_data);

/*	Functions coded in the file : dimension_driver.c		*/

void 	dimension_cb(Widget wi, XtPointer client_d, XtPointer call_data);
void	select_dim_axis();
void	make_query_box();
void	make_specify_dim_datum_box();
void	make_change_datum_box();
void 	dim_axis_ok_cb(Widget wi, XtPointer client_d, XtPointer call_data);
void 	chg_datum_axis_ok_cb(Widget wi,XtPointer client_d, XtPointer call_data);
void 	p1_sel_callback(Widget wi, XtPointer client_d, XtPointer call_data);
void 	p2_sel_callback(Widget wi, XtPointer client_d, XtPointer call_data);
void 	arc_sel_callback(Widget wi, XtPointer client_d, XtPointer call_data);
void 	display_path_callback(Widget wi, XtPointer cl_d, XtPointer call_data);
void 	chg_datum_callback(Widget wi, XtPointer cl_d, XtPointer call_data);
void 	del_dim_arc_cb(Widget wi, XtPointer cl_d, XtPointer call_data);

#endif

