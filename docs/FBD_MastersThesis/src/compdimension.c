/*******************************************************************************
*       FILENAME :      compdimension.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Dimensioning the Component
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   March 14, 1996.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"        	/* Classes Declarations :header file */
#include <string.h>


/*******************************************************************************
*
*       NAME            :Create_default_dim_graphs()
*
*       DESCRIPTION     : 
*
*       INPUT           :
*
*       OUTPUT          : Nothing
*
******************************************************************************/

void Component::Create_default_dim_graphs()
{


	printf("came to Creat_Default dimension graph\n");

	/*
	**		DimensionGraph is subclass of Graph. There is already a nodeList 
	**		in the Graph ( declared wrt firstnode). I will use that for now.In
	**		the DimNodes in Linearlist irrespective of their type or value
	**		The 4 lists in DimGraph will store the same DimNodes but
	**		sorted according to the axis type
	*/

	Block*	currb;			// current block

		/*
		**	Here the block list is traversed and faces are collected from
		**	them. With the help of faces, DimNodes are created.Then
		**	According the Face_axis_type, DimNodes are added to
		**	respective DimNodes list
		*/
							
	currb = comp_block;

	ref_dim_graph	= new	DimensionGraph(this);
	spec_dim_graph	= new	DimensionGraph(this);

	int		counter=0;

	/*
	**		NOTE:
	**		Every face that comes from the block gets capsulated by
	**		DimNode and gets added to "ref_dim_graph".But it may not be the
	**		case with "spec_dim_graph".The newly coming face is first checked
	**		with existing nodes for dimesnion and tolerance values.If the 
	**		match is found then the face is added to that DimNode and thus
	**		for that new face DimNode is not made. By this way we are
	**		making the coplaner faces as only one DimNode
	*/

	while(currb){

		Face* list = currb->Contribute_dim_Faces();

		printf(" Block Id = %d $$$$$$$$$$$$$\n",currb->Get_block_id());

			while(list){

				printf(" %d ------\n",list->Get_face_id());
				counter++;
				DimNode* dimr = new DimNode(list,currb->Get_block_id(),counter);
				ref_dim_graph->Add_to_dimlist(list->Get_face_type(),dimr);

				DimNode* match = spec_dim_graph->Get_matching_node(list);
				/*
				**		Returns NULL if no Match is found
				*/

				if(!match){

					DimNode* dims;
					dims = new DimNode(list,currb->Get_block_id(),counter);
					spec_dim_graph->Add_to_dimlist(list->Get_face_type(),dims);
					//printf("Adding DimNode with Id = %d\n",counter);
				}
				else{			// means match is found

					// printf("MATCH is found ******\n");
					DimPrimitive* tmp= new DimPlane(list,currb->Get_block_id());
					match->Add_to_node_prim_list(tmp);

				}
				list = list->Get_nextf();
			}

		currb = currb->Get_nextb();
	}

	spec_dim_graph->Fill_Dim_Arcs();
	spec_dim_graph->PrintYourself(stdout);
}


