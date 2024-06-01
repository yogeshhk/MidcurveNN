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
#include <ctype.h>
 
/*******************************************************************************
*
*       NAME            :Polygon..... Constructor
*
*       DESCRIPTION     :This is default constructor.
*
*       INPUT           : 
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Polygon::Polygon()
{
		polygon_id 		= 	0;          // Polygon number
        polygon_axis	= 	1;          // face type
        num_of_points	=	0;
        polygon_value	=	0;          // positional value on the axis
        V_list_head 	= 	NULL;       // circular doubly linked list
		normal			=   NULL; 
        nextp			=	NULL;       // next polygon in the list
        prevp			=	NULL; 		// previous polygon in the list
 

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
 
Polygon::Polygon(int pid ,int pa,int pv,Vertex *v1,Vertex *v2,Vertex *v3,Vertex *v4) 
{
 
		polygon_id 		= pid;			// Polygon number
        polygon_axis	= pa;           // face type
        polygon_value	= pv;          	// positional value on the axis
 
        V_list_head	= NULL;     // circular doubly linked list
        nextp		= NULL;  	// next polygon in the list
        prevp		= NULL;  	// next polygon in the list
 

        double x1   = v1->Get_x();
        double y1   = v1->Get_y();
        double z1   = v1->Get_z();
 
        double x2   = v2->Get_x();
        double y2   = v2->Get_y();
        double z2   = v2->Get_z();
 
        double x3   = v3->Get_x();
        double y3   = v3->Get_y();
        double z3   = v3->Get_z();
 
        double x4   = v4->Get_x();
        double y4   = v4->Get_y();
        double z4   = v4->Get_z();
 
        int i1  = v1->Get_vertex_id();
        int i2  = v2->Get_vertex_id();
        int i3  = v3->Get_vertex_id();
        int i4  = v4->Get_vertex_id();
 
        Vertex* vv1 = new Vertex(i1,x1,y1,z1);
        Vertex* vv2 = new Vertex(i2,x2,y2,z2);
        Vertex* vv3 = new Vertex(i3,x3,y3,z3);
        Vertex* vv4 = new Vertex(i4,x4,y4,z4);
 
        Add_to_the_V_list(vv1);
        Add_to_the_V_list(vv2);
        Add_to_the_V_list(vv3);
        Add_to_the_V_list(vv4);

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

		double x1	= V1->Get_x();
		double y1	= V1->Get_y();
		double z1	= V1->Get_z();

		double x2	= V2->Get_x();
		double y2	= V2->Get_y();
		double z2	= V2->Get_z();

		double x3	= V3->Get_x();
		double y3	= V3->Get_y();
		double z3	= V3->Get_z();

		double x4	= V4->Get_x();
		double y4	= V4->Get_y();
		double z4	= V4->Get_z();

		int	i1	= V1->Get_vertex_id();
		int	i2	= V2->Get_vertex_id();
		int	i3	= V3->Get_vertex_id();
		int	i4	= V4->Get_vertex_id();

		Vertex* vv1	= new Vertex(i1,x1,y1,z1);
		Vertex* vv2	= new Vertex(i2,x2,y2,z2);
		Vertex* vv3	= new Vertex(i3,x3,y3,z3);
		Vertex* vv4	= new Vertex(i4,x4,y4,z4);

        Add_to_the_V_list(vv1);
        Add_to_the_V_list(vv2);
        Add_to_the_V_list(vv3);
        Add_to_the_V_list(vv4);

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

	Vertex* ra = V_list_head;
	do{
		ra->Print();
		ra = ra->Get_nextv();

	}while( ra != V_list_head);
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
 
    num_of_points++;
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
 
    num_of_points++;
}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :Inserts Vertex between "Left" and "Right" vertex
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void Polygon::Insert_between(Vertex *left,Vertex *self,Vertex *right){
 
    if(left==NULL)return;
    if(self==NULL)return;
    if(right== NULL)return;
 
    left->Set_nextv(self);
    self->Set_prevv(left);
    right->Set_prevv(self);
    self->Set_nextv(right);
 
    num_of_points++;
}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :Removes "Vertex *de" form the Vertex list
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
int Polygon::Remove(Vertex *node){

	if(node->Get_nextv() == node){
		printf(" ONLY ONE LEFT...\n");
		V_list_head = NULL;
		num_of_points--;
		delete node;
		return TRUE;
	}

	node->Get_prevv()->Set_nextv(node->Get_nextv());
	node->Get_nextv()->Set_prevv(node->Get_prevv());

	if( node == V_list_head){
		V_list_head = V_list_head->Get_nextv();
	}

	num_of_points--;
	delete node;

	return FALSE;

 
/*
    if(V_list_head==NULL)return;
    if(de== NULL)return;

	if(de->Get_nextv() == de){	// want to delete the only vertex
		V_list_head = NULL; 
		num_of_points = 0;
	}
	else{

		if(de== V_list_head){
			V_list_head = V_list_head->Get_nextv();
		}
		Vertex *tmp = de;
		(de->Get_prevv())->Set_nextv(de->Get_nextv());
		(de->Get_nextv())->Set_prevv(de->Get_prevv());
		delete tmp;
    	num_of_points--;
	}

*/

}

/*******************************************************************************
*
*       NAME            :
*
*       DESCRIPTION     :Inserts Vertex between "Left" and "Right" vertex
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void Polygon::Remove_duplicate_Vertices(){

	Vertex* temp;
	if(V_list_head == NULL)return;
	Vertex* leader = V_list_head;

	do{

		Vertex* node = leader->Get_nextv();
		int DELETE_FLAG = FALSE;
		//while( (node != leader)){
		while( (node != leader)&&(node != NULL)){
	
            double dfx  = fabs(node->Get_x() - leader->Get_x());
            double dfy  = fabs(node->Get_y() - leader->Get_y());
            double dfz  = fabs(node->Get_z() - leader->Get_z());
 
            if((dfx < SMALL)&&(dfy <SMALL)&&(dfz<SMALL)){
	
				temp= node->Get_nextv();
				if(Remove(node))return;
				node = temp;
				DELETE_FLAG = TRUE;
			}
			else node = node->Get_nextv();

		}

		if(DELETE_FLAG == TRUE){

			temp = leader->Get_nextv();
			if(Remove(leader))return ;
			leader = temp;
		}
		leader = leader->Get_nextv();

	}while( V_list_head != leader);
/*

	printf("Came to REEEEEEEEEEEEEEEEE\n");

	Vertex *tracer = V_list_head;

	do{
		int flag = FALSE;
		Vertex *v2 = tracer->Get_nextv();

		do{
			double dfx	= fabs(tracer->Get_x() - v2->Get_x());
			double dfy	= fabs(tracer->Get_y() - v2->Get_y());
			double dfz	= fabs(tracer->Get_z() - v2->Get_z());

			if((dfx < SMALL)&&(dfy <SMALL)&&(dfz<SMALL)){

				//Remove(v2);
				v2->Set_rem_flag(TRUE);
				//tracer->Set_rem_flag(TRUE);
				flag = TRUE;
			}
				v2 = v2->Get_nextv();

		}while( v2 != V_list_head);

		if(flag == TRUE){
			tracer = tracer->Get_nextv();
			//Remove(tracer);
			tracer->Set_rem_flag(TRUE);
		}
		

		tracer = tracer->Get_nextv();

	}while( tracer != V_list_head);

	Vertex *see = V_list_head;

	do{

		if(see->Get_rem_flag()== TRUE){

			Vertex* dele = see;
			if(see->Get_nextv()== see){
				V_list_head = NULL;
				num_of_points = 0;
				return TRUE;
			}
			if(see==V_list_head){ V_list_head = V_list_head->Get_nextv();}

        	(see->Get_prevv())->Set_nextv(see->Get_nextv());
        	(see->Get_nextv())->Set_prevv(see->Get_prevv());
			 
			see = see->Get_nextv();

        	delete dele;

        	num_of_points--;
		}
		else{

			see = see->Get_nextv();
		}

	}while( see != V_list_head);

	//if(V_list_head->Get_nextv() == V_list_head)Remove(V_list_head);

	return TRUE;
*/

	printf("Finally Num_OF POINTS %d..\n",num_of_points);
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


			if((check1 == TRUE)&&(check2 == TRUE)){

				// OR condition is better,I know, But we will further need
				// something to avoid two perpendicular intersecting edges as
				// the intersecting point may also make one of the check = TRUE

				//  p1--q2   q1--p2
				// NEW Policy

 
                // I am trying to Insert the Vertex List of PQ polygon
                // Inbetween P2 and P1
 
                Vertex *collector = qv1;
                Vertex *before  = pv2;
 
                // Here we have to go backwards for collecting the Vertices
 
                while( collector != qv2){
 
                    // By keeping the same vertex id will duplicate the ids in
                    // the parent polygon.. We may write Update_ids function
 
                    int vid     = collector->Get_vertex_id();
                    double vx   = collector->Get_x();
                    double vy   = collector->Get_y();
                    double vz   = collector->Get_z();
 
                    Vertex *me  = new Vertex(vid,vx,vy,vz);
 
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
 
                Vertex *last = new Vertex(vvid,vvx,vvy,vvz);
 
                //pp->Insert_before(before,last);
                //pp->Insert_after(pv1,last);
                pp->Insert_between(pv1,last,before);

				pq->Set_V_list_head((Vertex *)NULL);

				/*	
					following is old Logic, won't work because
					same Vertex* gets added to many list and creates
					problem if any one of them gets deleted in Merging()
				*/

				/*	
					pv1->Set_nextv(qv1);	
					qv1->Set_prevv(pv1);	

					qv2->Set_nextv(pv2);	
					pv2->Set_prevv(qv2);	

				//Iyad has done following thing But I don't know why..
				// So I have commented it out

				//pq->Set_V_list_head((Vertex *)NULL);

					int num = pp->Get_num_of_points() + pq->Get_num_of_points();
					pp->Set_num_of_points(num);
				*/

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

        if( poly_list_head == NULL){
 
                poly_list_head = pp;                // first node in the list
                poly_list_head->Set_nextp((Polygon *)NULL);
                poly_list_head->Set_prevp((Polygon *)NULL);
        }
        else{
                Polygon *tracer = poly_list_head;      // starts at first node
 
                while( tracer->Get_nextp() != NULL){
                        tracer = tracer->Get_nextp();
                }
 
                pp->Set_prevp(tracer);
                tracer->Set_nextp(pp);
                tracer = tracer->Get_nextp();
                //tracer = pp;
                tracer->Set_nextp((Polygon *)NULL);
 
        }
		num_polygons++;
		pp->Set_polygon_id(num_polygons);

		//printf("Adding to %d the following Polygon\n",polygonset_id);
		//pp->Print_list();
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
					p1->Remove_duplicate_Vertices();
					if(p1->Get_num_of_points() < 3){

						printf(" I am deleting that polygon here itself\n");

    					if(poly_list_head==NULL)return;
    					if(p1== NULL)return;
 
        				Polygon *tmp = p1;

						if(p1== poly_list_head){
							delete poly_list_head;
                        	poly_list_head = NULL;
                        	num_polygons= 0;
                    	}
						else{

							while(tmp->Get_nextp() != p1){
								tmp = tmp->Get_nextp();
							}
							tmp->Set_nextp(p1->Get_nextp());
        					delete p1;
        					num_polygons--;
						} 
					}
			}
			else{

				p2 = p2->Get_nextp();
			}
		}
	
		p1 = p1->Get_nextp();
	}while(p1 != NULL);

            // We will have to check whether there are still some common
            // edges in the polygon. If yes, then we will have to split it
            // and add new polygon to the list.

	p1 = poly_list_head;   // the first one in the list
 
	if(p1==NULL)return;
   	do{
   		Polygon *p4;
 
     if ((p4 = p1->Split()) != NULL) {

		Add_to_poly_list(p4);
					/*
                    p4->Set_nextp(p1->Get_nextp());
                    p4->Set_prevp(p1);
                    if(p1->Get_nextp() != NULL)p1->Get_nextp()->Set_prevp(p4);
                    p1->Set_nextp(p4);
					*/
                }
        p1 = p1->Get_nextp();
   }while(p1 != NULL);
 
    p1 = poly_list_head;   // the first one in the list
 
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
 
Polygon* Polygon::Split(){

    Vertex *pv1 = V_list_head;
 
	int check=0;

    do{
 
        Vertex *pv2 = pv1->Get_nextv();
 
        Vertex *qv1 = pv2;
 
        while(qv1 != pv1){
 
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
 
            if((fabs(D3 - D1 -D2))< ZERO)check1 = TRUE; // inside
 
            D1 = fabs(qv2->distance(pv1));
            D2 = fabs(qv2->distance(pv2));
 
            if((fabs(D3 - D1 -D2))< ZERO)check2 = TRUE; // inside
 
 
            if((check1 == TRUE)&&(check2 == TRUE)){
 
                // OR condition is better,I know, But we will further need
                // something to avoid two perpendicular intersecting edges as
                // the intersecting point may also make one of the check = TRUE
 
                //  p1--q2   q1--p2
                // NEW Policy
 
				///////////////////////////////////////////////////////
				//////////////////////////////////////////////////

				pv1->Set_nextv(qv2);
				qv2->Set_prevv(pv1);
				pv2->Set_prevv(qv1);
				qv1->Set_nextv(pv2);
				// following checks are to see which loop has the V_List_head
				// so that the other loop can go to the new polygon
 
    			Vertex *tra = qv2;
 
    			do{
        			if(tra== V_list_head)check=1;
        			tra = tra->Get_nextv();
    			}while(tra != pv1);
 
    			tra = pv2;
 
    			do{
        			if(tra== V_list_head)check=2;
        			tra = tra->Get_nextv();
    			}while(tra != qv1);

				printf("CCCCCCCCCCCCCheck = %d\n",check);

				Polygon *p3 = new Polygon();

				switch(check){

					case 1:
						//V_list_head = qv2;
						p3->Set_V_list_head(pv2);
						/*
						Vertex* aa = pv2;
						do{
							int avid = aa->Get_vertex_id();
							double ax= aa->Get_x();
							double ay= aa->Get_y();
							double az= aa->Get_z();
							Vertex *bb = new Vertex(avid,ax,ay,az);
							p3->Add_to_the_V_list(bb);
							aa = aa->Get_nextv();
						}while(aa != pv2);
						*/

						break;
					case 2:
						//V_list_head = pv2;
						p3->Set_V_list_head(qv2);
						/*
                        Vertex* ba = qv2;
                        do{
                            int bvid = ba->Get_vertex_id();
                            double bx= ba->Get_x();
                            double by= ba->Get_y();
                            double bz= ba->Get_z();
                            Vertex *cb = new Vertex(bvid,bx,by,bz);
                            p3->Add_to_the_V_list(cb);
                            ba = ba->Get_nextv();
                        }while(ba != qv2);
						*/
						break;
					default:
						printf("No V Head\n");
						return (Polygon *)NULL;
						break;
				}

    printf("_____Original %d ___________________________\n",polygon_id);
    Vertex *atra = V_list_head;
	int pts =0; 
    do{
		pts++;
        atra->Print();
        atra = atra->Get_nextv();
    }while(atra != V_list_head);
	num_of_points = pts; 

    printf("_____P3 = %d ___________________________\n",p3->Get_polygon_id());
    Vertex *btra = p3->Get_V_list_head();
	int points = 0; 
    do{
		points++;
        btra->Print();
        btra = btra->Get_nextv();
    }while(btra != p3->Get_V_list_head());
 
    printf("________________________________\n");


    	Vertex *V1 = p3->Get_V_list_head();
    	Vertex *V2 = V1->Get_nextv();
    	Vertex *V3 = V2->Get_nextv();

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
 
        Vector *nor = new Vector(ix,iy,iz);

		p3->Set_normal(nor);
		p3->Set_num_of_points(points);

				// Here I should delete all the points gone to p3


			printf("WOWWWWWWWWW Got a new Polygon \n"); 
			return p3;
		}
            else{
 
                qv1 = qv1->Get_nextv();
            }
        }
 
        pv1 = pv1->Get_nextv();
 
    }while(pv1 != V_list_head);
 
    return (Polygon *)NULL;

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

	
    Polygon *p = poly_list_head;
 
    if(p == NULL)return;

	//printf(" Displaying %d ***********\n",polygonset_id);
    Ppoint_list_list3   point_list_list;
    Ppoint_list3        *point_lists;
    Ppoint3             *points;
 
	pset_int_colr_ind(3);		//  Just funny trick

    //I am using the same variables as Venkys as I am just copying without
    //much modification
 
    pset_int_style( PSTYLE_SOLID );
    pset_hlhsr_id( PHIGS_HLHSR_ID_ON );

    int pcounter    = 0;
    Vertex  *v = NULL;
 
    int n_poly  = 0;    
    int n_points= 0;  
	pset_face_cull_mode(PCULL_BACKFACE);

	
	while(p){
		n_poly++;
		p = p->Get_nextp();
	}								// Calculated the number of polygons

	point_lists	= new Ppoint_list3[n_poly];
	int i=0;

 
	Polygon *pp = poly_list_head;

	while(pp){


		switch(pp->Get_block_type()){


			case BLOC:
				pset_face_cull_mode(PCULL_BACKFACE);
				break;

			case SBLOC:
				pset_face_cull_mode(PCULL_FRONTFACE);
				break;

			default:
				pset_face_cull_mode(PCULL_BACKFACE);
				break;
		}

		pcounter++;
		// if(pcounter>1)pset_int_colr_ind(4);		//  Just funny trick

		n_points = pp->Get_num_of_points();

		if(n_points > 0){

			points	= new Ppoint3[n_points];
			v=NULL;
			v = pp->Get_V_list_head();

			int j=0;
			do{
			
				//Assign co-ordinates of each vertices
		
				points[j].x = v->Get_x();
				points[j].y = v->Get_y();
				points[j].z = v->Get_z();

				v=v->Get_nextv();
				j++;
			}while(v != pp->Get_V_list_head());

			point_lists[i].num_points = n_points;
			point_lists[i].points	= points;
			i++;

		}

		pp = pp->Get_nextp();
	}

	if(display_type == SOLID) for(int k = 0;k<n_poly;k++)
		ppolyline3(&point_lists[k]);

	else{


	point_list_list.num_point_lists = n_poly;
	point_list_list.point_lists	= point_lists;

	pset_int_style( PSTYLE_SOLID);
	pset_edge_flag(PEDGE_ON);
	Pgcolr	color;
	color.type	= PMODEL_RGB;
	color.val.general.x	= 0.0;
	color.val.general.y	= 0.0;
	color.val.general.z	= 0.0;
	
	pset_edge_colr(&color);
 
	// $$$$$$$$$!!!!!!!!!!!! Write well

	pfill_area_set3(&point_list_list);
	}
	
}
