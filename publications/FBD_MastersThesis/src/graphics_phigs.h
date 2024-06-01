/*******************************************************************************
*       FILENAME :      graphics_phigs.h      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Phigs Declarations
*
*       USAGE :         Wherever phigs calls are made,mainly for files having
*                       "_"in their name.These are basically graphics files.
*
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :   	MAY 27, 1995.
*
*******************************************************************************/

#ifndef 	_graphics_phigs_h
#define  	_graphics_phigs_h

/******************************************************************************
*                       INCLUDE FILES
******************************************************************************/

#include <X11/Intrinsic.h>
#include <X11/StringDefs.h>
#include <X11/Xatom.h>
#include <X11/phigs/phigs.h>


/*******************************************************************************
                MACRO DEFINITIONS
*******************************************************************************/

    /*
    **      Note:
    **
    **      Normally macros are not handled by compiler .Preprocessers
    **      substitutes them with constant value. Thats why they are type-unsafe
    **      and may cause problems if not handled properly.
    **      "enumeration" is a better way to handle such declarations.
    **      Following thing is done at very begining of the coding stage
    **      at that time I followed the method used in previous programs.
    **      and now it will be time consuming to change all those places
    **      Its definitely a better programming practice to code that way.
    */

/* PHIGS Identifiers */

#define WS_ID                   (Pint) 1
#define STRUCTURE_ID            (Pint) 1
#define INTERIOR_STYLE_LABEL    (Pint) 2

/* Window layout information */

#define WS_WIDTH                500
#define WS_HEIGHT               500
#define WS_BORDER_WIDTH         1


#define POLYGONSET              1
#define WIREFRAME               2
#define BLOCKWISE               3 

/******************************************************************************
                        GLOBAL  DECLARATIONS
******************************************************************************/

 
    /*
    **      Declaring globals is normally a BAD programming practice,
    **      especially in a project of this or bigger size.
    **      Following GLOBALS are declared mainly because of Motif.
    **      There is definitely scope for minimizing these GLOBALS
    **      by better program and class design.
    */
 

extern	int 	win_resizeflag ;        /* Auto-resizing */
extern	double	display_max ;			/* for resizing workstation */
extern	int		display_type ;			/* for component drawing */

/*******************************************************************************
        FUNCTION DECLARATIONS
*******************************************************************************/
 
/* 	Functions defined in graphics_phigs.c 	*/

void 	Init_Phigs();
void 	Close_Phigs();
void 	Resize_Ws(double max);
void 	DrawAxes(double l);
void    Set_HLHSR();
void	handle_input();				//	pg 445 Phigs Programming Manual


#endif

