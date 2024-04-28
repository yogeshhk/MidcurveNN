/*******************************************************************************
*       FILENAME :      dimensiongraph.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class DimensionGraph
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
*       NAME            :DimensionGraph..... Constructor
*
*       DESCRIPTION     :
*
*       INPUT           : 
*
*       OUTPUT          :
*
*******************************************************************************/
 
DimensionGraph::DimensionGraph():num_nodes(0),X_DimList(0),Z_DimList(0),
												Y_DimList(0),O_DimList(0){

}

/*******************************************************************************
*
*       NAME            :DimensionGraph..... Constructor
*
*       DESCRIPTION     :This is second constructor. Gets all the values
*                        reqd. to call Node constructor etc.
*
*       INPUT           : parent component 
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
DimensionGraph::DimensionGraph(Component *gc)
{
 
    graph_id    	= 	gc->Get_component_id();   
    graph_node  	= 	NULL;
    dim_comp 		= 	gc ;
	num_nodes		=	0; 
    X_DimList		=	NULL;     	// List of Dim nodes in X direction
    Y_DimList		=	NULL;     	// List of Dim nodes in Y direction
    Z_DimList		=	NULL;     	// List of Dim nodes in Z direction
    O_DimList		=	NULL;     	// List of Dim nodes in Other  direction

	//	Gets all the blocks of "gc" gets everybodies Facelist
	//	Creates dimplanes and adds to X/Y/Z list according to plane type.
	//	Also adds those DimNodes to *firstnode in Graph::

	printf("DimensionGraph Constructor\n");

}


/*******************************************************************************
*
*       NAME            :Add_to_dimlist(int type,DimNode* dn)
*
*       DESCRIPTION     : Adds the to the link list of Dimnodes
*
*       INPUT           : type of the list, and actual node to be added
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
 
void DimensionGraph::Add_to_dimlist(int type,DimNode* dn){
 
       // printf("Came to linking of the Node list in DimensionGraph\n");
 
    DimNode* tracer;
 
    switch(type){
 
        case XAXIS:
 
            if(!X_DimList){
                X_DimList = dn;                // first node in the list
                X_DimList->Set_nextdn((DimNode *)NULL);
            }
            else{
                tracer = X_DimList;      // starts at first node
                while(tracer->Get_nextdn())tracer = tracer->Get_nextdn();
                tracer->Set_nextdn(dn);
                tracer = tracer->Get_nextdn();
                tracer = dn;
                dn->Set_nextdn((DimNode *)NULL);
            }
            break;
 
        case YAXIS:
 
            if(!Y_DimList){
                Y_DimList = dn;                // first node in the list
                Y_DimList->Set_nextdn((DimNode *)NULL);
            }
            else{
                tracer = Y_DimList;      // starts at first node
                while(tracer->Get_nextdn())tracer = tracer->Get_nextdn();
                tracer->Set_nextdn(dn);
                tracer = tracer->Get_nextdn();
                tracer = dn;
                dn->Set_nextdn((DimNode *)NULL);
            }
            break;
 
 
        case ZAXIS:
 
            if(!Z_DimList){
                Z_DimList = dn;                // first node in the list
                Z_DimList->Set_nextdn((DimNode *)NULL);
            }
            else{
                tracer = Z_DimList;      // starts at first node
                while(tracer->Get_nextdn())tracer = tracer->Get_nextdn();
                tracer->Set_nextdn(dn);
                tracer = tracer->Get_nextdn();
                tracer = dn;
                dn->Set_nextdn((DimNode *)NULL);
            }
            break;
 
        default :
 
            if(!O_DimList){
                O_DimList = dn;                // first node in the list
                O_DimList->Set_nextdn((DimNode *)NULL);
            }
            else{
                tracer = O_DimList;      // starts at first node
                while(tracer->Get_nextdn())tracer = tracer->Get_nextdn();
                tracer->Set_nextdn(dn);
                tracer = tracer->Get_nextdn();
                tracer = dn;
                dn->Set_nextdn((DimNode *)NULL);
            }
            break;
 
    }
	num_nodes++;

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
 
void DimensionGraph::PrintYourself(FILE* fo){
 
    DimNode* tra;
 
    printf("**************************************************\n");
 
    /*
    **      Printing X Node list
    */
 
    tra = X_DimList;
    printf("\nX\n");
    while(tra){
        tra->PrintYourself(stdout);
        tra = tra->Get_nextdn();
    }
 
    tra = Y_DimList;
    printf("\nY\n");
    while(tra){
        tra->PrintYourself(stdout);
        tra = tra->Get_nextdn();
    }
 
    tra = Z_DimList;
    printf("\nZ\n");
    while(tra){
        tra->PrintYourself(stdout);
        tra = tra->Get_nextdn();
    }
 
    tra = O_DimList;
    printf("\nOthers\n");
 
    while(tra){
 
        tra->PrintYourself(stdout);
        tra = tra->Get_nextdn();
 
    }
 
    printf("**************************************************\n");
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
 
int*	DimensionGraph::Get_node_ids(int axs){

	int dim_axis;
	int node_count =0;
	DimNode* tra;
	int* id_list=NULL;
	int id=0;

    switch(axs){
 
        case XAXIS :
                dim_axis = XAXIS;
				tra	=	X_DimList;
				while(tra){
					node_count++;				
					if(tra)tra = tra->Get_nextdn();
				}
				id_list = new int[node_count+1];
				tra	=	X_DimList;
                while(tra){
					id_list[id] = tra->Get_dim_node_id();
                    ++id;  
                    if(tra)tra = tra->Get_nextdn();
                }

                break;
 
        case YAXIS :
                dim_axis = YAXIS;
                tra =   Y_DimList;              
                while(tra){
                    node_count++;  
                    if(tra)tra = tra->Get_nextdn();
                }
                id_list = new int[node_count+1];
                tra =   Y_DimList;
                while(tra){
                    id_list[id] = tra->Get_dim_node_id();
                    ++id;  
                    if(tra)tra = tra->Get_nextdn();
                }
 
                break;
 
        case ZAXIS :
                dim_axis = ZAXIS;
                tra =   Z_DimList;              
                while(tra){
                    node_count++;  
                    if(tra)tra = tra->Get_nextdn();
                }
                id_list = new int[node_count+1];
                tra =   Z_DimList;
                while(tra){
                    id_list[id] = tra->Get_dim_node_id();
                    ++id;  
                    if(tra)tra = tra->Get_nextdn();
                }
 
                break;
 
        case OAXIS :
                dim_axis = OAXIS;
                tra =   O_DimList;              
                while(tra){
                    node_count++;  
                    if(tra)tra = tra->Get_nextdn();
                }
                id_list = new int[node_count+1];
                tra =   O_DimList;
                while(tra){
                    id_list[id] = tra->Get_dim_node_id();
                    ++id;  
                    if(tra)tra = tra->Get_nextdn();
                }
 
                break;
        default :
                dim_axis = YAXIS ;
                break;
    }

	return id_list;
}

/*******************************************************************************
*
*       NAME            :	ComputePath()
*
*       DESCRIPTION     :	Takes two node ids and compute the path
*							between them.Returns list of arcs
*							connecting the two nodes
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
DimArc*    DimensionGraph::ComputePath(int node1,int node2){

	if(node1==node2)return (DimArc*)NULL;

	/*
	**	Above termination ensures that same nodes are not passed to
	**	the algorithm
	*/

	DimNode* w;
	DimNode* n1	= Get_DimNode(node1);
	DimNode* n2	= Get_DimNode(node2);

	printf("In Path Node1 = %d\n",n1->Get_dim_node_id());
	printf("In Path Node2 = %d\n",n2->Get_dim_node_id());

	Que<DimNode>*	L	= new Que<DimNode>();
	Stack<DimNode>*	S	= new Stack<DimNode>();

	if(n1->Is_Visited() == FALSE){
		n1->Set_Visited(TRUE);
		S->Push(n1);
	}

	while(!S->Empty()){

		n1	= S->Pop();
		L->Enqueue(n1);
		printf("Adding %d to List\n",n1->Get_dim_node_id());

		DimArc* arc	= n1->Get_dim_arcs_out();

		while(arc){
			w	= arc->Get_nodeB();
			printf("Going for Adj Node %d\n",w->Get_dim_node_id());

			if(w->Is_Visited()==FALSE){
				w->Set_Visited(TRUE);
				S->Push(w);
			}

			arc = arc->Get_nextda();

		}
	}

	printf("So Far So Good : Num items = %d \n",L->Get_num_elements());

	DimArc*	firsta = (DimArc*)NULL;
	double	value;
	int		counter=0;

	DimNode* tra2;
	DimNode* tra1	=	L->Dequeue();	// Has to be n1
	if(tra1)tra2	= 	L->Dequeue();
	if(tra2){
		value	= tra2->Get_dim_value() - tra1->Get_dim_value();
		firsta	= new DimArc(++counter,tra1,tra2,value,0);
	}

	while(tra2 != n2){

		tra1	= tra2;
		tra2	= L->Dequeue();
		if(tra2){

			DimArc* tmp;
        	value   = tra2->Get_dim_value() - tra1->Get_dim_value();
        	tmp		= new DimArc(++counter,tra1,tra2,value,0);
			DimArc *tra= firsta;
			while(tra->Get_nextda())tra = tra->Get_nextda();
			tra->Set_nextda(tmp);
			tra	= tmp;
			tra->Set_nextda((DimArc*)NULL);
		}
		else break;

	}
	return firsta;
}

/*******************************************************************************
*
*       NAME            :   Get_DimNode()
*
*       DESCRIPTION     :   Takes node id and returns the node
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
DimNode*    DimensionGraph::Get_DimNode(int node){
 
	DimNode*	tra	=	NULL;		//	traversal node
	int	id;
 
	for(tra	= X_DimList;tra;tra = tra->Get_nextdn()){
		id = tra->Get_dim_node_id();
		if(id==node)return tra;
	}
 
	for(tra	= Y_DimList;tra;tra = tra->Get_nextdn()){
		id = tra->Get_dim_node_id();
		if(id==node)return tra;
	}
	for(tra	= Z_DimList;tra;tra = tra->Get_nextdn()){
		id = tra->Get_dim_node_id();
		if(id==node)return tra;
	}
	for(tra	= O_DimList;tra;tra = tra->Get_nextdn()){
		id = tra->Get_dim_node_id();
		if(id==node)return tra;
	}

	printf("Dimension node %d Not found !!!\n",node);
	return (DimNode*)NULL;
}

/*******************************************************************************
*
*       NAME            :   DeleteArc()
*
*       DESCRIPTION     :   Takes node ids and removes the arc between them
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void	DimensionGraph::DeleteArc(int node1,int node2){

	printf("In delete Arc with %d and %d\n",node1,node2);

    DimNode*    nod1    = Get_DimNode(node1);
    DimNode*    nod2    = Get_DimNode(node2);
 
	nod1->RemoveArc(nod2);
	nod2->RemoveArc(nod1); 


}

/*******************************************************************************
*
*       NAME            :   BuildArc()
*
*       DESCRIPTION     :   Takes node ids and removes the arc between them
*
*       INPUT           :
*
*       OUTPUT          :
*
******************************************************************************/
 
void    DimensionGraph::BuildArc(int node1,int node2){

	DimNode*	nod1	= Get_DimNode(node1);
	DimNode*	nod2	= Get_DimNode(node2);
 
 
	double	value1	=	nod2->Get_dim_value() - nod1->Get_dim_value();
    DimArc* tmp1    = 	new DimArc(0,nod1,nod2,value1,0);
	// 	I dont know what to put for arc id
	//	Best way is to get ids of deleted arc(somehow) and then set it

	double	value2	=	nod1->Get_dim_value() - nod2->Get_dim_value();
    DimArc* tmp2    = 	new DimArc(0,nod1,nod2,value2,0);
	// 	I dont know what to put for arc id


	nod1->Add_to_dim_arclist_out(tmp1);
	nod2->Add_to_dim_arclist_out(tmp2);
	printf("In Build Arc with %d and %d\n",node1,node2);
}

DimNode* DimensionGraph::Get_matching_node(Face* face){
 
 
	if(!face)return (DimNode*)NULL;

	int type = face->Get_face_type();

	Vertex *v1  = face->Get_V1();

	double	value1;
	double	value2;

	DimNode* tra = NULL ;

    switch(type){
 
        case XAXIS:
 
            value1  =   v1->Get_x();    // numerical value of dimplane

			tra = X_DimList;
			
			if(!tra)return (DimNode*)NULL;

			while(tra){
            	value2  =   tra->Get_dim_value();           
				if(fabs(value2-value1)< SMALL)return tra;
				tra = tra->Get_nextdn();
			}

            break;
 
        case YAXIS:
 
            value1  =   v1->Get_y();    // numerical value of dimplane
            tra = Y_DimList;
			if(!tra)return (DimNode*)NULL;
 
            while(tra){
            	value2  =   tra->Get_dim_value();           
				double diff = fabs(value2-value1);
                if(fabs(value2-value1)< SMALL)return tra;
                tra = tra->Get_nextdn();
            }

            break;
 
        case ZAXIS:
 
            value1  =   v1->Get_z();    // numerical value of dimplane
            tra = Z_DimList;
			if(!tra)return (DimNode*)NULL;
 
            while(tra){
            	value2  =   tra->Get_dim_value();           
                if(fabs(value2-value1)< SMALL)return tra;
                tra = tra->Get_nextdn();
            }

            break;
 
        default:
 
            // Need to code for other category
            // We need to find out distance of the plane from origin and
            // with directional sense(+/-)
 
            break;
    }
 
    return (DimNode*)NULL;
}
 
 
void DimensionGraph::Fill_Dim_Arcs(){
 
    double  value=0;
    double  tol=0.1;
 
    int     arc_count=1;
 
    DimNode*    XDatum  =   X_DimList;
    DimNode*    Xtracer = NULL;
 
    if(XDatum)Xtracer   = XDatum->Get_nextdn();
 
    while(Xtracer){
 
        value   = (Xtracer->Get_dim_value()) - (XDatum->Get_dim_value());
        DimArc* xarc1= new DimArc(arc_count++,XDatum,Xtracer,value,tol);
        DimArc* xarc2= new DimArc(arc_count++,Xtracer,XDatum,- value,-tol);
        XDatum->Add_to_dim_arclist_out(xarc1);
        Xtracer->Add_to_dim_arclist_out(xarc2);
 
        Xtracer = Xtracer->Get_nextdn();
    }
 
    DimNode*    YDatum =   Y_DimList;
    DimNode*    Ytracer = NULL;
 
    if(YDatum)Ytracer  = YDatum->Get_nextdn();
 
    while(Ytracer){
 
        value   = (Ytracer->Get_dim_value()) - (YDatum->Get_dim_value());
        DimArc* yarc1= new DimArc(arc_count++,YDatum,Ytracer,value,tol);
        DimArc* yarc2= new DimArc(arc_count++,Ytracer,YDatum,-value,-tol);
        YDatum->Add_to_dim_arclist_out(yarc1);
        Ytracer->Add_to_dim_arclist_out(yarc2);
 
        Ytracer = Ytracer->Get_nextdn();
    }
 
    DimNode*    ZDatum =   Z_DimList;
    DimNode*    Ztracer = NULL;
 
    if(ZDatum)Ztracer  = ZDatum->Get_nextdn();
 
    while(Ztracer){
 
        value   = (Ztracer->Get_dim_value()) - (ZDatum->Get_dim_value());
        DimArc* zarc1= new DimArc(arc_count++,ZDatum,Ztracer,value,tol);
        DimArc* zarc2= new DimArc(arc_count++,Ztracer,ZDatum,-value,-tol);
        ZDatum->Add_to_dim_arclist_out(zarc1);
        Ztracer->Add_to_dim_arclist_out(zarc2);
 
        Ztracer = Ztracer->Get_nextdn();
    }
 
    DimNode*    ODatum =   O_DimList;
    DimNode*    Otracer = NULL;
 
    if(ODatum)Otracer  = ODatum->Get_nextdn();
 
    while(Otracer){
 
        value   = (Otracer->Get_dim_value()) - (ODatum->Get_dim_value());
        DimArc* oarc1= new DimArc(arc_count++,ODatum,Otracer,value,tol);
        DimArc* oarc2= new DimArc(arc_count++,Otracer,ODatum,-value,-tol);
        ODatum->Add_to_dim_arclist_out(oarc1);
        Otracer->Add_to_dim_arclist_out(oarc2);
 
        Otracer = Otracer->Get_nextdn();
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
 
void DimensionGraph::Write_to_file(FILE* fo){

	/*
	**		The format goes like this
	**		Every ile will have a keyword at the start and by which
	**		the switching takes palce and the further data is read
	**
	**		Write to the file whether this is REF graph or SPEC graph
	**		before coming here.
	*/
	
	DimNode* tra = NULL;
	tra = X_DimList;
	while(tra){
		tra->PrintYourself(fo);
		tra = tra->Get_nextdn();
	}

    tra = Y_DimList;
    while(tra){
		tra->PrintYourself(fo);
        tra = tra->Get_nextdn();
    }

    tra = Z_DimList;
    while(tra){
		tra->PrintYourself(fo);
        tra = tra->Get_nextdn();
    }

    tra = O_DimList;
    while(tra){
		tra->PrintYourself(fo);
        tra = tra->Get_nextdn();
    }

	fprintf(fo,"CLOSE\n");
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
 
void DimensionGraph::Read_from_file(FILE* fp){
 
}

