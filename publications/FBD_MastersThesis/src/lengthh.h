/*******************************************************************************
*       FILENAME :    lengthh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Length
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _LENGTHH_H
#define  _LENGTHH_H
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "application.h"

/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Length {

	/*
	**		Length Identification
	*/
	char	length_name[6];	// is set to global list of lenths
	int		fixed ;			// flag to see whether length is modificable
							// or not
							// TRUE means not allowed to modify
							// FALSE means allowed to modify

	/*
	**		Link List members
	*/
	Length		*nextl ;	// Next length
	Length_List *lenlist;	// from where to get value of length

	public :

		/*
		**		Constructor
		*/
		Length(){}
		Length(char *lenid);
		Length(int lenid,int lentype){}		// for length linking
											// it will search for lenid in
											// global list of Length_list
											// and set length_list to that
											// Length_List pointer
		/*
		**		Destructor
		*/
		~Length(){}

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
		char*		Get_length_name()			{ return length_name; }
		void		Set_length_name(char *num)	{ strcpy(length_name , num );}

        int     	Get_fixed()					{ return fixed ;}
        void    	Set_fixed(int fx)			{ fixed = fx ;}
 
		Length*		Get_nextl()					{ return nextl ;}
		void		Set_nextl( Length *ll)		{ nextl = ll ;}

		double		Get_length();
		void		Set_length( double lt);
		
		void		Scale(double);

		void			Set_length_list(Length_List *ll){ lenlist = ll;}
		Length_List*	Get_length_list()		{ return lenlist ;}

}; 
#endif
 
 

