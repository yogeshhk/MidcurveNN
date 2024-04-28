/*******************************************************************************
*       FILENAME :      node.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Node
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
*       NAME            :Node..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets the block
*			 Sets private members properly
*
*       INPUT           : Block *bn
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
 
Node::Node(Block *nb)
{

	node_id		= nb->Get_block_id();	// block_id is same as node id 
	node_list 	= NULL;					// yet to form node list of this node
	//Link_to_Nodelist(this);			// making list of nodes conncted to this


	nextn 		= NULL;
	nextqn 		= NULL;
	nextnl 		= NULL;
	arc_list 	= NULL ;
	arc_count 	= 0 ;					// not any arc is attached yet

	// following flags are for editing 
	// They should be initialized to proper value
	// before start of the editing


	Initialize_flags(FALSE);

	printf("Came to node constructor no.%d \n",node_id);

}

/*******************************************************************************
*
*       NAME            :Initialize_flags
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
*******************************************************************************/
 
void Node::Initialize_flags(int boo)
{

 
        available       = boo;
        visited         = boo;
        resolved        = boo;
        modify          = boo;

	Num		= boo; 
	Low		= boo;

}
/*******************************************************************************
*
*       NAME            :FeatureNode..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets the block
*                        Sets private members properly
*
*       INPUT           : Block *bn
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
 
FeatureNode::FeatureNode(Block *nb):Node(nb)
{
 
        node_block = nb;                // setting block in this node
 
        printf("Came to Featurenode constructor no.%d \n",node_id);
 
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
 
void Node::Link_to_Nodelist( Node *nl)
{
 
        if( node_list == NULL){
 
                node_list = nl;                // first node in the list
                nl->Set_nextnl((Node *)NULL);
        }
        else{
                Node *tracer = node_list ;	// starts at first node
 
                while( tracer->Get_nextnl() != NULL){
                        tracer = tracer->Get_nextnl();
                }

				tracer->Set_nextnl(nl);
                tracer = tracer->Get_nextnl();
				tracer = nl;
                nl->Set_nextnl((Node *)NULL);

        printf("Linking the Node list of%d by %d\n",node_id,nl->Get_node_id());
 
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
 
void Node::Link_to_Arclist( Arc *arc)
{
 
	arc_count++;		// incrementing the number of arcs attached
				// to this node

        if( arc_list == NULL){
 
                arc_list = arc;                // first arc in the list
                arc_list->Set_nextal((Arc *)NULL);
        }
        else{
                Arc *tracer = arc_list ;      // starts at first arc
 
                while( tracer->Get_nextal() != NULL){
                        tracer = tracer->Get_nextal();
                }
 
                tracer->Set_nextal(arc);
                tracer = tracer->Get_nextal();
                tracer = arc;
                arc->Set_nextal((Arc *)NULL);
 
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

CycleNode::CycleNode(Node* nn){

	cyl_node_id 	= nn->Get_node_id();    	// StrongCompNode id
    cyl_node		= NULL;       				// actual node
    cyl_arc_list	= NULL;   					// arc list associted with this
    nextcyln		= NULL;       				// next strongcompnode in cycle
    nextcn			= NULL;         			// next strcompnode horizontally
    cyl_node_list	= NULL;  					// list of str_nodes associated
 

	
}

 
