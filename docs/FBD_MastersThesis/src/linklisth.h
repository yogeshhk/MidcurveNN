/*******************************************************************************
*       FILENAME :    LinkList.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Template Class List
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       Sept 3, 1995.
*
*******************************************************************************/
 
#ifndef _LINKLIST_H_
#define _LINKLIST_H_
 
#include <iostream.h>
#include <stdio.h>

/*******************************************************************************
        GENERIC LINK LIST :
 
                It is always necessary to make link lists of a ( or many)
                objects for various purposes.Its not a good idea to add
                member variables (like next_node..) in the Class ( to avoid 
				confusion between lists) for every list and there is redundancy
				in the sense that similar functions have to be written for every 				list.
 
                I am trying to use mechanism of templates as generality to the
                data structures. Templates can be viewed as container classes
                ( generic classes) in which actual object is passed and rest
                of the functions are similar ( and coded only once).
 
                Care should be taken that the functions defined in template
                class should be operational for any agrument it takes.

		There are some bugs in g++ compiler regarding Template 
		implementation .Please refer to "bug" file in ./PSEUDOCODE/
		directory.People at bug-g++@prep.ai.mit.edu do respond to the
		queries regarding this bug..

		For more info : Newsgroup : gnu.g++.bug

*******************************************************************************/
 
/*******************************************************************************
                CLASS DECLARATION
******************************************************************************/

template<class T>
class List {
 
        protected:
		int	num_items;	// number of items in the list 
                Item<T> *firstitem;     // first item in the list
                Item<T> *lastitem;     	// last item in the list
 
        public :
                List(){ firstitem = NULL ;lastitem = NULL ;num_items = 1 ;}
                virtual	~List();

		// No default constructor or copy constructor or operator=()
		// is defined all are void functions now..

        virtual void   		Add_Last( T *om);
        virtual void   		Add_First(T *m);
		virtual void		Insert(T* om,Item<T>* before);
		virtual T*			Find(int id);
		virtual Item<T>*	Find(T* ss);
		virtual void		Remove(T* de);
		virtual void		Remove(Item<T>* de);
		virtual void		RemoveAll();
        virtual void        Print_list();
		virtual	int			Empty(){return (firstitem?0:1);}
};
 
/*******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
template<class T>
class Item{

	friend class List<T>;	// allowing acess of private ot class List
	friend class Stack<T>;	// allowing acess of private ot class Stack
	friend class Que<T>;	// allowing acess of private ot class Que

	protected :

		T*	item ;		// actual item that is being passed
		int	item_id;	// id of the item in the list
		Item<T>	*nextitem;	// next item pointer
		Item<T>	*previtem;	// previous item pointer
		
	public	:
		Item(){}
		Item(T* tt){ nextitem = previtem = NULL;item = tt ;item_id = 0;}
		~Item(){}


		T*	Get_item(){ return item;}

};

/*******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
template <class T> class Que : public List<T>{

	private :
		int q_type;

	public :

		Que(){}
		Que(int mm){ q_type = mm;}
		virtual ~Que(){}

		virtual int  Get_q_type(){ return q_type;}
        virtual int  Get_num_elements(){ return num_items;}
		virtual void Enqueue(T *qq){ Add_Last(qq);}
		virtual void Deque(){ Remove(firstitem);}
		virtual T*   Dequeue();
};

/*******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
template <class T> class Stack : public List<T>{


	public:

		Stack(){ }
		virtual ~Stack(){}

		virtual T* 		Get_top();
		virtual void 	Push(T *ite);
		virtual T*		Pop();
		virtual int*	Get_array();	// used specifically for Cycle
										// creation.Not very good method
										// is employed because I am
										// resrticting only 20 blocks

};


#endif
 
 

