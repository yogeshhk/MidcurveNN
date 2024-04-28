/*******************************************************************************
*       FILENAME :      component.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Component
*
*       FUNCTIONS   :   Constructor
*						Component::Link_Blocks( Block *bo)
*						Link_Comp( Component *co)
*						Display_by_phigs(int)
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   June 1, 1995.
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

/******************************************************************************e
*
*       NAME            :Component..... Constructor 
*
*       DESCRIPTION     :	This is second constructor. Gets all the values from
*			 				Data Table and calls the block constructor with all 
*			 				these vaules. Also sets comp_block = NULL at start
*			 				and then links the newly created block to link list
*			 				of block present in the private of Component.
*			 				Calls constuctor of graph and passes this new block
*			 				to pass to new ( first) node in private of Graph.
*
*       INPUT           : All the values form Block_Data_Entry Table
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
 
Component::Component(	char *cid,char *bid,
						double xn, double xx, 
						double yn, double yx, 
						double zn, double zx)
{

	component_id	= ++maxc;	// one more than current max comps
								// maxc is global in application.h
	strcpy(component_name ,cid);

	num_polygonsets = 0;

	comp_block	= NULL;
	firstset	= NULL;
	nextc		= NULL;
	
	block_id_counter= 000;			// will be assigned properly in new Block
	
	Block *fb  		= new Block(bid,this,xn, xx, yn, yx,zn, zx);
	
	Link_Blocks(fb);		// links the block to link lists and sets
							// comp_block pointer to the first block


	comp_graph		= new ComponentGraph(this,fb);

	ref_dim_graph	= NULL;
	spec_dim_graph	= NULL;

	block_flag	= BLOC;	// block_flag is global,BLOC says BOX type
} 

/*******************************************************************************
*
*       NAME            :Link_Blocks(Block *bo)
*
*       DESCRIPTION     : Adds the to the link list of blocks in Components
*                         private and sets pointer to first block (comp_block)
*                         This new block is added at the tail
*
*       INPUT           : Newly created Block
*
*       OUTPUT          : Nothing
*
******************************************************************************/

void Component::Link_Blocks( Block *bo)
{

	printf("Came to linking of the blocks \n");

	if( comp_block == NULL){

		comp_block = bo;		// first block in the list
		comp_block->Set_prevb((Block *)NULL);
		comp_block->Set_nextb((Block *)NULL);
	}
	else{
		Block *tracer = new Block;

		tracer = comp_block;	// starts with first block

		while( tracer->Get_nextb() != NULL){
			tracer = tracer->Get_nextb();
		}
		tracer->Set_nextb(bo);
		bo->Set_prevb(tracer);
		bo->Set_nextb((Block *)NULL);
	}
}

/*******************************************************************************
*
*       NAME            :Link_PolygonSets(PolygonSet *bo)
*
*       DESCRIPTION     : Adds the to the link list of PolygonSets in Components
*
*       INPUT           : Newly created PolygonSet
*
*       OUTPUT          : Nothing
*
******************************************************************************/

void Component::Link_PolygonSets( PolygonSet *bo)
{

	printf("\n Linking the polygonSet...\n");
    ++num_polygonsets;  // increment the number of polygon sets
    bo->Set_polygonset_id(num_polygonsets);

        if( firstset == NULL){

                firstset = bo;                // firstset in the list
                firstset->Set_nextps((PolygonSet *)NULL);
        }
        else{
                PolygonSet *tracer = firstset;

                while( tracer->Get_nextps() != NULL){
                        tracer = tracer->Get_nextps();
                }
                tracer->Set_nextps(bo);
				tracer = tracer->Get_nextps();
				//tracer = bo;
				tracer->Set_nextps((PolygonSet *)NULL);
        }

}



/*******************************************************************************
*
*       NAME            :void Link_Comp(Component *co)
*
*       DESCRIPTION     : Adds the component to the current link list
*                         of components and sets current component(currc)
*                         to this newly added component( at the tail)
*
*       INPUT           : Newly created component
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void  Link_Comp(Component *newc)
{
 
        /*
                firstc and currc are global pointers to the first and
                current components respectively in application.h
                They both are initialized to NULL in Init_App()
                defined above in this file.
        */
 
      Component *current_comp;
 
 
      if (firstc == NULL){
             	firstc = newc;
				firstc->Set_nextc((Component *)NULL);
             	currc = firstc;
 
        }
      else {
             	current_comp = firstc;
             	while (current_comp->Get_nextc() != NULL){

                    	current_comp = current_comp->Get_nextc();
		}

             	currc = current_comp->Get_nextc() ;
                currc=newc;
				currc->Set_nextc((Component *)NULL);
 
      }
}

/*******************************************************************************
*
*       NAME            :Get_max_dimension()
*
*       DESCRIPTION     : 
*
*       INPUT           : 
*
*       OUTPUT          : maximum dimension of all children blocks
*
******************************************************************************/
 
double Component::Get_max_dimension()
{
        Block 	*trace;
	double 	maximum = 50 ; 		// some initial value
 
        trace = comp_block;
 
        while(trace){
 
                if(maximum  <= trace->Get_max_dimension()){

			maximum = trace->Get_max_dimension();
		}
 
                trace = trace->Get_nextb();
        }



	return maximum ;
}
/*******************************************************************************
*
*       NAME            :Display_by_phigs(int type)
*
*       DESCRIPTION     :Depending on the type specified different dipslay func.
*			 			can be invoked. But every one will have same struct_id
*			 			which is (Pint)component_id. Interior setting and line
*			 			area displays may change
*			
*		STEPS 			:
*
*			 			opens struct.
*			 			gets global maximum dimension
*			 			sets the windows parameters to that dimension
*			 			traverses the block list and calls dipslay() of each
*			 			closes the struct
*			 			posts it 
*
*       INPUT           : type of display needed
*
*       OUTPUT          : picture on screen
*
******************************************************************************/
 
void Component::Display_by_phigs(int type)
{
 
		display_max = Get_max_dimension();

        drawing_width  = 1.5 * display_max;
        drawing_height = 1.5 * display_max;
 
		/*
		**		In Resize we already give offset of 1.5 times the dimension
		*/
        Resize_Ws(display_max);
 
		PolygonSet *head;
        Block *trace;

        popen_struct((Pint)component_id);   

        	pset_view_ind(1);
			//DrawAxes(display_max);
			switch(type){

				case WIREFRAME :
    				pset_hlhsr_id( PHIGS_HLHSR_ID_OFF );

					trace = comp_block;

					while(trace){
						trace->Display_by_phigs(); 
						trace = trace->Get_nextb();
					}
					break;

                case SOLID:
                    Set_HLHSR();
                    pset_int_style(PSTYLE_HOLLOW);
                    pset_hlhsr_id( PHIGS_HLHSR_ID_ON );
					Solid_Display();
					/*
                    head = firstset;

                    while(head){
                        head->Display_by_phigs();
                        head = head->Get_nextps();

                    }
					*/

                    break;

				case POLYSET:

					Set_HLHSR();
					pset_int_style(PSTYLE_SOLID);
					//pset_light_src_rep(WS_ID,(Pint)1,(Plight_src_bundle *)NULL);

    				pset_hlhsr_id( PHIGS_HLHSR_ID_ON );
					head = firstset;

            		while(head){
                		head->Display_by_phigs();
                		head = head->Get_nextps();
 
            		}
					break;

				default:
					break;

			}

		pclose_struct();
		ppost_struct(WS_ID,(Pint)component_id, (Pfloat)1.0);

		// handle_input();		//	Defined in graphics_phigs.h

		pupd_ws( WS_ID, PFLAG_PERFORM );

}

/*******************************************************************************
*
*       NAME            :Get_block()
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          : Block
*
******************************************************************************/
 
Block *Component::Get_block( int blk)
{
        Block   *trace;
 
        trace = comp_block;
 
        while(trace){
 
                if(trace->Get_block_id() == blk){
 
		break;
                }
 
                trace = trace->Get_nextb();
        }
 
 
 
        return trace;
}

/*******************************************************************************
*
*       NAME            :Get_component_name()
*
*       DESCRIPTION     :returns a component name
*
*       INPUT           :
*
*       OUTPUT          :Duplicate  name
*
******************************************************************************/
 
char* Component::Get_component_name(){

	char text[20];

	sprintf(text,"%s",component_name);

	return text;

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
 
void Component::Copy_for_Edit( Component* ec)
{

 
        component_id    = 100;       // one more than current max comps
                                        // maxc is global in application.h

        strcpy(component_name ,ec->Get_component_name());

		comp_graph	= NULL; 
        comp_block      = NULL;
        nextc           = NULL;
 
        block_id_counter = 000; // will be assigned properly in new Block
 

	Block* fb = ec->Get_comp_block();

	while(fb){

		char text[20];
	
		strcpy(text,fb->Get_block_name());

        	double  pxn     = fb->Get_Xmin();
        	double  pxx     = fb->Get_Xmax();
        	double  pyn     = fb->Get_Ymin();
        	double  pyx     = fb->Get_Ymax();
        	double  pzn     = fb->Get_Zmin();
        	double  pzx     = fb->Get_Zmax();

		Block *ne = new Block(text,this,pxn,pxx,pyn,pyx,pzn,pzx);

        	Link_Blocks(ne);// links the block to link lists and sets
                                 // comp_block pointer to the first block
 
		printf("CompEdit\n");

		fb = fb->Get_nextb();

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
 
int Component::Check_coplanarity(Polygon *p1, Polygon* p2){

	/*
		Given two planes , we want to find out whether they lie in the
		same plane or not..For the base plane (here p1)..we will get
		its normal vector.. normalize it..and check it with normalized
		vector of second plane..thus we can return FALSE if the planes are
		intersecting i.e all three dcs are not same..
		If planes are coplaner..then We will take normal of the base plane,
		and take a point on second plane and thus make a scalar Triple product
		with this normal..by this we get the volume of the paralleloped..refer
		"Adv. Engg. Mathematics..Kreszig"..If the volume comes out to be
		zero.. then these two planes are "coplaner"..

	*/

	Vector *v1;
	if(p1) v1  = p1->Get_normal();
	Vector *v2;
	if(p2)v2 = p2->Get_normal();

	double	n1x = v1->Get_dcx();
	double	n1y = v1->Get_dcy();
	double	n1z = v1->Get_dcz();
	double	n1d = v1->distance();
		
	double	n2x = v2->Get_dcx();
	double	n2y = v2->Get_dcy();
	double	n2z = v2->Get_dcz();
	double	n2d = v2->distance();

    /*
        Now we need to take cross product of these two "difference vectors"
 
 
        A X B = (aybz - azby)i - (axbz -bxaz)j + (axby -bxay)k
 

		We will normalize the normals first
    */
 
    double dx1 =n1x/n1d;
    double dy1 =n1y/n1d;
    double dz1 =n1z/n1d;
 
    double dx2 =n2x/n2d;
    double dy2 =n2y/n2d;
    double dz2 =n2z/n2d;

    double ix = (dy1*dz2) -(dz1*dy2);
    double iy = (dx2*dz1) -(dx1*dz2);
    double iz = (dx1*dy2) -(dx2*dy1);
	
	
	if((ix != 0)||(iy != 0)||(iz != 0)){
		return 0;
	}
	Vertex	*pt1 = p1->Get_V_list_head();
	Vertex	*pt4 = p2->Get_V_list_head();

	double diff_x = pt4->Get_x() - pt1->Get_x();
	double diff_y = pt4->Get_y() - pt1->Get_y();
	double diff_z = pt4->Get_z() - pt1->Get_z();

	double volume = fabs((diff_x*n1x) + (diff_y*n1y) + (diff_z*n1z));

	//printf("Volume is %f\n",volume);

	if(volume < ZERO){
		printf("So returning 1\n");
		return 1;
	}
	else {
		printf("So returning 0\n");
		return 0;
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
 
void Component::PolygonSet_Display()
{

            // Go to each block
 
            Block *see;
            see = comp_block;
 
			
            while(see){

                // Collect all the faces from that block
                // Need to modify this function for Cylinders
 
                // I will have one more function in Block say
                // create_polygons() which will return NULL in block but
                // return top and bottom polygons in cylinder
 

                Face *list = see->Create_Faces();
 
                while(list){
 
                    Polygon *pl = new Polygon(list);
 
					pl->Set_block_type(see->Get_block_type());

					int done = 1;
					
                    // check according to normal and distance and add it
                    // to the Polygon set or add it to newly created Polygon set
 
                      PolygonSet* ptra = firstset;
 
					if(ptra == NULL){
						PolygonSet* yy = new PolygonSet;
						yy->Add_to_poly_list(pl);
						Link_PolygonSets(yy);
						done = 0;
					}
					else{

                      while((ptra != NULL)&&(done != 0)){

                      	Polygon *fp = ptra->Get_poly_list_head();
 
						
                       	int flag = Check_coplanarity(fp,pl);
 
                            	if(flag){   // if they are co-planer
 
                                	ptra->Add_to_poly_list(pl);
                                	done = 0;
                            	}
                            	ptra = ptra->Get_nextps();
                       }
 
                    // done = non-zero all the time except when it visits
                    // upper done = 0 statement, where pl already gets added
                    // to the list. by this mechanism will are avoiding
                    // addition of pl twice..
 
			
                    	if(done){
                    		PolygonSet* sp = new PolygonSet;
                       		sp->Add_to_poly_list(pl);
                       		done = 0;
                       		Link_PolygonSets(sp);
                    	}

					}

                    list = list->Get_nextf();
                }


                Polygon *polylist = see->Create_Polygons();
 
                while(polylist){
 
                    // check according to normal and distance and add it
                    // to the Polygon set or add it to newly created Polygon set
                    // check according to normal and distance and add it
                    // to the Polygon set or add it to newly created Polygon set
 
                    int done = 1;

                    if(firstset == NULL){
                        firstset = new PolygonSet;
                        firstset->Add_to_poly_list(polylist);
                        firstset->Set_nextps((PolygonSet *)NULL);
                        done = 0;
                    }
 
                    if(done){
 
                        PolygonSet* ptra = firstset;
 
                        while(ptra){
 
                            Polygon *fp = ptra->Get_poly_list_head();
 
                            int flag = Check_coplanarity(fp,polylist);
 
                            if(flag){   // if they are co-planer
 
                                ptra->Add_to_poly_list(polylist);
                                done = 0;
                            }
 
                            ptra = ptra->Get_nextps();
                        }
                    }
 
                    // done = non-zero all the time except when it visits
                    // upper done = 0 , where polylist already gets added
                    // to the list. by this mechanism will are avoiding
                    // addition of polylist twice..
 
                    if(done){
                            PolygonSet* sp = new PolygonSet;
                            sp->Add_to_poly_list(polylist);
                            done = 0;
                            Link_PolygonSets(sp);
                    }
 

                    polylist = polylist->Get_nextp();
 
                }
 
                // Go to the next block
 
                see = see->Get_nextb();
            }
 

            // Now we have the list of PolygonSets pointed by *firstset in class
            // component
 
            // We need to traverse that list, Go toeach polygon set and call
            // merge function so that it merges all the containing polygons
 
            PolygonSet* tra =firstset;

            while(tra){
				printf("------------------------------------\n");
				tra->Print();
				printf("\nAfter Merging...\n");
                tra->Merge_the_polygons();
				printf("__________________________________\n");
				tra->Print();
				printf("Hi 2\n");
                tra = tra->Get_nextps();
				printf("Hi 3\n");
 
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

void Component::Scale(int ax,double val){

	Block   *trace = comp_block;

    while(trace){

		switch(ax){

			case XAXIS :
				trace->ScaleX(val);
				break;

			case YAXIS :
				trace->ScaleY(val);
				break;

			case ZAXIS :
				trace->ScaleY(val);
				break;

			default:
				printf("Wrong axis for scaling\n");
				break;

		}

		trace = trace->Get_nextb();
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

void Component::Solid_Display(){

	/*
	**	pset_of_fill_area_set3_data() primitive of the PHIGS+ is complex
	**	primitive. There are three nested list.
	**	Here, I am considering , Component as top level list, consisting
	**	of fill area sets of each block, which in tern are sets of faces
	*/
        Block *trace;
        trace = comp_block;

        while(trace){
        	trace->Solid_Display_by_phigs();
            trace = trace->Get_nextb();
        }



}
