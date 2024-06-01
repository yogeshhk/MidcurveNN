/******************************************************************************
*       FILENAME :    topolinkh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Declaration of Class Topolink
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       June 22, 1995.
*
******************************************************************************/
 
#ifndef _TOPOLINK_H_
#define _TOPOLINK_H_
 
/*****************************************************************************
*                       INCLUDE FILES
******************************************************************************/
 
#include "arch.h"
 

/*******************************************************************************

		Class heirarchy for topological links is as follows



			Topolink	( Virtual Base Class)
			  |
			  |
			SymmTopolink ( having two arcs : Symmetric)
			  |
			  |
		Shared_Plane_Match	
			  |
	|-----------------------|-------------------------|

Center_Face_Match  	One_Corner_Match	Center_Edge_Match
							|
					Two_Corner_Match
							|
					Four_Corner_Match



******************************************************************************/


/*******************************************************************************
*                       Class Topolink
*******************************************************************************/
 
 
class Topolink{

	protected :

        /*
        **      Topolink Identification
        */
		int	topolink_type;	// Type of the topological link

        /*
        **      Information Representation
        */
		int	Block_A_Id;	// parent block id (Same as the parent node)
		int	Block_B_Id;	// child  block id (Same as the parent node)

	public :

        /*
        **      Constructors
        */
		Topolink(){}
		Topolink(Topo_info *to,int newblk_id);

        /*
        **      Destructor
        */
		~Topolink(){}

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
 
		int	Get_Block_A_Id(){ return Block_A_Id ;}
		int	Get_Block_B_Id(){ return Block_B_Id ;}
		int	Get_topo_type(){ return topolink_type ;}


		/*
		** 	following functions are actually defined in
		** 	derived classes. Here they just get initialized
		** 	and in actual classes they get over-written with 
		** 	correct values
		*/

		virtual int	Get_Plane1_Id(){ return 0 ;}
		virtual int	Get_Plane2_Id(){ return 0 ;}
		virtual int	Get_Plane3_Id(){ return 0 ;}
		virtual int	Get_Plane4_Id(){ return 0 ;}
		virtual int	Get_Plane5_Id(){ return 0 ;}



};
/*******************************************************************************
*                       Class SymmTopolink
*******************************************************************************/
 
 
class SymmTopolink:virtual public Topolink {	// Virtaul base class
 
	protected :

        /*
        **      Information Representation
        */
        Arc     *arcAB;         // Arc from node_A to node_B
        Arc     *arcBA;         // Arc from node_B to node_A
 
    public :
 
		/*
        **      Constructors
        */
        SymmTopolink(){}
        SymmTopolink(Topo_info *to,int newblk_id);
 
        /*
        **      Destructor
        */
        ~SymmTopolink(){}
 
};

 
/*******************************************************************************
*                       Class Shared_Plane_Match
*******************************************************************************/
 
 
class Shared_Plane_Match : public SymmTopolink{
 
 	protected :
 
		/*
        **      Information Representation
        */
   		int     Plane1_Id ;   // Resting plane on parent block_A
 
	public :
 
		
        /*
        **      Constructors
        */
        Shared_Plane_Match(){}
        Shared_Plane_Match(Topo_info *tsp,int newblk_id);
 
        /*
        **      Destructor
        */
        ~Shared_Plane_Match(){}
 
		/*	
		**		Get data functions
		*/
		virtual int	Get_Plane1_Id(){ return Plane1_Id ;}
};

/*******************************************************************************
*                       Class Center_Face_Match
*******************************************************************************/
 
 
class Center_Face_Match : public Shared_Plane_Match {

	protected :

		// No further private members are necessary

	public :

        /*
        **      Constructors
        */
		Center_Face_Match(){}
		Center_Face_Match(Topo_info *tcfm,int newblk_id);

        /*
        **      Destructor
        */
		~Center_Face_Match(){}

};

/*******************************************************************************
*                       Class Center_Edge_Match
*******************************************************************************/
 
 
class Center_Edge_Match : public Shared_Plane_Match {
 
	protected :

        /*
        **      Information Representation
        */
        int     Plane2_Id ;   // Butting edge_plane on parent block_A
 
        
    public :

        /*
        **      Constructors
        */
        Center_Edge_Match(){}
        Center_Edge_Match(Topo_info *tcem,int newblk_id);
 
        /*
        **      Destructor
        */
        ~Center_Edge_Match(){}
 
        /*  
        **      Get data functions
        */
        virtual int     Get_Plane2_Id(){ return Plane2_Id ;}

};


/*******************************************************************************
*                       Class One_Corner_Match
*******************************************************************************/
 
 
class One_Corner_Match : public Shared_Plane_Match{
 
	protected :

        /*
        **      Information Representation
        */
        int     Plane2_Id ;   // Second corner plane on parent block_A
 
        
    public :
 
        /*
        **      Constructors
        */
        One_Corner_Match(){}
        One_Corner_Match(Topo_info *tocm,int newblk_id);
 
        /*
        **      Destructor
        */
        ~One_Corner_Match(){}
 
        /*  
        **      Get data functions
        */
        virtual int     Get_Plane2_Id(){ return Plane2_Id ;}

};

/*******************************************************************************
*                       Class Two_Corner_Match
*******************************************************************************/
 
 
class Two_Corner_Match : public One_Corner_Match{
 
	protected :

        /*
        **      Information Representation
        */
        int     Plane3_Id ;   // Third corner plane on parent block_A
 
        
    public :
 
        /*
        **      Constructors
        */
        Two_Corner_Match(){}
        Two_Corner_Match(Topo_info *ttcm,int newblk_id);
 
        /*
        **      Destructor
        */
        ~Two_Corner_Match(){}
 
        /*  
        **      Get data functions
        */
        virtual int     Get_Plane3_Id(){ return Plane3_Id ;}

};
 
/*******************************************************************************
*                       Class Four_Corner_Match
*******************************************************************************/
 
 
class Four_Corner_Match : public Two_Corner_Match{
 
	protected :

        /*
        **      Information Representation
        */
        int     Plane1_Id ;   // Resting plane on parent block_A
 
		// Here I did not name it as Plane5_Id because
		// when any instance of topolink asks for resting plane
		// the function should be Get_Plane1()
		// So to remain consistant with notation those two planes
		// are named as Plane1_Id...
 
        
    public :
 
        /*
        **      Constructors
        */
        Four_Corner_Match(){}
        Four_Corner_Match(Topo_info *tfcm,int newblk_id);
 
        /*
        **      Destructor
        */
        ~Four_Corner_Match(){}
 
        /*  
        **      Get data functions
        */
        virtual int     Get_Plane1_Id(){ return Plane1_Id ;}

};




#endif
