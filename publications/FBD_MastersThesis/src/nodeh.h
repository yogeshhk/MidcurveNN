/*******************************************************************************
*       FILENAME :    nodeh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Node
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _NODEH_H_
#define _NODEH_H_
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "blockh.h"
#include "arch.h"
#include "linklisth.h"
 
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Node{

	protected :

	/*
	**		Node Identification
	*/
	int		node_id ;		// node number

	/*
	**		Counters
	*/
	int		arc_count ;		// number of arcs eminating from this node

	/*
	**		Link List Memebers
	*/
	Node	*node_list ;	// first node of list of nodes connctd to this
	Node	*nextnl;		// next node of list of nodes connctd to this
	Node	*nextn;			// nextn is for linear list of nodes in graph
	Node	*nextqn;		// nextqn is for next in queue of nodes 
	Arc		*arc_list;		// list of all edges eminating from this node

	// following flags are used for editing purpose
	// This is not a very correct way of designing the class because
	// NODE as such does not have characteristics of following variables
	// They should go to the derived class say EDIT_NODE or similar
	// If time permits and if there are no major changes in the code I plan
	// to modify this to a more clean design


	int	available ;			// is it available for modification
	int	visited ;			// has it been visited means all nodes
							// adjacent to it are also resolved
							// work is complete and you can not touch it

	int	resolved ;			// imposed the topology and updated
	int	modify ;			// TRUE allowed to modify
							// FALSE not allowed to modify
							// DONE modification is complete

	int	Num;				// Used in StrongComp detection
	int	Low;				// Used in StrongComp detection
				
	public :

		/*
		**		Constructor
		*/
		Node(){}
		Node(Block *nb);	// Second constructor for first node
		
		/*
		**		Destructor
		*/
		~Node(){}

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
		int		Get_node_id()			{ return node_id ; }
		int		Get_id()				{ return node_id ; }
		Node*	Get_node_list()			{ return node_list;}
		Arc*	Get_arc_list()			{ return arc_list;}

		Node*	Get_nextn()				{ return nextn ;}
		void	Set_nextn( Node *nn)	{ nextn = nn; }

		Node*	Get_nextqn()			{ return nextqn ;}
		void	Set_nextqn( Node *nn)	{ nextqn = nn; }

		Node*	Get_nextnl()			{ return nextnl ;}
		void	Set_nextnl( Node *nnl)	{ nextnl = nnl ; }

        int     Get_arc_count()			{ return arc_count;}
        void    Set_arc_count(int fx)	{ arc_count = fx ;}

        int     Get_available()			{ return available;}
        void    Set_available(int fx)	{ available = fx ;}
 
		int		Get_Num()				{ return Num ;}
		void	Set_Num(int num)		{ Num = num ;}

		int		Get_Low()				{ return Low;}
		void	Set_Low(int low)		{ Low = low ;}

        int     Get_visited()			{ return visited;}
        void    Set_visited(int fx)		{ visited = fx ;}
 
        int     Get_resolved()			{ return resolved;}
        void    Set_resolved(int fx)	{ resolved = fx ;}
 
        int     Get_modify()			{ return modify;}
        void    Set_modify(int fx)		{ modify = fx ;}
 

		/*
		**		Reset functionality
		*/
		void	Initialize_flags(int boo);

		/*
		**		Link List operations
		*/
		void	Link_to_Nodelist(Node *n);
		void	Link_to_Arclist(Arc *a);

        /*
        **      All the Node classes will be derived from
        **      "this" class only. Lot of functionality is
        **      class specific and gets translated differently by
        **      each class.Power of inheritance can be achieved by
        **      Mechanism of virtual functions
        */

		/*
		**		Utility functions
		*/
		virtual	void	PrintYourself(FILE*){}


}; 

/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class FeatureNode : public Node{
 
	protected :

		/*
		**		Information Represntation
		*/
        Block   *node_block ;   // The block which this node represents
 
    public :

		/*
		**		Constructor
		*/
        FeatureNode(){}
        FeatureNode(Block *nb);	// Second constructor for first node
 
		/*
		**		Destructor
		*/
        ~FeatureNode(){}
 
		/*
		**		Get Data Functions
		*/
		Block*			Get_node_block(){ return node_block ;}

		/*
		**		Utility functions
		*/
		virtual	void	PrintYourself(FILE*){}
 
};
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class StrongCompNode : public Node{
 
	protected :

		/*
		**		StrongCompNode Identification
		*/
		int		str_node_id;	// StrongCompNode id 
		
		/*
		**		Link List Members
		*/
		Node*			str_node;		// actual node
		StrArc*			str_arc_list;	// arc list associted with this
		StrongCompNode* nextstrn;		// next strong comp node
		StrongCompNode* nextsn;			// next strcompnode horizontally
		StrongCompNode* str_node_list;	// list of str_nodes associated

		/*
		**		Utility Data structures
		*/
		Stack<StrongCompNode>* B ;	// as used in the book
 
	public :

		/*
		**		Constructors
		*/
   		StrongCompNode(){nextstrn = nextsn = str_node_list = NULL ;}
        StrongCompNode(Node* nn,int id);
 
		/*
		**		Destructor
		*/
        ~StrongCompNode(){}

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
		int				Get_str_node_id(){ return str_node_id;} 
		int				Get_node_id(){ return str_node->Get_node_id();} 
		Node*			Get_str_node(){ return str_node;}
		StrArc*			Get_str_arc_list(){ return str_arc_list;}	
		StrongCompNode*	Get_str_node_list(){ return str_node_list;}	
        StrongCompNode* Get_nextsn(){ return nextsn ;}
        StrongCompNode* Get_nextstrn(){ return nextstrn ;}

        void    		Set_nextsn(StrongCompNode* cn){ nextsn = cn ;}
        void    		Set_nextstrn(StrongCompNode* cn){ nextstrn = cn ;}

		/*
		**		Link List Operations
		*/
        void    Link_to_Nodelist(StrongCompNode *n);
        void    Link_to_Arclist(StrArc *a);

		/*
		**		Utility functions
		*/
		virtual	void	PrintYourself(FILE*){}

		/*
		**		Stack Operations
		*/
		Stack<StrongCompNode>* Get_B(){ return B;}
};


/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class CycleNode : public Node{
 
	protected :
 
        /*
        **      CycleNode Identification
        */

        int             cyl_node_id;    // StrongCompNode id
                
        /*
        **      Link List members
        */
        Node*           cyl_node;       // actual node
        Arc*            cyl_arc_list;   // arc list associted with this
        CycleNode* 		nextcyln;       // next strongcompnode in cycle
        CycleNode* 		nextcn;       	// next strcompnode horizontally
        CycleNode* 		cyl_node_list;  // list of str_nodes associated
 
	public :

        /*
        **      Constructors
        */
   		CycleNode(){}
		CycleNode(Node* nn);
 
		/*
        **      Destructor
        */
        ~CycleNode(){}
 
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
		void 		Set_nextcn(CycleNode* cn){ nextcn = cn ;}
		CycleNode*	Get_nextcn(){ return nextcn ;}

		/*
		**		Utility functions
		*/
		virtual	void	PrintYourself(FILE*){}

};

/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class DimNode : public Node{
 
    protected :
 
        /*
        **    DimNode Identification
        */
		int				dim_node_id;

        /*
        **      Link List members
        */
		DimArc*			dim_arcs_out;
		DimNode*		nextdn;

		/*
		**		Graph Traversal flags
		*/

		int		visited;
		int		arc_count ;		// number of arcs eminating from this node
		int		prim_count ;	// number of primitives

		/*
		**		Information Representation
		*/
		DimPrimitive	*node_prim;		// 	Primitive this node represents


    public :

        /*
        **      Constructors
        */
    	DimNode();
		DimNode(Face* face,int blkid,int id);

        /*
        **      Destructor
        */
        ~DimNode(){}
 
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
		int			Get_dim_node_id(){return dim_node_id;}
		DimNode*	Get_nextdn(){return nextdn;}
		double		Get_dim_value(){if(node_prim)return 
									node_prim->Get_dim_value();}
		void		Set_nextdn(DimNode* dn){nextdn = dn;}
		DimArc*		Get_dim_arcs_out(){ return dim_arcs_out;}

		/*
		**		Link List Operations
		*/
		void		Add_to_dim_arclist_out(DimArc* ad);
        void    	RemoveArc(DimNode* endnode);
        void    	Remove_all_Arcs();
		void		Add_to_node_prim_list(DimPrimitive*);

		/*
		**		Graph Traversal functions
		*/

		int		Is_Visited(){return visited;}
		void	Set_Visited(int flg){visited = flg;}

		/*		
		**		Utility functions
		*/
		virtual	void	PrintYourself(FILE*);
};

#endif
 
 

