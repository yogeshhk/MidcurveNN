/*******************************************************************************
*       FILENAME :      strongcomp.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class StrongComp
*
*       FUNCTIONS   :   Constructor
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   Sept 20, 1995.
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
*       NAME            :StrongComp..... Constructor
*
*       DESCRIPTION     :This is second constructor.
*			 Sets private members properly
*
*       INPUT           : int Id
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
 
StrongComp::StrongComp(int Id)
{

	str_comp_id		= Id ;
	str_node_list	= NULL;
	nextstrcomp		= NULL;

	printf("Came to StrongComp constructor no.%d \n",str_comp_id);

}

/*******************************************************************************
*
*       NAME            :Link_StrongCompNodes( StrongCompNode *nl)
*
*       DESCRIPTION     : Adds the to the link list of nodes connected to this
*                         node and sets pointer to first node (str_node_list)
*                         This new node is added at the tail
*
*       INPUT           : Newly created StrongCompNode
*
*       OUTPUT          : Nothing
*
******************************************************************************/
 
void StrongComp::Link_StrongCompNodes( StrongCompNode *nl)
{
	printf("Came to Linking to Strong Comp %d\n",nl->Get_str_node_id());
 
        if( str_node_list == NULL){
 
                str_node_list = nl;                // first node in the list
                str_node_list->Set_nextstrn((StrongCompNode *)NULL);
                nl->Set_nextstrn((StrongCompNode *)NULL);
        }
        else{
                StrongCompNode *tracer = str_node_list;	// starts at first node
 
                while( tracer->Get_nextstrn() != NULL){
                        tracer = tracer->Get_nextstrn();
                }

				tracer->Set_nextstrn(nl);
                tracer = tracer->Get_nextstrn();
				tracer = nl;
                nl->Set_nextstrn((StrongCompNode *)NULL);

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

void Link_str_comps(StrongComp* ss){
 
 
        if( firststr == NULL){
 
                firststr = ss;                // first node in the list
                firststr->Set_nextstrcomp((StrongComp*)NULL);
                ss->Set_nextstrcomp((StrongComp*)NULL);
        }
        else{
                StrongComp *tracer = firststr;      // starts at first node
 
                while( tracer->Get_nextstrcomp() != NULL){
                        tracer = tracer->Get_nextstrcomp();
                }
 
                tracer->Set_nextstrcomp(ss);
                tracer = tracer->Get_nextstrcomp();
                tracer = ss;
                ss->Set_nextstrcomp((StrongComp*)NULL);
                tracer->Set_nextstrcomp((StrongComp*)NULL);
 
        }
        printf("Linking to strong comps\n");
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

int StrongComp::is_member(int id){
 
        int flag = FALSE ;
 
        if(str_node_list == NULL) printf("No stong Comps\n");
        else{
                StrongCompNode* tra = str_node_list;
                while(tra){
					Node* nnn = tra->Get_str_node();
                    if( nnn->Get_node_id() == id)flag = TRUE ;
                	tra = tra->Get_nextstrn() ;
                }
        }
 
        return flag ;
 
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

StrongCompNode* StrongComp::Get_str_node(int ii){
 
 
        StrongCompNode* currn;
 
        currn = str_node_list;
 
        while (currn != NULL) {
 
		Node* nnn = currn->Get_str_node();

               if (nnn->Get_node_id() == ii) break ;
               else
                   currn = currn->Get_nextstrn() ;
        }
        if (currn == NULL) {
                return (StrongCompNode*)NULL;
        }
        else  return (currn) ;
 
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

void StrongComp::fill_arcs(Graph* gg){
 
 
        printf("FILLING arcs\n");
 
        StrongCompNode* fn = str_node_list;
 
        while(fn){
 
                Node *gn = gg->Get_node(fn->Get_node_id());
                Arc* ga = gn->Get_arc_list() ;
 
                while(ga){
 
					int n1 = (ga->Get_node_A())->Get_node_id();
                    int n2 = (ga->Get_node_B())->Get_node_id();
 
                    if( is_member(n1) && is_member(n2) ){
 
                    	printf("Both %d %d are member of strc\n",n1,n2);
 
						StrongCompNode *st1 =Get_str_node(n1);
						StrongCompNode *st2 =Get_str_node(n2);
						st1->Link_to_Nodelist(st2);
						StrArc* sa = new StrArc(ga,st1,st2);
						st1->Link_to_Arclist(sa);
                	}
                    ga = ga->Get_nextal();

                }
                fn = fn->Get_nextstrn();
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

void StrongComp::Print(){
 
        printf("------------------------------------------\n");
 
        if(str_node_list == NULL)printf("No stong Comps NODES\n");
        else{
                StrongCompNode* tt = str_node_list;
                while(tt){
                   	printf("S_Node_id %d \n",tt->Get_node_id());
               		tt = tt->Get_nextstrn();
                }
        }
 
        printf("------------------------------------------\n");
 
}

