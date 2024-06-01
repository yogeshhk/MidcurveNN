/*******************************************************************************
*       FILENAME :      componentgraph.c      DESIGN REF :  FBD(CAD/CAPP)
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
*       NAME            :ComponentGraph..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to call Node constructor etc.
*
*       INPUT           : parent component and Block to pass to first node
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
ComponentGraph::ComponentGraph(Component *gc ,Block *gb)
{
 
    graph_id    = gc->Get_component_id();   // same as parent comp_number
    graph_node  = NULL;
    Node *gn    = new FeatureNode(gb);
 
    gb->Set_block_node(gn);
    Link_Node(gn);
 
    graph_comp = gc ;

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

void ComponentGraph::PrintYourself(FILE*fp =stdout){

 
    Node *see = graph_node;
 
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
