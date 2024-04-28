/*******************************************************************************
*       FILENAME :      strongcompnode.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class StrongCompNode
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   MAY 29, 1995.
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

StrongCompNode::StrongCompNode(Node* nn,int id){

	str_node_id 	= id ;
	str_node		= nn;
	str_arc_list	= NULL;
	nextstrn		= NULL;
	nextsn			= NULL;
	str_node_list	= NULL;
	available		= TRUE;				// for cycle detection algo
										// all nodes sould be available at start
	B	= new Stack<StrongCompNode>();	// for UNMARK algo in book
}

 
/*******************************************************************************
*
*       NAME            :Link_to_Nodelist(Node *nl)
*
*       DESCRIPTION     : Adds the to the link list of nodes connected to this
*                         node and sets pointer to first node (node_list)
*                         This new node is added at the tail
*
*       INPUT           : Newly created Node
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void StrongCompNode::Link_to_Nodelist( StrongCompNode *nl)
{
 
        if( str_node_list == NULL){
 
                str_node_list = nl;                // first node in the list
                nl->Set_nextsn((StrongCompNode *)NULL);
        }
        else{
                StrongCompNode *tracer = str_node_list ; 
 
                while( tracer->Get_nextsn() != NULL){
                        tracer = tracer->Get_nextsn();
                }
 
                tracer->Set_nextsn(nl);
                tracer = tracer->Get_nextsn();
                tracer = nl;
                nl->Set_nextsn((StrongCompNode *)NULL);
 
        printf("Linking Node list of%d by %d\n",str_node_id,nl->Get_node_id());
 
        }
}

/*******************************************************************************
*
*       NAME            :Link_to_Arclist(Arc *arc)
*
*       DESCRIPTION     : Adds the to the link list of arcs connected to this
*                         node and sets pointer to first arc ( *arc_list)
*                         This new arc is added at the tail
*
*       INPUT           : Newly created Arc
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void StrongCompNode::Link_to_Arclist( StrArc *arc)
{
 
        arc_count++;            // incrementing the number of arcs attached
                                // to this node
 
        if( str_arc_list == NULL){
 
                str_arc_list = arc;                // first arc in the list
                str_arc_list->Set_nextsal((StrArc *)NULL);
        }
        else{
                StrArc *tracer = str_arc_list ;      // starts at first arc
 
                while( tracer->Get_nextsal() != NULL){
                        tracer = tracer->Get_nextsal();
                }
 
                tracer->Set_nextsal(arc);
                tracer = tracer->Get_nextsal();
                tracer = arc;
                arc->Set_nextsal((StrArc *)NULL);
 
        }
}

 
