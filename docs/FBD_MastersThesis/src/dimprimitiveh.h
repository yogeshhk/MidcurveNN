/*******************************************************************************
*       FILENAME :    dimprimitiveh.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :	Declaration of Class DimPrimitive
*
*       USAGE :
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/
 
#ifndef _DIMPRIMITIVE_H
#define _DIMPRIMITIVE_H
 
/*******************************************************************************
                FOLLOWING  HEADER FILES ARE INCLUDED
*******************************************************************************/
 
#include "application.h"
 
/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class DimPrimitive{

	/*
	**		Virtual Base class
	*/

	DimPrimitive*	nextdp;


	public:

		DimPrimitive();
		~DimPrimitive(){}
		/*
		**			Get Data Functions
		*/
		virtual	double	Get_dim_value()=0;

		DimPrimitive*	Get_nextdp(){return nextdp;}
		void			Set_nextdp(DimPrimitive* dp){nextdp=dp;}
};

/******************************************************************************
                CLASS DECLARATION
******************************************************************************/
 
class DimPlane :public DimPrimitive{

	protected:

		/*
		**		DimPlane Identification
		*/
		int			dimplane_id ;			// dimplane number
		int			block_id;				// the parent block
		int			dimplane_type ;			// type along which this dimplane is
		Vector*		normal;					// Normal vector

		/*
		**		Information Representation
		*/
		double		dimplane_value ;			// numerical value of dimplane


	public :

		/*
		**		Constructor
		*/
		DimPlane(){}	
		DimPlane(Face* ff,int blk_id);
		
		/*
		**		Destructor
		*/
		~DimPlane(){}

        /*
        **      Following functions are specific to this class
        **      and are not translated differently by the subclasses
        **      thats why they are not virtual
        **
        **      GET and SET functions are normally avoided in Object oriented
        **      Programming but some restrucutions posed by Motif and to
        **      continue the method adopted by earlier programs those functions
        **      are still used.
        */
		int		Get_dimplane_type()				{ return dimplane_type; }
		double	Get_dim_value()					{ return dimplane_value ;}
		void	Set_dimplane_value(double pval)	{ dimplane_value = pval;}



}; 
#endif
 
 

