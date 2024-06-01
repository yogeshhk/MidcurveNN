/*******************************************************************************
*       FILENAME :      data_entry_callbacks.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from bspline data_entry Table
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   May 8, 1996.
*
*******************************************************************************/
 
 
/******************************************************************************
                       INCLUDE FILES
******************************************************************************/
 
#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "classes.h"        	/* Classes Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
 
#define	CURVE_WS	2			/* Workstation Id for Bspline curve display*/
#define	SPLINE_ID	50			/* Structure Id */

	/*
	**		Following structure is used to temporarily store
	**		the specifications of spline
	**		Defined in Application.h
	*/

SplineData  spline_data;    //  used to store spline information

/*******************************************************************************
*
*       NAME            :addspl_data_ok()
*
*       DESCRIPTION     :
*
******************************************************************************/
 
void 
addspl_data_ok(Widget widget,XtPointer client_data,XtPointer call_data)
{
        Widget a=(Widget)client_data;   // shell to destroy data_entry table

		int m;
 
		char *xval;
		char *yval;
		char *zval;

		float xx;
		float yy;
		float zz;

		Vertex	points[6];

		for(m=0;m<6;m++){

			xval	=	XmTextGetString(spl_x[m]);
			yval	=	XmTextGetString(spl_y[m]);
			zval	=	XmTextGetString(spl_z[m]);
			xx		=	atof(xval);
			yy		=	atof(yval);
			zz		=	atof(zval);
			spline_data.u_pts[m].Set_x(xx);		//	Its global
			spline_data.u_pts[m].Set_y(yy);		//	Its global
			spline_data.u_pts[m].Set_z(zz);		//	Its global
			points[m].Set_x(xx);		
			points[m].Set_y(yy);	
			points[m].Set_z(zz);
		}

        char *blkid  = XmTextGetString(block_id);

        char *xmin  = XmTextGetString(x_min);
        char *xmax  = XmTextGetString(x_max);
        char *xmid  = XmTextGetString(x_mid);
        char *xlen  = XmTextGetString(x_len);
 
        char *ymin  = XmTextGetString(y_min);
        char *ymax  = XmTextGetString(y_max);
        char *ymid  = XmTextGetString(y_mid);
        char *ylen  = XmTextGetString(y_len);
 
        char *zmin  = XmTextGetString(z_min);
        char *zmax  = XmTextGetString(z_max);
        char *zmid  = XmTextGetString(z_mid);
        char *zlen  = XmTextGetString(z_len);
 
        float xmn = atof(xmin);
        float xmx = atof(xmax);
        float xmd = atof(xmid);
        float xln = atof(xlen);
 
        float ymn = atof(ymin);
        float ymx = atof(ymax);
        float ymd = atof(ymid);
        float yln = atof(ylen);
 
        float zmn = atof(zmin);
        float zmx = atof(zmax);
        float zmd = atof(zmid);
        float zln = atof(zlen);
 
        XtFree(xmin);
        XtFree(xmax);
        XtFree(xmid);
        XtFree(xlen);
 
        XtFree(ymin);
        XtFree(ymax);
        XtFree(ymid);
        XtFree(ylen);
 
        XtFree(zmin);
        XtFree(zmax);
        XtFree(zmid);
        XtFree(zlen);
 
        XtFree(xval);
        XtFree(yval);
        XtFree(zval);

        printf("blkid %s\n",blkid);
        printf("%f %f\n",xmn,xmx);
        printf("%f %f\n",ymn,ymx);
        printf("%f %f\n",zmn,zmx);


	/* Now actual Instanciation will start */

	
      	Block *nb;

		int	ax	=	wedge_axis;				//	wedge_axis is global

		nb = new Bspline(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx,ax,points);

		int newblk_id	= nb->Get_block_id();

        currc->Link_Blocks(nb);        	// links the block to linklist and sets
                                		// comp_block pointer to the first block
 

	
        Node *nn = new FeatureNode(nb);				// New node
		nb->Set_block_node(nn);						// set block in that node
        currc->Get_comp_graph()->Link_Node(nn); 	// link it to the graph
 

	/*
		We have stored information about Topology in an global
		array called topo_info[]. Not all the array is filled
		To know upto what array node value has been fixed we
		search array till block_id is zero. Because before
		filling information all array nodes were initialized to 0
		We start the search from i= 1 and not i=0 as we started
		filling the information from topo_info[1]

	*/

	for( int i = 1;topo_info[i].block_id != 0 ;i++){

		switch(topo_info[i].topo_type){

			case CFM :

				Center_Face_Match *tcfm;
				tcfm = new Center_Face_Match( &topo_info[i],newblk_id);
				break;

			case CEM :
 
               	Center_Edge_Match *tcem;
                tcem = new Center_Edge_Match( &topo_info[i],newblk_id);
                break;
 
            case CM :
 
                One_Corner_Match *tocm;
                tocm = new One_Corner_Match( &topo_info[i],newblk_id);
                break;

            case TCM :
 
                Two_Corner_Match *ttcm;
                ttcm = new Two_Corner_Match( &topo_info[i],newblk_id);
                break;

            case FCM :
 
                Four_Corner_Match *tfcm;
                tfcm = new Four_Corner_Match( &topo_info[i],newblk_id);
                break;

            case SP :
 
                Shared_Plane_Match *tsp;
                tsp = new Shared_Plane_Match( &topo_info[i],newblk_id);
                break;

		}
 
	}

 
	/*
		After doing everything do the following
	*/
 
        menu_flag       = NO_MENU ;
 
        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;  // X-Data flags
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;  // Y-Data flags
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;  // Z-Data flags
 
        make_Topo_info_null();          // No topo_info         (application.c)
        make_temp_planes_null();        // No planes selection  (application.c)
 
        XtFree(blkid);
        XtPopdown(a);                   // popdown the Data Entry table
    	//pclose_ws( CURVE_WS);			// Closing 2D workstation at OK
 
}

 
/*******************************************************************************
*
*       NAME            :addspl_data_ok()
*
*       DESCRIPTION     :
*
******************************************************************************/

void
addspl_data_apply(Widget widget,XtPointer client_data,XtPointer call_data)
{

        char *xval;
        char *yval;
        char *zval;

        float xx;
        float yy;
        float zz;
		int m;

        Vertex  points[6];

        for(m=0;m<6;m++){

            xval    =   XmTextGetString(spl_x[m]);
            yval    =   XmTextGetString(spl_y[m]);
            zval    =   XmTextGetString(spl_z[m]);
            xx      =   atof(xval);
            yy      =   atof(yval);
            zz      =   atof(zval);
            spline_data.u_pts[m].Set_x(xx);     //  Its global
            spline_data.u_pts[m].Set_y(yy);     //  Its global
            spline_data.u_pts[m].Set_z(zz);     //  Its global
            points[m].Set_x(xx);
            points[m].Set_y(yy);
            points[m].Set_z(zz);
        }

		/*
		** 		Here a separate PHIGS workstation will be opened
		**		and a 2D curve will be shown
		*/

		Ppoint3			control_points[6];
		Pfloat   		knots_3ord[] = {1,1,1,2,3,4,5,5,5};
    	Pint        	order, i;
    	Pfloat      	min, max;
    	Pfloat_list     knots;
    	Ppoint_list34   cpts;
    	Ppoint_list3    markers;

		for(int j=0;j<6;j++){

			control_points[j].x	=	points[j].Get_x();
			control_points[j].y	=	points[j].Get_y();
			control_points[j].z	=	points[j].Get_z();
		}
    	popen_ws( CURVE_WS, (void *)NULL, phigs_ws_type_x_tool );

    	/* Assign the control-point list. */

    	cpts.num_points = 6;
    	cpts.points.point3d = control_points;

    	/* Use markers to show the control points. */

    	markers.num_points = 6;
    	markers.points = control_points;

    	popen_struct( SPLINE_ID );

    	/* Third order curve. */
    	order = 3;
    	knots.floats = knots_3ord;
    	knots.num_floats = cpts.num_points + order;
    	min = knots_3ord[order-1];
    	max = knots_3ord[knots.num_floats - order];
    	for ( i = 0; i < 6; i++ ) /* shift it down a bit */
        	control_points[i].y -= 0.3;
    	pnuni_bsp_curv( order, &knots, PNON_RATIONAL, &cpts, min, max );
    	ppolymarker3( &markers );
		pclose_struct();
    	pupd_ws( CURVE_WS, PFLAG_PERFORM );

		//	Closing the work station at OK callback

        XtFree(xval);
        XtFree(yval);
        XtFree(zval);

}
/*******************************************************************************
*
*       NAME            :make_spl_data_box()
*
*       DESCRIPTION     :
*
******************************************************************************/


void
make_spl_data_box(Widget widget,XtPointer client_data,XtPointer call_data)
{
        Widget a=(Widget)client_data;   // shell to destroy data_entry table

        char *blkid  = XmTextGetString(block_id);

        char *xmin  = XmTextGetString(x_min);
        char *xmax  = XmTextGetString(x_max);
        char *xmid  = XmTextGetString(x_mid);
        char *xlen  = XmTextGetString(x_len);

        char *ymin  = XmTextGetString(y_min);
        char *ymax  = XmTextGetString(y_max);
        char *ymid  = XmTextGetString(y_mid);
        char *ylen  = XmTextGetString(y_len);

        char *zmin  = XmTextGetString(z_min);
        char *zmax  = XmTextGetString(z_max);
        char *zmid  = XmTextGetString(z_mid);
        char *zlen  = XmTextGetString(z_len);

		/*
		**		Following are the absolute coordinates
		**		Need to parametrize the input to 0-1 scale
		**		so (x -Xmin)/Xlen
		*/

		/*
        float xmn = atof(xmin);
        float xmx = atof(xmax);
        float xmd = atof(xmid);
        float xln = atof(xlen);

        float ymn = atof(ymin);
        float ymx = atof(ymax);
        float ymd = atof(ymid);
        float yln = atof(ylen);

        float zmn = atof(zmin);
        float zmx = atof(zmax);
        float zmd = atof(zmid);
        float zln = atof(zlen);

		*/

        float xmn = 0.0;
        float xmx = 1.0;
        float xmd = 0.5;
        float xln = 1.0;

        float ymn = 0.0;
        float ymx =	1.0;
        float ymd = 0.5;
        float yln = 1.0;

        float zmn = 0.0;
        float zmx = 1.0;
        float zmd = 0.5;
        float zln =	1.0;


		float xinc=	xln/5;
		float yinc=	yln/5;
		float zinc=	zln/5;


		/*
		**		we will make data entry table now
		*/

        Widget data_shell ;     
        data_shell = XmCreateDialogShell(toplevel,"Spline Data Input",NULL,0);

        Widget data_rc ;       
        data_rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,data_shell,
                        XmNorientation, XmVERTICAL,
                        XmNwidth,      500,
                        NULL);



        /*------------------------------------------------------------------*/


        Widget  form_title ;        // contains name of dialog box

        form_title = XtVaCreateManagedWidget("title",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               500,
                NULL);

        Widget  fram ;          // gives itched border to widget

        fram = XtVaCreateManagedWidget("fram",
                xmFrameWidgetClass,     form_title,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_FORM,
                XmNrightAttachment,     XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);


        Widget  nam ;           // label widget with name

		char axis[6];

		switch(cyl_axis){

			case XAXIS:

					strcpy(axis,"XAXIS");
					break;

			case YAXIS:

					strcpy(axis,"YAXIS");
					break;

			case ZAXIS:

					strcpy(axis,"ZAXIS");
					break;

			default:

					strcpy(axis,"WRONG AXIS");
					break;

		}

		char heading[72];
		sprintf(heading,"  Spline Data    Order = 3  and Axis = %s", axis);
        nam = XtVaCreateManagedWidget(heading,
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);

        /*------------------------------------------------------------------*/


        Widget  form_pts ;     // form manager

        form_pts = XtVaCreateManagedWidget("minimum",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               500,
                XmNfractionBase,        7,
                NULL);


        Widget  label_pts ;        // label before text widget
        Widget  label_min ;        // label before text widget
        Widget  label_max ;        // label before text widget
		Widget	label_num[4];

        label_pts = XtVaCreateManagedWidget("POINTS ",
                xmLabelGadgetClass,     form_pts,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       1,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

        label_min = XtVaCreateManagedWidget(" MIN ",
                xmLabelGadgetClass,     form_pts,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        1,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

        label_max = XtVaCreateManagedWidget(" MAX(6) ",
                xmLabelGadgetClass,     form_pts,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        6,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       7,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

		char pt_num[6];

		for(int n =0;n<4;n++){

			sprintf(pt_num," %d ",n+2);

        	label_num[n] = XtVaCreateManagedWidget(pt_num,
                xmLabelGadgetClass,     form_pts,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        n+2,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       n+3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);


		}

		Widget formX,labelX;
		Widget formY,labelY;
		Widget formZ,labelZ;

        formX = XtVaCreateManagedWidget("Xform",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               500,
                XmNfractionBase,        7,
                NULL);


        labelX = XtVaCreateManagedWidget(" X ",
                xmLabelGadgetClass,     formX,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       1,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);


        formY = XtVaCreateManagedWidget("Yform",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               500,
                XmNfractionBase,        7,
                NULL);


        labelY = XtVaCreateManagedWidget(" Y ",
                xmLabelGadgetClass,     formY,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       1,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

        formZ = XtVaCreateManagedWidget("Zform",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               500,
                XmNfractionBase,        7,
                NULL);


        labelZ = XtVaCreateManagedWidget(" Z ",
                xmLabelGadgetClass,     formZ,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       1,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);

		char val[10];					//	default values
		int m;
		float tmp;

		switch(cyl_axis){			//	though misnomer I am using this Global

			case XAXIS:

				//	Assume curve to be on Yaxis i.e U direction

			for(m=0;m<6;m++){
				
				sprintf(val,"%3.2f",xmd);

        		spl_x[m]= XtVaCreateManagedWidget(" X",
                	xmTextWidgetClass,      formX,
                	XmNtraversalOn,         true,
                	XmNleftAttachment,      XmATTACH_POSITION,
                	XmNleftPosition,        m+1,
                	XmNrightAttachment,     XmATTACH_POSITION,
                	XmNrightPosition,       m+2,
                	XmNtopAttachment,       XmATTACH_FORM,
                	XmNbottomAttachment,    XmATTACH_FORM,
                	XmNvalue,               val,
                	NULL);


                tmp = ymn + yinc*m;

                sprintf(val,"%5.2f",tmp);

                spl_y[m]= XtVaCreateManagedWidget(" Y",
                    xmTextWidgetClass,      formY,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);

                sprintf(val,"%3.2f",zmx);

                spl_z[m]= XtVaCreateManagedWidget(" Z",
                    xmTextWidgetClass,      formZ,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);

			}

			break;

            case YAXIS:

                //  Assume curve to be on Zaxis i.e U direction

            for(m=0;m<6;m++){
                
                sprintf(val,"%3.2f",xmx);

                spl_x[m]= XtVaCreateManagedWidget(" X",
                    xmTextWidgetClass,      formX,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);


                sprintf(val,"%3.2f",ymd);

                spl_y[m]= XtVaCreateManagedWidget(" Y",
                    xmTextWidgetClass,      formY,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);
				
				tmp = zmn + zinc*m;

                sprintf(val,"%3.2f",tmp);

                spl_z[m]= XtVaCreateManagedWidget(" Z",
                    xmTextWidgetClass,      formZ,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);

            }

            break;

            case ZAXIS:

                //  Assume curve to be on Xaxis i.e U direction

            for(m=0;m<6;m++){
                
				tmp = xmn + xinc*m;

                sprintf(val,"%5.2f",tmp);

                spl_x[m]= XtVaCreateManagedWidget(" X",
                    xmTextWidgetClass,      formX,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);


                sprintf(val,"%3.2f",ymx);

                spl_y[m]= XtVaCreateManagedWidget(" Y",
                    xmTextWidgetClass,      formY,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);

                sprintf(val,"%3.2f",zmd);

                spl_z[m]= XtVaCreateManagedWidget(" Z",
                    xmTextWidgetClass,      formZ,
                    XmNtraversalOn,         true,
                    XmNleftAttachment,      XmATTACH_POSITION,
                    XmNleftPosition,        m+1,
                    XmNrightAttachment,     XmATTACH_POSITION,
                    XmNrightPosition,       m+2,
                    XmNtopAttachment,       XmATTACH_FORM,
                    XmNbottomAttachment,    XmATTACH_FORM,
                    XmNvalue,               val,
                    NULL);

            }

            break;

			default:

				post_msg("Wrong Axis choice");
				break;

		}
        Widget sep1;

        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass,         data_rc,
                NULL);


        /*----------Control Area buttons -----------------------------------*/

        Widget  form_ok;

        form_ok = XtVaCreateManagedWidget("control",
                xmFormWidgetClass,      data_rc,
                XmNheight,              30,
                XmNwidth,               500,
                XmNfractionBase,        8,
                NULL);

        Widget ok,can,apply;

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
                (XtCallbackProc)addspl_data_ok,
                (XtPointer)data_shell);

        apply = XtVaCreateManagedWidget("  APPLY ",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightPosition,       5,
                XmNalignment,           XmALIGNMENT_END,
                NULL);

        XtAddCallback(apply,XmNactivateCallback,
                (XtCallbackProc)addspl_data_apply,
                (XtPointer)data_shell);


        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        6,
                XmNrightPosition,       8,
                NULL);

        XtAddCallback(can,XmNactivateCallback,
                (XtCallbackProc)data_entry_can,
                (XtPointer)data_shell);

        XtManageChild(data_rc);
        XtManageChild(data_shell);

        XtFree(xmin);
        XtFree(xmax);
        XtFree(xmid);
        XtFree(xlen);

        XtFree(ymin);
        XtFree(ymax);
        XtFree(ymid);
        XtFree(ylen);

        XtFree(zmin);
        XtFree(zmax);
        XtFree(zmid);
        XtFree(zlen);

        XtFree(blkid);
        XtPopdown(a);                   // popdown the Data Entry table

}

