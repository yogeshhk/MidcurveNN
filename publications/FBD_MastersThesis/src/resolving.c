/*******************************************************************************
*       FILENAME :      resolving.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Algorithms concerned with Multinode editing
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 27, 1995.
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
*       NAME            :Resolve()
*
*       DESCRIPTION     :Tries to maintain the relationship between *ba & *de
*			 defined by Topolink. It takes values of *b as reference
*			 and maps them into *d
*
*       INPUT           :Both Nodes and the topolink between them 
*
*       OUTPUT          : 
*
*******************************************************************************/
 
void Resolve(Node* ba, Node* de ,Topolink* to){

	int done = 0;	// to check the success of intermediate processes

	if( de->Get_modify() == DONE){ done = 1;}
	if( de->Get_visited() == TRUE){ done = 1;}


	// the above checking prevents a node whose modification has been
	// complete to enter into Imposing_topology procedure


	if( done == 0){


		int id1 = ba->Get_node_id();
		int id2 = de->Get_node_id();

		printf("Resolving link between %d %d \n",id1,id2);


		Block* base = Get_block(currc,id1);
		Block* dest = Get_block(currc,id2);


		int type = to->Get_topo_type();

		int P1	= to->Get_Plane1_Id();
		int P2	= to->Get_Plane2_Id();
		int P3	= to->Get_Plane3_Id();
		int P4	= to->Get_Plane4_Id();
		int P5	= to->Get_Plane5_Id();


		// following resolve funcs are defined in topo_data_resolving.c

		switch(type){

			case CFM :
				
				cfm_for_resolve(id1,id2,P1);	
				break;

			case CM :

				cm_for_resolve(id1,id2,P1,P2,P3);
				break;
			
			case CEM :

				cem_for_resolve(id1,id2,P1,P2);
				break;

			case TCM :
			
				tcm_for_resolve(id1,id2,P1,P2,P3,P4);
				break;

			case FCM :

				fcm_for_resolve(id1,id2,P1);
				break;

			case SP	:

				spm_for_resolve(id1,id2,P1);
				break;

			default :

				print_msg("topolink not specified",NO_VALUE);
				break;
		}

		de->Set_resolved(TRUE);

	}
	else{

		printf(" Node already Visited or Done \n");

	}	
}

/*******************************************************************************
*
*       NAME            :Resolve_adj_nodes()
*
*       DESCRIPTION     :Calls function Resolve for every adjacent node
*			 of the given Base_Node along the given axis
*
*       INPUT           :Base_Node, and the editing_axis
*
*       OUTPUT          :
*
*******************************************************************************/
 
void Resolve_adj_nodes(Node* base, int axis)
{

	Arc *arc = base->Get_arc_list();	// Traverse the arc_list

	while(arc){

		Node *A = arc->Get_node_A();
		Node *B = arc->Get_node_B();

		Topolink *T = arc->Get_arc_topo();

		// now we have all the information to call the Resolve function
		// By this function edited_nodes information will be transferred		// to all the adjacent nodes and topological relationship is
		// maintained


		// RESOLVE the node only if it is UNRESOLVED or length
		// MODIFICATION is allowed

		if((B->Get_resolved()== FALSE) || ( B->Get_modify() == TRUE )){

			Resolve(A,B,T);	// this will fix only relavent planes
					// function is defined just above this

			Block *blke = currc->Get_block(B->Get_node_id());

			if(B->Get_modify() == FALSE){

				blke->Update(axis);

			}
		// Let other axes of node B be Unresolved 

		// Needs some more THOUGHT here..

		Add_to_edit_Q(axis,blke);
					// here the new dimensions will be 
					// checked and if different the node
					// B will be added to the Q

		// go to the next arc

		}

		arc = arc->Get_nextal();
	}

}
