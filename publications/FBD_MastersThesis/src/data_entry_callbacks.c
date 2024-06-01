/*******************************************************************************
*       FILENAME :      data_entry_callbacks.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from data_entry Table
*
*       FUNCTIONS   :   
*			data_entry_ok()
*			data_entry_can()
*			compid_data_cb()
*			blkid_data_cb()
*			addblk_data_ok()
*			addblk_data_can()
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 4, 1995.
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
*       NAME            :data_entry_ok()
*
*       DESCRIPTION     :Called when OK is pressed in DataEntry Table
*			 Collectes all the values from all widgets and
*			 calls the component constructor with these values
*
******************************************************************************/
 
void    data_entry_ok(Widget widget,XtPointer client_data,XtPointer call_data)
{


        Widget a=(Widget)client_data;   // shell to destroy data_entry table
 
        char *compid = XmTextGetString(comp_id);
        char *blkid  = XmTextGetString(block_id);
 
        char *xmin  = XmTextGetString(x_min);
        char *xmax  = XmTextGetString(x_max);
 
        char *ymin  = XmTextGetString(y_min);
        char *ymax  = XmTextGetString(y_max);
 
        char *zmin  = XmTextGetString(z_min);
        char *zmax  = XmTextGetString(z_max);
 
        /* Converting them to values */

				// compid is taken as string 
 
        float xmn = atof(xmin);
        float xmx = atof(xmax);
 
        float ymn = atof(ymin);
        float ymx = atof(ymax);
 
        float zmn = atof(zmin);
        float zmx = atof(zmax);
 
        /* Free the memory for the characters */

				// compid is reqd in constructor thus not freed 
        XtFree(xmin);
        XtFree(xmax);
 
        XtFree(ymin);
        XtFree(ymax);
 
        XtFree(zmin);
        XtFree(zmax);
 

	printf("compid %s blkid %s\n",compid,blkid);
	printf("%f %f\n",xmn,xmx);
	printf("%f %f\n",ymn,ymx);
	printf("%f %f\n",zmn,zmx);


	Component *newcomp ;

	newcomp = new Component(compid,blkid ,xmn, xmx, ymn, ymx, zmn, zmx);

	Link_Comp(newcomp);		// Links newcomp to comp_link_list

	comp_flag = OLD_COMP;		// component creattion complete

	comp_num  = maxc ;		// currently named component
	//blk_num   = blk ;		// currently named block
	

	newcomp->Display_by_phigs(WIREFRAME);

	comp_num++;			// sets incremented value for next comp

                                        // data_flags are initialized

        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;	// X-Data flags   
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;	// Y-Data flags   
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;	// Z-Data flags   
 
 
        XtFree(compid);			// now we can free comp_id
        XtFree(blkid);			// now we can free blk_id

        XtPopdown(a);                  	// popdown the Data Entry table

}

/*******************************************************************************
*
*       NAME            :data_entry_can()
*
*       DESCRIPTION     :Called when CANCEL is selected at Data Entry Table
*
******************************************************************************/
 
void    data_entry_can(Widget widget,XtPointer client_data,XtPointer call_data)
{
        Widget a=(Widget)client_data;   // shell to destroy data_entry table


					// flags are initialized again
	menu_flag = NO_MENU ;
	comp_flag = NO_COMP ;
	block_flag = NO_BLOCK ; 

	comp_num--;			// reducing by one from current value

					// data_flags are initialized

        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;  // X-Data flags   
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;  // Y-Data flags   
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;  // Z-Data flags   
 


        XtPopdown(a);                   // popdown the Data Entry table
 
}
 
/*******************************************************************************
*
*       NAME    :       void
*                       compid_data_cb()
*
*
*       DESCRIPTION :   Reads the value
*
*******************************************************************************/
 
void compid_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

}

/*******************************************************************************
*
*       NAME    :       void
*                       blkid_data_cb()
*
*
*       DESCRIPTION :   Reads the value
*
*******************************************************************************/
 
void blkid_data_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{
 
}


/*******************************************************************************
*
*       NAME            :addblk_data_ok()
*
*       DESCRIPTION     :Called when CANCEL is selected at ADD_Blk_Data Table
*
******************************************************************************/
 
void addblk_data_ok(Widget widget,XtPointer client_data,XtPointer call_data)
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
 
        /* Converting them to values */
 
                                // compid is taken as string
 
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
 
        /* Free the memory for the characters */
 
                                // compid is reqd in constructor thus not freed
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
 

        printf("blkid %s\n",blkid);
        printf("%f %f\n",xmn,xmx);
        printf("%f %f\n",ymn,ymx);
        printf("%f %f\n",zmn,zmx);


	/* Now actual Instanciation will start */

	
      	Block *nb;

	/*
	**		block_flag	is global variable which is already set to the
	**		type just chosen
	**		So depeding on it constructor of block is called.
	**		FOR ANY SHAPE at first block constructor is called as the
	**		encapsulation. The info specific to that shape is either
	**		derived or can be extracted from global variables and
	**		set to proper member variables in the constructor of that
	**		shape
	*/

	int	ax;
	int	p1;
	int	p2;

	switch(block_flag){

		case BLOC :
        		nb = new Block(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx);
				break;

		case SBLOC :

        		nb = new SubBlock(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx);
				break;

		case CYLINDR :

			
        		nb =new Cylinder(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx);
				break;

		case SCYLINDR :

        	    nb=new SubCylinder(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx);
				break;

		case WEDGE	:

				ax	=	wedge_axis;				//	Global
				p1	=	wedge_planes[0];		//	Global
				p2	=	wedge_planes[1];		//	Global
				nb= new Wedge(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx,ax,p1,p2);
				break;

		case SWEDGE	:

                ax  =   wedge_axis;         	//  Global
                p1  =   wedge_planes[0];        //  Global
                p2  =   wedge_planes[1];        //  Global
                nb= new SubWedge(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx,ax,p1,p2);
                break;

		case BSPLINE :


				break;
		default	:		// By default it will create BLOCK

        		nb = new Block(blkid,currc,xmn,xmx,ymn,ymx,zmn,zmx);
			break;

	}

	int newblk_id	= nb->Get_block_id();

        currc->Link_Blocks(nb);        // links the block to link lists and sets
                                // comp_block pointer to the first block
 

	
        Node *nn = new FeatureNode(nb);		// New node
		nb->Set_block_node(nn);			// set block in that node
        currc->Get_comp_graph()->Link_Node(nn); // link it to the graph
 

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

 
	//print_graph();	// debugging

	/*
		After doing everything do the following
	*/
 
                                        // flags are initialized again
        menu_flag       = NO_MENU ;
 
                                        // data_flags are initialized
 
        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;  // X-Data flags
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;  // Y-Data flags
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;  // Z-Data flags
 
        make_Topo_info_null();          // No topo_info         (application.c)
        make_temp_planes_null();        // No planes selection  (application.c)
 
        XtFree(blkid);
        XtPopdown(a);                   // popdown the Data Entry table
 
}

/*******************************************************************************
*
*       NAME            :addblk_data_can()
*
*       DESCRIPTION     :Called when CANCEL is selected at ADD_Blk_Data Table
*
******************************************************************************/
 
void addblk_data_can(Widget widget,XtPointer client_data,XtPointer call_data)
{
        Widget a=(Widget)client_data;   // shell to destroy data_entry table
 
 
                                        // flags are initialized again
        menu_flag 	= NO_MENU ;
 
                                        // data_flags are initialized
 
        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;  // X-Data flags
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;  // Y-Data flags
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;  // Z-Data flags
 
        make_Topo_info_null();          // No topo_info         (application.c)
        make_temp_planes_null();        // No planes selection  (application.c)
 
        XtPopdown(a);                   // popdown the Data Entry table
 
}
 

