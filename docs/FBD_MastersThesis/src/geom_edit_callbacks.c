/*******************************************************************************
*       FILENAME :      geom_edit_callbacks.c DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the callbacks from edit_len_selection Table
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
 
/*****************************************************************************
*
*       NAME    :       geom_edit_ok()
*
*       DESCRIPTION :   Called when OK is pressed in Geom_Edit widget
*			A very imp decision is now being taken(Sept 29,7.30pm)
*			I will change this algo because of so called Motif
*			limitaion ( or may be my fault to understand it)
*			Steps: 	Ask for lenth ..upto ..new Queues. will remain
*			First Cycles will get detected.. and processed..Q
*			may get built in the process.AFter selecting the proper
*			cycle..OK->Traverse the cycle..and then Go to Qs for
*			Resolving adjacent Nodes..As any way.. Cycles will be 
*			There because of Undirected Graph Nature..
*			Wish All the Best !!!
*
******************************************************************************/
 
void geom_edit_ok(Widget widget, XtPointer client_data, XtPointer call_data)
{
        Widget i = (Widget)client_data;
 
	FILE *fo;

	fo = fopen("edit","w");

	currc->Write_to_file(fo);

	fclose(fo);


	editc = new Component;	// editc is a global comp for storing the copy

	editc->Copy_for_Edit(currc);	// editc is now copy of currc
					// editc contains only list of 
					// blocks and nothing else so
					// can not be used for retrieving back
					// for that Read_from_file("edit")

	int done = 1;

	// now we have folowing information avaialble from gobal variables

	// block to be edited 		: blk_num
	// length to be modified	: len_axis
	// constrain plane		: constrn_pln
	// new_length			: value from widget edit_length

        char *nl = XmTextGetString(edit_length);
        float newl = atof(nl);
        XtFree(nl);
 
	int blkid = blk_num ;
	int len   = len_axis ;
	int con   = constrn_pln ;

	Block *eb = currc->Get_block(blkid);

	int ask = Ask_Length(blkid,len,newl);

	if( ask == FAILURE){

		print_msg("No change in length, thus ABORTING !!!",NO_VALUE);

		Abort_editing();	// restores original component
		
		done = 0  ;		// avoide the further procesing
	}

	while( done ){			// i.e. Ask_Length() was successful

		Init_edit_flags(currc);	// in application.c

		// Now instantiate the global queues

		Xlen_Q 		= new NodeQueue(X_Q);	
		Ylen_Q 		= new NodeQueue(Y_Q);
		Zlen_Q 		= new NodeQueue(Z_Q);
		Link_len_Q 	= new NodeQueue(L_Q);


		int modf = Modify_Length(blkid,len,con,newl);	// in editing.c

		Add_to_edit_Q(len,eb);	// add to the editing Q of type len
		

					// CYCLE EDITING //

		Cycle* cyl;	// first cycle in the list
		Graph* gra;	// Original graph

		gra = currc->Get_comp_graph();

		// Right now I am finding Cycles taking root as edited Node only
		// But actually we need to find cycles for all the base nodes
		// that come in different Qs.

		// It is safe to assume that every node in the graph will some
		// time or other will go to the Q and so it will be possible
		// to find cycles for all nodes here only and the after
		// processing present them to the user

		Node* edited_node = gra->Get_node(blkid);

		cyl = Find_Cycles( edited_node ,gra);
				

		// This cyl is actually "firstcyl" which is declared global
		// I am returnig the pointer to the first cycle (though not
		// needed) because there may be cases where you may reuire
		// firstcycle locally


		// Here processing of the cycles will be done 
		// In processing all the cyccles with Path 2 (ie only 2 members)
		// will be deleted

		// Duplicate Cycles will also be deleted
		// So after processing the list that will be attached to 
		// firstcyl will be of unique cycles


		// If nothing remains in the list then don't present the
		// Create_Cycle_Selection_box() but just the notice box saying
		// that NO Uniquiee cycles and Press ok to proceed
		// OK will  go to Select_Cycle_callback..

		Process_Cycles();

		Remove_duplicate_cycles();

		Create_Cycle_Selection_box();	// You dont have to pass cyl
						// as it is globally available
						// cyl is nothing but firstcycle



		done = 0 ;	// at last done is complete now

	}

	XtPopdown(i); 
 
}
/*****************************************************************************
*
*       NAME    :       geom_edit_can()
*
*       DESCRIPTION :   Called when CANCEL is pressed in Geom_Edit widget
*
*
******************************************************************************/
 
void geom_edit_can(Widget widget, XtPointer client_data, XtPointer call_data)
{
        Widget i = (Widget)client_data;
 
	Abort_editing();	// restores component from file - edit

	print_msg("Because of CANCEL original comp has been restored",NO_VALUE);


        XtPopdown(i); 
 
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
 
void select_cycle_ok(Widget widget, XtPointer client_data, XtPointer call_data){

        Widget i = (Widget)client_data;

        char *nl = XmTextGetString(modf_node);
        int bid  = atoi(nl);		// Id of the Modification Node
        XtFree(nl);

	// cycle_num is global variable in which cycle_id is stored
	// blk_num is global variable in which edited_node_id is stored
	// Now we have to Get the actual Cycle first
	// See the members. Get the respective Nodes from the Graph
	// Go to graph again and and get Topolink between them.
	// Pass this info to Resolve() and then ADD this node to the Qs
	// This traversal should be done form Edited node to modif_node in
	// both direction

	if(cycle_num != NO_VALUE){ 

		Cycle *currcyl = Get_Cycle(cycle_num);

		if(currcyl == NULL){ 
				
			printf("NO Cycles selected\n");
			return;
		}

		// we will check whether what we got as Modf_node is member of
		// the currcyle or not

		if(currcyl->Is_member(bid) == FALSE){

			printf("Selection of Modf_node is wrong\n");
			return;
		}

		Graph* currg = currc->Get_comp_graph();

		Node* root = currg->Get_node(blk_num);
		Node* modf = currg->Get_node(bid);
	
		modf->Set_modify(TRUE);

	// Now I will traverse in two directuions CLOCKWISE from root to modf
	// and then anticlockwise from modf to root( ie taking left..

		int tra_rt = blk_num ;	// traveler to the right till modf(bid)
		int tra_lt = blk_num ;	// traveler to the right till modf(bid)
		int axis = len_axis; 	// len_axis is global

		currcyl->print_member_ids();

		printf("Is edited node = %d and Modf Noed = %d \n",blk_num,bid);

		while( currcyl->Get_right_member_id(tra_rt) != currcyl->Get_right_member_id(bid)){

			Node* A = currg->Get_node(tra_rt);	
			tra_rt = currcyl->Get_right_member_id(tra_rt);

			Node* B = currg->Get_node(tra_rt);	

			Arc* ra = A->Get_arc_list();
			Topolink* T;

			while(ra){

				Node* BB = ra->Get_node_B();

				if(BB == B){
				
					T = ra->Get_arc_topo();
				}
			
				ra = ra->Get_nextal();
			}			
                        if((B->Get_resolved()==FALSE)||(B->Get_modify()==TRUE)){

				Resolve(A,B,T);

                		Block *blke =currc->Get_block(B->Get_node_id());

				if(B->Get_modify == FALSE){

                			blke->Update(axis); 

				}
				// the other plane values are calculated
                        	// and get fixed. len_axis is global
                		// Let other axes of node B be Unresolved
                		// Needs some more THOUGHT here..
 
                		Add_to_edit_Q(axis,blke);
                                        // here the new dimensions will be
                                        // checked and if different the node
                                        // B will be added to the Q
			} 
		}

        	while( currcyl->Get_left_member_id(tra_lt) != currcyl->Get_left_member_id(bid)){
 
 
			Node* f1 = currg->Get_node(tra_lt);	
                	tra_lt = currcyl->Get_left_member_id(tra_lt);
			Node* f2 = currg->Get_node(tra_lt);	

                        Arc* la = f1->Get_arc_list();
                        Topolink* lt;
 
			// Trying to get T* form arc_lists

                        while(la){
 
                                Node* BB = la->Get_node_B();
 
                                if(BB == f2){
 
                                        lt = la->Get_arc_topo();
                                }
 
                                la = la->Get_nextal();
                        }

                	if((f2->Get_resolved()==FALSE)||(f2->Get_modify()==TRUE)){
 
                        	Resolve(f1,f2,lt); 
                        	Block *blkl=currc->Get_block(f2->Get_node_id());

				if(f2->Get_modify == FALSE){

                        		blkl->Update(axis);
				} 

                        	// the other plane values are calculated
                        	// and get fixed. len_axis is global
                        	// Let other axes of node B be Unresolved
                        	// Needs some more THOUGHT here..
 
                        	Add_to_edit_Q(axis,blkl);
                                        // here the new dimensions will be
                                        // checked and if different the node
                                        // B will be added to the Q
 
			}


        	}

		// Now we will Update the modification node

		Block *blkr=currc->Get_block(root->Get_node_id());
		root->Set_resolved(TRUE);
		root->Set_modify(DONE);

		Block *blkm=currc->Get_block(modf->Get_node_id());
		int f_sum = blkm->Get_flags_sum(axis);
		printf("F SUM %d\n",f_sum);
		if(f_sum < 2){
 
                                print_msg("DO YO WANT TO QUIT",NO_VALUE);
                                printf("DO YO WANT TO QUIT\n");
    Widget      dialog;
    XmString    msg, yes, no;
 
    dialog      = XmCreateQuestionDialog (toplevel, "dialog", NULL, 0);
 
    yes         = XmStringCreateLocalized ("Yes");
    no          = XmStringCreateLocalized ("No");
    msg         = XmStringCreateLocalized ("Bad Modf Node  Press Yes to Abort");
 
 
    XtVaSetValues(dialog,
                XmNmessageString,       msg,
                XmNokLabelString,       yes,
                XmNcancelLabelString,   no,
                XmNdefaultButtonType,   XmDIALOG_CANCEL_BUTTON,
                NULL);
 
    XtUnmanageChild(XmMessageBoxGetChild(dialog, XmDIALOG_HELP_BUTTON));
    XtAddCallback(dialog, XmNokCallback, (XtCallbackProc)geom_edit_can,XtParent(dialog));
 
    XmStringFree(msg);
    XmStringFree(yes);
    XmStringFree(no);
 
    XtManageChild (dialog);
    XtPopup (XtParent (dialog), XtGrabNone);

 
		}

		blkm->Update(axis);
		modf->Set_modify(DONE);


	}
	int done = 1;

	while(done){

		// NEED TO TRAVERSE THE SELECTED CYCLE

                int x_num = Xlen_Q->Get_num_elements();
                int y_num = Ylen_Q->Get_num_elements();
                int z_num = Zlen_Q->Get_num_elements();
 
                while( (x_num != 0) || (y_num != 0)||(z_num != 0)){
 
                        NodeQueue* curr_Q;      // Current queue
                        int c_num;              // number of elements in Curr_Q
 
 
                        // First see which Q is not empty
                        // and assign the non_empty Q as curr_Q
 
                        if( x_num != 0){
                                        curr_Q = Xlen_Q;
                                        c_num = curr_Q->Get_num_elements();
                                        --x_num;
                                        }
 
                        if( y_num != 0){
                                        curr_Q = Ylen_Q;
                                        c_num = curr_Q->Get_num_elements();
                                        --y_num;
 
                                        }
 
                        if( z_num != 0){
                                        curr_Q = Zlen_Q;
                                        c_num = curr_Q->Get_num_elements();
                                        --z_num;
                                        }
 
 
                        while( c_num != 0){
 
                                // withdraw head from current Q
                                // and make it a Base Node
 
                                Node* basenode = curr_Q->Dequeue();
 
                                --c_num;        // decreament elements
                                                // in the current Q
 
        			int len   = len_axis ;	// global variable
 
				if(basenode){

                                	Resolve_adj_nodes(basenode,len);
                                	basenode->Set_visited(TRUE);
				}
				else{
        				XtPopdown(i);
					return;
				}
 
                        }
 
                // During the resolving operation some nodes may get
                // added to some queues So again we will have to check
                // which one is having how many nodes

                x_num = Xlen_Q->Get_num_elements();
                y_num = Ylen_Q->Get_num_elements();
                z_num = Zlen_Q->Get_num_elements();
 
                }

			done = 0;

	}
        XtPopdown(i);
 



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

void Create_Cycle_Selection_box(){

        /*
 
                some help for user in terms of message in Message box
 
        */
 
        Widget shell;   /*  Dialog Shell for this custom dialog */
 
        shell = XmCreateDialogShell(toplevel,"CYCLE SELECTION",NULL,0);
 
 
        Widget rc;      /* rc is RowColumn manager,children in vertical stack */
 
        rc = XtVaCreateWidget("row_col",xmRowColumnWidgetClass ,shell,
                        XmNorientation,         XmVERTICAL,
                        XmNwidth,               300,
                        NULL);
 
 
/*--------------------Title of the Dialog Box --------------------------------*/
 
        Widget form_title ;     // form manager for tile bar
 
        form_title = XtVaCreateManagedWidget("title",
 
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               300,
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
 
        nam = XtVaCreateManagedWidget( "Cycle_Selecion",
                xmLabelGadgetClass,     fram,
                XmNalignment,           XmALIGNMENT_CENTER,
                NULL);
 
 
/*---------------------- Headings for different fields------------------------*/
 
        Widget form_heading,blkscroll,topos,con_pln;
 
        form_heading = XtVaCreateManagedWidget("heading",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        3,
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
 
        Widget sep2;
 
        sep2 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
 
 
        Widget form_mid ;       // middle form
 
        form_mid = XtVaCreateManagedWidget("middle",
                xmFormWidgetClass,      rc,
                XmNfractionBase,        3,
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
 
        blk_list = XtVaCreateManagedWidget("Cycles",
                xmListWidgetClass,              scroll_list,
                XmNwidth,                       300,
                XmNheight,                      300,
                NULL);
 
 
 
        /*
                Here we have to present block ids of the current
                cycle.We have to make a big String consisting of
		Cycle_id and member block ids. So in fisrt char[5]
		Cycle_id is stored and blk_ids are concatenated in the
		while loop resulting in complete string called "blkid"
		 
 
        */
 
                int     n=0;
                char    blkid[100];
                Arg     args[5];
                XmString strn, str_list;
 
		int *mem = new int[20];
                int i = 1;
                if (currc == NULL)
                        return;
 
		Cycle* cy = firstcyl;

		while(cy){

			if(cy->Is_member(blk_num)){

				int cy_id = cy->Get_cycle_id();
				char c_id[5];
				sprintf(c_id,"%d",cy_id);
				strcpy(blkid,c_id);
				mem = cy->Get_member_ids();

				int j =0;
			
				while(mem[j]){

					char c_mm[15];
					sprintf(c_mm,"   %d  ,",mem[j]);
					strcat(blkid,c_mm);

					j++;
				}

                        	strn = XmStringCreateLocalized (blkid);
                        	XmListAddItem (blk_list, strn, i);
                        	XmStringFree (strn);

			}
			else{
				int cl_id = cy->Get_cycle_id();
				char cy_ids[5];
				sprintf(cy_ids,"%d",cl_id);
				strcpy(blkid,cy_ids);
				mem = cy->Get_member_ids();
                                int k =0;
 
                                while(mem[k]){
 
                                        char cl_mm[15];
                                        sprintf(cl_mm,"   %d  ,",mem[k]);
                                        strcat(blkid,cl_mm);
 
                                        k++;
                                }

				print_msg(blkid,NO_VALUE);
			}
			cy = cy->Get_nextcycle();
			i++;
		}
                XtManageChild (blk_list);
 
  XtAddCallback (blk_list, XmNdefaultActionCallback, cycle_sel_callback, NULL);
  XtAddCallback (blk_list, XmNbrowseSelectionCallback, cycle_sel_callback,NULL);
 
 
        Widget form_link;       // form manager for set of toggle buttons
 
        form_link = XtVaCreateManagedWidget("Link_Type",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               300,
                XmNfractionBase,        3,
                NULL);
 
 
 
        Widget radio_box,xaxi;
 
        radio_box = XmCreateRadioBox (form_link, "radio_box", NULL, 0);
 
        xaxi = XtVaCreateManagedWidget ("     PRESS:_If_You_dont_Want_Cycles",
                xmToggleButtonGadgetClass, radio_box, NULL);
 
        XtAddCallback(xaxi,XmNvalueChangedCallback,cyl_sel_cb,NULL);
 
 
        XtManageChild (radio_box);

        Widget sep1;
 
        sep1 =XtVaCreateManagedWidget("seperator",
                xmSeparatorGadgetClass, rc,
                NULL);
 
        Widget  form_l;             // form manager
 
        form_l = XtVaCreateManagedWidget("minimum",
                xmFormWidgetClass,      rc,
                XmNheight,              30,
                XmNwidth,               300,
                XmNfractionBase,        3,
                NULL);
 
 
        Widget  label_length;            // label before text widget
 
        label_length = XtVaCreateManagedWidget("Modification Node =",
                xmLabelGadgetClass,     form_l,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        0,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       2,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                NULL);
 
 
        modf_node = XtVaCreateManagedWidget("modification Node",
                xmTextWidgetClass,      form_l,
                XmNtraversalOn,         true,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        2,
                XmNrightAttachment,     XmATTACH_POSITION,
                XmNrightPosition,       3,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNvalue,               "1",
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
                XmNwidth,               300,
                XmNfractionBase,        5,
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
 
XtAddCallback(ok,XmNactivateCallback,select_cycle_ok,(XtPointer)shell);
 
 
        can = XtVaCreateManagedWidget("CANCEL",
                xmPushButtonWidgetClass,form_ok,
                XmNtopAttachment,       XmATTACH_FORM,
                XmNbottomAttachment,    XmATTACH_FORM,
                XmNleftAttachment,      XmATTACH_POSITION,
                XmNleftPosition,        3,
                XmNrightPosition,       5,
                NULL);
 
 
XtAddCallback(can,XmNactivateCallback,geom_edit_can,(XtPointer)shell);
XtAddCallback(can,XmNactivateCallback,temp_action,(XtPointer)shell);
 
        XtManageChild(rc);
        XtManageChild(shell);
 
 
 
 
} 

/*****************************************************************************
*
*       NAME    :       cycle_sel_callback()
*
*       DESCRIPTION :   This is called when cycle is selected from the list
*
******************************************************************************/
 
 
void
cycle_sel_callback(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
 
    char        *str;
    int s                       = (int) client_data;
    XmListCallbackStruct *cbs   = (XmListCallbackStruct *) call_data;
    XmStringGetLtoR (cbs->item, XmFONTLIST_DEFAULT_TAG, &str);
 
	char cid[5];
	
	if(str){

	sprintf(cid,"%c%c%c%c%c",str[0],str[1],str[2],str[3],str[4],str[5]);

        	int nn          = atoi(cid);    // converts string got from list
                                        // to integer
		cycle_num	= nn;	// cycle_num is the global variable

	}
	else{

		cycle_num	= NO_VALUE;
	}
}
 
 
/*****************************************************************************
*
*       NAME    :       cyle_sel_cb()
*
*       DESCRIPTION :   This is called when cycle is selected from the list
*
******************************************************************************/
 
 
void
cyl_sel_cb(Widget list_w, XtPointer client_data, XtPointer call_data)
{
 
                cycle_num       = NO_VALUE;
}
