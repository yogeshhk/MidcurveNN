/******************************************************************************
*       FILENAME :    cycleh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Declaration of Class Cycle
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       Sept 20, 1995.
*
******************************************************************************/
 
#ifndef _CYCLE_H_
#define _CYCLE_H_
 
/*****************************************************************************
*                       INCLUDE FILES
******************************************************************************/

#include "nodeh.h"

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
 
class Cycle {

	protected :

		/*
		**		Cycle Identification
		*/
		int 		cycle_id;		// identification number

		/*
		**		Link List memebers
		*/
		Cycle*		nextcycle ;	
		CycleNode*	cycle_node_list;	// vertical list

		/*
		**		Information it stores
		*/
		int			*member_ids;	// Array of member_nodes ids
									// putting it in an array is not really
									// a good idea,it would be better if you
									// implement this as circular link list
									// For the time being I assume that, no.
									// of blocks in cycle wont go more than
									// 20.. I think thats ok..

	public :

        /*
        **      Constructors
        */
		Cycle(){}
		Cycle(int iii);

        /*
        **      Destructor
        */
		~Cycle(){}

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
		Cycle*	Get_nextcycle()				{ return nextcycle;}
		void	Set_nextcycle(Cycle* cx)	{ nextcycle = cx;}
		void	Set_member_ids(int *aa);

		int		Get_cycle_id()				{ return cycle_id ;}
		int*	Get_member_ids()			{ return member_ids;}
		int		Get_member(int me)			{return member_ids[me];}
		int		Get_first_member()			{ return member_ids[0];}

		int		Get_left_member_id(int me);
		int		Get_right_member_id(int me);
		int		Get_num_members();

		/*
		**		Utility functions
		*/
		int		Is_member(int me);
		void	print_member_ids();

		/*
		**		Link List functionality
		*/
		void	Link_CycleNodes( CycleNode *nl);

};

#endif
