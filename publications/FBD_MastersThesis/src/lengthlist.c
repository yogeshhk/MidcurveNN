/*******************************************************************************
*       FILENAME :      lengthlist.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Length_List
*
*       FUNCTIONS   :   Constructor
*			void Link_Length_List(Length_List *lo)
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   MAY 29, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
#include "classes.h"            /* Classes Declarations :header file */
#include <string.h>
 
/*******************************************************************************
*  
*       NAME            :Length_List..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to compute planes etc..Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : id and value
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
   
Length_List::Length_List(char *lnum,double l_value, Length *len)
{

	len_id = len_link_num;

	strcpy(lengthl_name , lnum);	// copies the name because at start
					// there is nothing to concatenate
	num_links = 0 ;			// no linking at the start

	length_value = l_value ;
	
	firstl = NULL;

	nextll	= NULL;

	Add_Link(len);			// add to the link list

	len->Set_length_list(this);

	printf("Came LengthList %d\n",len_id);

}


/*******************************************************************************
*
*       NAME            :void Link_Length_List(Length_List *lo)
*
*       DESCRIPTION     : Adds the lengthlist to the current link list
*                         of length_lists and adds new Length_List at tail.
*
*       INPUT           : Newly created Length_List ( actually only one length)
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void  Link_Length_List(Length_List *newl)
{
 
        /*
                firstll is global pointers to the first Length_List
                It is initialized to NULL in Init_App()
        */
 
	Length_List	*current_len ;

 
      if (firstll == NULL){

		printf(" came to firstll\n");

             	firstll = newl;
		firstll->Set_nextll((Length_List *)NULL);
        	len_link_num++;			// incrementing global counter

	 
        }
      else {
		printf(" came to currll\n");
                current_len = firstll;
                while (current_len->Get_nextll() != NULL){
 
                        current_len = current_len->Get_nextll();
                }
 
              	current_len = current_len->Get_nextll();
		current_len = newl;
		newl->Set_nextll((Length_List *)NULL);
        	len_link_num++;			// incrementing global counter

      }

}

/*******************************************************************************
*
*       NAME            :void Add_Link(Length *lo)
*
*       DESCRIPTION     : Adds the length to the current link list
*                         of length and adds new Length at tail.
*
*       INPUT           : Length * 
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void  Length_List::Add_Link(Length *newl)
{
 
        /*
                firstl is pointers to the first Length
                It is initialized to NULL in constructor of Length_list
        */
 
        Length *current_len ;
 
 
      if (firstl == NULL){

                firstl = newl;
                firstl->Set_nextl((Length *)NULL);
		num_links++; 
 
        }
      else {

                current_len = firstl;
                while (current_len->Get_nextl() != NULL){
 
                        current_len = current_len->Get_nextl();
                }
 
                current_len = current_len->Get_nextl();
                current_len = newl;
                newl->Set_nextl((Length *)NULL);
		num_links++; 
      }
 
}

