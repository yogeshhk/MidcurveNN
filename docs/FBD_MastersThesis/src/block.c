/*******************************************************************************
*       FILENAME :      block.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Block
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   JUN 5, 1995.
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
*       NAME            :Block..... Constructor
*
*       DESCRIPTION     :	This is second constructor. Gets all the values
*			 				reqd. to compute planes etc..Calls constructors of
*			 				private members with appropraite values 
*
*       INPUT           : id , parent component and plane values
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
 
Block::Block(	char *blkid,Component *co,
				double xmn,	double xmx,
				double ymn, double ymx, 
				double zmn, double zmx)
{
	
	strcpy(block_name , blkid);			// copies block name
										// block_id gets assigned in the
										// Link_block in Component

	block_type	= block_flag;

	int temp ;
	temp = co->Get_block_id_counter();	// get maximum no. of blocks
	block_id = ++temp ;					// assignened the incremented value
	co->Set_block_id_counter(temp);		// reset block_id_counter in Component ;

	nextb	= NULL ;		// next block is NULL
	prevb	= NULL ;		// previous block is NULL

	block_comp = co;		// parent component

	double	xmd = (xmn+xmx)/2 ;	// calculating X mid plane value
	double	ymd = (ymn+ymx)/2 ;	// calculating Y mid plane value
	double	zmd = (zmn+zmx)/2 ;	// calculating Z mid plane value


	double	xln = (xmx - xmn );	// calculating X length
	double	yln = (ymx - ymn );	// calculating Y length
	double	zln = (zmx - zmn );	// calculating Z length

	/*

		Plane ids are assignend explicitely with numbers
		because for sure there are 9 planes only and naming
		can be made consistant

	*/

	Xmin	= new Plane(1,XMIN,xmn);// Plane( id ,type, value)
	Xmid	= new Plane(2,XMID,xmd);
	Xmax	= new Plane(3,XMAX,xmx);

	Ymin	= new Plane(4,YMIN,ymn);
	Ymid	= new Plane(5,YMID,ymd);
	Ymax	= new Plane(6,YMAX,ymx);

	Zmin	= new Plane(7,ZMIN,zmn);
	Zmid	= new Plane(8,ZMID,zmd);
	Zmax	= new Plane(9,ZMAX,zmx);

	/*

        Naming convention for lengths :
 
                Its a four bit string out of which second 2 are of block_ids
                (thus restricting no. of blocks to 99) and the forth bit is for
                axis. X=1, Y=2 and Z=3 ;
                The first digit could be used for comp num
 
                Lenght_List just concatenates these length_names whenever
                they are linked to this specific Length_list
 

	*/

	char	lx[4];
	sprintf(lx,"%1d%2d",co->Get_component_id(),block_id);	
	strcat(lx,"1");				// concatenate with 1 for X

	Xlen	= new Length(lx);

        char    ly[4];
	sprintf(ly,"%1d%2d",co->Get_component_id(),block_id);	
        strcat(ly,"2");				// 2 for Y

	Ylen	= new Length(ly);

        char    lz[4];	
	sprintf(lz,"%1d%2d",co->Get_component_id(),block_id);	
        strcat(lz,"3");				// 3 for Z

	Zlen	= new Length(lz);


	/*

		Now we have to prepare list of global Length_List
		It will be local declaration because they are not
		in the private of the Block
		Same length_name is passed for this also

	*/

	Length_List *xll = new Length_List(lx,xln,Xlen);
	Link_Length_List(xll);		// adding to the global list

	Length_List *yll = new Length_List(ly,yln,Ylen);
	Link_Length_List(yll);

	Length_List *zll = new Length_List(lz,zln,Zlen);
	Link_Length_List(zll);


	printf( "Came to block constructor with no. %s \n",block_name);
} 


/*******************************************************************************
*
*       NAME            :	Face *Create_Faces()
*
*       DESCRIPTION     :	Creates list of faces from plane values,
*			 				Can be used for Display purposes 
*
*       INPUT           : Nothing
*
*       OUTPUT          : Pointer to the first face in the face list
*
******************************************************************************/
 
Face *Block::Create_Faces()
{


	/*

		Values of Min_Max planes are sufficient to calculate
		all the 8 vertices and 6 faces with values
		Verices are oriented such that by right hand rule
		the direction of thumb is away from the material

	*/


	// lets get values from planes and store them temporarily

	double	pxn	= Xmin->Get_plane_value();
	double	pxx	= Xmax->Get_plane_value();
	double	pyn	= Ymin->Get_plane_value();
	double	pyx	= Ymax->Get_plane_value();
    double  pzn = Zmin->Get_plane_value();
    double  pzx = Zmax->Get_plane_value();         
 
	// bottom four vertices

	Vertex *v1	= new Vertex(1,pxn,pyn,pzx);
	Vertex *v2	= new Vertex(2,pxx,pyn,pzx);
	Vertex *v3	= new Vertex(3,pxx,pyn,pzn);
	Vertex *v4	= new Vertex(4,pxn,pyn,pzn);

	// top four vertices

	Vertex *v5	= new Vertex(5,pxn,pyx,pzx);
	Vertex *v6	= new Vertex(6,pxx,pyx,pzx);
	Vertex *v7	= new Vertex(7,pxx,pyx,pzn);
	Vertex *v8	= new Vertex(8,pxn,pyx,pzn);

        // bottom face
 
        Face    *f6     = new Face(6,YAXIS,v1,v4,v3,v2);

		// front face

		Face	*f1		= new Face(1,ZAXIS,v1,v2,v6,v5);
        f6->Set_nextf(f1);

		// right face

		Face	*f2		= new Face(2,XAXIS,v2,v3,v7,v6);
		f1->Set_nextf(f2);

        // back face

        Face    *f3     = new Face(3,ZAXIS,v3,v4,v8,v7);
        f2->Set_nextf(f3);


        // left face

        Face    *f4     = new Face(4,XAXIS,v4,v1,v5,v8);
        f3->Set_nextf(f4);


        // top face
 
        Face    *f5     = new Face(5,YAXIS,v5,v6,v7,v8);
        f4->Set_nextf(f5);




		return f6 ;	// return the pointer to the first face of list

	
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
******************************************************************************/
 
int Block::Get_flags_sum(int ax){

        int minf, midf,maxf,lenf;       // flags to see which one are fixed
        int sum;                        // to see how many were fixed
 

        switch(ax){
 
                case XAXIS :
 
                        minf = Get_fix_xmin();
                        midf = Get_fix_xmid();
                        maxf = Get_fix_xmax();
                        lenf = Get_fix_xlen();
 
                        sum = minf + midf + maxf + lenf ;
						break;

                case YAXIS :
 
                        minf = Get_fix_ymin();
                        midf = Get_fix_ymid();
                        maxf = Get_fix_ymax();
                        lenf = Get_fix_ylen();
 
                        sum = minf + midf + maxf + lenf ;
                        break;

                case ZAXIS :
 
                        minf = Get_fix_zmin();
                        midf = Get_fix_zmid();
                        maxf = Get_fix_zmax();
                        lenf = Get_fix_zlen();
 
                        sum = minf + midf + maxf + lenf ;
                        break;

		default:
			printf("Bad choice\n");
			break;
	}

	return sum;


}
/*******************************************************************************
*
*       NAME            :Get_max_dimension()
*
*       DESCRIPTION     :
*
*       INPUT           :
*
*       OUTPUT          : maximum dimension of all planes
*
******************************************************************************/
 
double Block::Get_max_dimension()
{
        double  maximum = 50 ;          // some initial value
 
        double  pxn     = Xmin->Get_plane_value();
        double  pxx     = Xmax->Get_plane_value();
        double  pyn     = Ymin->Get_plane_value();
        double  pyx     = Ymax->Get_plane_value();
        double  pzn     = Zmin->Get_plane_value();
        double  pzx     = Zmax->Get_plane_value();

		// fabs(double ) returns absolute float

	if( fabs(pxn) >= maximum) maximum = fabs(pxn);
	if( fabs(pxx) >= maximum) maximum = fabs(pxx);
	if( fabs(pyn) >= maximum) maximum = fabs(pyn);
	if( fabs(pyx) >= maximum) maximum = fabs(pyx);
	if( fabs(pzn) >= maximum) maximum = fabs(pzn);
	if( fabs(pzx) >= maximum) maximum = fabs(pzx);

	return maximum;

}
/*******************************************************************************
*
*       NAME            :	Display_by_phigs()
*
*       DESCRIPTION     :	Temporarily creates list of faces and then
*			 				traverses each face to get the vertices
*			 				Uses PHIGS calls to display
*
*       INPUT           : 	Nothing
*
*       OUTPUT          : 	Creation of structure in phigs
*
******************************************************************************/
 
void Block::Display_by_phigs()
{

	Face *tracef = Create_Faces();	// gets the first face in the face list

	Ppoint3			pt[6][4];		// six faces & each has 4 points
	Ppoint_list3	faces[6];		//six faces


	for(int i=0;i<6;i++){

		faces[i].num_points 	= 4;
		faces[i].points		= pt[i];
	}


	int j=0;			// temporary counter

	while(tracef){

		Vertex *v1 = tracef->Get_V1();
		Vertex *v2 = tracef->Get_V2();
		Vertex *v3 = tracef->Get_V3();
		Vertex *v4 = tracef->Get_V4();

		pt[j][0].x		= (Pfloat)v1->Get_x();
		pt[j][0].y		= (Pfloat)v1->Get_y();
		pt[j][0].z		= (Pfloat)v1->Get_z();

        pt[j][1].x      = (Pfloat)v2->Get_x();
        pt[j][1].y      = (Pfloat)v2->Get_y();
        pt[j][1].z      = (Pfloat)v2->Get_z();

        pt[j][2].x      = (Pfloat)v3->Get_x();
        pt[j][2].y      = (Pfloat)v3->Get_y();
        pt[j][2].z      = (Pfloat)v3->Get_z();

        pt[j][3].x      = (Pfloat)v4->Get_x();
        pt[j][3].y      = (Pfloat)v4->Get_y();
        pt[j][3].z      = (Pfloat)v4->Get_z();


        pset_linetype( PLINE_SOLID );
        pset_linewidth((Pfloat) 2.0);
		pset_line_colr_ind( (Pint) 3);
		ppolyline3( &faces[j]);
		tracef = tracef->Get_nextf();
		j++;
	}

}


/*******************************************************************************
*
*       NAME            :Get_block( Component *c, int id)
*
*       DESCRIPTION     :Global function which returns Block* by traversing
*			the block list in the passed Component*
*
*       INPUT           :Parent component, Block_Id
*
*       OUTPUT          : Block pointer
*
******************************************************************************/
 
Block *Get_block( Component *c, int id)
{


	/*

		Here traversing could have been done through
		graph also. But specially for simple traversals
		and display purpose a separate list of blocks
		( though redundant) is maintained, and used here

	*/

	Block *tracer = c->Get_comp_block();	// now at firts block in "c"

	while( tracer->Get_nextb() != NULL){

		if( tracer->Get_block_id() == id){
	
			break;
		}
		
		tracer = tracer->Get_nextb();
	}

	return tracer;



}

/*******************************************************************************
*
*       NAME            :Initialize_flags()
*
*       DESCRIPTION     :	Sets all the data flags to FALSE
*			 				Used at the start of editing function
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 

void Block::Initialize_flags(int boo)
{

                fix_xmin(boo);
                fix_xmid(boo);
                fix_xmax(boo);
                fix_xlen(boo);
 
                fix_ymin(boo);
                fix_ymid(boo);
                fix_ymax(boo);
                fix_ylen(boo);
 
 
                fix_zmin(boo);
                fix_zmid(boo);
                fix_zmax(boo);
                fix_zlen(boo);
                                                            
}

/*******************************************************************************
*
*       NAME            :Initialize_flags()
*
*       DESCRIPTION     :   Sets all the data flags to FALSE
*                           Used at the start of editing function
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/


void Block::Scale(int ax,double val){


        switch(ax){

            case XAXIS :
				Xmin->Scale(val);
				Xmid->Scale(val);
				Xmax->Scale(val);
				Xlen->Scale(val);
                break;

            case YAXIS :
				Ymin->Scale(val);
				Ymid->Scale(val);
				Ymax->Scale(val);
				Ylen->Scale(val);
                break;

            case ZAXIS :
				Zmin->Scale(val);
				Zmid->Scale(val);
				Zmax->Scale(val);
				Zlen->Scale(val);
                break;

            default:
                printf("Wrong axis for scaling\n");
                break;

        }

}

double Block::Volume(){

}

void Block::Solid_Display_by_phigs()
{

    Face *tracef = Create_Faces();  // gets the first face in the face list

    Ppoint3         pt[6][4];       // six faces & each has 4 points
    Ppoint_list3    faces[6];       //six faces

    Ppoint_list_list3    faces_set[6];       //six faces

	pset_int_style( PSTYLE_SOLID);
	pset_line_colr_ind( (Pint) 3);
	pset_edge_flag( PEDGE_ON);

	int i;

    for(i=0;i<6;i++){
        faces_set[i].num_point_lists     = 1;
        faces_set[i].point_lists     = &(faces[i]);
    }
    for(i=0;i<6;i++){
        faces[i].num_points     = 4;
        faces[i].points     = pt[i];
    }


    int j=0;            // temporary counter

    while(tracef){

        Vertex *v1 = tracef->Get_V1();
        Vertex *v2 = tracef->Get_V2();
        Vertex *v3 = tracef->Get_V3();
        Vertex *v4 = tracef->Get_V4();

        pt[j][0].x      = (Pfloat)v1->Get_x();
        pt[j][0].y      = (Pfloat)v1->Get_y();
        pt[j][0].z      = (Pfloat)v1->Get_z();

        pt[j][1].x      = (Pfloat)v2->Get_x();
        pt[j][1].y      = (Pfloat)v2->Get_y();
        pt[j][1].z      = (Pfloat)v2->Get_z();

        pt[j][2].x      = (Pfloat)v3->Get_x();
        pt[j][2].y      = (Pfloat)v3->Get_y();
        pt[j][2].z      = (Pfloat)v3->Get_z();

        pt[j][3].x      = (Pfloat)v4->Get_x();
        pt[j][3].y      = (Pfloat)v4->Get_y();
        pt[j][3].z      = (Pfloat)v4->Get_z();


        pfill_area_set3( &faces_set[j]);
        tracef = tracef->Get_nextf();
        j++;
    }

}


