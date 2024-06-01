/*******************************************************************************
*       FILENAME :      topolink.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Topolink
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JUN 22, 1995.
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
*       NAME            :Topolink..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of the newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Topolink::Topolink( Topo_info *topo ,int newblk_id)
{

        printf(" I will not be able to instantiate myself as being Virtual\n");
}

/*******************************************************************************
*
*       NAME            :SymmTopolink..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of the newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
SymmTopolink::SymmTopolink(Topo_info *topo ,int blk_id):Topolink(topo,blk_id)
{
        Block_A_Id      = topo->block_id ;      // Parent block id
        Block_B_Id      = blk_id ;           // New child block id
 
        topolink_type   = topo->topo_type;      // Topology link type
 

        Block *blk_A    = currc->Get_block( Block_A_Id);        // Get the block
        Block *blk_B    = currc->Get_block( Block_B_Id);        // Get the block
 
        Node *node_A    = blk_A->Get_block_node();              // Get the node
        Node *node_B    = blk_B->Get_block_node();              // Get the node
 
printf("Topolink between %d*%d\n",node_A->Get_node_id(),node_B->Get_node_id());
 
        /*
 
        Naming convention for arcs:
 
                Its a 6 digit string.
                first will be the comp_id
                next 2 will be parent block id, the next two will be
                child block id and the last one will be number of the topolinks
                between these two blocks
 
 
        */
 
        char nab[7];
        char nba[7];
 
sprintf(nab,"%1d%2d%2d_1",currc->Get_component_id(),Block_A_Id,Block_B_Id);
sprintf(nba,"%1d%2d%2d_1",currc->Get_component_id(),Block_B_Id,Block_A_Id);
 
        arcAB   = new Arc(nab, node_A ,node_B ,this);
        arcBA   = new Arc(nba, node_B ,node_A ,this);
 
 
        node_A->Link_to_Arclist(arcAB); // arcAB eminates from node_A
        node_B->Link_to_Arclist(arcBA); // arcBA eminates from node_B
 
 
        node_A->Link_to_Nodelist( node_B);
        node_B->Link_to_Nodelist( node_A);
 
 
}

/*******************************************************************************
*
*       NAME            :Shared_Plane_Match..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Shared_Plane_Match::Shared_Plane_Match(Topo_info *t,int id):SymmTopolink(t,id)
{
        Plane1_Id       = t->Plane1 ;        // resting plane for CFM
 
}

/*******************************************************************************
*
*       NAME            :Center_Face_Match..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Center_Face_Match::Center_Face_Match(Topo_info *t,int i):Shared_Plane_Match(t,i)
{
        printf("CFM constructor\n");

	// No further plane assignments are necessary
}
/*******************************************************************************
*
*       NAME            :Center_Edge_Match..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Center_Edge_Match::Center_Edge_Match(Topo_info *t,int i):Shared_Plane_Match(t,i)
{
        Plane2_Id       = t->Plane2 ;        // Edge plane for CEM
 
}

/*******************************************************************************
*
*       NAME            :One_Corner_Match..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
One_Corner_Match::One_Corner_Match(Topo_info *t,int id):Shared_Plane_Match(t,id)
{
 
        Plane2_Id       = t->Plane2 ;        // resting plane for CM
 
}
/*******************************************************************************
*
*       NAME            :Two_Corner_Match..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Two_Corner_Match::Two_Corner_Match(Topo_info *t,int id):One_Corner_Match(t,id)
{
        Plane3_Id       = t->Plane3 ;        // resting plane for TCM
 
}

/*******************************************************************************
*
*       NAME            :Four_Corner_Match..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. by global array of Topoinfo.Calls constructors of
*                        private members with appropraite values
*
*       INPUT           : Topo_info[i], Id of newly created block
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Four_Corner_Match::Four_Corner_Match(Topo_info *t,int id):Two_Corner_Match(t,id)
{
        Plane1_Id       = t->Plane1 ;        // resting plane for TCM
 
}

