/******************************************************************************
*       FILENAME :    arch.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Arc
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 31, 1995.
*
******************************************************************************/
 
#ifndef _ARCH_H_
#define _ARCH_H_

/*****************************************************************************
*                       INCLUDE FILES
******************************************************************************/

#include "nodeh.h"
#include "topolinkh.h"

/*******************************************************************************
*			Class Arc
*******************************************************************************/


class Arc {

	protected :

		/*
		**		Arc Identification
		*/
		char		arc_name[10];		// unique arc name
		int			arc_id ;			// unique id
		int			edge_type;			// used in editing as TREE, CROSS..

		/*
		**		Graph(Arc) Representation
		*/
		Node		*node_A ;			// Source node for this arc
		Node		*node_B ;			// Destination node for this arc

		/*
		**		Link List memebers
		*/
        Arc     	*nextal;       		// next arc of list of arcs to this arc

		/*
		**		Topological information it stores
		*/
		Topolink	*arc_topo;			// topolink which this represents

	public :

		/*
		**		Constructors
		*/
		Arc(){}		
		Arc(char* name,Node *a, Node *b, Topolink *tp);

		/*
		**		Destructors
		*/
		~Arc(){}

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrucutions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		char*	Get_arc_name()			{ return arc_name; }
		int		Get_arc_id()			{ return arc_id ;}

		int		Get_edge_type()			{ return edge_type ;}
		void	Set_edge_type(int ed)	{ edge_type = ed ;}

		Node*	Get_node_A()			{ return node_A ;}
		Node*	Get_node_B()			{ return node_B ;}

        Arc*    Get_nextal()			{ return nextal ;}
        void    Set_nextal( Arc *nal)	{ nextal = nal ; }

		Topolink* Get_arc_topo()		{ return arc_topo ;}
 
		Arc*	Get_mate();			


}; 


/*******************************************************************************
*           Class Arc
*******************************************************************************/
 
class StrArc:public Arc{

	protected :

		/*
		**		Most of the following variables can be
		**		avoided by better program design and all the 
		**		functionality of base class could have been used
		**		efficiently by mechanism of virtual functions.
		**		If time permits this will be definitely one of the
		**		first few things to be done.
		**		Right now ,power of inheritance is not used to a full
		**		extent
		*/
		int 			arc_count ;

        /*
        **      Link List members
        */
		StrArc*			nextsal;

        /*
        **      Graph(Node) Representation
        */
		StrongCompNode*	strnodeA;
		StrongCompNode*	strnodeB;

        /*
        **      Connection to Arc
        */
		Arc*			parent;

	public:

        /*
        **      Constructors
        */
		StrArc(){}
		StrArc(Arc* aa,StrongCompNode* aa,StrongCompNode* bb);

        /*
        **      Destructor
        */
		~StrArc(){}

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrucutions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		void 			Set_nextsal(StrArc* aa)		{ nextsal = aa ;}
		StrArc*			Get_nextsal()				{ return nextsal;}

		StrongCompNode* Get_Node_A()				{ return strnodeA;}
		StrongCompNode* Get_Node_B()				{ return strnodeB;}

		int 			Get_arc_count()				{ return arc_count ;}
		Arc*			Get_arc()					{ return parent;}



		virtual	void	PrintYourself(FILE*){}

};

/*******************************************************************************
                CLASS DECLARATION
*******************************************************************************/
 
class DimArc:public Arc{

	protected:

		/*
		**		Identification
		*/
		int		dim_arc_id;
        /*
        **      Graph(Node) Representation
        */
		DimNode		*start;
		DimNode		*end;

		/*
		**		Dimensioning and Tolerancing Information
		*/
		double		dim_value;
		double		tolerance;

        /*
        **      Link List members
        */
		DimArc*		nextda;			


	public:

        /*
        **      Constructors
        */
		DimArc(){}
		DimArc(int id,DimNode* A,DimNode* B,double dimension,double tol);

        /*
        **      Destructor
        */
		~DimArc(){}

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrucutions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		int			Get_dim_arc_id(){	return dim_arc_id;}	
		DimArc*		Get_nextda(){return nextda;}
		void		Set_nextda(DimArc* da){nextda =da;}
		DimNode*	Get_nodeA(){return start;}
		DimNode*	Get_nodeB(){return end;}
		double		Get_tolerance(){return tolerance;}
		double		Get_dim_value(){return dim_value;}

		virtual	void	PrintYourself(FILE*);
};


#endif
 
 

