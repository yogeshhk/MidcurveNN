/*******************************************************************************
*       FILENAME :      compfile.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Component
*			Save and Retrive .. related to file operations
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
#include "vertexh.h"

/*******************************************************************************
*
*       NAME            :Write_to_file
*
*       DESCRIPTION     : This function will be used to Save the component
*
*        COMPONENT (component_name) (name_of_first_block) (axis) (extra)
*                   (xmin) (xmax) (ymin) (ymax) (zmin) (zmax)
* 
*        From second block onwards...
* 
*        BLOCK   (component_name) (block_name) (axis) (type_of_block)
*                   (xmin) (xmax) (ymin) (ymax) (zmin) (zmax)
* 
*        Avoiding duplicate topolink...
* 
*        TOPOLINK (component_name) (type_of_link) (blk1) (blk2)
*                 (plane1) (plane2) (plane3) (plane4) (plane5)
* 
*
*       INPUT           : File pointer
*
*       OUTPUT          :Component Saved in the specified file
*
*******************************************************************************/
 
 
void Component::Write_to_file( FILE *fo)
{

	// At the first line we will say COMPONENT and give all the arguments
	// required to call its constructor
	// This line when retrieved will create first block and a graph which
	// in turn will create first node

	fprintf(fo,"%s %s ","COMPONENT",component_name);

	Block *cb = comp_block;

	// This is the first block, though axis is not implemented i will keep
	// one field for it

	char text[20];

	strcpy(text,cb->Get_block_name());

	float	xn	= cb->Get_Xmin();
	float	xx	= cb->Get_Xmax();

	float	yn	= cb->Get_Ymin();
	float	yx	= cb->Get_Ymax();

	float	zn	= cb->Get_Zmin();
	float	zx	= cb->Get_Zmax();

	int axis =0;		// these two fields are not in use now
	int extra = 0;

	fprintf(fo,"%s %d %d ",text,axis,extra);
	fprintf(fo,"%f %f %f %f %f %f\n",xn ,xx,yn,yx,zn,zx);

	cb = cb->Get_nextb();	// from second block onwards we will traverse 
				// the list of blocks and get the information

	while(cb){

		fprintf(fo,"%s %s ","BLOCK",component_name);	

		strcpy(text,cb->Get_block_name());

		xn       = cb->Get_Xmin();
        xx       = cb->Get_Xmax();
 
        yn       = cb->Get_Ymin();
        yx       = cb->Get_Ymax();
 
        zn       = cb->Get_Zmin();
        zx       = cb->Get_Zmax();
 
        int type = cb->Get_block_type();

        switch(cb->Get_block_type()){
 
            case BLOC :
            case SBLOC :
                axis = 0;
        		fprintf(fo,"%s %d %d ",text,axis,type);
        		fprintf(fo,"%f %f %f %f %f %f\n",xn ,xx,yn,yx,zn,zx);
                break ;
 
            case CYLINDR:
            case SCYLINDR:
                axis = cb->Get_axis();
        		fprintf(fo,"%s %d %d ",text,axis,type);
        		fprintf(fo,"%f %f %f %f %f %f\n",xn ,xx,yn,yx,zn,zx);
                break ;

			case WEDGE:
			case SWEDGE:
                axis = cb->Get_axis();
				int b1,b2;	//	Butting planes for wedge	 
				b1	=	cb->Get_butting_plane1();
				b2	=	cb->Get_butting_plane2();
        		fprintf(fo,"%s %d %d ",text,axis,type);
        		fprintf(fo,"%f %f %f %f %f %f",xn ,xx,yn,yx,zn,zx);
				fprintf(fo," %d %d \n",b1,b2);
				break;

			case BSPLINE:
                axis = cb->Get_axis();
                fprintf(fo,"%s %d %d ",text,axis,type);
                fprintf(fo,"%f %f %f %f %f %f",xn ,xx,yn,yx,zn,zx);
				cb->Write_to_file(fo);
				break;
            default :
				printf("Saving Unknown Block !!\n");
				break;
 
        }
		cb=cb->Get_nextb();
	}

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
			// it is common for two arcs. So as to avoide
			// this extra thing( arcs) I will follow the
			// convention that I will include the arc if
			// Node_B_Id is more than Node_A_Id

			Node *na = ar->Get_node_A();
			Node *nb = ar->Get_node_B();

			int noda = na->Get_node_id();
			int nodb = nb->Get_node_id();

			if( nodb > noda){

				extra = 0;	// not needed now

				//char name[30];
				//strcpy(name,ar->Get_arc_name());

				Topolink *topo = ar->Get_arc_topo();
				
				int type = topo->Get_topo_type();

				int blk1 = topo->Get_Block_A_Id();
				int blk2 = topo->Get_Block_B_Id();
	
				int pln1 = topo->Get_Plane1_Id();
				int pln2 = topo->Get_Plane2_Id();
				int pln3 = topo->Get_Plane3_Id();
				int pln4 = topo->Get_Plane4_Id();
				int pln5 = topo->Get_Plane5_Id();

				fprintf(fo,"%s %s ","TOPOLINK",component_name);
				fprintf(fo,"%d %d %d %d ",type,blk1,blk2,pln1);
				fprintf(fo,"%d %d %d %d\n",pln2,pln3,pln4,pln5);
			}
			
			else{
				printf("Skipping the arc\n");	
			}

			ar = ar->Get_nextal();
		}

	nn = nn->Get_nextn();

	}

	// All the saving has been finished . So a DONE mark is kept at end

	fprintf(fo,"%s","DONE");
	fclose(fo);

	/*
	**		This is for temporary purpose
	*/

	/*
	FILE *ref	= fopen("ref_graph.out","w");

		fprintf(ref,"REF\n");
		ref_dim_graph->Write_to_file(ref);
		fprintf(ref,"SPEC\n");
		spec_dim_graph->Write_to_file(ref);
		fprintf(ref,"DONE");

	fclose(ref);
	*/
	printf("Saving completed\n");
}

/*******************************************************************************
*
*       NAME            :Read_from_file
*
*       DESCRIPTION     : This function will be used to retrieve the compoenet
*
*       INPUT           : File pointer
*
*       OUTPUT          :Component Retrieved from the specified file
*
*******************************************************************************/
 
 
void Read_from_file( FILE *fi)
{
 
	int done = 0;	// used to abort whenever required

	char stype[12];	// string_type, used to gather first string(from file)

	while( done != 1){

		fscanf(fi,"%s", stype);

		Node *nn;
		int pl1		=0;  			// Plane1_Id...
        int pl2		=0;  			// Plane2_Id...
        int pl3		=0;  			// Plane3_Id...
        int pl4		=0;  			// Plane4_Id...
        int pl5		=0;  			// Plane5_Id...
        int topty	=0;   			// topo_type
        int bla		=0;  			// Block_A_Id
        int blb		=0;  			// Block_B_Id



		switch(stype[0]){

			case 'C' :		// COMPONENT

				char	cid[20];
				char	bid[20];
				int	ax;
				int	ty;

				fscanf(fi,"%s %s %d %d ",cid,bid,&ax,&ty);

				float xx ,xn;
				fscanf(fi,"%f %f ", &xn,&xx); 

				float yx ,yn;
				fscanf(fi,"%f %f ", &yn,&yx); 

				float zx ,zn;
				fscanf(fi,"%f %f\n", &zn,&zx); 

				// Now we have all the data to call the
				// constructor of the class Component

        		Component *nc ;
 
        		nc = new Component(cid,bid,xn,xx,yn,yx,zn,zx);
 
        		Link_Comp(nc);       	// above ,nc gets set as currc
        		comp_flag = OLD_COMP; 	// component complete
       			comp_num  = maxc ;		// current component
       			nc->Display_by_phigs(WIREFRAME);
       			comp_num++;				// sets incremented no. for next comp
 
		
				break;

			case 'B' :			// BLOCK

                fscanf(fi,"%s %s %d %d ",cid,bid,&ax,&ty);
                fscanf(fi,"%f %f ", &xn,&xx);
                fscanf(fi,"%f %f ", &yn,&yx);
                fscanf(fi,"%f %f ", &zn,&zx);
 
                // Now we have all the data to call the
                // constructor of the class Block

        	Block *nb;
 
        	switch(ty){
 
                	case BLOC :
 
                        	nb = new Block(bid,currc,xn,xx,yn,yx,zn,zx);
                	        break;
 
                	case SBLOC :
 
                        	nb = new SubBlock(bid,currc,xn,xx,yn,yx,zn,zx);
                        	break;
 
                	case CYLINDR :
 
                        	nb =new Cylinder(bid,currc,xn,xx,yn,yx,zn,zx);
                        	break;
 
                	case SCYLINDR :
 
                        	nb=new SubCylinder(bid,currc,xn,xx,yn,yx,zn,zx);
                        	break;

					case WEDGE:
							int b1,b2;		//	butting planes
							b1=b2=0;

							fscanf(fi,"%d %d\n",&b1,&b2);

							nb=new Wedge(bid,currc,
										xn,xx,yn,yx,zn,zx,
										ax,b1,b2);
							break; 

					case BSPLINE:
				
							double x;
							double y;
							double z;

							double xd[6];
							double yd[6];
							double zd[6];

							for(int ww=0;ww<6;ww++){
								fscanf(fi,"%f",&x);
								fscanf(fi,"%f",&y);
								fscanf(fi,"%f",&z);

								xd[ww]	=	x;
								yd[ww]	=	y;
								zd[ww]	=	z;
							}
							fscanf(fi,"\n");

                        	nb = new Block(bid,currc,xn,xx,yn,yx,zn,zx);

							/*

							nb = new Bspline(bid,currc,
										xn,xx,yn,yx,zn,zx,
										ax,
										xd[0],yd[0],zd[0],
										xd[1],yd[1],zd[1],
										xd[2],yd[2],zd[2],
										xd[3],yd[3],zd[3],
										xd[4],yd[4],zd[4],
										xd[5],yd[5],zd[5]
										);
							
							*/

							post_msg("Bspline Retrieving is Not Implemented");

							break;
                	default :             // By default it will create BLOCK
 
                        	nb = new Block(bid,currc,xn,xx,yn,yx,zn,zx);
                        	break;
 
        	}
 
			
			fscanf(fi,"\n");	
        	currc->Link_Blocks(nb); 

			       				// links the block to link lists and sets
                                // comp_block pointer to the first block
 
        	nn = new FeatureNode(nb);         		// New node
        	nb->Set_block_node(nn);                 // set block in the node
        	currc->Get_comp_graph()->Link_Node(nn); // link it to the graph

				break;

			case 'T' :		// TOPOLOGY

				//char an[20] ;	// arc_name

				fscanf(fi,"%s ",cid);
				fscanf(fi,"%d %d %d ",&topty,&bla,&blb);
				fscanf(fi,"%d %d %d ",&pl1,&pl2,&pl3);
				fscanf(fi,"%d %d\n",&pl4,&pl5);

				Topo_info ti;

				ti.block_id	= bla;
				ti.topo_type	= topty;
				ti.Plane1	= pl1;
				ti.Plane2	= pl2;
				ti.Plane3	= pl3;
				ti.Plane4	= pl4;
				ti.Plane5	= pl5;


                	switch(topty){

 
                        	case CFM :
 
                        		Center_Face_Match *tcfm;
                        		tcfm = new Center_Face_Match(&ti,blb);
                        		break;
 
                        	case CEM :
 
                        		Center_Edge_Match *tcem;
                        		tcem = new Center_Edge_Match(&ti,blb);
                        		break;
 
                        	case CM :
 
                        		One_Corner_Match *tocm;
                        		tocm = new One_Corner_Match( &ti,blb);
                        		break;
 
                        	case TCM :
 
                        		Two_Corner_Match *ttcm;
                        		ttcm = new Two_Corner_Match(&ti,blb);
                        		break;
 
                        	case FCM :
 
                        		Four_Corner_Match *tfcm;
                        		tfcm = new Four_Corner_Match(&ti,blb);
                        		break;
 
                        	case SP :
 
                        		Shared_Plane_Match *tsp;
                        		tsp = new Shared_Plane_Match(&ti,blb);
                        		break;
 
                	}

				break;		// Break for TOPOLOGY


			case 'D' :		// DONE means abort

				done = 1 ;
				break;

			default : 		// Nothing specified thus abort
				done = 1 ;
				break ;
		}

	}

	print_graph();

	fclose(fi);		
	
}
