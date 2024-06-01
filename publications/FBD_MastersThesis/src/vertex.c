/*******************************************************************************
*       FILENAME :      vertex.c      DESIGN REF :  FBD(CAD/CAPP)
*
*       DESCRIPTION :   Member functions related to Class Vertex
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
*       NAME            :Vertex..... Constructor
*
*       DESCRIPTION     :This is second constructor.
*
*       INPUT           : All the vertex values 
*
*       OUTPUT          : Undefined by C++
*
*******************************************************************************/
 
Vertex::Vertex(int vid ,double vx,double vy,double vz)
{
	vertex_id = vid ;

	rem_flag = FALSE;

	x = vx ;
	y = vy ;
	z = vz ;

	nextv = NULL;
	prevv = NULL;
}
 
Vertex* Vertex::operator=(Vertex* rv){

	vertex_id = rv->Get_vertex_id();

	x = rv->Get_x();
	y = rv->Get_y();
	z = rv->Get_z();

	nextv = rv->Get_nextv();
	prevv = rv->Get_prevv();

}

double Vertex::distance(){

	return sqrt( x*x + y*y + z*z);
}
double Vertex::distance(Vertex* v){

	double vx = v->Get_x();
	double vy = v->Get_y();
	double vz = v->Get_z();

	double dx = vx - x;
	double dy = vy - y;
	double dz = vz - z;

	return sqrt( dx*dx + dy*dy + dz*dz);
}

double Vertex::angle_xy(){

	return atan2(y,x);
}

double Vertex::angle_yz(){

	return atan2(z,y);
}


double Vertex::angle_zx(){

	return atan2(x,z);
}

Vertex* Vertex::operator+(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    double dx = vx + x;
    double dy = vy + y;
    double dz = vz + z;

    x = dx;
    y = dy;
    z = dz;

    return this;

}

Vertex* Vertex::operator-(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    double dx = vx - x;
    double dy = vy - y;
    double dz = vz - z;

	x = dx;
	y = dy;
	z = dz;

    return this;

}

Vertex* Vertex::operator+(){

	return this;
}

Vertex* Vertex::operator-(){

	double xx = x;
	double yy = y;
	double zz = z;

	x = xx;
	y = yy;
	z = zz;

	return this;
}

Vertex* Vertex::operator*(double f){

    double xx = x;
    double yy = y;
    double zz = z;

    x = xx*f;
    y = yy*f;
    z = zz*f;

    return this;

}
Vertex* Vertex::operator/(double f){

    double xx = x;
    double yy = y;
    double zz = z;

    x = xx/f;
    y = yy/f;
    z = zz/f;

    return this;

}
Vertex* Vertex::operator+=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    x += vx;
    y += vy;
    z += vz;

    return this;

}
Vertex* Vertex::operator-=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    x -= vx;
    y -= vy;
    z -= vz;

    return this;

}

Vertex* Vertex::operator*=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    x *= vx;
    y *= vy;
    z *= vz;

    return this;

}
Vertex* Vertex::operator/=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    x /= vx;
    y /= vy;
    z /= vz;

    return this;

}

Vertex* Vertex::operator++(){

	x++;
	y++;
	z++;
	return this;
}

Vertex* Vertex::operator--(){

    x--;
    y--;
    z--;
    return this;
}

int  Vertex::operator>(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

	if( (x > vx) && (y > vy) && ( z > vz))return TRUE;
	else FALSE;
}

int  Vertex::operator<(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    if( (x < vx) && (y < vy) && ( z < vz))return TRUE;
    else FALSE;
}

int  Vertex::operator>=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    if( (x >= vx) && (y >= vy) && ( z >= vz))return TRUE;
    else FALSE;
}

int  Vertex::operator<=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    if( (x <= vx) && (y <= vy) && ( z <= vz))return TRUE;
    else FALSE;
}

int  Vertex::operator==(Vertex *v){

    double vx = fabs(v->Get_x() - x);
    double vy = fabs(v->Get_y() - y);
    double vz = fabs(v->Get_z() - z);

    if( (vx < SMALL) && (vy < SMALL) && ( vz < SMALL))return TRUE;
    else FALSE;
}
int  Vertex::operator!=(Vertex *v){

    double vx = v->Get_x();
    double vy = v->Get_y();
    double vz = v->Get_z();

    if( (x != vx) && (y != vy) && ( z != vz))return TRUE;
    else FALSE;
}

void Vertex::Print(){

	printf("Vertex[%d] = %f %f %f\n",vertex_id,x,y,z);
}




