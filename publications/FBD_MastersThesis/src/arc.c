/*******************************************************************************
*       FILENAME :      arc.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Arc
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JUN 22, 1995.
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
*       NAME            :Arc ... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. .Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : 
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 

Arc::Arc(char* name,Node *a, Node *b, Topolink *tp)
{

	strcpy(arc_name,name);			// copy the string as arc_name
	
	node_A		= a ;				// parent node
	node_B		= b ;				// child node
	arc_id 		= arc_counter ;		// arc_counter is a global counter
	edge_type 	= 0 ;				// No edge_type yet

	arc_counter++;					// next new arc (id) will be incremented

	nextal		= NULL;				// next arc is not attached yet
	arc_topo	= tp;				// topolink which it represents


	printf("Arc Constructor : Topo type is %d\n",tp->Get_topo_type());

}

/*******************************************************************************
*
*       NAME            :Get_mate()
*
*       DESCRIPTION     :This function returns "mate" of this arc
*			 This is required in SAVE option for Venkys files
*
*       INPUT           :
*
*       OUTPUT          : mate Arc*
*
*******************************************************************************/
 
Arc* Arc::Get_mate()
{

	int na = node_A->Get_node_id();
	int nb = node_B->Get_node_id();


	Arc *aa = node_B->Get_arc_list();	// Get the arcs of second node

	while(aa){				// Traverse all the arc list

		Node *an = aa->Get_node_B();	// Get the destination node

		int anid = an->Get_node_id();	// get its id

		printf("Arcs %d\n",anid);

		if( anid == na)break;		// If it matches with original
						// node_A_id then we have 
						// found the correct arc
						// thus break from the loop

		aa = aa->Get_nextal();

	}

	return aa;				// return the arc where "break"

}

