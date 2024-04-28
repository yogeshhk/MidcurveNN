/*******************************************************************************
*       FILENAME :      cycle.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Cycle
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   Sept 20, 1995.
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
*       NAME            :Cycle..... Constructor
*
*       DESCRIPTION     :This is second constructor.
*			 Sets private members properly
*
*       INPUT           : int Id
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Cycle::Cycle(int Id)
{

	cycle_id		= Id ;
	cycle_node_list	= NULL;
	nextcycle		= NULL;
	member_ids		= new int[20];

	for(int i = 0;i <20;i++)member_ids[i]=0;

	printf("Came to Cycle constructor no.%d \n",cycle_id);

}

/*******************************************************************************
*
*       NAME            :Link_CycleNodes(CycleNode *nl)
*
*       DESCRIPTION     : Adds the to the link list of nodes connected to this
*                         node and sets pointer to first node (cycle_node_list)
*                         This new node is added at the tail
*
*       INPUT           : Newly created CycleNode
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void Cycle::Link_CycleNodes( CycleNode *nl)
{
 
        if( cycle_node_list == NULL){
 
                cycle_node_list = nl;                // first node in the list
                nl->Set_nextcn((CycleNode *)NULL);
        }
        else{
                CycleNode *tracer = cycle_node_list;	// starts at first node
 
                while( tracer->Get_nextcn() != NULL){
                        tracer = tracer->Get_nextcn();
                }

				tracer->Set_nextcn(nl);
                tracer = tracer->Get_nextcn();
				tracer = nl;
                nl->Set_nextcn((CycleNode *)NULL);

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
 
void Link_cycles(Cycle* ss){
 
 
        if( firstcyl == NULL){
 
                firstcyl = ss;                // first node in the list
                firstcyl->Set_nextcycle((Cycle*)NULL);
        }
        else{
                Cycle *tracer = firstcyl;      // starts at first node
 
                while( tracer->Get_nextcycle() != NULL){
                        tracer = tracer->Get_nextcycle();
                }
 
                tracer->Set_nextcycle(ss);
                tracer = tracer->Get_nextcycle();
                tracer = ss;
                ss->Set_nextcycle((Cycle*)NULL);
 
        }
        printf("Linking to Cycles \n");
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
 
void Cycle::Set_member_ids(int *aa){

	int i,j;
	for(i=0,j=0;i<20;i++,j++){

		member_ids[i]=aa[j];
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
 
void Cycle::print_member_ids(){
 
 
        for(int i=0;i<20;i++){
 
                printf("MEMBERS are %d\n",member_ids[i]);
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
 
Cycle* Get_Cycle(int cye_num){

        Cycle	*trace;
 
        trace = firstcyl;
 
        while(trace){
 
                if(trace->Get_cycle_id() == cye_num){
 
                break;
                }
 
                trace = trace->Get_nextcycle();
        }
        return trace;
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
 
int Cycle::Get_left_member_id(int me){

	int k=0;
	int position=0;

	while(member_ids[k]){

		if(member_ids[k] == me){
			position = k;
		}
		
		k++;
	}
	// Now position is the index where "me" is
	// and k is total number of non-zero members
        printf("TOTAL = %d and Position of %d is %d ",k,me,position);

	int kk = position - 1;	
	int kkk = k - 1;	

	if( position == 0){ // he is the first one so we have to return
			   // the last non-zero as it is Circular list
		
		printf("LEFT = %d\n",member_ids[kkk]);
		return member_ids[kkk];
	}
	else{
		printf("LEFT = %d\n",member_ids[kk]);
		return member_ids[kk];
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
 
int Cycle::Get_right_member_id(int me){

        int k=0;
        int position=0;
 
        while(member_ids[k]){
 
                if(member_ids[k] == me){
                        position = k;
                }
 
                k++;
        }
        // Now position is the index where "me" is
        // and k is total number of non-zero members

        printf("TOTAL = %d and Position of %d is %d ",k,me,position);
       	int kk 	= position +1; 
		int kkk = k - 1;	
 
        if( position == kkk){ 	// he is the last one so we have to return
                           		// the first as it is Circular list
                
                printf("(Last cha RIGHT = %d\n",member_ids[0]);
                return member_ids[0];
        }
        else{
                printf("RIGHT = %d\n",member_ids[kk]);
                return member_ids[kk];
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
 
int Cycle::Is_member(int me){
 
        int k		=0;
        int is_mem	=0;
 
        while(member_ids[k]){
 
                if(member_ids[k] == me){
					is_mem = TRUE;
                }
                k++;
        }
 
	return is_mem;
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
 
int Cycle::Get_num_members(){

        int k=0;
        while(member_ids[k])k++;

	printf("TOTAL members %d\n",k);
	
	return k;

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
 
void Process_Cycles(){

	printf("CAME TO PROCESSING OF THE CYCLES\n");


	Cycle * cyc = firstcyl;

	while(cyc){

		// First we will delete those cycles which have only two
		// members

		if( cyc->Get_num_members() <= 2){
			printf(" %d Not Really A CYCLE\n",cyc->Get_cycle_id());
			Delete_Cycle(cyc);
		}
		if(cyc == NULL){

			printf("No more Cycles Left\n");
			return;
		}
		cyc = cyc->Get_nextcycle();

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
 
void Delete_Cycle(Cycle* de){

                if(de == NULL)return;
                if(firstcyl == NULL)return;

		if(de == firstcyl){
            printf("In Delete Cycle :de == firstcuycle\n");
			firstcyl = firstcyl->Get_nextcycle();
		}
		else{

			Cycle *trac = firstcyl;

			while( trac){

				if( trac->Get_nextcycle() == de){
		
					trac->Set_nextcycle(de->Get_nextcycle());
					printf("Deleteing %d\n",trac->Get_cycle_id());

				}
				
				trac = trac->Get_nextcycle();
			}

		}

		delete de;				
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
 
void Remove_duplicate_cycles(){

	if(firstcyl == NULL){

		print_msg("NO CYCLES",NO_VALUE);
		return;
	}
	if(firstcyl->Get_nextcycle() == NULL){

		print_msg("ONLY ONE CYCLE LEFT",NO_VALUE);
		return;
	}

	Cycle* A;
	Cycle* B;

	// I will pivot A and check itself with all the remaining cycles
	// If duplicate is found, delete it
	// If no duplicate is found, A gets changed to nextcycle and then checks
	// the further cycles
	// A traverses till END of the List

	A = firstcyl; 

	while(A){
		B = A->Get_nextcycle();
	
		if( A->Get_num_members() == B->Get_num_members()){
		
			int total = A->Get_num_members();	// total members
			int check = 1;

			for(int m = 0;m < total;m++){

				check *= B->Is_member( A->Get_member(m));
			}

			if(check){	// B is just the duplicate

				Delete_Cycle(B);
			}
		}

		A = A->Get_nextcycle();

	}
}
