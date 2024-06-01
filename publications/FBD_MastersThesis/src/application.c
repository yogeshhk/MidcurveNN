/*******************************************************************************
*       FILENAME :      application.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   contains functions related to application and defined as*			global functions in application.h  They are not utility
*			functiond un the sense that they are totally defined for*			application and not for communication with interface
*
*       FUNCTIONS   :   
*			Init_App()
*			Close_App()
*			make_Topo_info_null()
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   June 14, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
#include "classes.h"        	/* Application classes declaration */

/******************************************************************************
                        Global Data(Application)
******************************************************************************/

int comp_num;           // component id no.
int blk_num;            // block id no.
int cycle_num;          // cycle id no.
int len_link_num; 	// Length_List id counter
int arc_counter;  	// arc id counter
int maxc ;		// Maximum no. of componet so far
int topo_type;		// Type of the topological link
int plane_type;		// Type of the plane selected
int cyl_axis;  		// Type of cylinder axis
int wedge_axis;  		// Type of Wedge axis
int len_axis;  		// Type of length axis ( for editing)
int constrn_pln; 	// Type of constrain plane
int temp_planes[6]; 	// used to store planes info
int	wedge_planes[2];	//	used to store wedge planes

Component *firstc;	// first component in the component link list
Component *editc;	// component storing a copy before editing
Component *currc;	// current component in the component link list
StrongComp *firststr; 	// first strongComp for editing
Cycle	*firstcyl;	// first cycle for editing

NodeQueue *Xlen_Q;      // queue of x_lengths
NodeQueue *Ylen_Q;      // queue of y_lengths
NodeQueue *Zlen_Q;      // queue of z_lengths
NodeQueue *Link_len_Q;  // queue of linked lengths
 

Length_List *firstll;	// first of global length Link list

Topo_info topo_info[10];// used to store topo_links info



/*******************************************************************************
*
*       NAME            :void Init_App()
*
*       DESCRIPTION     :Called at the start of main()
*			 Initializes all global(app. and interface) variables.
*			 Starts application with proper initialized values
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing 
*
******************************************************************************/

void Init_App()
{

        printf("APPLICATION INITIALIZATION\n");


        /*
		All the initializations wrt application should be done here
                Basically all the flags to be set to there proper values
	*/

        comp_num        = 1;            // Initializing		(application.h)
        blk_num         = 1;            // Initializing		(application.h)
        cycle_num       = 1;            // Initializing		(application.h)
        len_link_num	= 1;            // Initializing		(application.h)
        arc_counter	= 1;            // Initializing		(application.h)
	

	firstc		= NULL;		// No comp in list	(application.h)
	editc		= NULL;		// No comp in list	(application.h)
	currc		= NULL;		// No current comp	(application.h)
	firststr	= NULL;		// No current Strcomp	(application.h)
	firstcyl	= NULL;		// No current Cycle	(application.h)

	Xlen_Q		= NULL;		// no x_lengths in Q	(application.h)
	Ylen_Q		= NULL;		// no x_lengths in Q	(application.h)
	Zlen_Q		= NULL;		// no x_lengths in Q	(application.h)
	Link_len_Q	= NULL;		// no link lengths in Q	(application.h)

	firstll		= NULL;		// No length links	(application.h)
	maxc		= 0 ;		// No components	(application.h)
	topo_type	= 0 ;		// No topo_links	(application.h)
	plane_type	= 0 ;		// No plane selected	(application.h)

	cyl_axis	= 0 ;     	// cylinder axis	(application.h)
	wedge_axis	= 0 ;     	// wedge axis		(application.h)
	len_axis	= 0 ;     	// length axis		(application.h)
	constrn_pln	= 0 ;     	// constrain plane	(application.h)


	make_Topo_info_null();		// No topo_info		(application.h)
	make_temp_planes_null();	// No planes selection	(application.h)

	/* 
		Widgets in main_window.h can not and are not initialized here. 
	*/

	comp_flag	= NO_COMP ;	// initialization	(main_window.h)	
	block_flag	= NO_BLOCK ;	// initialization	(main_window.h)
	menu_flag	= NO_MENU ;	// initialization	(main_window.h)

	x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;// X-Data flags 	(main_window.h)
	y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;// Y-Data flags 	(main_window.h)
	z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;// Z-Data flags 	(main_window.h)
 

        drawing_width   = WIDTH; 	// equal to 500		(main_window.h)
        drawing_height  = HEIGHT;	// equal to 500		(main_window.h)


}

/*******************************************************************************
*
*       NAME            :void Close_App()
*
*       DESCRIPTION     : 	Clears the memory allocated for global variables.
*			  				Calls all the destructors
*			  				Destroys motif widgets
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/


void Close_App()
{

        printf("APPLICATION CLOSING\n");


        /*	
				All the closing wrt application should be done here
                Basically all flags to be set to there proper values 

		*/

        comp_num        = 0;            // No components        (application.h)
        blk_num         = 0;            // No blocks            (application.h)
        cycle_num       = 0;            // No blocks            (application.h)
        len_link_num    = 0;            // Initializing         (application.h)
        arc_counter		= 0;            // Initializing         (application.h)
 
        firstc      	= NULL;         // No comp in list      (application.h)
		editc			= NULL;			// No comp in list		(application.h)
        currc 			= NULL;         // No current comp      (application.h)
		firststr		= NULL;			// No current Strcomp	(application.h)
		firstcyl		= NULL;			// No current Cycle	(application.h)
 
        Xlen_Q          = NULL;         // no x_lengths in Q    (application.h)
        Ylen_Q          = NULL;         // no x_lengths in Q    (application.h)
        Zlen_Q          = NULL;         // no x_lengths in Q    (application.h)
        Link_len_Q      = NULL;         // no link lengths in Q (application.h)
 
	firstll		= NULL;		// No length links	(application.h)
	maxc		= 0 ;		// No components	(application.h)
	topo_type	= 0 ;		// No topo_links	(application.h)
	plane_type	= 0 ;		// No plane selected	(application.h)

        cyl_axis        = 0 ;           // cylinder axis        (application.h)
		wedge_axis		= 0 ;  			// wedge axis			(application.h)
        len_axis        = 0 ;           // length axis        	(application.h)
		constrn_pln		= 0 ;     		// constrain plane	(application.h)
 

	make_Topo_info_null();		// No topo_info		(application.h)
	make_temp_planes_null();	// No planes selection	(application.h)

        /* 
		Widgets in main_window.h can't and are not freed here. 
		*/
 
        comp_flag       = NO_COMP ;     // closing		(main_window.h)
        block_flag      = NO_BLOCK ;    // closing		(main_window.h)
        menu_flag       = NO_MENU ;     // closing		(main_window.h)
 
        x_minf=x_maxf=x_midf=x_lenf= NO_VALUE;// X-Data flags   (main_window.h)
        y_minf=y_maxf=y_midf=y_lenf= NO_VALUE;// Y-Data flags   (main_window.h)
        z_minf=z_maxf=z_midf=z_lenf= NO_VALUE;// Z-Data flags   (main_window.h)
 
 
 
        drawing_width   = 500;        	// equal to 500         (main_window.h)
        drawing_height  = 500;       	// equal to 500         (main_window.h)
 

	/**************************************************************

		Here you need to traverse the link-list of compoenents
		and delete every one of them.The destructor of component
		will intern call all the destructors of other classes

		You may wish to destroy the motif global wiidgets

	***************************************************************/
}


 

/*******************************************************************************
*
*       NAME            :void make_Topo_info_null()
*
*       DESCRIPTION     :Initializes members of struct Topo_info to NULL 
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 
void make_Topo_info_null()
{

	for( int i = 0;i< 10;i++){

		topo_info[i].block_id	= 0;
		topo_info[i].topo_type	= 0;
		topo_info[i].Plane1	= 0;
		topo_info[i].Plane2	= 0;
		topo_info[i].Plane3	= 0;
		topo_info[i].Plane4	= 0;
		topo_info[i].Plane5	= 0;
		
	}
} 
/*******************************************************************************
*
*       NAME            :void make_temp_planes_null()
*
*       DESCRIPTION     :Initializes members of array of temp_planes to NULL
*
*       INPUT           :Nothing
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 
void make_temp_planes_null()
{
 
        for( int i = 0;i< 6;i++){
 
		temp_planes[i] = 0; 
        }
}


/*******************************************************************************
*
*       NAME            :Get_Comp()
*
*       DESCRIPTION     :Searches the link_list of components and returns i th.
*
*       INPUT           :Component_id  (i)
*
*       OUTPUT          :Component *
*
******************************************************************************/
 
Component* Get_Comp(int i)
{
 
        Component*  current_comp;
 
        current_comp = firstc;

        while (current_comp != NULL) {

		printf("Tracing %d\n",current_comp->Get_component_id());
               if (current_comp->Get_component_id() == i) break ;

               else
                   current_comp = current_comp->Get_nextc() ;
        }
        if (current_comp == NULL) {

		print_msg("Component not found ",NO_VALUE);
            	return (Component*)NULL;
        }
        else  return (current_comp) ;
}

/*******************************************************************************
*
*       NAME            :void Init_edit_flags()
*
*       DESCRIPTION     :
*                        Initializes all the data flags associated with editing
*
*       INPUT           :Component*
*
*       OUTPUT          :Nothing
*
******************************************************************************/
 
void Init_edit_flags(Component *co)
{
 
        printf("Flags INITIALIZATION\n");

	Block* bc = co->Get_comp_block();

	while(bc){

		bc->Initialize_flags(FALSE);

		Node* nc = bc->Get_block_node();
	
		nc->Initialize_flags(FALSE);

		bc = bc->Get_nextb();

	}

}
