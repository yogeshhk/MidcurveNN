/*******************************************************************************
*       FILENAME :      graphics_phigs.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Graphics routins with PHIGS
*
*       FUNCTIONS   :   
*						Init_Phigs()
*						Close_Phigs()
*						Resize_Ws()
*						DrawAxes()
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   MAY 31, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */

/******************************************************************************
                        GLOBAL  DECLARATIONS
******************************************************************************/

int 	win_resizeflag 	= 1;			/* Auto-resizing */
double 	display_max 	= 500 ;			/* Resizing max dimension */
int		display_type	= WIREFRAME ;	/* type at start is wire_frame */

/*****************************************************************************
*
*       NAME    :       Init_Phigs()
*
*       DESCRIPTION :	Initialization of phigs variables   
*
******************************************************************************/

void Init_Phigs()
{

    Window                      xid;
    Pconnid_x_drawable          conn_id;
    XSetWindowAttributes        win_attrs;
    Pxphigs_info                xphigs_info;
    unsigned long               mask;

    xid = XtWindow( drawing_a );
    XSetWMColormapWindows( XtDisplay(toplevel), XtWindow(toplevel), &xid, 1 );

    mask = PXPHIGS_INFO_FLAGS_NO_MON;
    xphigs_info.flags.no_monitor = 1;
    popen_xphigs( PDEF_ERR_FILE, PDEF_MEM_SIZE, mask, &xphigs_info );

    win_attrs.backing_store = NotUseful;
    XChangeWindowAttributes( XtDisplay(drawing_a), XtWindow(drawing_a),
        CWBackingStore, &win_attrs );

    conn_id.display = XtDisplay(drawing_a);
    conn_id.drawable_id = XtWindow(drawing_a);

    popen_ws( WS_ID, (void *)&conn_id, phigs_ws_type_x_drawable);

	/*
	**		This is very important call.
	**		By setting WS catagory to phigs_ws_type_x_drawable
	**		we fix many characteristics like now this is OUTPUT only
	**		primitive. It can not accept PHIGS input devices I guess.
	**		we need to depend on X event queue to perform actions
	**		corresponding to callbacks
	*/

    pset_disp_upd_st( WS_ID, PDEFER_WAIT, PMODE_NIVE );

	Resize_Ws(display_max);		// proper drawing dimension at start		


}


/*****************************************************************************
*
*       NAME    :       Close_Phigs()
*
*       DESCRIPTION :   Closing of the phigs
*
******************************************************************************/

void Close_Phigs()
{

        pclose_ws( WS_ID );
        pclose_phigs();

}
/*****************************************************************************
*
*       NAME    :       Resize_Ws()
*
*       DESCRIPTION :   Resizes Phigs view_port dimensions
*
******************************************************************************/
 
void Resize_Ws(double max)
{
		Pview_rep3      vrep;                           //  view structure
		Pview_map3      view_map ;

        Pcolr_rep       rep;
        Pupd_st         upd_st;
        Plimit3         req_win_lim, cur_win_lim, req_vp_lim, cur_vp_lim,l;

        Ppoint3			vrp = {0., 0.0, 0.0 };          //  origin
        Pvec3 			vpn = {1.0,0.6,1.0};            //  view plane normal
        Pvec3 			vup = {0., 1.0, 0.0 };          //  view up vector
        Pint            err;
 

				// see page 133 in PHIGS programming manual

        rep.rgb.red     = 1.;
        rep.rgb.green   = 1.;
        rep.rgb.blue    = 1.;
 

				// get the value of variables assocaiated with
				// our workstation WS_ID.All the parameters
				// preceded by & are what we get outside

        pinq_ws_tran3(WS_ID, &err, &upd_st ,&req_win_lim, &cur_win_lim,
                      &req_vp_lim, &cur_vp_lim);
 
        Plimit3	lm      = cur_vp_lim;
        Pint    x_size  = (Pint)(lm.x_max - lm.x_min);	// get width of window
        Pint    y_size  = (Pint)(lm.y_max - lm.y_min);	// get height of window

        Pint    size    = (x_size > y_size) ? x_size : y_size;	// take the max


				// aspect ratio calculations

        Pfloat  ratio_x = (Pfloat)x_size/(Pfloat)size;
        Pfloat  ratio_y = (Pfloat)y_size/(Pfloat)size;


				// deciding the display volume

        l.x_min = 0;
        l.y_min = 0;
        l.z_min = 0;
        l.x_max =  ratio_x;
        l.y_max =  ratio_y;
        l.z_max = 1.000 ;
 
 
        pset_ws_win3(WS_ID,&l);
 
        pinq_ws_tran3(	WS_ID, &err, &upd_st ,
						&req_win_lim, &cur_win_lim,
                      	&req_vp_lim, &cur_vp_lim);


			// see page 444 PHIGS programming manual
 
        view_map.win.x_min      = - 1.5 * max;
        view_map.win.x_max      =   1.5 * max;
        view_map.win.y_min      = - 1.5 * max;
        view_map.win.y_max      =   1.5 * max;
        view_map.front_plane 	=   3.0 * max;
        view_map.back_plane 	= - 3.0 * max;

        view_map.proj_vp        = req_win_lim;

        view_map.proj_ref_point.x = 0.0;
        view_map.proj_ref_point.y = 0.0;
        view_map.proj_ref_point.z = 5 * max;
 
        view_map.view_plane 	= 0.0;
        view_map.proj_type 		= PTYPE_PARAL;
 
        peval_view_ori_matrix3( &vrp, &vpn, &vup, &err, vrep.ori_matrix);
        peval_view_map_matrix3(&view_map, &err, vrep.map_matrix);

        vrep.clip_limit	= view_map.proj_vp;

        vrep.xy_clip 	= PIND_NO_CLIP;
        vrep.back_clip 	= PIND_NO_CLIP;
        vrep.front_clip = PIND_NO_CLIP;

        pset_view_rep3(WS_ID,(Pint)1,&vrep);
        pset_colr_rep(WS_ID,0,&rep);

			// see page 595 PHIGS programming manual

        pset_disp_upd_st(WS_ID,PDEFER_WAIT,PMODE_NIVE);
        pupd_ws(WS_ID,PFLAG_PERFORM);
 
}
 
 
/************************************************************************
        FUNCTION TO DRAW AXES IN PHIGS DISPLAY WINDOW
 
************************************************************************/
void DrawAxes(double length)
{


    Pptco3              	x_axis[2], y_axis[2], z_axis[2];
    Pline_vdata_list3   	axes[3];
	Ppoint3					text_pt[3];
	Pvec3					view[2];
	Pgcolr					color;
	Ptext_align				alignment;
	Pvec					up_vector;
 
    /* Set the axes coordinates and colors. */

    	x_axis[0].point.x = x_axis[0].point.y = x_axis[0].point.z = 0;
    	x_axis[1].point.x = length;
    	x_axis[1].point.y = 0;
    	x_axis[1].point.z = 0;
    	x_axis[0].colr.direct.rgb.red 	= 1;
    	x_axis[0].colr.direct.rgb.green = 0;
    	x_axis[0].colr.direct.rgb.blue 	= 0;
    	x_axis[1].colr.direct.rgb = x_axis[0].colr.direct.rgb;
 

    	y_axis[0].point.x = y_axis[0].point.y = y_axis[0].point.z = 0;
    	y_axis[1].point.x = 0;
    	y_axis[1].point.y = length;
    	y_axis[1].point.z = 0;
    	y_axis[0].colr.direct.rgb.red 	= 1;
    	y_axis[0].colr.direct.rgb.green = 1;
    	y_axis[0].colr.direct.rgb.blue 	= 0;
    	y_axis[1].colr.direct.rgb = y_axis[0].colr.direct.rgb;
 
    	z_axis[0].point.x = z_axis[0].point.y = z_axis[0].point.z = 0;
    	z_axis[1].point.x = 0;
    	z_axis[1].point.y = 0;
    	z_axis[1].point.z = length;
    	z_axis[0].colr.direct.rgb.red = 0;
    	z_axis[0].colr.direct.rgb.green = 0;
    	z_axis[0].colr.direct.rgb.blue = 1;
    	z_axis[1].colr.direct.rgb = z_axis[0].colr.direct.rgb;
 
    /* Build a polyline set for the axes. */

    	axes[0].num_vertices = 2;
    	axes[1].num_vertices = 2;
    	axes[2].num_vertices = 2;
    	axes[0].vertex_data.ptcolrs = x_axis;
    	axes[1].vertex_data.ptcolrs = y_axis;
    	axes[2].vertex_data.ptcolrs = z_axis;


	/* Set text color to grey */

	color.type	= PMODEL_RGB;

	color.val.general.x	= 1.;
	color.val.general.y	= 0.;
	color.val.general.z	= 1.;

	pset_text_colr( &color);

	/* Center the string using the text alignment */

	alignment.hor	= PHOR_CTR;
	alignment.vert	= PVERT_HALF;
	pset_text_align( &alignment);
	
	/* add some character spacing 1% of the character height */

	/* Write the axes names */

	pset_char_ht( (Pfloat)(0.05*length));

	text_pt[0].x	= 1.05*length;
	text_pt[0].y	= 0.0*length;
	text_pt[0].z	= 0.0*length;
	
	/* first direction vector */

	view[0].delta_x	= 1.0;
	view[0].delta_y	= 0.0;
	view[0].delta_z	= 0.0;

	/* second direction vector */

	view[1].delta_x	= 1.0;
	view[1].delta_y	= 1.0;
	view[1].delta_z	= 0.0;

	ptext3( &text_pt[0], view ,"X");

	text_pt[1].x    = 0.0*length;
   	text_pt[1].y    = 1.15*length;
    text_pt[1].z    = 0.0*length;
 
    /* first direction vector */
 
    view[0].delta_x = 1.0;
    view[0].delta_y = 0.0;
    view[0].delta_z = 0.0;
 
    /* second direction vector */
 
    view[1].delta_x = 1.0;
    view[1].delta_y = 1.0;
    view[1].delta_z = 0.0;
 

	ptext3( &text_pt[1], view ,"Y");


	/* rotate the text to some degrees clockwise */

    /* first direction vector */
 
    view[0].delta_x = 1.0;
    view[0].delta_y = 0.0;
    view[0].delta_z = 0.0;
 
    /* second direction vector */
 
    view[1].delta_x = 1.0;
    view[1].delta_y = 1.0;
    view[1].delta_z = 0.0;
 
    text_pt[2].x    = 0.00*length;
    text_pt[2].y    = 0.00*length;
    text_pt[2].z    = 1.05*length;
 
 
    ptext3( &text_pt[2], view ,"Z");
 

    ppolyline_set3_data( PVERT_COORD_COLOUR, PMODEL_RGB, (Pint) 3, axes ); 
 
}

void Set_HLHSR(){

    Pint        err;
    Pstore      store;
    void       *conn_id;
    Pint        ws_instance;
    Pint        hlhsr_mode;
    Pint        hlhsr_list_start;
    Pint        hlhsr_length_list;
    Pint_list   hlhsr_list;

    /* Create storage for use in inquiry functions. */
    pcreate_store(&err, &store);
    if (err != 0) {
        /*
         * We won't be able to inquire the available HLHSR modes, so
         * leave the HLHSR mode at its default value.
         */
        return;
    }

    /* Get the workstation type of WSID. */
    pinq_ws_conn_type(WS_ID, store, &err, &conn_id, &ws_instance);
    if (err != 0) {
        /*
         * We won't be able to inquire the available HLHSR modes, so
         * leave the HLHSR mode at its default value.
         */
        return;
    }

    hlhsr_list.ints = &hlhsr_mode;
    hlhsr_list_start = 0;

    /* Keep inquiring the HLHSR modes until we find one we want. */
    do {

        pinq_hlhsr_mode_facs (ws_instance, 1, hlhsr_list_start, &err,
            &hlhsr_list, &hlhsr_length_list);

        if (err != 0) {
            break;
        }

        if (hlhsr_mode == PHIGS_HLHSR_MODE_ZBUFF){
                /* Enable Z-buffering. */
                pset_hlhsr_mode(WS_ID, hlhsr_mode);
                return;
        }

        hlhsr_list_start++;

    } while (hlhsr_list_start < hlhsr_length_list);

    /* No valid HLHSR mode was found for this workstation. */
    pset_hlhsr_mode(WS_ID, PHIGS_HLHSR_MODE_NONE);

}


void
handle_input()
{
    XEvent      event;
    int         lastx, lasty, done = 0;
    float       theta = 3.142/4, phi = 3.142/4;
	float		scale = 3.142/500;


        Ppoint3  	vrp ;                          //  origin
        Pvec3    	vpn ;                          //  view plane normal
        Pvec3    	vup ;                          //  view up vector
        Pview_rep3  vrep;                           //  view structure
        Pview_map3 	view_map ;
		Pint		error;


    XSelectInput(  XtDisplay(drawing_a), XtWindow(drawing_a),
    ButtonPressMask | Button1MotionMask | ExposureMask );
    while ( !done ) {
    XNextEvent(  XtDisplay(drawing_a), &event );
    if ( event.type == ButtonPress ) {
        switch ( event.xbutton.button ) {
        case Button1:
            /* Reset last X and last Y. */
            lastx = event.xbutton.x;
            lasty = event.xbutton.y;
            break;
        default:
            done = 1;
            break;
        }

    } else if ( event.type == MotionNotify ) {
        /* Increment the view plane normal angles. */
        theta += scale * (event.xmotion.x - lastx);
        phi += scale * (lasty - event.xmotion.y);


        /* Reset the view plane normal. */
        vpn.delta_x = cos( phi ) * sin( theta );
        vpn.delta_y = sin( phi );
        vpn.delta_z = cos( phi ) * cos( theta );

        /* Calculate the new orientation matrix. */
        peval_view_ori_matrix3( &vrp, &vpn,
        &vup, &error, vrep.ori_matrix );

        /* Set the view if orientation is okay. */
        if ( !error )
        pset_view_rep3( WS_ID, (Pint) 1, &vrep );

        lastx = event.xmotion.x;
        lasty = event.xmotion.y;

        } else switch ( event.type ) {
        case Expose:
            if ( event.xexpose.count == 0 )
            break;
        }
    }
}


