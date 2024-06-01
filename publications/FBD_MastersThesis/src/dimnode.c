/*******************************************************************************
*       FILENAME :      dimnode.c      DESIGN REF :  FBD(CAD/CAPP)
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
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
DimNode::DimNode(){

    dim_node_id 	= 0;
    arc_count   	= 0;
    prim_count   	= 0;
    nextdn      	= NULL;
    dim_arcs_out	= NULL;
    visited     	= FALSE;
    node_prim   	= NULL;
 
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
 
DimNode::DimNode(Face* nn,int blkid,int id){
 
 
	dim_node_id			= id;
	arc_count			= 0;
	prim_count			= 0;
	nextdn				= NULL;
	dim_arcs_out		= NULL;
	visited				= FALSE;
    node_prim   		= NULL;
	DimPrimitive* tmp 	= new DimPlane(nn,blkid);

	Add_to_node_prim_list(tmp);

	// 	printf("DimNode constructor %d\n",id);
}

/*******************************************************************************
*
*       NAME            :PrintYourself()
*
*       DESCRIPTION     : 
*
*       INPUT           : Nothing
*
*       OUTPUT          : Nothing
*
******************************************************************************/

void DimNode::PrintYourself(FILE* fo){


	double 	dim_val;
	if(node_prim)	dim_val	=	node_prim->Get_dim_value();

	fprintf(fo,"NODE %d [%f]:	\n",dim_node_id,dim_val);

	DimArc* tra= dim_arcs_out;

	while(tra){

		tra->PrintYourself(fo);
		tra = tra->Get_nextda();
	}
}

/*******************************************************************************
*
*       NAME            :Add_to_dim_arclist_out(DimArc *arc)
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
 
void DimNode::Add_to_dim_arclist_out( DimArc *arc)
{
 
        if( dim_arcs_out== NULL){
                dim_arcs_out= arc;                // first arc in the list
                dim_arcs_out->Set_nextda((DimArc *)NULL);
        }
        else{
                DimArc *tracer = dim_arcs_out;      // starts at first arc
                while( tracer->Get_nextda() != NULL){
                        tracer = tracer->Get_nextda();
                }
 
                tracer->Set_nextda(arc);
                tracer = tracer->Get_nextda();
                tracer = arc;
                arc->Set_nextda((DimArc *)NULL);
 
        }

		arc_count++;
}

 
/*******************************************************************************
*
*       NAME            :Add_to_node_prim_list(DimPrimitive* dp)
*
*       DESCRIPTION     : Adds the to the link list of dimprimitives
*                         represented by the node
*
*       INPUT           : Newly created dimprimitive
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void DimNode::Add_to_node_prim_list(DimPrimitive* dp)
{
 
        if( node_prim== NULL){
                node_prim= dp;                
                node_prim->Set_nextdp((DimPrimitive*)NULL);
        }
        else{
                DimPrimitive *tracer = node_prim;      // starts at first arc
 
                while( tracer->Get_nextdp() != NULL){
                        tracer = tracer->Get_nextdp();
                }
                tracer->Set_nextdp(dp);
                tracer = tracer->Get_nextdp();
                tracer = dp;
                dp->Set_nextdp((DimPrimitive*)NULL);
 
        }
 
        prim_count++;
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

void DimNode::Remove_all_Arcs(){

    DimArc* tra = dim_arcs_out;
	DimArc* de;

	while(tra){
		printf("Deleting %d\n",tra->Get_dim_arc_id());
		de = tra;
        dim_arcs_out = tra->Get_nextda();
		tra = dim_arcs_out;
        delete de;
    }

	dim_arcs_out = NULL;
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
 
void DimNode::RemoveArc(DimNode* endnode){

	DimArc* tra = dim_arcs_out;

	while(tra){

		DimNode* gotit	= tra->Get_nodeB();
		if(gotit==endnode)break;
		tra = tra->Get_nextda();
	}

	if(tra==dim_arcs_out){		// the only arc
		dim_arcs_out = tra->Get_nextda();
		delete tra;
		printf("Only arc\n");
	}
	else{

		DimArc*	see = dim_arcs_out;
		while(see){
			if(see->Get_nextda()==tra)break;
			see = see->Get_nextda();
		}
		see->Set_nextda(tra->Get_nextda());
		delete tra;
		printf("Not Only arc\n");
	}
}
