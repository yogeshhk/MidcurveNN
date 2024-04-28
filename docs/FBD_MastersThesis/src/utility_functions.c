/*******************************************************************************
*       FILENAME :      utility_functions.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Common Bridge functions between Interface,App,Graphics
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
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/


void print_msg(char text[],float value)
{

	char msg[200];

	if(value==NO_VALUE){
	
		sprintf(msg,"%s",text);
                XtVaSetValues (lab,
                        XmNvalue,       msg,
                        NULL);
	}
	else{
		
		sprintf(msg,"%s = %3.2f",text,value);
                XtVaSetValues (lab,
                        XmNvalue,       msg,
                        NULL);

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


Widget PostDialog(Widget parent,int dialog_type,char *msg)
{
    Widget dialog;
    XmString text;

    dialog = XmCreateMessageDialog(parent, "dialog", NULL, 0);
    text = XmStringCreateLtoR(msg, XmSTRING_DEFAULT_CHARSET);
    XtVaSetValues(dialog,
        XmNdialogType,    dialog_type,
        XmNmessageString, text,
        NULL);
    XmStringFree(text);
    XtUnmanageChild(
        XmMessageBoxGetChild(dialog, XmDIALOG_CANCEL_BUTTON));
    XtSetSensitive(
        XmMessageBoxGetChild(dialog, XmDIALOG_HELP_BUTTON), False);
    XtAddCallback(dialog, XmNokCallback,  temp_action, XtParent(dialog));
    XtManageChild(dialog);
    return dialog;

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

void post_msg(char *prompt)
{
        char msg[200];
        int dialog_type;

        dialog_type=XmDIALOG_ERROR;

        sprintf(msg,"%s",prompt);

        Widget post = PostDialog(main_w,dialog_type,msg);


        XmStringFree((unsigned char *)prompt);

}

/********************************************************************************
*
*       NAME    :       void
*                       temp_action(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   for destroying the widget which calls this function
*                       this function is for temporay use,just to popdown 
*
*******************************************************************************/
 
void temp_action(Widget widget, XtPointer button, XtPointer call_data)
{
  	XtPopdown((Widget)button);
}
/*******************************************************************************
*
*       NAME            :Write_in_Data_table()
*
*       DESCRIPTION     :This function will check the global values of planes
*			 and write the in Data_table
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 
void Write_in_Data_table()
{

	if( x_minf != NO_VALUE){

                        char xnc[10];
                        sprintf(xnc,"%5.2f",x_minf);    // put value identfy
 
                        XtVaSetValues (x_min,
                                XmNvalue,          xnc,
                                XmNeditable,       False,// Locking
                                NULL);

	}

 
        if( x_midf != NO_VALUE){
 
                        char xdc[10];
                        sprintf(xdc,"%5.2f",x_midf);    // put value identfy
 
                        XtVaSetValues (x_mid,
                                XmNvalue,          xdc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
        if( x_maxf != NO_VALUE){
 
                        char xxc[10];
                        sprintf(xxc,"%5.2f",x_maxf);    // put value identfy
 
                        XtVaSetValues (x_max,
                                XmNvalue,          xxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
        if( x_lenf != NO_VALUE){
 
                        char xlc[10];
                        sprintf(xlc,"%5.2f",x_lenf);    // put value identfy
 
                        XtVaSetValues (x_len,
                                XmNvalue,          xlc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 


        if( y_minf != NO_VALUE){
 
                        char ync[10];
                        sprintf(ync,"%5.2f",y_minf);    // put value identfy
 
                        XtVaSetValues (y_min,
                                XmNvalue,          ync,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
 
        if( y_midf != NO_VALUE){
 
                        char ydc[10];
                        sprintf(ydc,"%5.2f",y_midf);    // put value identfy
 
                        XtVaSetValues (y_mid,
                                XmNvalue,          ydc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
        if( y_maxf != NO_VALUE){
 
                        char yxc[10];
                        sprintf(yxc,"%5.2f",y_maxf);    // put value identfy
 
                        XtVaSetValues (y_max,
                                XmNvalue,          yxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
        if( y_lenf != NO_VALUE){
 
                        char ylc[10];
                        sprintf(ylc,"%5.2f",y_lenf);    // put value identfy
 
                        XtVaSetValues (y_len,
                                XmNvalue,          ylc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }


        if( z_minf != NO_VALUE){
 
                        char znc[10];
                        sprintf(znc,"%5.2f",z_minf);    // put value identfy
 
                        XtVaSetValues (z_min,
                                XmNvalue,          znc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
 
        if( z_midf != NO_VALUE){
 
                        char zdc[10];
                        sprintf(zdc,"%5.2f",z_midf);    // put value identfy
 
                        XtVaSetValues (z_mid,
                                XmNvalue,          zdc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
        if( z_maxf != NO_VALUE){
 
                        char zxc[10];
                        sprintf(zxc,"%5.2f",z_maxf);    // put value identfy
 
                        XtVaSetValues (z_max,
                                XmNvalue,          zxc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }
 
        if( z_lenf != NO_VALUE){
 
                        char zlc[10];
                        sprintf(zlc,"%5.2f",z_lenf);    // put value identfy
 
                        XtVaSetValues (z_len,
                                XmNvalue,          zlc,
                                XmNeditable,       False,// Locking
                                NULL);
 
        }





} 

/*******************************************************************************
*
*
*       NAME    :       void
*                       print_graph()
*
*
*       DESCRIPTION : Mainly used for debugging purpose.Prints ( on screen)
*		      Node_list in the graph of current component and
*		      members of those nodes.  
*
*******************************************************************************/
 
void print_graph()
{


	printf("**************************************************\n");

	Graph *gr = currc->Get_comp_graph();

	Node *see = gr->Get_graph_node();

	while(see != NULL){

		printf("Node Id = %d\n",see->Get_node_id());
		printf("\tNodes attached are\n");

		Node *tra = see->Get_node_list();

		while(tra){

			printf("\tNode num.\t%d\n",tra->Get_node_id());
			tra = tra->Get_nextnl();
		}


                Arc *ra = see->Get_arc_list();
 
                while(ra){
 
                        printf("\tArc name.\t%s\n",ra->Get_arc_name());
                        ra = ra->Get_nextal();
                }
 

		
		see = see->Get_nextn();
		printf("\n");
	}

	printf("**************************************************\n");
}
