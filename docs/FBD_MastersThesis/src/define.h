/*******************************************************************************
*       FILENAME :   define.h         DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :Header file for Phigs C++
*
*       USAGE :	This is to over_write phigs declarations in phigsextern.h
*
*       AUTHOR      :   Yogesh Kulkarni
*
*       DATE    :       May 27, 1995.
*
*******************************************************************************/

#ifndef _DEFINE_H_
#define _DEFINE_H_

void pbuild_tran_matrix3(Ppoint3*,Ppoint3*,Pfloat,Pfloat,Pfloat,Pvec3*,Pint*,Pmatrix3);
void pclose_struct(void);
void pclose_ws(Pint);
void pclose_phigs(void);
void pcreate_store(Pint*,Pstore*);
void pfill_area_set3(Ppoint_list_list3*);
void peval_view_ori_matrix3(Ppoint3*,Pvec3*,Pvec3*,Pint*,Pmatrix3);
void peval_view_map_matrix3(Pview_map3*,Pint*,Pmatrix3);
void pinq_ws_conn_type(Pint, Pstore,Pint*,void**,Pint*);
void pinq_sys_st(Psys_st *st);
void pinq_ws_st(Pws_st *ss);
void pinq_disp_space_size3(Pint,Pint*,Pdisp_space_size3*);
void pinq_hlhsr_mode(Pint,Pint*,Pupd_st*,Pint*,Pint*);
void pinq_hlhsr_mode_facs(Pint,Pint,Pint,Pint*,Pint_list*,Pint*);
void pinq_ws_tran3(Pint,Pint*,Pupd_st*,Plimit3*,Plimit3*,Plimit3*,Plimit3*);  
void ppolyline(Ppoint_list *ptr);
void ppolyline_set3_data(Pint , Pint ,Pint, Pline_vdata_list3 *po);
void pexec_struct(Pint);
void ppost_struct(Pint,Pint,Pfloat);
void predraw_all_structs(Pint,Pctrl_flag);
void pfill_area3(Ppoint_list3*);
void ppost_struct(Pint,Pint,Pfloat);
Pint phigs_ws_type_create(Pint,Phigs_ws_type_attr);
void pset_light_src_rep(Pint,Pint,Plight_src_bundle*);
void pnuni_bsp_curv(Pint,Pfloat_list*,Prational,Ppoint_list34*,Pfloat,Pfloat);
void pnuni_bsp_surf(Pint,Pint,Pfloat_list*,Pfloat_list*,
					Prational,Ppoint_grid34*,Pint,Ptrimcurve_list *);
void pset_para_surf_characs(Pint ,Ppara_surf_characs *);
void pset_surf_approx(Pint,Pfloat,Pfloat);
void ppolymarker3(Ppoint_list3*);


void ppolyline3(Ppoint_list3*);
void  popen_struct(Pint);
void popen_phigs(char *tt, size_t);
void popen_ws(Pint,Pconnid*,Pint);
void poffset_elem_ptr(Pint);
void plabel(Pint);

void  pset_char_expan( Pfloat );
void  pset_char_space( Pfloat );
void  pset_char_up_vec( Pvec *up);
void  pset_text_path( Ptext_path );
void  pset_text_align( Ptext_align *align);
void  pset_disp_upd_st(Pint,Pdefer_mode,Pmod_mode);
void  pset_edit_mode(Pedit_mode);
void  pset_elem_ptr(Pint);
void pset_elem_ptr_label(Pint);
void pset_local_tran3(Pmatrix3,Pcompose_type);
void pset_int_style(Pint_style);
void  pset_hlhsr_id(Pint);
void pset_int_colr_ind(Pint);
void pset_view_rep3(Pint, Pint,Pview_rep3 *rep);
void pset_hlhsr_mode(Pint,Pint);
void pset_linewidth(Pfloat);
void pset_linetype(Pint);
void pset_line_colr_ind(Pint);
void pset_text_colr_ind(Pint);
void pset_text_colr(Pgcolr *col);
void pset_text_font(Pint);
void pset_text_prec(Ptext_prec prc);
void pset_char_ht(Pfloat);
void pset_view_ind(Pint);
void pset_face_cull_mode(Pcull_mode);
void pset_ws_win3(Pint , Plimit3*);
void pset_ws_vp3(Pint, Plimit3*);
void pset_colr_rep(Pint,Pint,Pcolr_rep*);
void pset_colr_model(Pint,Pint);         
void pset_edge_flag(Pedge_flag);
void pset_edge_colr_ind(Pint);
void pset_edge_colr(Pgcolr *);
void pdel_struct(Pint);
void pdel_all_structs();
void punpost_all_structs(Pint);
void punpost_struct(Pint,Pint);
void pupd_ws(Pint,Pregen_flag);
void ptranslate3(Pvec3*,Pint*,Pmatrix3);
void ptext(Ppoint *text,char *tt);
void ptext3(Ppoint3*,Pvec3 dir[2],char*);


void protate_x(Pfloat,Pint*,Pmatrix3);
void protate_y(Pfloat,Pint*,Pmatrix3);
void protate_z(Pfloat,Pint*,Pmatrix3);
void popen_xphigs(char*,size_t,unsigned long,Pxphigs_info*);

#endif
