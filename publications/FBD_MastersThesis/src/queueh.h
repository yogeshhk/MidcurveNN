/*******************************************************************************
*       FILENAME :    queueh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Queue
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       July 24, 1995.
*
*******************************************************************************/
 
#ifndef _QUEUE_H_
#define _QUEUE_H_
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "nodeh.h"
 
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Queue{

	protected :

        /*
        **      Plane Identification
        */
		int	q_type ;		// whether X or Y or editing or other

        /*
        **      Counters
        */
		int	num_elements ;	// current number of elements in Q

		
	public :

        /*
        **      Constructors
        */
		Queue(){}
		
        /*
        **      Destructor
        */
		~Queue(){}

		/*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrictions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */

		int	Get_q_type(){ return q_type;}
		int	Get_num_elements(){ return num_elements ;}
}; 


/******************************************************************************
                CLASS DECLARATION
******************************************************************************/

class NodeQueue : public Queue
{


	protected :

        /*
        **      Link List members
        */
		Node*	front;	// first node in the queue
		Node*	rear;	// last node in the queue


	public :

        /*
        **      Constructors
        */
		NodeQueue(){ front = NULL ; rear= NULL ;}
		NodeQueue(int ty);

        /*
        **      Destructor
        */
		~NodeQueue(){}

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrictions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		Node*	Get_front(){ return front ;}
		Node*	Get_rear(){ return rear;}

        /*
        **          Link List Operations
        */
		void	Enqueue(Node *qn);
		Node*	Dequeue();
		int		Is_empty();	// is queue empty
};


#endif
 
 

