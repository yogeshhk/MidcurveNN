/*******************************************************************************
*       FILENAME :      blockUpdate.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Update functions related to Class Block
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JULY 26, 1995.
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
*       NAME            :Update()
*
*       DESCRIPTION     :Sees which flags are fixed, depending on them tries
*			 to calucualte rest of the fields and fixes them.
*			 If only one flag is fixed : length is taken as second
*			 parameter to calculate the other values.
*
*       INPUT           :In which direction Update has to act
*
*       OUTPUT          :Flags fixed in the direction of the axis
*
******************************************************************************/
 
void Block::Update(int axis){

	int minf, midf,maxf,lenf;	// flags to see which one are fixed
	int sum;			// to see how many were fixed

	double mn, mx ,md,ln;		// actual values

	Node *nbb = Get_block_node();
	
	int modf = nbb->Get_modify();

	Node* nb;

	switch(axis){

		case XAXIS :

			minf = Get_fix_xmin();
			midf = Get_fix_xmid();
			maxf = Get_fix_xmax();
			lenf = Get_fix_xlen();

			sum = minf + midf + maxf + lenf ;

			nb = Get_block_node();

			if((nb->Get_modify()==TRUE)&&( sum < 2)){

				print_msg("DO YO WANT TO QUIT",NO_VALUE);
				printf("DO YO WANT TO QUIT");
        
			}
                        mn = Get_Xmin();
                        md = Get_Xmid();
                        mx = Get_Xmax();
 
                        Length *xl;
                        xl = Get_Xlen();
 
                        ln = xl->Get_length();
 

			switch(sum){

				case 0 :
					
					// Do not do any thing

					// set all the flags to TRUE
					// and set modify == DONE

					// This case should not happen at all

					print_msg("ERROR",NO_VALUE);

					break;

				case 1 :

					if(modf== FALSE){

						if(minf){

							mx = mn + ln;
							md = (mx + mn)/2;

							Set_Xmid(md);
							Set_Xmax(mx);
							
							break;
						}

                                               if(midf){
 
                                                        mx = md + (ln/2);
                                                        mn = md - (ln/2);
 
                                                        Set_Xmin(mn);
                                                        Set_Xmax(mx);
                        
                                                        break;
                                                }

                                               if(maxf){
 
                                                        mn = mx - ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Xmin(mn);
                                                        Set_Xmid(md);
                        
                                                        break;
                                                }
 
                                        fix_xmin(TRUE);
                                        fix_xmid(TRUE);
                                        fix_xmax(TRUE);
                                        fix_xlen(TRUE);
 
					nbb->Set_modify(DONE);

					// no more modification is allowed

					}

					else{

						// dont do anything

					}
					break;

				case 2:
				case 3:
				case 4:

					if(minf){

						if(midf){
						
                                                        mx = (2*md) - mn;
                                                        Set_Xmax(mx);
 
							break;
						}
						if(maxf){
							md = (mx + mn)/2;
							Set_Xmid(md);

							break;
						}
						if(lenf){
							mx = mn + ln ;
							md = (mx + mn)/2;

							Set_Xmax(mx);
							Set_Xmid(md);

							break;
						}

						break;
					}

                                        if(midf){
 
                                                if(minf){

                                                        mx = (2*md) - mn;
                                                        Set_Xmax(mx);
 
                                                        break;
                                                }
                                                if(maxf){
						
                                                        mn = (2*md) - mx;
                                                        Set_Xmin(mn);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        mx = md + (ln/2) ;
                                                        mn = md - (ln/2) ;
 
                                                        Set_Xmax(mx);
                                                        Set_Xmin(mn);
 
                                                        break;
                                                }
 
                                                break;
                                        }

                                        if(maxf){
 
                                                if(midf){
                                                
                                                        mn = (2*md) - mx;
                                                        Set_Xmin(mn);
 
                                                        break;
                                                }
                                                if(minf){

                                                        md = (mx + mn)/2;
                                                        Set_Xmid(md);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        md = mx - (ln/2) ;
                                                        mn = mx - ln ;
 
                                                        Set_Xmid(md);
                                                        Set_Xmin(mn);
 
                                                        break;
                                                }
 
                                                break;
                                        }
                                        if(lenf){
 
                                                if(midf){
 
							mn = md - (ln/2);
							mx = md + (ln/2);

							Set_Xmin(mn);
							Set_Xmax(mx);

                                                        break;
                                                }
                                                if(maxf){
							mn = mx - ln;
							md = (mx + mn)/2;

							Set_Xmin(mn);
							Set_Xmid(md);
 
                                                        break;
                                                }
                                                if(minf){
					
							md = mn + (ln/2);
							mx = mn + ln;
							
							Set_Xmid(md);
							Set_Xmax(mx);
 
                                                        break;
                                                }
 
                                                break;
                                        }

 
                                        fix_xmin(TRUE);
                                        fix_xmid(TRUE);
                                        fix_xmax(TRUE);
                                        fix_xlen(TRUE);
 
                                        nbb->Set_modify(DONE);
 
					break;
		
				default:
					break;

			}
			// end of case XAXIS


			break;

		case YAXIS :


                        minf = Get_fix_ymin();
                        midf = Get_fix_ymid();
                        maxf = Get_fix_ymax();
                        lenf = Get_fix_ylen();
 
                        sum = minf + midf + maxf + lenf ;
 
 
                        mn = Get_Ymin();
                        md = Get_Ymid();
                        mx = Get_Ymax();
 
                        Length *yl;
                        yl = Get_Ylen();
 
                        ln = yl->Get_length();
 
 
                        switch(sum){
 
                                case 0 :
 
                                        // Do not do any thing
 
                                        // set all the flags to TRUE
                                        // and set modify == DONE
 
                                        // This case should not happen at all
 
                                        print_msg("ERROR",NO_VALUE);
 
                                        break;
 
                                case 1 :
 
                                        if(modf== FALSE){
 
                                                if(minf){
 
                                                        mx = mn + ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Ymid(md);
                                                        Set_Ymax(mx);
 
                                                        break;
                                                }
 
                                               if(midf){
 
                                                        mx = md + (ln/2);
                                                        mn = md - (ln/2);
 
                                                        Set_Ymin(mn);
 
                                                        Set_Ymax(mx);
 
                                                        break;
                                                }
 
                                               if(maxf){
 
                                                        mn = mx - ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Ymin(mn);
                                                        Set_Ymid(md);
 
                                                        break;
                                                }
 
                                        fix_ymin(TRUE);
                                        fix_ymid(TRUE);
                                        fix_ymax(TRUE);
                                        fix_ylen(TRUE);
 
                                        nbb->Set_modify(DONE);
 
                                        // no more modification is allowed
 
                                        }
 
                                        else{
 
                                                // dont do anything
 
                                        }
                                        break;
 
                                case 2:
                                case 3:
                                case 4:
 
                                        if(minf){
 
                                                if(midf){
 
                                                        mx = (2*md) - mn;
                                                        Set_Ymax(mx);
 
                                                        break;
                                                }
                                                if(maxf){
                                                        md = (mx + mn)/2;
                                                        Set_Ymid(md);
 
                                                        break;
                                                }
                                                if(lenf){
 
                                                        mx = mn + ln ;
                                                        md = (mx + mn)/2;
 
                                                        Set_Ymax(mx);
                                                        Set_Ymid(md);
 
                                                        break;
                                                }
 
                                                break;
                                        }
 
                                        if(midf){
 
                                                if(minf){
 
                                                        mx = (2*md) - mn;
                                                        Set_Ymax(mx);
 
                                                        break;
                                                }
                                                if(maxf){
 
                                                        mn = (2*md) - mx;
                                                        Set_Ymin(mn);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        mx = md + (ln/2) ;
                                                        mn = md - (ln/2) ;
 
                                                        Set_Ymax(mx);
                                                        Set_Ymin(mn);
 
                                                        break;
                                                }
 
                                                break;
                                        }
 
                                        if(maxf){
 
                                                if(midf){
 
                                                        mn = (2*md) - mx;
                                                        Set_Ymin(mn);
 
                                                        break;
                                                }
                                                if(minf){
 
                                                        md = (mx + mn)/2;
                                                        Set_Ymid(md);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        md = mx - (ln/2) ;
                                                        mn = mx - ln ;
 
                                                        Set_Ymid(md);
                                                        Set_Ymin(mn);
 
                                                        break;
                                                }
 
                                                break;
                                        }
                                        if(lenf){
 
                                                if(midf){
 
                                                        mn = md - (ln/2);
                                                        mx = md + (ln/2);
 
                                                        Set_Ymin(mn);
                                                        Set_Ymax(mx);
 
                                                        break;
                                                }
                                                if(maxf){
                                                        mn = mx - ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Ymin(mn);
                                                        Set_Ymid(md);
 
                                                        break;
                                                }
                                                if(minf){
 
                                                        md = mn + (ln/2);
                                                        mx = mn + ln;
 
                                                        Set_Ymid(md);
                                                        Set_Ymax(mx);
 
                                                        break;
                                                }
 
                                                break;
                                        }
 
 
                                        fix_ymin(TRUE);
                                        fix_ymid(TRUE);
                                        fix_ymax(TRUE);
                                        fix_ylen(TRUE);
 
                                        nbb->Set_modify(DONE);
 
                                        break;
 
                                default:
                                        break;
 
                        }
                        // end of case YAXIS
 
			break;

		case ZAXIS :

                        minf = Get_fix_zmin();
                        midf = Get_fix_zmid();
                        maxf = Get_fix_zmax();
                        lenf = Get_fix_zlen();
 
                        sum = minf + midf + maxf + lenf ;
 
 
                        mn = Get_Zmin();
                        md = Get_Zmid();
                        mx = Get_Zmax();
 
                        Length *zl;
                        zl = Get_Zlen();
 
                        ln = zl->Get_length();
 
 
                        switch(sum){
 
                                case 0 :
 
                                        // Do not do any thing
 
                                        // set all the flags to TRUE
                                        // and set modify == DONE
 
                                        // This case should not happen at all
 
                                        print_msg("ERROR",NO_VALUE);
 
                                        break;
 
                                case 1 :
 
                                        if(modf== FALSE){
 
                                                if(minf){
 
                                                        mx = mn + ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Zmid(md);
                                                        Set_Zmax(mx);
 
                                                        break;
                                                }
 
 
                                               if(midf){
 
                                                        mx = md + (ln/2);
                                                        mn = md - (ln/2);
 
                                                        Set_Zmin(mn);
                                                        Set_Zmax(mx);
 
                                                        break;
                                                }
 
                                               if(maxf){
 
                                                        mn = mx - ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Zmin(mn);
                                                        Set_Zmid(md);
 
                                                        break;
                                                }
 
                                        fix_zmin(TRUE);
                                        fix_zmid(TRUE);
                                        fix_zmax(TRUE);
                                        fix_zlen(TRUE);
 
                                        nbb->Set_modify(DONE);
 
                                        // no more modification is allowed
 
                                        }
 
                                        else{
 
                                                // dont do anything
 
                                        }
                                        break;
 
                                case 2:
                                case 3:
                                case 4:
 
                                        if(minf){
 
                                                if(midf){
 
                                                        mx = (2*md) - mn;
                                                        Set_Zmax(mx);
 
                                                        break;
                                                }
 
                                                if(maxf){
                                                        md = (mx + mn)/2;
                                                        Set_Zmid(md);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        mx = mn + ln ;
                                                        md = (mx + mn)/2;
 
                                                        Set_Zmax(mx);
                                                        Set_Zmid(md);
 
                                                        break;
                                                }
 
                                                break;
                                        }
 
                                        if(midf){
 
                                                if(minf){
 
                                                        mx = (2*md) - mn;
                                                        Set_Zmax(mx);
 
                                                        break;
                                                }
                                                if(maxf){
 
                                                        mn = (2*md) - mx;
                                                        Set_Zmin(mn);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        mx = md + (ln/2) ;
                                                        mn = md - (ln/2) ;
 
                                                        Set_Zmax(mx);
                                                        Set_Zmin(mn);
 
                                                        break;
                                                }
 
                                                break;
                                        }
 
                                        if(maxf){
 
                                                if(midf){
 
                                                        mn = (2*md) - mx;
                                                        Set_Zmin(mn);
 
 
                                                        break;
                                                }
                                                if(minf){
 
                                                        md = (mx + mn)/2;
                                                        Set_Zmid(md);
 
                                                        break;
                                                }
                                                if(lenf){
                                                        md = mx - (ln/2) ;
                                                        mn = mx - ln ;
 
                                                        Set_Zmid(md);
                                                        Set_Zmin(mn);
 
                                                        break;
                                                }
 
                                                break;
                                        }
                                        if(lenf){
 
                                                if(midf){
 
                                                        mn = md - (ln/2);
                                                        mx = md + (ln/2);
 
                                                        Set_Zmin(mn);
                                                        Set_Zmax(mx);
 
                                                        break;
                                                }
                                                if(maxf){
                                                        mn = mx - ln;
                                                        md = (mx + mn)/2;
 
                                                        Set_Zmin(mn);
                                                        Set_Zmid(md);
 
                                                        break;
                                                }
                                                if(minf){
 
                                                        md = mn + (ln/2);
                                                        mx = mn + ln;
 
                                                        Set_Zmid(md);
                                                        Set_Zmax(mx);
 
                                                        break;
                                                }
 
					} 
 
                                        fix_zmin(TRUE);
                                        fix_zmid(TRUE);
                                        fix_zmax(TRUE);
                                        fix_zlen(TRUE);
 
                                        nbb->Set_modify(DONE);
 
                                        break;
 
                                default:
                                        break;
 
                        }
                        // end of case ZAXIS
 
 
			break;

		default :

			break;

	}
}
