/*******************************************************************************
*       FILENAME :      polygon.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Polygon
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   MAY 29, 1995.
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
*       NAME            :Polygon..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to set vertices etc..
*
*       INPUT           : id , axis,value and four vertices
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Polygon::Polygon(int pid ,int pa,int pv,Vertex *v1,Vertex *v2,Vertex *v3,Vertex *v4) 
{
 
	polygon_id 		= pid;		// Polygon number
	polygon_axis	= pa;           // face type
    polygon_value	= pv;          	// positional value on the axis
 
    V_list_head	= NULL;        	// circular doubly linked list
    nextp		= NULL;  	// next polygon in the list
    prevp		= NULL;  	// next polygon in the list
 
	Add_to_the_V_list(v1);
	Add_to_the_V_list(v2);
	Add_to_the_V_list(v3);
	Add_to_the_V_list(v4);

	double dx1 = v1->Get_x() - v2->Get_x();
	double dy1 = v1->Get_y() - v2->Get_y();
	double dz1 = v1->Get_z() - v2->Get_z();

	double dx2 = v3->Get_x() - v2->Get_x();
	double dy2 = v3->Get_y() - v2->Get_y();
	double dz2 = v3->Get_z() - v2->Get_z();

	/* 
		Now we need to take cross product of these two "difference vectors"


		A X B = (aybz - azby)i - (axbz -bxaz)j + (axby -bxay)k

	*/

	double ix = (dy1*dz2) -(dz1*dy2);
	double iy = (dx2*dz1) -(dx1*dz2);
	double iz = (dx1*dy2) -(dx2*dy1);
	
	normal = new Vector(ix,iy,iz);
}
 
/*******************************************************************************
*
*       NAME            :Polygon..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to set vertices etc..
*
*       INPUT           : id , axis,value and four vertices
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/

Polygon::Polygon(Face *ff)
{

        polygon_id      = ff->Get_face_id();          // Polygon number

        V_list_head     = NULL;         // circular doubly linked list
        nextp           = NULL;         // next polygon in the list
        prevp           = NULL;         // previous polygon in the list
		num_of_points	= 0;
		polygon_axis	= ff->Get_face_type();

        Vertex *V1 = ff->Get_V1();
        Vertex *V2 = ff->Get_V2();
        Vertex *V3 = ff->Get_V3();
        Vertex *V4 = ff->Get_V4();

        Add_to_the_V_list(V1);
        Add_to_the_V_list(V2);
        Add_to_the_V_list(V3);
        Add_to_the_V_list(V4);

    	double dx1 = V1->Get_x() - V2->Get_x();
    	double dy1 = V1->Get_y() - V2->Get_y();
    	double dz1 = V1->Get_z() - V2->Get_z();
 
    	double dx2 = V3->Get_x() - V2->Get_x();
    	double dy2 = V3->Get_y() - V2->Get_y();
    	double dz2 = V3->Get_z() - V2->Get_z();
 
    /*
        Now we need to take cross product of these two "difference vectors"
 
 
        A X B = (aybz - azby)i - (axbz -bxaz)j + (axby -bxay)k
 
    */
 
    	double ix = (dy1*dz2) -(dz1*dy2);
    	double iy = (dx2*dz1) -(dx1*dz2);
    	double iz = (dx1*dy2) -(dx2*dy1);
 
    	normal = new Vector(ix,iy,iz);

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

void Polygon::Add_to_the_V_list(Vertex* vv){

	if( V_list_head == NULL){
	
		V_list_head = vv;
		V_list_head->Set_nextv(V_list_head);
		V_list_head->Set_prevv(V_list_head);

		// vv is now actually head. Its next is itself and its
		// previous is also itself
	}
	else{

		Vertex* q = V_list_head->Get_prevv();
		// By this we get the last element in the list as this is a
		// circular list , head's left is nothing but the last element

		V_list_head->Set_prevv(vv);
		// As we want to add new element at the last we set it to the 
		// head's left thereby taking him to the last positon

		vv->Set_nextv(V_list_head);
		// this last elements next hould obviously be the head as we
		// are going in the circular fashion

		q->Set_nextv(vv);
		// q  is the "old" last element. So new "last " element should
		// be at the right of the "old" last element

		vv->Set_prevv(q);
		// and "new" last elemnts left should point to the 'old' last
		// element
		// Thus every ne element gets added at the tail
	}

	num_of_points++;

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

void Polygon::Print_list(){

	if(V_list_head == NULL)return;

	printf("\nPolygon %d\t",polygon_id);
	printf("Normal\t");
	normal->Print();
/*
	Vertex* tr = V_list_head;
	do{
		tr->Print();
		tr = tr->Get_nextv();

	}while( tr != V_list_head);
*/
}
/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :Inserts Vertex "behind" the "before" Vertex
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void Polygon::Insert_before(Vertex *before,Vertex *vv){

	if(before == NULL)return;
	if(vv == NULL)return;

	Vertex* bbfore = before->Get_prevv();
	bbfore->Set_nextv(vv);
	vv->Set_nextv(before);
	vv->Set_prevv(bbfore);
	before->Set_prevv(vv);

	num_points++;
}
/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :Inserts Vertex after the "After" vertex
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void Polygon::Insert_after(Vertex *after,Vertex *vv){

	if(after==NULL)return;
	if(vv == NULL)return;

	Vertex *aafter = after->Get_nextv();
	vv->Set_nextv(aafter);
	aafter->Set_prevv(vv);
	after->Set_nextv(vv);
	vv->Set_prevv(after);

	num_points++;
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
 

int PolygonSet::Join_if_touching(Polygon *pp,Polygon *pq){


	Vertex *pv1	= pp->Get_V_list_head();

	do{

		Vertex *pv2 = pv1->Get_nextv();

		Vertex *qv1 = pq->Get_V_list_head();

		do{

			Vertex *qv2 = qv1->Get_nextv();
			
			// Now we want to test whether line(pv1,pv2) and line(qv1,qv2)
			// share any common part or not.

			// We will test in the following way.
			// D1 is distance of Q from P1 and D2 is from P2 then..
			// D3 is distance between P1 and P2

			// If D3 = D1 + D2 then Q lies between P1 and P2...
			//( !!!! Distances have to be absolute,)


			double D1 = fabs(qv1->distance(pv1));
			double D2 = fabs(qv1->distance(pv2));
			double D3 = fabs(pv1->distance(pv2));
			

			int check1 = FALSE;
			int check2 = FALSE;

			if((fabs(D3 - D1 -D2))< ZERO)check1 = TRUE;	// inside

			D1 = fabs(qv2->distance(pv1));
			D2 = fabs(qv2->distance(pv2));

			if((fabs(D3 - D1 -D2))< ZERO)check2 = TRUE;	// inside


			if((check1 == TRUE)||(check2 == TRUE)){

				// Atleast one of them lies inside the line (pv1,pv2)

				//  p1--q2  q1--p2

				// I am trying to Insert the Vertex List of PQ polygon 
				// Inbetween P2 and P1

				Vertex *collector = qv1;
				Vertex *before	= pv2;

				// Here we have to go backwards for collecting the Vertices

				while( collector != qv2){

					// By keeping the same vertex id will duplicate the ids in
					// the parent polygon.. We may write Update_ids function

					int vid 	= collector->Get_vertex_id();
					double vx	= collector->Get_x();
					double vy	= collector->Get_y();
					double vz	= collector->Get_z();

					Vertex *me	= new Vertex(vid,vx,vy,vz);
					
					pp->Insert_before(before,me);
						
					//Next time when new vertex comes it should go before "me"
					// thus I will make before = me

					printf("ADDING %d int %d\n",vid,pp->Get_polygon_id());
					before = me;
					collector = collector->Get_prevv();

				}

				// Now collector is the last point from PQ ie "qv2"

				int vvid     = collector->Get_vertex_id();
                double vvx   = collector->Get_x();
                double vvy   = collector->Get_y();
                double vvz   = collector->Get_z();

				Vetrex *last = new Vertex(vvid,vvx,vvy,vvz);

				pp->Insert_before(before,last);
				pp->Insert_after(pv1,last);
				return TRUE;
			}
			else{

				qv1 = qv1->Get_nextv();
			}
		}while( qv1 != pq->Get_V_list_head());

		pv1 = pv1->Get_nextv();

	}while(pv1 != pp->Get_V_list_head());

	return FALSE;
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
 
PolygonSet::PolygonSet(){

	polygonset_id =0;
	num_polygons = 0;
	plane_normal = NULL;
	poly_list_head = NULL;
	nextps = NULL;

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
 
void PolygonSet::Print(){

		printf("*****PolygonSet No = %d\n",polygonset_id);

		Polygon *see = poly_list_head;

		while(see){
			printf("^^^^^^^%d\n",see->Get_polygon_id());
			see->Print_list();
			see = see->Get_nextp();
		}
		printf("Whats problem\n");
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
 
void PolygonSet::Add_to_poly_list(Polygon *pp){

		num_polygons++;
		pp->Set_polygon_id(num_polygons);

        if( poly_list_head == NULL){
 
                poly_list_head = pp;                // first node in the list
                pp->Set_nextp((Polygon *)NULL);
                poly_list_head->Set_nextp((Polygon *)NULL);
                poly_list_head->Set_prevp((Polygon *)NULL);
        }
        else{
                Polygon *tracer = poly_list_head;      // starts at first node
 
                while( tracer->Get_nextp() != NULL){
                        tracer = tracer->Get_nextp();
                }
 
                pp->Set_nextp((Polygon *)NULL);
                pp->Set_prevp(tracer);
                tracer->Set_nextp(pp);
                tracer = tracer->Get_nextp();
                tracer = pp;
                tracer->Set_nextp((Polygon *)NULL);
 
        }
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
 
void PolygonSet::Merge_the_polygons(){

	//Here I am using the same variable names as Iyad's as I am trying to
	//imitate his already proven algorithm

	printf("Came in the function for %d Polygon Set!!!!\n",polygonset_id);

	Polygon *p1 = poly_list_head;	// the first one in the list

	do{

		Polygon *p2 = p1->Get_nextp();


		while(p2 != NULL){

			if(Join_if_touching(p1,p2) == TRUE){

				// this means they share a common edge and the vertices are
				// with P1 now.. we will delete p2 then..

				printf("Both Have common Edge\n");
				Polygon *p3 = p2;
				Polygon *tmp = p2->Get_prevp();
				tmp->Set_nextp(p2->Get_nextp());
				p2 = p2->Get_nextp();
				delete p3;	// remove p2
				printf("Deleting p2\n");
			}
			else{

				p2 = p2->Get_nextp();
			}
		}
	
		p1 = p1->Get_nextp();
	}while(p1 != NULL);


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
 
void Polygon::Display_by_phigs(){

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
 
void PolygonSet::Display_by_phigs(){

	
        printf("PolygonSet No = %d\n",polygonset_id);

    Ppoint_list_list3   point_list_list;
    Ppoint_list3        *point_lists;
    Ppoint3             *points;
 
    //I am using the same variables as Venkys as I am just copying without
    //much modification
 
    int pcounter    = 0;
    Vertex  *v;
 
    int n_poly  = 0;    
    int n_points= 0;  

	
    Polygon *p = poly_list_head;     
 
	while(p){
			n_poly++;
			p = p->Get_nextp();
	}								// Calculated the number of polygons

        Polygon *see = poly_list_head;
	
		
	point_lists	= new Ppoint_list3[n_poly];
	int i=0;

 
	Polygon *pp = poly_list_head;

	while(pp){

		pcounter++;

		Vertex *vv = pp->Get_V_list_head();
/*
		do{
			n_points++;
			vv = vv->Get_nextv();
		}while(vv != pp->Get_V_list_head());
*/
		n_points = pp->Get_num_of_points();
		//printf("NUM POINTS %d\n",n_points);

		points	= new Ppoint3[n_points];

		v = pp->Get_V_list_head();

		int j=0;
		do{
			
			//Assign co-ordinates of each vertices
		
			points[j].x = v->Get_x();
			points[j].y = v->Get_y();
			points[j].z = v->Get_z();

			v=v->Get_nextv();
			j++;
		}while(vv != pp->Get_V_list_head());

		point_lists[i].num_points = n_points;
		point_lists[i].points	= points;
		i++;

		pp = pp->Get_nextp();
	}

	point_list_list.num_point_lists = n_poly;
	point_list_list.point_lists	= point_lists;

/*
	pset_int_style( PSTYLE_SOLID);
	pset_edge_flag(PEDGE_ON);
	Pgcolr	color;
	color.type	= PMODEL_RGB;
	color.val.general.x	= 0.0;
	color.val.general.y	= 1.0;
	color.val.general.z	= 0.0;
	
	pset_edge_colr(&color);
 
*/
	// $$$$$$$$$!!!!!!!!!!!! Write well

	pfill_area_set3(&point_list_list);
	
}
