/*******************************************************************************
*       FILENAME :      cycleEditing.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Algorithms related to Cycle detection
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   Sept 21, 1995.
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
 
/******************************************************************************
                        GLOBAL DECLARATIONS
******************************************************************************/
 
int	i 		= 0 ;		// Used in STRONG() below
int Cycle_Id= 0 ;   	//cycle counter


Stack<Node>*			stack;	// declarations are in linklisth.h
Stack<StrongCompNode>*	path;	// declarations are in linklisth.h


/*******************************************************************************
*
*       NAME            :Find_Cycles( Node* base,Graph* gra)
*
*       DESCRIPTION     :	The is one of the recursive algos in the project
*			 				It first splits graph into strongly connected
*			 				components and then finds cycles within component
*			 				containing the base Node
*
*       INPUT           : Base (edited) Node , and Parent graph
*
*       OUTPUT          :List of cycles containing the Base node
*
******************************************************************************/
 
Cycle* Find_Cycles( Node* base,Graph* gra){


	printf("\n\nFINDING CYCLES\n");

	// The functions STRONG and CYCLE are recursive in Nature 
	// They are almost one to one mapping from the algo stated in the
	// book - " Combinatorial Algorithms ,Theory and practice " by
	//		Edward M Reingold
	//		Jurg Nievergelt
	//		Narsingh Deo
	//	ISBN	0-13-152447-X

	// There is no return type provided by the algos..

	// STEP 1 :
		// Traverse the graph and call STRONG for all the nodes
		// in the graph. Nodes are collected as link list
		// with StrongComp* firststr as head to the list.It is declared
		// global in applications.h 


	stack  	= new Stack<Node>();		// used in STRONG
	path	= new Stack<StrongCompNode>();		// used in CYCLE

	Node* gn = gra->Get_graph_node();	// first node in the graph

	while(gn){

		if( gn->Get_Num() == 0 ){

			printf("Putting %d from main\n",gn->Get_node_id());
	
			STRONG(gn,(Node *)NULL,gra);
		}

		gn = gn->Get_nextn();

	}
        StrongComp* trc = firststr;
 
        while(trc){
 
                if(trc->is_member(base->Get_node_id())){
	
			// base node is in the strong component now get it

			StrongCompNode* s ;
			s = trc->Get_str_node(base->Get_node_id());
			int ff = FALSE ;	// initialization of flag

			CYCLE(s,ff,base);
		} 

		trc = trc->Get_nextstrcomp();
        }


	return firstcyl ;
}

/*******************************************************************************
*
*       NAME            :STRONG(Node* v,Node* u,Graph *gra)
*
*       DESCRIPTION     :	The is one of the recursive algos in the project
*			 				Ref.pg.339	Combinatorial algorithms
*
*       INPUT           : child node and parent node( Graph.. not reqd)
*
*       OUTPUT          :
*
******************************************************************************/
 
void STRONG(Node* v,Node* u,Graph* gra){


	Node* w;	// some temporary node..

	static int Id = 0;	// for id to strong Component

	i = i + 1 ;	// i is defined global in this file only
			// I am using "i" because book uses the same variables

	printf("Global Counter is %d\n",i);

	v->Set_Num(i);
	v->Set_Low(i);

	// Now printing the status of the Node
	printf("\tV [ %d %d %d ]\n",v->Get_node_id(),v->Get_Num(),v->Get_Low());


	stack->Push(v);

	Arc* e = v->Get_arc_list();

	while(e){

		w = e->Get_node_B();	// Got the adjacent node
	
		printf("Adj to %d is %d\n",v->Get_node_id(),w->Get_node_id());

		if( w->Get_Num() == 0){

				// ( v,w) is a TREE edge

				e->Set_edge_type(TREE);

				//*********** RECURSIVE CALL *******

				STRONG( w , v,gra );

				int tmp_low = MIN(v->Get_Low(),w->Get_Low());
				v->Set_Low(tmp_low);
printf("\tAft STR V [ %d %d %d ]\n",v->Get_node_id(),v->Get_Num(),v->Get_Low());				

		}
		else{

			if( (w->Get_Num()) < ( v->Get_Num())){

				// ( v , w) is a back edge or a cross edge

				e->Set_edge_type(BACK);	// dont know why

				if( stack->Find(w->Get_node_id()) != NULL){

					// at this point w is in the same
					// strongly connected component as v
					// since w is adjacent to v and w on
					// Stack means that there is a path
					// from w to v

					int tmp_low ;

					tmp_low= MIN(v->Get_Low(),w->Get_Num());

					v->Set_Low(tmp_low);
printf("\tAft BCK V [ %d %d %d ]\n",v->Get_node_id(),v->Get_Num(),v->Get_Low());

				} // no else for this

			}

		}

		if( v->Get_Low() ==  v->Get_Num()){

			// v is root of strongly connected component

			printf( "Making of New StrongComp\n");

			StrongComp* str = new StrongComp(++Id);

			int counter = 0;

	
			while((stack->Get_top()) && ((stack->Get_top())->Get_Num() >= v->Get_Num())){

				Node* xy = stack->Pop();

				++counter;	// gives id to new StrongCompNode

				StrongCompNode* sxy = new StrongCompNode(xy,counter);

				str->Link_StrongCompNodes(sxy);
			}
			str->fill_arcs(gra);//filling the arcs in strong comp
			Link_str_comps(str);
			str->Print();

		}

	e = e->Get_nextal();

	}

}

/*******************************************************************************
*
*       NAME            :CYCLE(Node* v,int& fl)
*
*       DESCRIPTION     :The is one of the recursive algos in the project
*			 Ref.pg.351 	Combinatorial algorithms
*
*       INPUT           : base node and flag
*
*       OUTPUT          :
*
******************************************************************************/
 
void CYCLE(StrongCompNode* v,int& fl,Node* base){
 
        printf("Came to cycle with %d\n",v->Get_str_node_id());

        fl = FALSE ;

        path->Push(v);
 
        v->Set_available(FALSE) ;

        StrArc* wa = v->Get_str_arc_list();
 
        while(wa){
 
                StrongCompNode* w = wa->Get_Node_B();   // adjacent in Strcomp
 
		if( w->Get_str_node() == base){  
				// coming again to same node forming a cycle
 
                        printf(" CYCLE WAs Found !!!!!\n");
                        printf("********************\n");
			++Cycle_Id;

                        path->Print_list();

			int *members = new int[20];// to collect what in "path"
			members = path->Get_array();

			Cycle* cycle = new Cycle(Cycle_Id);
			cycle->Set_member_ids(members);

			Link_cycles(cycle);	// link to the global list

                        fl = TRUE ;
                }
                else{
			 
                        if( w->Get_available() == TRUE ){
                                int g;  // used as flag
                                CYCLE(w,g,base);// g can be any thing
                                printf(" flag = %d and g = %d\n",fl,g);
                                if( (fl == TRUE) || (g == TRUE) ) fl = TRUE;
                        }
 
                }

                wa = wa->Get_nextsal();       // next arc
        }
        if( fl == TRUE)UNMARK(v);
        else{
                StrArc* aa = v->Get_str_arc_list();
 
                while(aa){
 
                        StrongCompNode* ww = aa->Get_Node_B();
                        (ww->Get_B())->Push(v);
                        aa = aa->Get_nextsal();
                }
                // add all the adjacent nodes to B(w)
        }
 
        // write a function to Pop specific element path->Pop();
        // Here we have to POp v only
 
        path->Remove(v);
 
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
 
void UNMARK( StrongCompNode* u){
 
        u->Set_available(TRUE) ;
 
 
        StrongCompNode* w = (u->Get_B())->Get_top();
        //StrongCompNode* w = NULL;
		//if(u->Get_B())w  = (u->Get_B())->Get_top();
 
        while(w){
 
                if( w->Get_available() == TRUE){
 
                (u->Get_B())->Remove(w);
 
                }
                else{
                        UNMARK(w);
                        }
 
        w = (u->Get_B())->Pop();
        }
        return;
}

