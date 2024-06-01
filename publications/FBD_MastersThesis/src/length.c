/*******************************************************************************
*       FILENAME :      length.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Length
*
*       FUNCTIONS   :   Constructor
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
*       NAME            :Length..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to compute planes etc..Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Plane id ,type and plane value
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
  
Length::Length(char *lid) 
{
 
	strcpy(length_name, lid);
	
	fixed = TRUE ;	// not allowed to modify

	nextl = NULL;

	lenlist = NULL ;	// it will be assigned afterwords

	printf("Lengthname %s\n", length_name);
 
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
*******************************************************************************/
 
double Length::Get_length()
{


	Length* ln = lenlist->Get_firstl();

	while(ln){

		char text[6];
		strcpy(text,ln->Get_length_name());

		if(strcmp(text,length_name) == 0){	// strings are equal

			return lenlist->Get_length_value() ;
		}
		else{

			printf("Linking was not found\n");
	
		}

		ln = ln->Get_nextl();
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
*******************************************************************************/
 
void Length::Set_length(double dd)
{
 
 
        Length* ln = lenlist->Get_firstl();
 
        while(ln){
 
                char text[6];
                strcpy(text,ln->Get_length_name());
 
                if(strcmp(text,length_name) == 0 ){
 
                        printf("Linking was foound\n");
                        
                        lenlist->Set_length_value(dd);
                }
                else{
 
                        printf("Linking was not found\n");
                                                                    
                }
 
                ln = ln->Get_nextl();
        }

	// This function needs something more because if we change value of 
	// length then all the other lengths in length_list will get this
	// new value. Its OK for now !!! 
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
*******************************************************************************/

void Length::Scale(double val){


	double tmp = Get_length();
	Set_length( tmp*val);
}
 


