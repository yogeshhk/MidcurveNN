/*******************************************************************************
*       FILENAME :      mode_driver.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   callbacks related to Mode option on Parent_Menubar
*
*       FUNCTIONS   :   
*			mode_design_cb()
*			mode_mfg_cb()
*			Create_design_menubar()
*			Create_mfg_menubar()
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE        :   APR 12, 1995.
*
*******************************************************************************/


/******************************************************************************
                       INCLUDE FILES
******************************************************************************/

#include "main_window.h"        /* Motif Declarations :header file */
#include "application.h"        /* Application Declarations :header file */
//#include "graphics_phigs.h"     /* Phigs Declarations :header file */

/******************************************************************************
                        GLOBAL DECLARATIONS(INTERFACE)
******************************************************************************/

/********************************************************************************
*
*       NAME    :       void
*                       mode_design__cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   design menu bellow main_menu.Gets called when Design in
*                       Mode of main-menu is selected.
*
*******************************************************************************/

void mode_design_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	Create_design_menubar();
}

/*******************************************************************************
*
*
*       NAME    :       void
*                       mode_mfg_cb(Widget , XtPointer , XtPointer )
*
*
*       DESCRIPTION :   manuf. menu bellow main_menu.Gets called when Design in
*                       Mode of main-menu is selected.
*
*******************************************************************************/

void mode_mfg_cb(Widget widget, XtPointer client_data, XtPointer call_data)
{

	Create_mfg_menubar();
}


/*******************************************************************************
*
*       NAME            :void Create_design_menubar()	
*
*       DESCRIPTION     :Creates design menubar and pulldowns and pullrights
*
*       INPUT           :Uses global child_menu widget as manager
*
*       OUTPUT          :sets global widget design_menubar
*
******************************************************************************/

void Create_design_menubar()
{


        XmString create,deletion,edit,dim,mesh;

        create          = XmStringCreateSimple("Create");
        deletion        = XmStringCreateSimple("Delete");
        edit            = XmStringCreateSimple("Edit");
        dim				= XmStringCreateSimple("DimTol");
        mesh            = XmStringCreateSimple("Mesh");

    design_menubar = XmVaCreateSimpleMenuBar(child_menu, "design_menubar",
                        XmVaCASCADEBUTTON,create,       'C',
                        XmVaCASCADEBUTTON,deletion,     'D',
                        XmVaCASCADEBUTTON,edit,         'E',
                        XmVaCASCADEBUTTON,dim,         	'T',
                        XmVaCASCADEBUTTON,mesh,         'M',
                        XmNrightAttachment,     XmATTACH_FORM,
                        XmNleftAttachment,      XmATTACH_FORM,
                        XmNtopAttachment,       XmATTACH_FORM,
                        XmNbottomAttachment,    XmATTACH_FORM,
                        NULL);

        XmStringFree(create);
        XmStringFree(deletion);
        XmStringFree(edit);
        XmStringFree(dim);
        XmStringFree(mesh);


    XtManageChild (design_menubar);

/*----------------------- Create menu pulldown options declarations---------*/


        Widget pullcreate,pulldelet,pulledit,pulldim,pullmesh;
        Widget pullrightnewcomp,pullrightaddblk,pullrightaddtopolink;

        XmString component,block,topolink;
        XmString geoedit,addlink,dellink;

/*------------------------ Create menu pulldown options ----------------------*/


        component       = XmStringCreateSimple("New_Component");
        block           = XmStringCreateSimple("Add_Block");
        topolink        = XmStringCreateSimple("Add_Topolink");

    pullcreate = XmVaCreateSimplePulldownMenu(design_menubar, "create_menu",
                        0,create_addtopo_cb,
                        XmVaCASCADEBUTTON,component,    'C',
                        XmVaCASCADEBUTTON,block,        'B',
                        XmVaPUSHBUTTON,topolink,        'T',NULL,NULL,
                        NULL);


        /* Note : after first two buttons there is no NULL because we have added
           cascade(pull right )to it.For third option there is no Pullright */

        XmStringFree(component);
        XmStringFree(block);
        XmStringFree(topolink);

/*-----------------------Pull right options for NEW COMPONENT ---------------*/


        XmString rectblock,cylinder,prsmblk;

        rectblock       = XmStringCreateSimple("Block");
        cylinder        = XmStringCreateSimple("Cylinder");
        prsmblk         = XmStringCreateSimple("Prism_Block");

    pullrightnewcomp = XmVaCreateSimplePulldownMenu(pullcreate, "newblk_menu",
                        0,create_newcomp_cb,
                        XmVaPUSHBUTTON,rectblock,       'B',NULL,NULL,
                        XmVaPUSHBUTTON,cylinder,        'C',NULL,NULL,
                        XmVaPUSHBUTTON,prsmblk,         'P',NULL,NULL,
                        NULL);

        XmStringFree(rectblock);
        XmStringFree(cylinder);
        XmStringFree(prsmblk);


/*-------------------------Pull right options for ADD BLOCK  ---------------*/


        XmString addblock,subtblk,addcyl,subtcyl,addprsmblk,subprsmblk,addbspl;

        addblock        = XmStringCreateSimple("ADDT_Block");
        subtblk         = XmStringCreateSimple("SUBT_Block");
        addcyl          = XmStringCreateSimple("ADDT_Cylinder");
        subtcyl         = XmStringCreateSimple("SUBT_Cylinder");
        addprsmblk      = XmStringCreateSimple("ADDT_Wedge");
        subprsmblk      = XmStringCreateSimple("SUBT_Wedge");
        addbspl			= XmStringCreateSimple("ADDT_Bspline");

    pullrightaddblk = XmVaCreateSimplePulldownMenu(pullcreate, "addblk_menu",
                        1,addblk_cb,
                        XmVaPUSHBUTTON,addblock,        'A',NULL,NULL,
                        XmVaPUSHBUTTON,subtblk,         'B',NULL,NULL,
                        XmVaPUSHBUTTON,addcyl,          'C',NULL,NULL,
                        XmVaPUSHBUTTON,subtcyl,         'S',NULL,NULL,
                        XmVaPUSHBUTTON,addprsmblk,      'P',NULL,NULL,
                        XmVaPUSHBUTTON,subprsmblk,      'W',NULL,NULL,
                        XmVaPUSHBUTTON,addbspl,      	'T',NULL,NULL,
                        NULL);

        XmStringFree(addblock);
        XmStringFree(subtblk);
        XmStringFree(addcyl);
        XmStringFree(subtcyl);
        XmStringFree(addprsmblk);
        XmStringFree(subprsmblk);
        XmStringFree(addbspl);

/*-----------------------Pull right options for ADD TOPOLINK  ---------------*/

/*      This is not a cascade button in the pullcreate ,thus adding a call back
        to it is done by other way : attached a call back to pullcreate and here
        it is said that have callback "addtopo_cb" to the button no.2(i.e.third)
        of pullcreate option.
                                                                                */

    pullrightaddtopolink = XmVaCreateSimplePulldownMenu(pullcreate, "addtopo",
                        2,create_addtopo_cb,
                        NULL);


/*-----------------------Pulldown options for DELET  -------------------------*/

        component       = XmStringCreateSimple("Component");
        block           = XmStringCreateSimple("Block");
        topolink        = XmStringCreateSimple("Topolink");

    pulldelet = XmVaCreateSimplePulldownMenu(design_menubar, "delete_menu",
                        1,NULL,
                        XmVaPUSHBUTTON,component,       'C',NULL,NULL,
                        XmVaPUSHBUTTON,block,           'B',NULL,NULL,
                        XmVaPUSHBUTTON,topolink,        'T',NULL,NULL,
                        NULL);

        XmStringFree(component);
        XmStringFree(block);
        XmStringFree(topolink);



/*--------------------------Pulldown options for EDIT  -----------------------*/


        geoedit         = XmStringCreateSimple("Geom_Edit");
        addlink         = XmStringCreateSimple("Add_GeomLink");
        dellink         = XmStringCreateSimple("Del_GeomLink");

    pulledit = XmVaCreateSimplePulldownMenu(design_menubar, "edit_menu",
                        2, edit_cb,
                        XmVaPUSHBUTTON,geoedit,       'G',NULL,NULL,
                        XmVaPUSHBUTTON,addlink,       'A',NULL,NULL,
                        XmVaPUSHBUTTON,dellink,       'D',NULL,NULL,
                        NULL);

        XmStringFree(geoedit);
        XmStringFree(addlink);
        XmStringFree(dellink);

/*-----------------------Pulldown options for DIMENSIONING ------------------*/
 
        XmString defdim,spedim,chgdat,query;

        defdim			= XmStringCreateSimple("DefaultDim");
        spedim			= XmStringCreateSimple("Specify_dim");
        chgdat			= XmStringCreateSimple("ChangeDatum");
        query			= XmStringCreateSimple("Query");
 
    pulldim = XmVaCreateSimplePulldownMenu(design_menubar, "dim_menu",
                        3,dimension_cb,
                        XmVaPUSHBUTTON,defdim,       	'D',NULL,NULL,
                        XmVaPUSHBUTTON,spedim,           'S',NULL,NULL,
                        XmVaPUSHBUTTON,chgdat,        	'C',NULL,NULL,
                        XmVaPUSHBUTTON,query,        	'Q',NULL,NULL,
                        NULL);
 
        XmStringFree(defdim);
        XmStringFree(spedim);
        XmStringFree(chgdat);
        XmStringFree(query);
}

/*******************************************************************************
*
*       NAME            :void Create_mfg_menubar()   
*
*       DESCRIPTION     :Creates manufact. menubar and pulldowns and pullrights
*
*       INPUT           :Uses global child_menu widget as manager
*
*       OUTPUT          :sets global widget mfg_menubar
*
******************************************************************************/

void Create_mfg_menubar()
{

        XmString process,nc,refine;

        process         = XmStringCreateSimple("Process");
        nc              = XmStringCreateSimple("NC_code");
        refine          = XmStringCreateSimple("Refine");



    mfg_menubar = XmVaCreateSimpleMenuBar(child_menu, "mfg_menubar",
                        XmVaCASCADEBUTTON,process,      'P',
                        XmVaCASCADEBUTTON,nc,           'N',
                        XmVaCASCADEBUTTON,refine,       'R',
                        XmNrightAttachment,     XmATTACH_FORM,
                        XmNleftAttachment,      XmATTACH_FORM,
                        XmNtopAttachment,       XmATTACH_FORM,
                        XmNbottomAttachment,    XmATTACH_FORM,
                        NULL);


        XmStringFree(process);
        XmStringFree(nc);
        XmStringFree(refine);

    XtManageChild (mfg_menubar);

}

