/*******************************************************************************
*       FILENAME :      editing.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Algorithms concerned with Multinode editing
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   July 24, 1995.
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
*       NAME            :Abort_editing()
*
*       DESCRIPTION     :
*
*       INPUT           : 
*
*       OUTPUT          : 
*
*******************************************************************************/
 
void Abort_editing()
{

	// After coding " delete " for component , first delete current
	// component here. because if this is not done every call to abort
	// function will create new component when it retrieves from file
	// as done below


	// You may need to delete Component* editc which is not necessary
	// after aborting the process


        FILE *fi;
 
        fi = fopen("edit","r");
 
        Read_from_file(fi);
 
        print_msg("Aborting the edition Process",NO_VALUE);
 
        fclose(fi);
 


}
/*******************************************************************************
*
*       NAME            :Ask_Length()
*
*       DESCRIPTION     :
*
*       INPUT           : Block_id,Length_axis,new_length
*
*       OUTPUT          : SUCCESS or FAILURE
*
*******************************************************************************/
 
int Ask_Length(int blk,int ax,double newl)
{

	// goes to block, gets the length value
	// checks it with new_length
	// if it is same returns FAILURE or else SUCCESS

	Block *eb= currc->Get_block(blk);

	Length *le ;

	switch(ax){

		case XAXIS :

			le = eb->Get_Xlen();
			break;

		case YAXIS :

			le = eb->Get_Ylen();
			break;

		case ZAXIS :

			le = eb->Get_Zlen();
			break;

		default :
	
			print_msg("Length Specification is wrong",NO_VALUE);
			break;

	}


	double oldl = le->Get_length();


	if(newl== oldl)return FAILURE;
	else return SUCCESS;

}


/*******************************************************************************
*
*       NAME            :Modify_Length()
*
*       DESCRIPTION     :
*
*       INPUT           : Block_id,Length_axis,new_length
*
*       OUTPUT          : SUCCESS or FAILURE
*
*******************************************************************************/

int Modify_Length(int blk,int ax,int con ,double newl)
{

        Block *eb= currc->Get_block(blk);
 
        Length *le ;
 
        switch(ax){
 
                case XAXIS :
 
                        le = eb->Get_Xlen();
                        break;
 
                case YAXIS :
 
                        le = eb->Get_Ylen();
                        break;
 
                case ZAXIS :
 
                        le = eb->Get_Zlen();
                        break;
 
                default :
 
                        print_msg("Length Specification is wrong",NO_VALUE);
                        break;
 
        }


	int check = 1 ;		// to check whether operation is successful

	Length_List* ll = le->Get_length_list();


	printf("Number of links %d\n",ll->Get_num_links());

	Length* fl = ll->Get_firstl();

	while(fl){

		double val = fl->Get_length();

		int fix = fl->Get_fixed();

		if( (val == 0) || (fix == TRUE) ){

			check = 0 ;	// operation unsuccessful

			// because changing the linked length which has been
			// already fixed will create Inconsistancy , thus
			// we do not allow such case


			return FAILURE;
		}
		

		fl = fl->Get_nextl();
	}

	if(check != 0){ 	// No fixed length was found in list of lengths


		// again traverse the list of lengths to gather the blocks

		Length* fl = ll->Get_firstl();

		while(fl){


			// in the length_name second and third places give
			// block_id. So we need to separate them and convert 
			// them to integer value for getting the acual block

			char text[6];

			strcpy(text,fl->Get_length_name());

			char te[2];

			sprintf(te,"%c%c",text[1],text[2]);

			int id = atoi(te);

			Block* bb= currc->Get_block(id);

			Node* nb = bb->Get_block_node();

			// now update the values, FIX them and add the node
			// to the Queue of that type

			// If id matches the blk i.e. if we get the edited
			// node then do the further processing or else
			// add the node to Len_Q.

			// after primary editing process is over we will
			// go to Len_Q and then resolve one bye one

			double xn;
            double xd;
            double xx;

			double yx;
			double yn;
            double yd;

            double zn;
            double zd;
            double zx;

			if ( id == blk){

			switch(ax){
 
            	case XAXIS :

				Length* xl;

				// we will have to Update the values
				// according to constrai plane - con

				xn = bb->Get_Xmin();
				xd = bb->Get_Xmid();
				xx = bb->Get_Xmax();

					switch(con){

						case MINF:
							xx = xn + newl;
							xd = (xx+xn)/2;

							bb->Set_Xmin(xn);
							bb->Set_Xmid(xd);
							bb->Set_Xmax(xx);

							xl = bb->Get_Xlen();
							xl->Set_length(newl);

							break;

						case MIDF:

							xx = xd +(newl/2);
							xn = xd -(newl/2);

                                                        bb->Set_Xmin(xn);
                                                        bb->Set_Xmid(xd);
                                                        bb->Set_Xmax(xx);
 
                                                        xl = bb->Get_Xlen();
                                                        xl->Set_length(newl);
 
							break;

						case MAXF:

							xn = xx - newl;
							xd = ( xx + xn )/2;

                                                        bb->Set_Xmin(xn);
                                                        bb->Set_Xmid(xd);
                                                        bb->Set_Xmax(xx);
 
                                                        xl = bb->Get_Xlen();
                                                        xl->Set_length(newl);
 
							break;
						
						default:
                                                        xx = xd +(newl/2);
                                                        xn = xd -(newl/2);
 
                                                        bb->Set_Xmin(xn);
                                                        bb->Set_Xmid(xd);
                                                        bb->Set_Xmax(xx);
 
                                                        xl = bb->Get_Xlen();
                                                        xl->Set_length(newl);
 
							break;

					}
 
                                        // Now fix all of them
 
                                        bb->fix_xmin(TRUE);
                                        bb->fix_xmid(TRUE);
                                        bb->fix_xmax(TRUE);
                                        bb->fix_xlen(TRUE);

                        		break;
 
                		case YAXIS :

                                Length* yl;
 
                                // we will have to Update the values
                                // according to constrai plane - con
 
                                yn = bb->Get_Ymin();
                                yd = bb->Get_Ymid();
                                yx = bb->Get_Ymax();
 
                                        switch(con){
 
                                                case MINF:
                                                        yx = yn + newl;
                                                        yd = (yx+yn)/2;
 
                                                        bb->Set_Ymin(yn);
                                                        bb->Set_Ymid(yd);
                                                        bb->Set_Ymax(yx);
 
                                                        yl = bb->Get_Ylen();
                                                        yl->Set_length(newl);
 
                                                        break;
 
                                                case MIDF:
 
                                                        yx = yd +(newl/2);
                                                        yn = yd -(newl/2);
 
                                                        bb->Set_Ymin(yn);
                                                        bb->Set_Ymid(yd);
                                                        bb->Set_Ymax(yx);
 
                                                        yl = bb->Get_Ylen();
                                                        yl->Set_length(newl);
 
                                                        break;
 
                                                case MAXF:
 
                                                        yn = yx - newl;
                                                        yd = ( yx + yn )/2;
 
                                                        bb->Set_Ymin(yn);
                                                        bb->Set_Ymid(yd);
                                                        bb->Set_Ymax(yx);
 
                                                        yl = bb->Get_Ylen();
                                                        yl->Set_length(newl);
 
                                                        break;
 
                                                default:
                                                        yx = yd +(newl/2);
                                                        yn = yd -(newl/2);
 
                                                        bb->Set_Ymin(yn);
                                                        bb->Set_Ymid(yd);
                                                        bb->Set_Ymax(yx);
 
                                                        yl = bb->Get_Ylen();
                                                        yl->Set_length(newl);
 
                                                        break;
 
                                        }
                                        // Now fix all of them
 
                                        bb->fix_ymin(TRUE);
                                        bb->fix_ymid(TRUE);
                                        bb->fix_ymax(TRUE);
                                        bb->fix_ylen(TRUE);
 
                        		break;
 
                		case ZAXIS :

                                Length* zl;
 
                                // we will have to Update the values
                                // according to constrai plane - con
 
                                zn = bb->Get_Zmin();
                                zd = bb->Get_Zmid();
                                zx = bb->Get_Zmax();
 
                                        switch(con){
 
                                                case MINF:
                                                        zx = zn + newl;
                                                        zd = (zx+zn)/2;
 
                                                        bb->Set_Zmin(zn);
                                                        bb->Set_Zmid(zd);
                                                        bb->Set_Zmax(zx);
 
                                                        zl = bb->Get_Zlen();
                                                        zl->Set_length(newl);
 
                                                        break;
 
                                                case MIDF:
 
                                                        zx = zd +(newl/2);
                                                        zn = zd -(newl/2);
 
                                                        bb->Set_Zmin(zn);
                                                        bb->Set_Zmid(zd);
                                                        bb->Set_Zmax(zx);
 
                                                        zl = bb->Get_Zlen();
                                                        zl->Set_length(newl);
 
                                                        break;

                                                case MAXF:
 
                                                        zn = zx - newl;
                                                        zd = ( zx + zn )/2;
 
                                                        bb->Set_Zmin(zn);
                                                        bb->Set_Zmid(zd);
                                                        bb->Set_Zmax(zx);
 
                                                        zl = bb->Get_Zlen();
                                                        zl->Set_length(newl);
 
                                                        break;
 
                                                default:
                                                        zx = zd +(newl/2);
                                                        zn = zd -(newl/2);
 
                                                        bb->Set_Zmin(zn);
                                                        bb->Set_Zmid(zd);
                                                        bb->Set_Zmax(zx);
 
                                                        zl = bb->Get_Zlen();
                                                        zl->Set_length(newl);
 
                                                        break;
 
                                        }
 
                                        // Now fix all of them
 
                                        bb->fix_zmin(TRUE);
                                        bb->fix_zmid(TRUE);
                                        bb->fix_zmax(TRUE);
                                        bb->fix_zlen(TRUE);
 
                        		break;
 
                		default :
                        		break;
 
        		}

			}// end of if ckecking id and blk
			else{

				printf("ADDing to Len_Q\n");

				// Add_to_Q(Len Q)
			}
			fl = fl->Get_nextl();
		}
	}
}
