/*******************************************************************************
*       FILENAME :      compfile2.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Component
*			Save and Retrive .. related to file operations
*			Contains Save in Venky's format
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 14, 1995.
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
*       NAME            :Write_to_file
*
*       DESCRIPTION     : This function will be used to Save the component
*
*
*        Starting from first block...
*
*        NODE    (node_no) (block_type) (axis) (rest_for_prsm_block)
*                (xmin) (xmid) (xmax) (xlen) (xlength_id)
*                (ymin) (ymid) (ymax) (ylen) (ylength_id)
*                (zmin) (zmid) (zmax) (zlen) (zlength_id)
*
*        Traversing the list of arcs
*
*        EDGE    ( edge_no) (edge_mate_no) (node_A_id) ( node_B_id)
*                ( edge_type)    (plan1_A) (plan1_B)
*                                (plan2_A) (plan2_B)
*                                (plan3_A) (plan3_B)
*                                (plan4_A) (plan4_B)
*                                (plan5_A) (plan5_B)
*
*
*
*
*       INPUT           : File pointer
*
*       OUTPUT          :Component Saved in the specified file
*
*******************************************************************************/
 
 
void Component::Write_to_Venkys_file( FILE *fo)
{


	Block *cb = comp_block;

	// This is the first block, though axis is not implemented i will keep
	// one field for it

	// "rest" is field specifically used for Prismatic block by Venky

	int axis =0;		
	int rest = 0;

	// we will traverse link list of blocks in the Component
	// and name it as NODE

	while(cb){

		Node *nb = cb->Get_block_node();

		fprintf(fo,"\n%s %3d","NODE",nb->Get_node_id());	
		fprintf(fo," %3d",cb->Get_block_type());	

		switch(cb->Get_block_type()){

			case BLOC :
			case SBLOC :
				axis = 0;
				break ;

			default :
			
				axis = cb->Get_axis();
				break ;

		}
		
		fprintf(fo," %3d %3d ",axis,rest);

		float	xn      = cb->Get_Xmin();
		float	xx      = cb->Get_Xmax();
		float	xl      = (xx - xn );
		float	xm      = (xx + xn )/2;
 
		float	yn      = cb->Get_Ymin();
       	float	yx      = cb->Get_Ymax();
		float	yl      = (yx - yn );
		float	ym      = (yx + yn )/2;

		float	zn      = cb->Get_Zmin();
       	float	zx      = cb->Get_Zmax();
		float	zl      = (zx - zn );
		float	zm      = (zx + zn )/2;


		Length *xln	= cb->Get_Xlen();
		Length_List *xll= xln->Get_length_list();
		int xnum	= xll->Get_len_id();


		Length *yln	= cb->Get_Ylen();
		Length_List *yll= yln->Get_length_list();
		int ynum	= yll->Get_len_id();


		Length *zln	= cb->Get_Zlen();
		Length_List *zll= zln->Get_length_list();
		int znum	= zll->Get_len_id();


		fprintf(fo," %3.1f %3.1f %3.1f %3.1f %3d",xn,xm,xx,xl,xnum);
		fprintf(fo," %3.1f %3.1f %3.1f %3.1f %3d",yn,ym,yx,yl,ynum);
		fprintf(fo," %3.1f %3.1f %3.1f %3.1f %3d",zn,zm,zx,zl,znum);


		cb=cb->Get_nextb();
	}

	printf("Venkys blocks are finished\n");

	// We will now go to Graph then Traverse the Vertical list of Nodes
	// Then each node will have arc_list which conatains all the
	// arcs emonating from that Node. So traverse that List and Store
	// information about each Arc as TOPOLOGY

	Graph *gr = comp_graph;

	Node *nn = comp_graph->Get_graph_node();

	while(nn){
	
		Arc *ar = nn->Get_arc_list();

		while(ar){

			// This topo will occure twice because
			// it is common for two arcs.

			Node *na = ar->Get_node_A();
			Node *nb = ar->Get_node_B();

			int arca = ar->Get_arc_id();

			Arc *mate= ar->Get_mate();

			int arcb = mate->Get_arc_id();

			printf("A %d B %d \n", arca,arcb);

			int noda = na->Get_node_id();
			int nodb = nb->Get_node_id();

			Topolink *topo = ar->Get_arc_topo();
				
			int type = topo->Get_topo_type();

			int blk1 = topo->Get_Block_A_Id();
			int blk2 = topo->Get_Block_B_Id();
	
			int pln1 = topo->Get_Plane1_Id();
			int pln2 = topo->Get_Plane2_Id();
			int pln3 = topo->Get_Plane3_Id();
			int pln4 = topo->Get_Plane4_Id();
			int pln5 = topo->Get_Plane5_Id();

			fprintf(fo,"\n%s%3d%3d","EDGE",arca,arcb);
			fprintf(fo,"%3d%3d%3d%3d",noda,nodb,type,pln1);
			fprintf(fo,"%3d%3d%3d%3d",pln2,pln3,pln4,pln5);

			ar = ar->Get_nextal();
		}

	nn = nn->Get_nextn();

	}

	// All the saving has been finished . So a DONE mark is kept at end

	fprintf(fo,"\n%s","DONE");
	fclose(fo);
	printf("Venkys Saving completed\n");
}

