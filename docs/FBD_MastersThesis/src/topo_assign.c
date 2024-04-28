/*******************************************************************************
*       FILENAME :      topo_data_assignments.c DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains all the data assignments for topo_links
*
*       FUNCTIONS   :   
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   June 17, 1995.
*
*******************************************************************************/
 
 
/******************************************************************************
                       INCLUDE FILES
******************************************************************************/
 
#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "classes.h"        	/* Classes Declarations :header file */
#include "graphics_phigs.h"     /* Phigs Declarations :header file */
 
/*****************************************************************************
*
*       NAME    :       cfm_for_data_table()
*
*       DESCRIPTION :	Assignment of plane values takes place   
*
******************************************************************************/

void cfm_for_data_table(int id ,int tp1){

        Block *b = Get_block( currc , id);
 
	/*

	 	Now b is the Block of id in the currc
	 	We need to get this parent blocks palne values
	 	and then set corresponding data planes

	*/


	double bx_min	= b->Get_Xmin();
	double bx_mid	= b->Get_Xmid();
	double bx_max	= b->Get_Xmax();

	double by_min	= b->Get_Ymin();
	double by_mid	= b->Get_Ymid();
	double by_max	= b->Get_Ymax();

	double bz_min	= b->Get_Zmin();
	double bz_mid	= b->Get_Zmid();
	double bz_max	= b->Get_Zmax();

	/*
		tp1 is a resting plane. Depending on this following planes
		have to be fixed :

			resting plane for second block
			mid planes of other axes

	*/

	switch(tp1){		

                case XMIN_MIN :
 
				x_minf = bx_min;
				y_midf = by_mid;
				z_midf = bz_mid;	

                                break;
                case XMIN_MAX :
				x_maxf = bx_min;
                                y_midf = by_mid;       
                                z_midf = bz_mid;       
 
                                break;
                case YMIN_MIN :
				y_minf = by_min;
                                x_midf = bx_mid;       
                                z_midf = bz_mid;       
 
                                break;
                case YMIN_MAX :
				y_maxf = by_min;
                                x_midf = bx_mid;       
                                z_midf = bz_mid;       
 
                                break;
                case ZMIN_MIN :
				z_minf = bz_min;
                                y_midf = by_mid;       
                                x_midf = bx_mid;       
 
                                break;
                case ZMIN_MAX :
				z_maxf = bz_min;
                                y_midf = by_mid;       
                                x_midf = bx_mid;       
 
                                break;

		case XMAX_MIN :
				x_minf = bx_max;
                                y_midf = by_mid;       
                                z_midf = bz_mid;       

				break;
		case XMAX_MAX :
				x_maxf = bx_max;
                                y_midf = by_mid;       
                                z_midf = bz_mid;       

				break;
		case YMAX_MIN :
				y_minf = by_max;
                                x_midf = bx_mid;       
                                z_midf = bz_mid;       

				break;
		case YMAX_MAX :
				y_maxf = by_max;
                                x_midf = bx_mid;       
                                z_midf = bz_mid;       

				break;
		case ZMAX_MIN :
				z_minf = bz_max;
                                y_midf = by_mid;       
                                x_midf = bx_mid;       

				break;
		case ZMAX_MAX :
				z_maxf = bz_max;
                                y_midf = by_mid;       
                                x_midf = bx_mid;       
				
				break;
	}
}

/*****************************************************************************
*
*       NAME    :       cm_for_data_table()
*
*       DESCRIPTION :   Assignment of plane values takes place   
*
******************************************************************************/
 
void cm_for_data_table(int id ,int tp1 ,int tp2 ,int tp3)
{
        Block *b = Get_block( currc , id);
 
        /*
 
                Now b is the Block of id in the currc
                We need to get this parent blocks palne values
                and then set corresponding data planes
 
        */
 
 
        double bx_min   = b->Get_Xmin();
        double bx_mid   = b->Get_Xmid();
        double bx_max   = b->Get_Xmax();
 
 
        double by_min   = b->Get_Ymin();
        double by_mid   = b->Get_Ymid();
        double by_max   = b->Get_Ymax();
 
        double bz_min   = b->Get_Zmin();
        double bz_mid   = b->Get_Zmid();
        double bz_max   = b->Get_Zmax();
 
        /*
                tp1 is a resting plane. Depending on this following planes
                have to be fixed :
 
                        resting plane for second block
                        mid planes of other axes
 
        */
 
        switch(tp1){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
                                break;
                case XMIN_MAX :
                                x_maxf = bx_min;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
                                break;
                case YMIN_MAX :
                                y_maxf = by_min;
 
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
                                break;
                case ZMIN_MAX :
                                z_maxf = bz_min;
                                break;
 
                case XMAX_MIN :
                                x_minf = bx_max;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
                                break;
                case YMAX_MIN :
                                y_minf = by_max;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
                                break;
                case ZMAX_MIN :
                                z_minf = bz_max;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
                                break;
        }
 
        /*
                Error checking is necessary here to see if the
                same axes comes for the second plane  which is
                an error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 
        */
 
        switch(tp2){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
                                break;
		default	:
				post_msg("Error! Choose MIN_MIN or MAX_MAX !");
				break;
        }

        switch(tp3){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
                                break;
		default	:
				post_msg("Error! Choose MIN_MIN or MAX_MAX !");
				break;
        }

}

/*****************************************************************************
*
*       NAME    :       cem_for_data_table()
*
*       DESCRIPTION :   Assignment of plane values takes place   
*
******************************************************************************/
 
void cem_for_data_table(int id ,int tp1 ,int tp2)
{

        Block *b = Get_block( currc , id);
 
        /*
 
                Now b is the Block of id in the currc
                We need to get this parent blocks palne values
                and then set corresponding data planes
 
        */
 
 
        double bx_min   = b->Get_Xmin();
        double bx_mid   = b->Get_Xmid();
        double bx_max   = b->Get_Xmax();
 
 
        double by_min   = b->Get_Ymin();
        double by_mid   = b->Get_Ymid();
        double by_max   = b->Get_Ymax();
 
        double bz_min   = b->Get_Zmin();
        double bz_mid   = b->Get_Zmid();
        double bz_max   = b->Get_Zmax();
 
        /*
                tp1 is a resting plane. Depending on this following planes
                have to be fixed :
 
                        resting plane for second block
                        mid planes of other axes
 
        */
 
        switch(tp1){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
                                break;
                case XMIN_MAX :
                                x_maxf = bx_min;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
                                break;
                case YMIN_MAX :
                                y_maxf = by_min;
 
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
                                break;
                case ZMIN_MAX :
                                z_maxf = bz_min;
                                break;
 
                case XMAX_MIN :
                                x_minf = bx_max;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
                                break;
                case YMAX_MIN :
                                y_minf = by_max;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
                                break;
                case ZMAX_MIN :
                                z_minf = bz_max;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
                                break;
        }

	/*
		Error checking is necessary here to see if the
		same axes comes for the second plane  which is
		an error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	*/

        switch(tp2){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
				x_midf = bx_mid;
                                break;
                case XMIN_MAX :
                                x_maxf = bx_min;
				x_midf = bx_mid;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
				y_midf = by_mid;
                                break;
                case YMIN_MAX :
                                y_maxf = by_min;
				y_midf = by_mid;
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
				z_midf = bz_mid;
                                break;
                case ZMIN_MAX :
                                z_maxf = bz_min;
				z_midf = bz_mid;
                                break;
                case XMAX_MIN :
                                x_minf = bx_max;
				x_midf = bx_mid;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
				x_midf = bx_mid;
                                break;
                case YMAX_MIN :
                                y_minf = by_max;
				y_midf = by_mid;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
				y_midf = by_mid;
                                break;
                case ZMAX_MIN :
                                z_minf = bz_max;
				z_midf = bz_mid;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
				z_midf = bz_mid;
                                break;
        }

}

/*****************************************************************************
*
*       NAME    :       tcm_for_data_table()
*
*       DESCRIPTION :   Assignment of plane values takes place   
*
******************************************************************************/
 
void tcm_for_data_table(int id ,int tp1,int tp2,int tp3,int tp4)
{

        Block *b = Get_block( currc , id);
 
        /*
 
                Now b is the Block of id in the currc
                We need to get this parent blocks palne values
                and then set corresponding data planes
 
        */
 
 
        double bx_min   = b->Get_Xmin();
        double bx_mid   = b->Get_Xmid();
        double bx_max   = b->Get_Xmax();
 
 
        double by_min   = b->Get_Ymin();
        double by_mid   = b->Get_Ymid();
        double by_max   = b->Get_Ymax();
 
        double bz_min   = b->Get_Zmin();
        double bz_mid   = b->Get_Zmid();
        double bz_max   = b->Get_Zmax();
 
        /*
                tp1 is a resting plane. Depending on this following planes
                have to be fixed :
 
                        resting plane for second block
                        mid planes of other axes
 
        */
 
        switch(tp1){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
                                break;
                case XMIN_MAX :
                                x_maxf = bx_min;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
                                break;
                case YMIN_MAX :
 
                                y_maxf = by_min;
 
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
                                break;
                case ZMIN_MAX :
                                z_maxf = bz_min;
                                break;
 
                case XMAX_MIN :
                                x_minf = bx_max;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
                                break;
                case YMAX_MIN :
                                y_minf = by_max;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
                                break;
                case ZMAX_MIN :
                                z_minf = bz_max;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
                                break;
        }
 
        /*
                Error checking is necessary here to see if the
                same axes comes for the second plane  which is
                an error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 
        */
 
        switch(tp2){
 
                case XMIN_MIN :
                case XMAX_MAX :
 
                      	x_minf = bx_min;
                      	x_midf = bx_mid;
                      	x_maxf = bx_max;
                      	x_lenf = bx_max - bx_min;

			switch(tp3){
 
                		case YMIN_MIN :
                               		y_minf = by_min;
                                	break;

                		case ZMIN_MIN :
                                	z_minf = bz_min;
                                	break;

                		case YMAX_MAX :
                                	y_maxf = by_max;
                                	break;

                		case ZMAX_MAX :
                                	z_maxf = bz_max;
                                	break;

                		default :

                                post_msg("Error! Choose MIN_MIN or MAX_MAX !");
                                break;
        		}

                                break;


                case YMIN_MIN :
                case YMAX_MAX :

                        y_minf = by_min;
                        y_midf = by_mid;
                        y_maxf = by_max;
                        y_lenf = by_max - by_min;

                        switch(tp3){
 
                                case XMIN_MIN :
                                        x_minf = bx_min;
                                        break;
 
                                case ZMIN_MIN :
                                        z_minf = bz_min;
                                        break;
 
                                case XMAX_MAX :
                                        x_maxf = bx_max;
                                        break;
 
                                case ZMAX_MAX :
                                        z_maxf = bz_max;
                                        break;
 
                                default :
 
                                post_msg("Error! Choose MIN_MIN or MAX_MAX !");
                                break;
                        }

                                break;
                case ZMIN_MIN :
                case ZMAX_MAX :

                        z_minf = bz_min;
                        z_midf = bz_mid;
                        z_maxf = bz_max;
                        z_lenf = bz_max - bz_min;

                        switch(tp3){
 
                                case YMIN_MIN :
                                        y_minf = by_min;
                                        break;
 
                                case XMIN_MIN :
                                        x_minf = bx_min;
                                        break;
 
                                case YMAX_MAX :
                                        y_maxf = by_max;
                                        break;
 
                                case XMAX_MAX :
                                        x_maxf = bx_max;
                                        break;
 
                                default :
 
                                post_msg("Error! Choose MIN_MIN or MAX_MAX !");
                                break;
                        }

                                break;
                default :
                                post_msg("Error! Choose MIN_MIN or MAX_MAX !");
                                break;
        }
 

	/*

		!!!!! Here I have ignored tp4 as it has to be
		opposite to tp2 and here user may make some mistakes
		so one way could be to have extensive error checking
		or just neglect it. For the time being 2nd option
		is chosen

	*/

 


}

/*****************************************************************************
*
*       NAME    :       fcm_for_data_table()
*
*       DESCRIPTION :   Assignment of plane values takes place   
*
******************************************************************************/
 
void fcm_for_data_table(int id ,int tp1)
{

        Block *b = Get_block( currc , id);
 
        /*
 
                Now b is the Block of id in the currc
                We need to get this parent blocks palne values
                and then set corresponding data planes
 
        */
 
 
        double bx_min   = b->Get_Xmin();
        double bx_mid   = b->Get_Xmid();
        double bx_max   = b->Get_Xmax();
 
 
        double by_min   = b->Get_Ymin();
        double by_mid   = b->Get_Ymid();
        double by_max   = b->Get_Ymax();
 
        double bz_min   = b->Get_Zmin();
        double bz_mid   = b->Get_Zmid();
        double bz_max   = b->Get_Zmax();
 
        /*
                tp1 is a resting plane. Depending on this following planes
                have to be fixed :
 
                        resting plane for second block
 
		Here MIN_MIN and MAX_MAX options are physically
		unrealizable thus removed
        */
 
        switch(tp1){
 
                case XMIN_MAX :
                                x_maxf = bx_min;
 
				y_minf = by_min;
				y_midf = by_mid;
				y_maxf = by_max;
				y_lenf = by_max - by_min ;

                                z_minf = bz_min;
                                z_midf = bz_mid;
                                z_maxf = bz_max;
                                z_lenf = bz_max - bz_min ;

                                break;
                case YMIN_MAX :
                                y_maxf = by_min;

                                x_minf = bx_min;
                                x_midf = bx_mid;
                                x_maxf = bx_max;
                                x_lenf = bx_max - bx_min ;
 
                                z_minf = bz_min;
                                z_midf = bz_mid;
                                z_maxf = bz_max;
                                z_lenf = bz_max - bz_min ;
 

                                break;
                case ZMIN_MAX :
                                z_maxf = bz_min;

                                y_minf = by_min;
                                y_midf = by_mid;
                                y_maxf = by_max;
                                y_lenf = by_max - by_min ;
 
                                x_minf = bx_min;
                                x_midf = bx_mid;
                                x_maxf = bx_max;
                                x_lenf = bx_max - bx_min ;
 

                                break;
 
                case XMAX_MIN :
                                x_minf = bx_max;

                                y_minf = by_min;
                                y_midf = by_mid;
                                y_maxf = by_max;
                                y_lenf = by_max - by_min ;
 
                                z_minf = bz_min;
                                z_midf = bz_mid;
                                z_maxf = bz_max;
                                z_lenf = bz_max - bz_min ;
 
                                break;
                case YMAX_MIN :
                                y_minf = by_max;

                                x_minf = bx_min;
                                x_midf = bx_mid;
                                x_maxf = bx_max;
                                x_lenf = bx_max - bx_min ;
 
                                z_minf = bz_min;
                                z_midf = bz_mid;
                                z_maxf = bz_max;
                                z_lenf = bz_max - bz_min ;
 
                                break;
                case ZMAX_MIN :
                                z_minf = bz_max;

                                y_minf = by_min;
                                y_midf = by_mid;
                                y_maxf = by_max;
                                y_lenf = by_max - by_min ;
 
                                x_minf = bx_min;
                                x_midf = bx_mid;
                                x_maxf = bx_max;
                                x_lenf = bx_max - bx_min ;
 
                                break;

		default 	:

				post_msg("Error ! No MIN_MIN and MAX_MAX ");
				break;
        }

}

/*****************************************************************************
*
*       NAME    :       spm_for_data_table()
*
*       DESCRIPTION :   Assignment of plane values takes place   
*
******************************************************************************/
 
void spm_for_data_table(int id ,int tp1)
{

        Block *b = Get_block( currc , id);
 
        /*
 
                Now b is the Block of id in the currc
                We need to get this parent blocks palne values
                and then set corresponding data planes
 
        */
 
 
        double bx_min   = b->Get_Xmin();
        double bx_mid   = b->Get_Xmid();
        double bx_max   = b->Get_Xmax();
 
 
        double by_min   = b->Get_Ymin();
        double by_mid   = b->Get_Ymid();
        double by_max   = b->Get_Ymax();
 
        double bz_min   = b->Get_Zmin();
        double bz_mid   = b->Get_Zmid();
        double bz_max   = b->Get_Zmax();
 
        /*
                tp1 is a resting plane. Depending on this following planes
                have to be fixed :
 
                        resting plane for second block
                        mid planes of other axes
 
        */
 
        switch(tp1){
 
                case XMIN_MIN :
 
                                x_minf = bx_min;
                                break;
                case XMIN_MAX :
                                x_maxf = bx_min;
                                break;
                case YMIN_MIN :
                                y_minf = by_min;
                                break;
                case YMIN_MAX :
                                y_maxf = by_min;
                                break;
                case ZMIN_MIN :
                                z_minf = bz_min;
                                break;
                case ZMIN_MAX :
                                z_maxf = bz_min;
                                break;
 
                case XMAX_MIN :
                                x_minf = bx_max;
                                break;
                case XMAX_MAX :
                                x_maxf = bx_max;
                                break;
                case YMAX_MIN :
                                y_minf = by_max;
                                break;
                case YMAX_MAX :
                                y_maxf = by_max;
                                break;
                case ZMAX_MIN :
                                z_minf = bz_max;
                                break;
                case ZMAX_MAX :
                                z_maxf = bz_max;
                                break;
        }
}



 

 
