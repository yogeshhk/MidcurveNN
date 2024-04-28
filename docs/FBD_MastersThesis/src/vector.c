/*******************************************************************************
*       FILENAME :      vector.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Vector
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
#include <math.h>
 
#define	VERY_SMALL	0.0001

/*******************************************************************************
*
*       NAME            :Vector..... Constructor
*
*       DESCRIPTION     :This is second constructor.
*
*       INPUT           : All the vertedx values 
*
*       OUTPUT          : Undefined bdy C++
*
*******************************************************************************/
 
Vector::Vector(double vdx,double vdy,double vdz)
{

	dx = vdx ;
	dy = vdy ;
	dz = vdz ;
	
	dist = sqrt( (dx*dx) + (dy*dy) + (dz*dz));

}
 
Vector* Vector::operator=(Vector* rv){

	dx = rv->Get_dcx();
	dy = rv->Get_dcy();
	dz = rv->Get_dcz();

}

double Vector::distance(){

	return sqrt( dx*dx + dy*dy + dz*dz);
}
double Vector::distance(Vector* v){

	double vdx = v->Get_dcx();
	double vdy = v->Get_dcy();
	double vdz = v->Get_dcz();

	double ddx = vdx - dx;
	double ddy = vdy - dy;
	double ddz = vdz - dz;

	return sqrt( ddx*ddx + ddy*ddy + ddz*ddz);
}

double Vector::angle_xy(){

	return atan2(dy,dx);
}

double Vector::angle_yz(){

	return atan2(dz,dy);
}


double Vector::angle_zx(){

	return atan2(dx,dz);
}

Vector* Vector::operator+(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    double ddx = vdx + dx;
    double ddy = vdy + dy;
    double ddz = vdz + dz;

    dx = ddx;
    dy = ddy;
    dz = ddz;

    return this;

}

Vector* Vector::operator-(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    double ddx = vdx - dx;
    double ddy = vdy - dy;
    double ddz = vdz - dz;

	dx = ddx;
	dy = ddy;
	dz = ddz;

    return this;

}

Vector* Vector::operator+(){

	return this;
}

Vector* Vector::operator-(){

	double dxdx = dx;
	double dydy = dy;
	double dzdz = dz;

	dx = -dxdx;
	dy = -dydy;
	dz = -dzdz;

	return this;
}

Vector* Vector::operator*(double f){

    double dxdx = dx;
    double dydy = dy;
    double dzdz = dz;

    dx = dxdx*f;
    dy = dydy*f;
    dz = dzdz*f;

    return this;

}
Vector* Vector::operator/(double f){

    double dxdx = dx;
    double dydy = dy;
    double dzdz = dz;

    dx = dxdx/f;
    dy = dydy/f;
    dz = dzdz/f;

    return this;

}
Vector* Vector::operator+=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    dx += vdx;
    dy += vdy;
    dz += vdz;

    return this;

}
Vector* Vector::operator-=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    dx -= vdx;
    dy -= vdy;
    dz -= vdz;

    return this;

}

Vector* Vector::operator*=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    dx *= vdx;
    dy *= vdy;
    dz *= vdz;

    return this;

}
Vector* Vector::operator/=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    dx /= vdx;
    dy /= vdy;
    dz /= vdz;

    return this;

}

Vector* Vector::operator++(){

	dx++;
	dy++;
	dz++;
	return this;
}

Vector* Vector::operator--(){

    dx--;
    dy--;
    dz--;
    return this;
}

int  Vector::operator>(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

	if( (dx > vdx) && (dy > vdy) && ( dz > vdz))return TRUE;
	else FALSE;
}

int  Vector::operator<(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    if( (dx < vdx) && (dy < vdy) && ( dz < vdz))return TRUE;
    else FALSE;
}

int  Vector::operator>=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    if( (dx >= vdx) && (dy >= vdy) && ( dz >= vdz))return TRUE;
    else FALSE;
}

int  Vector::operator<=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    if( (dx <= vdx) && (dy <= vdy) && ( dz <= vdz))return TRUE;
    else FALSE;
}

int  Vector::operator==(Vector *v){

    double vdx = v->Get_dcx() - dx ;
    double vdy = v->Get_dcy() - dy ;
    double vdz = v->Get_dcz() - dz ;
	double ddist = v->distance() -dist;

    if((vdx <= VERY_SMALL)&&(vdy <=VERY_SMALL)&&(vdz <=VERY_SMALL)&&(ddist<= VERY_SMALL))return TRUE;
    else return FALSE;
}
int  Vector::operator!=(Vector *v){

    double vdx = v->Get_dcx();
    double vdy = v->Get_dcy();
    double vdz = v->Get_dcz();

    if( (dx != vdx) && (dy != vdy) && ( dz != vdz))return TRUE;
    else FALSE;
}

void Vector::Print(){

	printf("Vector = %f %f %f\n",dx,dy,dz);
}




