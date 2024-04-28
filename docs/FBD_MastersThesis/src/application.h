/*******************************************************************************
*       FILENAME :      application.h      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Application data/functions Declarations
*
*       USAGE :         Wherever class function calls are made .For files not
*						having "_"in their name.These are basically APP files.
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :   	MAY 31, 1995.
*
*******************************************************************************/

#ifndef _APPLICATION_H_
#define _APPLICATION_H_

/******************************************************************************
                FOLLOWING  STANDARD HEADER FILES ARE INCLUDED
******************************************************************************/

#include <iostream.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#include "vertexh.h"

	/*
	**	Following few lines of code is MUST when
	**	PHIGS is used in C++ programme, or else
	**	compiler gives errrors due to incompatible
	**	function prototyping in /phigs/phigsextern.h
	**
	**	define.h is a file in which new prototyping
	**	is done
	*/

#define PHIGS_EXTERN_INCLUDED
 
#include <X11/phigs/phigs.h>
 
extern "C" {
#include "define.h"
}

/*******************************************************************************

                CLASS (PRE) DECLARATIONS
				
				This is required to avoid "declaration confusion"
				that occurs because of order of inclusion of
				class header files

*******************************************************************************/

	class       Component;

	class       Graph;
	class       	ComponentGraph;
	class       	DimensionGraph;

	class       Block;
	class       	SubBlock;
	class			Cylinder;
	class				SubCylinder;
	class			Prismatic;
	class				Wedge;
	class					SubWedge;
	class				Bspline;

	class       Arc;
	class       	StrArc;
	class       	DimArc;

	class       Face;

	class       Polygon;

	class       PolygonSet;

	class  		Length; 

	class  		Length_List; 

	class       Node;
	class       	FeatureNode;
	class			DimNode;
	class       	StrongCompNode;
	class       	CycleNode;

	class       Plane;

	class       Vertex;

	class       Vector;

	class 		Queue;
	class 			NodeQueue;

	class 		Topolink;
	class 			SymmTopolink;
	class 				Center_Face_Match;
	class 				Center_Edge_Match;
	class 				One_Corner_Match;
	class 					Two_Corner_Match;
	class 						Four_Corner_Match;
	class 			Shared_Plane_Match;

	class 		Cycle;

	class 		StrongComp;

/*******************************************************************************
                MACRO DEFINITIONS
*******************************************************************************/


	/*
	**		Note:
	**	
	**		Normally macros are not handled by compiler .Preprocessers
	**		substitutes them with constant value. Thats why they are type-unsafe
	**		and may cause problems if not handled properly.
	**		"enumeration" is a better way to handle such declarations.
	**		Following thing is done at very begining of the coding stage
	**		at that time I followed the method used in previous programs.
	**		and now it will be time consuming to change all those places
	**		Its definitely a better programming practice to code that way.
	*/

/*	Axis Selection 		*/

#define 	XAXIS      	1
#define 	YAXIS      	2
#define 	ZAXIS      	3
#define		OAXIS		4

/*	Face type			*/

#define		RECTANGLE	1
#define		CIRCULAR	2


/*	Q Selection 		*/

#define 	X_Q			1
#define 	Y_Q			2
#define 	Z_Q			3
#define 	L_Q			4

/*	Plane Selection 	*/

#define 	FIRST      	1 
#define 	SECOND      2
#define 	THIRD       3
#define 	FOURTH      4 
#define 	FIFTH       5 



/*	Xlib macros 		*/

#define 	RED 		2
#define     WS1 		1
#define     VIEW_IND 	1
#define     MIN(x,y)    ((x < y) ? (x) : (y))
#define     MAX(x,y)	((x > y) ? (x) : (y))

/*	EDGE types ( Editing )  */

#define 	TREE		1
#define		BACK		2
#define		FORWARD		3
#define		CROSS		4



/*	Plane - Axis Selection 	*/

#define     XMAX        1
#define     XMID        2  
#define     XMIN        3 

#define     YMAX        4 
#define     YMID        5 
#define     YMIN        6 

#define     ZMAX        7 
#define     ZMID        8 
#define     ZMIN        9 


/*	Topolink type  		*/

#define     CFM			1
#define     CEM			2	
#define     CM			3	
#define     TCM			4	
#define     FCM			5	
#define     SP			6	




/*	Data_plane type  	*/

#define     MAX_MIN		1
#define     MIN_MAX		2	
#define     MAX_MAX		3		       		
#define     MIN_MIN		4		       		

#define     XMAX_MIN	1
#define     XMIN_MAX	2	
#define     XMAX_MAX	3		       		
#define     XMIN_MIN	4		       		

#define     YMAX_MIN	5	
#define     YMIN_MAX	6	
#define     YMAX_MAX	7		       		
#define     YMIN_MIN	8		       		

#define     ZMAX_MIN	9	
#define     ZMIN_MAX	10	
#define     ZMAX_MAX	11		       		
#define     ZMIN_MIN	12		       		

/*	Boolean macros 		*/

#define     DONE		2
#define     TRUE 		1
#define     FALSE		0


#define     FAILURE		0
#define     SUCCESS		1

/*	Display type 		*/

#define		SOLID		1
#define		WIREFRAME	2	
#define		BLKWISE		3	
#define		POLYSET		4	



/*	Projection Type 	*/

#define		PERSPECTIVE	1
#define		ORTHO		2	
#define		ISOMETRIC	3	



/*	Rotation Direction 	*/

#define		CW			1
#define		CCW			2	

#define		SMALL		0.0001

/*     Defined by Venky */

#define   	NO_BLOCK  	0 
#define   	BLOC        1
#define   	CYLINDR     2
#define   	SBLOC       3               /* subtractive block	*/
#define   	SCYLINDR    4               /* subtractive cylinder	*/
#define   	INHBLOCK    5               /* inherited block 	*/
#define   	PBLOCK      6              	/* prism block 		*/
#define   	WEDGE		7              	/* Wedge block 		*/
#define   	SWEDGE		8              	/* Subtractive Wedge block 		*/
#define		BSPLINE		9				/* Extruded Bspline surface */

#define   	MINF        1
#define   	MIDF        2
#define   	MAXF        3
#define   	LENGTHF     4

#define   	MAXWIN      18
#define   	MAXMENU     13
#define   	BORDER      5

typedef    	int         Id;
typedef     void        (*PF)();

	/*
	**		Following structure is used only to facillitate
	**		transfer of information from Motif to Applications
	**		This is just to show how information can be gathered from
	**		Widget and then passed to App.
	**		Similar structures could be defined for rest of the
	**		Callbacks for cleaner and readable program design
	**		rather than declaring globals for every information
	**		needed( currently there are some such globals still present)
	*/

typedef struct topoinfo{

	int	block_id;	// existing block with which new block is linked
	int	topo_type;	// Type of topological link
	int	Plane1;		// resting plane and following are other planes
	int	Plane2;
	int	Plane3;
	int	Plane4;
	int	Plane5;

}Topo_info;



typedef struct bspline_data{

	Vertex	u_pts[6];			//	All other things are hard coded
								//	As and when needed add the variables

}SplineData;

/*******************************************************************************
		GLOBAL VARIABLE DECLARATIONS
*******************************************************************************/


	/*
	**		Declaring globals is normally a BAD programming practice,
	**		especially in a project of this or bigger size.
	**		Following GLOBALS are declared mainly because of Motif.
	**		There is definitely scope for minimizing these GLOBALS
	**		by better program and class design.
	*/

extern	Component	*firstc ;		// first component
extern	Component	*editc ;		// editing component
extern	Component	*currc ;		// current component

extern	StrongComp	*firststr;		// first strongComp for editing
extern	Cycle		*firstcyl;		// first Cycle for editing

extern	NodeQueue	*Xlen_Q;		// queue of x_lengths
extern	NodeQueue	*Ylen_Q;		// queue of x_lengths
extern	NodeQueue	*Zlen_Q;		// queue of x_lengths
extern	NodeQueue	*Link_len_Q;		// queue of linked lengths

extern	Length_List	*firstll ;		// start of length linking list

extern	int 		len_link_num; 	// Length_List id counter
extern	int 		arc_counter; 	// arc id counter
extern	int 		comp_num;       // selected component id no.
extern	int 		blk_num;        // selected block id no.
extern	int 		cycle_num;      // selected cycle id no.

extern	int 		maxc;           // Maximum no. of components far
extern	int 		topo_type ;		// Type of topolink
extern	int 		plane_type;		// Type of plane

extern	Topo_info	topo_info[10];	// used to store topo_links info
extern	int			temp_planes[6];// used to store planes info
extern	int			wedge_planes[2];//	used to store wdge info

extern	int 		cyl_axis;		// Type of cylinder axis
extern	int 		wedge_axis;		// Type of Wedge axis
extern	int 		len_axis;		// Type of edit_length axis
extern	int 		constrn_pln;	// Type of constrain plane

extern	SplineData	spline_data;	//	used to store spline information


/*******************************************************************************
        FUNCTION DECLARATIONS
*******************************************************************************/

/*	Functions coded in application.c are the following */

void 		Init_App();
void 		Close_App();
void 		make_Topo_info_null();
void 		make_temp_planes_null();
void 		Init_edit_flags(Component *co);
Component* 	Get_Comp(int i);

/*	Functions coded in editing.c are the following */

void 		Abort_editing();
int 		Ask_Length(int blk,int ax,double newl);
int 		Modify_Length(int blk,int ax,int con,double newl);

/*	Functions coded in component.c are the following */

void 		Link_Comp( Component *co);

/*	Functions coded in compfile.c are the following */

void 		Read_from_file( FILE *fi);

/*	Functions coded in block.c are the following */

Block*		Get_block(Component *co,int blkid);

/*	Functions coded in lengthlist.c are the following */

void		Link_Length_List( Length_List *lo);

/*	Functions coded in queue.c are the following */

void 		Add_to_edit_Q(int type,Block* no);

/*	Functions coded in resolving.c are the following */

void 		Resolve(Node* base, Node* destin ,Topolink* to);
void 		Resolve_adj_nodes(Node* base, int axis);

/*      Functions coded in file : topo_data_resolve.c	*/
 
void 		cfm_for_resolve(int,int ,int);
void 		cm_for_resolve(int,int ,int,int,int);
void 		cem_for_resolve(int, int ,int,int);
void 		tcm_for_resolve(int,int ,int,int,int,int);
void 		fcm_for_resolve(int,int ,int);
void 		spm_for_resolve(int,int ,int);

/*	Functions coded in CycleEditing.c are the following */

Cycle*		Find_Cycles( Node* base,Graph* gra);
void		STRONG(Node* nnn,Node* nnnn,Graph* gg);
void		CYCLE(StrongCompNode* mm,int& fl,Node* base_nod);
void		UNMARK(StrongCompNode* vv);

/* 	Functions coded in strongcomp.c ar the following  */

void		Link_str_comps(StrongComp* ss);

/* 	Functions coded in cycle.c ar the following  */

void 		Link_cycles(Cycle* ss);
Cycle* 		Get_Cycle(int cy_num);
void 		Process_Cycles();
void		Delete_Cycle(Cycle* de);
void		Remove_duplicate_cycles();

#endif

