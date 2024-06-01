/******************************************************************************
*       FILENAME :    strongcomph.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Declaration of Class StrongComp
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       Sept 20, 1995.
*
******************************************************************************/
 
#ifndef _STRONGCOMP_H_
#define _STRONGCOMP_H_
 
/*****************************************************************************
*                       INCLUDE FILES
******************************************************************************/

#include "nodeh.h"

 
class StrongComp{

	protected :
		
        /*
        **      StrongComp Identification
        */
		int 			str_comp_id ;	// Identification Number

        /*
        **      Link List members
        */
		StrongComp*		nextstrcomp;	// next StrongComp
		StrongCompNode*	str_node_list;	//vertical list

	public :

        /*
        **      Constructors
        */
		StrongComp(){}
		StrongComp(int iii);

        /*
        **      Destructor
        */
		~StrongComp(){}

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
		StrongComp*		Get_nextstrcomp(){ return nextstrcomp;}
		void			Set_nextstrcomp(StrongComp* mm){ nextstrcomp = mm;}
		StrongCompNode* Get_str_node(){ return str_node_list;}
		StrongCompNode*	Get_str_node(int data_node_id);

        int     		Get_str_comp_id(){ return str_comp_id;}

        /*
        **          Link List Operations
        */
        void    		Link_StrongCompNodes( StrongCompNode *nl);
		virtual int		is_member(int ll);

		/*
		**			Application Specific
		*/
		virtual	void	fill_arcs(Graph* gg);

		/*
		**			Utility functions
		*/
		virtual	void	Print();

};

#endif
