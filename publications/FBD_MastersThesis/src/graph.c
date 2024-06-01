/*******************************************************************************
*       FILENAME :      graph.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Graph
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
*       NAME            :Graph..... Constructor
*
*       DESCRIPTION     :
*
*       INPUT           : 
*
*       OUTPUT          :
*
*******************************************************************************/
 
Graph::Graph(){

}

/*******************************************************************************
*
*       NAME            :Link_Node(Node *nl)
*
*       DESCRIPTION     : Adds the to the link list of nodes connected to this
*                         node and sets pointer to first node (graph_node)
*                         This new node is added at the tail
*
*       INPUT           : Newly created Block
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void Graph::Link_Node( Node *nl)
{
 
        printf("Came to linking of the Node list in Graph\n");
 
        if(graph_node == NULL){
 
                graph_node = nl;                // first node in the list
                graph_node->Set_nextn((Node *)NULL);
        }
        else{
                Node *tracer = graph_node;      // starts at first node
 
                while( tracer->Get_nextn() != NULL){
                        tracer = tracer->Get_nextn();
                }
 
                tracer->Set_nextn(nl);
                tracer = tracer->Get_nextn();
                tracer = nl;
                nl->Set_nextn((Node *)NULL);
 
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

Node* Graph::Get_node(int ii){
 
 
        Node* currn;
 
        currn = graph_node;
 
        while (currn != NULL) {
 
               if (currn->Get_node_id() == ii) break ;
 
               else
                   currn = currn->Get_nextn() ;
        }
        if (currn == NULL) {
 
                return (Node*)NULL;
        }
        else  return (currn) ;
 
}

