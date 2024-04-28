/*******************************************************************************
*       FILENAME :    lengthlisth.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class Length_List
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _LENGTHLISTH_H
#define  _LENGTHLISTH_H
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "application.h"
 
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class Length_List {


	/*
	**		Length List Identification
	*/
	int		len_id ;
	char	lengthl_name[20];	// name in this global list of lengths


	/*
	**	Pecularity of this name is that it consists of bunch
	**	of 4 digits representing the block_lengths associated with
	**	this global list. Every time linking is done that block_length
	**	is concatenated to this
	*/

	/*
	**		Counters
	*/
	int			num_links ;	// number of length links

	/*
	**		Information Representation
	*/
	double		length_value ;

	/*
	**		Link List Variables
	*/
	Length*		firstl;		// first length in the list of Lengths
	Length_List	*nextll ;

	public :

		/*
		**		Constructor
		*/
		Length_List(){}
		Length_List(char *llid,double llvalue,Length *len);

		/*
		**		Destructor
		*/
		~Length_List(){}

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
		double			Get_length_value()		{ return length_value ;}
		char*			Get_length_name()		{ return lengthl_name ;}
		Length_List*	Get_nextll()			{ return nextll ;}
		Length*			Get_firstl()			{ return firstl ; }
		int				Get_num_links()			{ return num_links ;}
		int				Get_len_id()			{ return len_id;}

		void			Set_length_name(char *lnum){ strcat(lengthl_name,lnum);}
		void			Set_length_value(double lk){length_value = lk ;} 
		void			Set_nextll(Length_List *ll){ nextll = ll ; }
		void			Set_len_id(int ii)		   { len_id = ii;}

		/*
		**			Link List Operations
		*/
		void			Add_Link( Length *len );
		void			Del_Link( Length *len ){}

}; 
#endif
 
 

