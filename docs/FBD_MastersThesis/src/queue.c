/*******************************************************************************
*       FILENAME :      queue.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Queue
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 24, 1995.
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
*       NAME            :Constructor
*
*       DESCRIPTION     :Initializes the private members of class NodeQueue
*
*       INPUT           :Type of the Queue
*
*       OUTPUT          :Undefined by C++
*
*******************************************************************************/
 
NodeQueue::NodeQueue(int type)
{

	front = NULL ;		// Nothing at front
	rear = NULL ;		// Nothig at rear
	
	q_type = type ;		// assign the type of queue

	num_elements = 0;	// no elements

}
/*******************************************************************************
*
*       NAME            :Is_empty()
*
*       DESCRIPTION     :Checks whether the Queue is empty or not
*
*       INPUT           :
*
*       OUTPUT          :TRUE means empty
*
*******************************************************************************/
 
int NodeQueue::Is_empty()
{
     if( (front == NULL) && (rear == NULL) ) return(TRUE);
     else return(FALSE);
}
 

/*******************************************************************************
*
*       NAME            :Enqueue()
*
*       DESCRIPTION     :Adds new node at the tail of the queue
*
*       INPUT           :the new node
*
*       OUTPUT          :
*
*******************************************************************************/
 
void NodeQueue::Enqueue(Node *qn)
{

	// we always add the Node at the rear end

	if(Is_empty() == TRUE){
		printf("EMPTY adding %d to Q\n",qn->Get_node_id());

		rear = qn;
		rear->Set_nextqn((Node *)NULL);
		front= rear;
	}
	else{

		printf("NOT EMPTY adding %d to Q\n",qn->Get_node_id());

		rear->Set_nextqn(qn);
		rear = rear->Get_nextqn();
		rear->Set_nextqn((Node *)NULL);
	}

	++num_elements;		// increment the number of elements
}

/*******************************************************************************
*
*       NAME            :Dequeue()
*
*       DESCRIPTION     :Remove node which is at the head
*
*       INPUT           :
*
*       OUTPUT          :First Node
*
*******************************************************************************/
 
Node* NodeQueue::Dequeue()
{

	// we remove the node from front end and set second to first position

	if(front == NULL){
                front= NULL;
                rear = NULL;
 
                return NULL;

	}
	else{

		Node* temp = front ;
                front = front->Get_nextqn();
                --num_elements;
                if(front == NULL)rear = NULL;
 
		printf("Dequeing %d\n",temp->Get_node_id());

                return temp;

	}
}
 

/*******************************************************************************
*
*       NAME            :Add_to_edit_Q
*
*       DESCRIPTION     :Adds to one of the 4 editing Queues
*
*       INPUT           :Type of the Q and the block to be added
*
*       OUTPUT          :
*
*******************************************************************************/
 
void Add_to_edit_Q( int type,Block *bb)
{

	int done = 0;		// this flag is checks successful completetion

	Node* no = bb->Get_block_node();

	int vis = no->Get_visited();

	// Node is not added to Q if it has been already visited

	if(vis == TRUE){
		
		done = 1 ;		// means abort
	}

	if( done == 0){

	int id = bb->Get_block_id();

	Block* ob = editc->Get_block(id);	// get the block from 
						// originally copied comp

	// if the original dimensions and edited dimensions are same
	// then there is no need to add the edited node in the queue
	// this procedere is done only along edited axis or by default
	// edited node goes to Link_len_Q

	// we will add node to Q only if done != 4
	// that means alteast one value is different and not all are same

    double xn;
    double xd;
    double xx;

    Length* xl;
    double xle;

    double oxn;
    double oxd;
    double oxx;

    Length* oxl;
    double oxle;


	double yn;
    double yd;
    double yx;

    Length* yl;
    double yle;

    double oyn;
    double oyd;
    double oyx;

    Length* oyl;
    double oyle;

    double zn;
    double zd;
    double zx;

    Length* zl;
    double zle;

    double ozn;
    double ozd;
    double ozx;

    Length* ozl;
    double ozle;

	switch(type){

		case X_Q :

        		xn = bb->Get_Xmin();
        		xd = bb->Get_Xmid();
        		xx = bb->Get_Xmax();
 
        		xl= bb->Get_Xlen();
        		xle= xl->Get_length();
 
        		oxn = ob->Get_Xmin();
        		oxd = ob->Get_Xmid();
        		oxx = ob->Get_Xmax();
 
        		oxl= ob->Get_Xlen();
        		oxle= oxl->Get_length();

			if( oxn == xn){ done++  ; }
			if( oxd == xd){ done++  ; }
			if( oxx == xx){ done++  ; }
			if( oxle== xle){done++  ; }
			
			printf("X_Done %d\n",done);
	
			if( done != 4){
			
				Xlen_Q->Enqueue(no);
			
				// add the node to X_length_q
			
			}
			break;
				
                case Y_Q :

        		yn = bb->Get_Ymin();
        		yd = bb->Get_Ymid();
        		yx = bb->Get_Ymax();
 
        		yl= bb->Get_Ylen();
        		yle= yl->Get_length();
 
        		oyn = ob->Get_Ymin();
        		oyd = ob->Get_Ymid();
        		oyx = ob->Get_Ymax();
 
        		oyl= ob->Get_Ylen();
        		oyle= oyl->Get_length();
 
                        if( oyn == yn){ done++  ; }
                        if( oyd == yd){ done++  ; }
                        if( oyx == yx){ done++  ; }
                        if( oyle== yle){done++  ; }
 
                        printf("Add_ %d to Q:matching dimensions %d\n",id,done);
 
                        if( done != 4){
 
                                Ylen_Q->Enqueue(no);
                        
                                // add the node to Y_length_q
 
                        }

                        break;

                case Z_Q :
 
        		zn = bb->Get_Zmin();
        		zd = bb->Get_Zmid();
        		zx = bb->Get_Zmax();
 
        		zl= bb->Get_Zlen();
        		zle= zl->Get_length();
 
	
        		ozn = ob->Get_Zmin();
        		ozd = ob->Get_Zmid();
        		ozx = ob->Get_Zmax();
 
        		ozl= ob->Get_Zlen();
        		ozle= ozl->Get_length();

                        if( ozn == zn){ done++  ; }
                        if( ozd == zd){ done++  ; }
                        if( ozx == zx){ done++  ; }
                        if( ozle== zle){done++  ; }
 
                        printf("Z_Done %d\n",done);
 
                        if( done != 4){
 
                                Zlen_Q->Enqueue(no);
                        
                                // add the node to Z_length_q
 
                        }
                        break;

		case L_Q :
		default	 :

				Link_len_Q->Enqueue(no);

				// add the node to linked_lengths_q	
			break;


	}

	}
	else{

		print_msg("The node has already been visited",NO_VALUE);

	}


}
