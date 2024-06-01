/*******************************************************************************
*       FILENAME :    graphh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Graph
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _GRAPHH_H_
#define _GRAPHH_H_
 
 
/*******************************************************************************
                FOLLOWING  HEADER FILES WERE INCLUDED
*******************************************************************************/
 
#include "nodeh.h"
#include "componenth.h"
#include <stdio.h>

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class Graph{

	protected :

		/*
		**			Graph Identification
		*/
		int		graph_id ;		// graph number

		/*
		**			Infromation Representation
		*/
		Node	*graph_node ;	// first node of the list of nodes 


	public :

		/*
		**			Constructors
		*/
		Graph()	;							

		/*
		**			Destructor
		*/
		~Graph(){}						

		/*
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrictions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */

		virtual		int		Get_graph_id(){ return graph_id ; }
		virtual		Node*	Get_graph_node(){ return graph_node ;}
		virtual		Node*	Get_node(int ii);

		/*
		**			Link List Operations
		*/
		virtual		void	Link_Node(Node *gn);

		/*
		**			Utility functions
		*/
		virtual		void	PrintYourself(FILE*)=0;

}; 

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 

class ComponentGraph :public Graph{
 
	protected :

		/*
		**			Information representation
		*/
        Component       *graph_comp ;   // component which this represents
 
 
    public :

		/*
		**			Constructor
		*/
		ComponentGraph(){}               				// Constructor
        ComponentGraph(Component *gc ,Block *gb);      	// Constructor

		/*
		**			Destructor
		*/
        ~ComponentGraph(){}              				// Destructor
 
		/*
		**			Utility functions
		*/
		virtual		void	PrintYourself(FILE*);	// same as print_graph()
};


/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
 
class DimensionGraph: public Graph{
 
    protected :
 
        /*
        **      Few of the following variables can be
        **      avoided by better program design and all the
        **      functionality of base class could have been used
        **      efficiently by mechanism of virtual functions.
        **      If time permits this will be definitely one of the
        **      first few things to be done.
        **      Right now ,power of inheritance is not used to a full
        **      extent
        */

		/*
		**			Counters
		*/

		int		num_nodes;				// Number of nodes in graph
		/*
		**				Information Representation
		*/
		DimNode			*X_DimList;		// List of Dim nodes in X direction
		DimNode			*Y_DimList;		// List of Dim nodes in Y direction
		DimNode			*Z_DimList;		// List of Dim nodes in Z direction
		DimNode			*O_DimList;		// List of Dim nodes in Other  direction

		Component		*dim_comp;		// Component it represents

    public :
 
		/*
		**			Constructor
		*/
        DimensionGraph() ;                             	// Constructor
        DimensionGraph(Component *gc );       			// Constructor

		/*
		**			Destructor
		*/
        ~DimensionGraph(){}                             // Destructor
 

		/*
		**			Link List Operations
		*/
		void			Add_to_dimlist(int type,DimNode* dn);
		void			Fill_Dim_Arcs();
		DimNode*		Get_DimNode(int id);
		DimNode*		Get_matching_node(Face* lis);
		

		void			DeleteArc(int node1,int node2);
		void			BuildArc(int node1,int node2);
		/*
		**			Get Data functions
		*/
		int*		Get_node_ids(int axis);

		DimNode*	Get_X_DimList()			{return X_DimList;}
		DimNode*	Get_Y_DimList()			{return Y_DimList;}
		DimNode*	Get_Z_DimList()			{return Z_DimList;}
		DimNode*	Get_O_DimList()			{return O_DimList;}

		/*
		**			Graph Traversal Functions
		*/

		DimArc*		ComputePath(int node1,int node2);
		/*
		**			Utility functions
		*/
		virtual	void	PrintYourself(FILE*);	

		/*
		**			File Operations
		*/

		void		Write_to_file(FILE*);
		void		Read_from_file(FILE*);


};

#endif
 
 

