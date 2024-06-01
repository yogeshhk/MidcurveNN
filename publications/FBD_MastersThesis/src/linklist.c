/*******************************************************************************
*       FILENAME :      linklist.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to template Class List
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   Sept 3, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "linklisth.h"            /* Classes Declarations :header file */
#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"            /* Classes Declarations :header file */
#include <string.h>
 
/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/

template<class T> void List<T>::Add_Last(T* tt){

	Item<T>* om = new Item<T>(tt);	// Put it in an Item..

	om->item_id = num_items;	// assign the id

	if( firstitem == NULL){

		firstitem = lastitem = om ;
			// List is a friend class thus we dont need Get &
			// Set functions for any private member of class Item
	}
	else {

		lastitem->nextitem = om;
		om->previtem = lastitem;
		lastitem = om ;


/*
		Item<T>* te = firstitem ;

		while(te->nextitem){
			te = te->nextitem;
		}
		te->nextitem = om;
		te = te->nextitem ;
		te = om ;
		om->nextitem = (Item<T>*)NULL;
*/
	}

	++num_items;	// increment the number of items
}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 
template<class T> void List<T>::Add_First(T* tt){
 
	// Simulation of this algo shows that firstitem is going last ??

        Item<T>* om = new Item<T>(tt);  // Put it in an Item..
 
        om->item_id = num_items;        // assign the id
 
        if( firstitem == NULL){
 
                firstitem = lastitem = om ;
                        // List is a friend class thus we dont need Get &
                        // Set functions for any private member of class Item
        }
        else {
 
                firstitem->nextitem = om;
                om->previtem = firstitem;
                firstitem = om ;
 
        }
 
        ++num_items;    // increment the number of items
}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 
template<class T> void List<T> :: Print_list(){

	Item<T> *see;

	printf("came to display\n");

	see = firstitem;

	while(see){


		printf("Data \n");

		see = see->nextitem;

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

template<class T> List<T>::~List(){

	RemoveAll();
	num_items = 0;
}

/*******************************************************************************
*
*       NAME            : Insert
*
*       DESCRIPTION     :Inserts an object before the given node
*
*       INPUT           :T *ite is an item to insert before Item<T>* before
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 

template<class T> void List<T>::Insert(T *ite,Item<T>* before){

	Item<T>* newitem = new Item<T>(ite);

	newitem->nextitem = before ;
	newitem->previtem = before->previtem;
	before->previtem->nextitem = newitem;
	before->previtem = newitem ;

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

template<class T> T* List<T> :: Find(int id){

	Item<T>* tracer = firstitem;

	while(tracer){
		
		if(tracer->item->Get_id() == id){
			printf("Non NULL Find\n");
			return tracer->item;
		}
		tracer = tracer->nextitem;
	}
	
	printf("NULL Find\n");
	return NULL;
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

template<class T> Item<T>* List<T> :: Find(T* id){
 
        Item<T>* tracer ;
 
	for( tracer = firstitem; tracer;tracer = tracer->nextitem){

		if( tracer->item == id){ return tracer ;}
	}
	return NULL;

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

template<class T> void List<T> :: Remove(T* de){

	Item<T>* tmp = Find(de);

	if(tmp) {

		Remove(tmp);
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

template<class T> void List<T> :: Remove( Item<T>* de){


		if(de == NULL)return;

		if( firstitem == lastitem){
			printf("In Remove:firstitem == lastitem\n");			
			firstitem = lastitem = NULL;
		}
		else if ( de == firstitem){
			printf("In Remove:de == firstitem\n");			

			firstitem = firstitem->nextitem;
			firstitem->previtem = NULL;
		}
		else if ( de == lastitem){

			printf("In Remove:de == lastitem\n");			
			lastitem = lastitem->previtem;
			lastitem->nextitem = NULL ;
		}
		else {

			printf("In Remove:ELSE\n");			
			de->nextitem->previtem = de->previtem;
			de->previtem->nextitem = de->nextitem;
		}

		delete de ;

		// here I don't say --num_items; because while
		// adding new elemnts "num_items" is used to give ids
		// There may be possibility that two items may get
		// same item_ids.Count() may be provided to count num of elemnts
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

template<class T> void List<T>::RemoveAll(){

	Item<T>* tmp;

	for( tmp = firstitem ; tmp ; tmp = firstitem){
	
		firstitem = tmp->nextitem ;
		delete tmp;
	}

	firstitem = lastitem = NULL ;
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

template<class T> void Stack<T>:: Push(T* itm){
 
	Item<T>* nn = new Item<T>(itm);
        nn->item_id = num_items;        // assign the id

        if( firstitem == NULL){
 
                        //nn->nextitem = (Item<T> *)NULL;
                        firstitem = lastitem = nn;
                        firstitem->nextitem = (Item<T> *)NULL;
                        firstitem->previtem = (Item<T> *)NULL;
                        lastitem->nextitem = (Item<T> *)NULL;
                        lastitem->previtem = (Item<T> *)NULL;
 
                        ++num_items;
        }
        else{
 
                Item<T>* temp = firstitem;
                ++num_items;
		firstitem = nn;
                firstitem->nextitem = temp;
		temp->previtem = firstitem;
                firstitem->previtem = (Item<T>*)NULL;
                //top = nn;
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

template<class T> T* Que<T>::Dequeue(){
        Item<T>* temp;
 
        if(firstitem){
 
                temp = firstitem;
                firstitem = firstitem->nextitem;
 
                --num_items;
                return temp->item;
 
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

template<class T> T* Stack<T>:: Pop(){

        Item<T>* temp;
 
        if(firstitem){
 
                temp = firstitem;
                firstitem = firstitem->nextitem;
 
                --num_items;
                return temp->item;
 
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

template<class T> T* Stack<T>:: Get_top(){

	if(firstitem){

		return firstitem->item;
	}
	else{

		return NULL ;

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

template<class T>int* Stack<T>::Get_array(){
        Item<T> *see;

	/*
 
        see = firstitem;
 
        while(see){
 
 
                printf("Data = %d\n",see->item->Get_id());
 
                see = see->nextitem;
 
        }


	*/

	int *array = new int[20];

	for(int j=0;j < 20;j++)array[j]=0;	// array initialization

	int i=0;

	for(see = firstitem; see != NULL ;see = see->nextitem ){

		printf("IDDD for %ds %d\n",i,see->item->Get_node_id());
		array[i] = see->item->Get_node_id();
		++i;
	}

	return array;

}
/*****************************************************************************
		Class Prototyping Required for Templates
		It should be (physically) done here.
	
		This is a g++ bug and for more info Read below..

******************************************************************************/

template class List<Node> ;
template class Stack<Node> ;
template class Que<Node> ;
template class Item<Node>;

template class List<StrongCompNode> ;
template class Stack<StrongCompNode> ;
template class Que<StrongCompNode> ;
template class Item<StrongCompNode>;

template class List<CycleNode> ;
template class Stack<CycleNode> ;
template class Que<CycleNode> ;
template class Item<CycleNode>;

template class List<DimNode> ;
template class Stack<DimNode> ;
template class Que<DimNode> ;
template class Item<DimNode>;
/*****************************************************************************

	BUG Report to   bug-g++@prep.ai.mit.edu


From: rjl@iassf.easams.COM.AU (Rohan LENARD)
Date: 12 Sep 1995 17:51:26 -0400
Newsgroups: gnu.g++.bug
Subject: Re: TEMPLATE fail to create instance


 I get undefined symbols when using templates
 ============================================

    (Thanks to Jason Merrill for this section).

    g++ does not automatically instantiate templates defined in other
 files.  Because of this, code written for cfront will often produce
 undefined symbol errors when compiled with g++.  You need to tell g++
 which template instances you want, by explicitly instantiating them in
 the file where they are defined.  For instance, given the files

    `templates.h':
      template <class T>
      class A {
      public:
        void f ();
        T t;
      };

      template <class T> void g (T a);

    `templates.cc':
      #include "templates.h"

      template <class T>
      void A<T>::f () { }

      template <class T>
      void g (T a) { }

    main.cc:
      #include "templates.h"

      main ()
      {
        A<int> a;
        a.f ();
        g (a);
      }
 
    compiling everything with `g++ main.cc templates.cc' will result in
 undefined symbol errors for `A<int>::f ()' and `g (A<int>)'.  To fix
 these errors, add the lines
 
      template class A<int>;
      template void g (A<int>);
 
    to the bottom of `templates.cc' and recompile.
 

******************************************************************************/
