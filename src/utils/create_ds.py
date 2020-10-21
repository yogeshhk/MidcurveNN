# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 12:36:52 2019

@author: prnvb
"""

import cv2
import numpy as np
import imutils

IMAGE_SHAPE = (256, 256)
BG_COLOR = (255, 255, 255)  # (0,0,0)
FG_COLOR = (0, 0, 0)  # (255,255,255)
dtype = 'uint8'
BASE_DIR = 'D:/dev/midcurve/MidcurveNN/reorg/'


def draw_polygon(image, points, color, thickness):
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        image = cv2.line(image, p1, p2, color, thickness, cv2.LINE_AA)
    return image


def fill_rectangle(image, x1, y1, x2, y2, color):
    # x1,y1 -> top left corner
    # x2,y2 -> bottom right corner
    for y in range(y1, y2 + 1):
        image = cv2.line(image, (x1, y), (x2, y), color, 1, cv2.LINE_AA)
    return image


def rotate(image, midcurve, roi, rotation):
    if rotation > 0:
        '''
        image = imutils.rotate_bound(image,rotation)
        midcurve = imutils.rotate_bound(midcurve,rotation)
        roi = imutils.rotate_bound(roi,rotation)
        '''
        M = cv2.getRotationMatrix2D((IMAGE_SHAPE[0] / 2, IMAGE_SHAPE[1] / 2),
                                    rotation, 1.0)
        image = cv2.warpAffine(image, M, (IMAGE_SHAPE[0], IMAGE_SHAPE[1]),
                               borderMode=cv2.BORDER_CONSTANT,
                               borderValue=BG_COLOR)

        midcurve = cv2.warpAffine(midcurve, M, (IMAGE_SHAPE[0], IMAGE_SHAPE[1]),
                                  borderMode=cv2.BORDER_CONSTANT,
                                  borderValue=BG_COLOR)

        roi = cv2.warpAffine(roi, M, (IMAGE_SHAPE[0], IMAGE_SHAPE[1]),
                             borderMode=cv2.BORDER_CONSTANT,
                             borderValue=BG_COLOR)
    return image, midcurve, roi


def draw_T(image, midcurve, roi, x, y, width, height, length,
           color=(0, 0, 0), thickness=1):
    points = []
    points.append((x, y))  # a
    points.append((x, y + width))  # b
    points.append((x + int((length - width) / 2), y + width))  # c
    points.append((x + int((length - width) / 2), y + height))  # d
    points.append((x + int((length - width) / 2) + width, y + height))  # e
    points.append((x + int((length - width) / 2) + width, y + width))  # f
    points.append((x + length, y + width))  # g
    points.append((x + length, y))  # h
    points.append((x, y))  # a

    image = draw_polygon(image, points, color, thickness)

    points = []
    points.append((x, y + int(width / 2)))
    points.append((x + length, y + int(width / 2)))
    points.append((x + int(length / 2), y + int(width / 2)))
    points.append((x + int(length / 2), y + height))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    # ROI:
    roi = fill_rectangle(roi, x, y, x + length, y + width, color)
    roi = fill_rectangle(roi, x + int((length - width) / 2), y + width,
                         x + int((length - width) / 2) + width, y + height, color)

    return image, midcurve, roi


def draw_I(image, midcurve, roi, x, y, width, height, length,
           color=(0, 0, 0), thickness=1):
    points = []
    points.append((x, y))  # a
    points.append((x, y + width))  # b
    points.append((x + int((length - width) / 2), y + width))  # c
    points.append((x + int((length - width) / 2), y + height - width))  # d
    points.append((x, y + height - width))  # e
    points.append((x, y + height))  # f
    points.append((x + length, y + height))  # g
    points.append((x + length, y + height - width))  # h
    points.append((x + length - int((length - width) / 2), y + height - width))  # i
    points.append((x + length - int((length - width) / 2), y + width))  # j
    points.append((x + length, y + width))  # k
    points.append((x + length, y))  # l
    points.append((x, y))  # a

    image = draw_polygon(image, points, color, thickness)

    points = []
    points.append((x, y + int(width / 2)))
    points.append((x + length, y + int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    points = []
    points.append((x + int(length / 2), y + int(width / 2)))
    points.append((x + int(length / 2), y + height - int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    points = []
    points.append((x, y + height - int(width / 2)))
    points.append((x + length, y + height - int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    roi = fill_rectangle(roi, x, y, x + length, y + width, color)
    roi = fill_rectangle(roi, x + int((length - width) / 2), y + width,
                         x + length - int((length - width) / 2), y + height - width,
                         color)
    roi = fill_rectangle(roi, x, y + height - width, x + length, y + height, color)

    return image, midcurve, roi


def draw_C(image, midcurve, roi, x, y, width, height, length,
           color=(0, 0, 0), thickness=1):
    points = []
    points.append((x, y))  # a
    points.append((x, y + height))  # b
    points.append((x + length, y + height))  # c
    points.append((x + length, y + height - width))  # d
    points.append((x + width, y + height - width))  # e
    points.append((x + width, y + width))  # f
    points.append((x + length, y + width))  # g
    points.append((x + length, y))  # h
    points.append((x, y))  # a

    image = draw_polygon(image, points, color, thickness)

    points = []
    points.append((x + length, y + int(width / 2)))
    points.append((x + int(width / 2), y + int(width / 2)))
    points.append((x + int(width / 2), y + height - int(width / 2)))
    points.append((x + length, y + height - int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    roi = fill_rectangle(roi, x, y, x + length, y + width, color)
    roi = fill_rectangle(roi, x, y + width, x + width, y + height - width, color)
    roi = fill_rectangle(roi, x, y + height - width, x + length, y + height, color)

    return image, midcurve, roi


def draw_E(image, midcurve, roi, x, y, width, height, length,
           color=(0, 0, 0), thickness=1):
    height_2 = int((height - 3 * width) / 2)

    points = []
    points.append((x, y))  # a
    points.append((x, y + height))  # b
    points.append((x + length, y + height))  # c
    points.append((x + length, y + height - width))  # d
    points.append((x + width, y + height - width))  # e
    points.append((x + width, y + height - width - height_2))  # f
    points.append((x + length, y + height - width - height_2))  # g
    points.append((x + length, y + height - 2 * width - height_2))  # h
    points.append((x + width, y + height - 2 * width - height_2))  # i
    points.append((x + width, y + width))  # j
    points.append((x + length, y + width))  # k
    points.append((x + length, y))  # l
    points.append((x, y))  # a

    image = draw_polygon(image, points, color, thickness)

    points = []
    points.append((x + length, y + int(width / 2)))
    points.append((x + int(width / 2), y + int(width / 2)))
    points.append((x + int(width / 2), y + int(3 * width / 2) + height_2))
    points.append((x + length, y + int(3 * width / 2) + height_2))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    points = []
    points.append((x + int(width / 2), y + int(3 * width / 2) + height_2))
    points.append((x + int(width / 2), y + height - int(width / 2)))
    points.append((x + length, y + height - int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    roi = fill_rectangle(roi, x, y, x + length, y + width, color)
    roi = fill_rectangle(roi, x, y + width, x + width, y + height - 2 * width - height_2, color)
    roi = fill_rectangle(roi, x, y + height - 2 * width - height_2,
                         x + length, y + height - width - height_2, color)
    roi = fill_rectangle(roi, x, y + height - width - height_2,
                         x + width, y + height - width, color)
    roi = fill_rectangle(roi, x, y + height - width,
                         x + length, y + height, color)

    return image, midcurve, roi


def draw_L(image, midcurve, roi, x, y, width, height, length,
           color=(0, 0, 0), thickness=1):
    points = []
    points.append((x, y))  # a
    points.append((x, y + height))  # b
    points.append((x + length, y + height))  # c
    points.append((x + length, y + height - width))  # d
    points.append((x + width, y + height - width))  # e
    points.append((x + width, y))  # f
    points.append((x, y))  # a

    image = draw_polygon(image, points, color, thickness)

    points = []
    points.append((x + int(width / 2), y))
    points.append((x + int(width / 2), y + height - int(width / 2)))
    points.append((x + length, y + height - int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    roi = fill_rectangle(roi, x, y, x + width, y + height - width, color)
    roi = fill_rectangle(roi, x, y + height - width, x + length, y + height, color)

    return image, midcurve, roi


def draw_F(image, midcurve, roi, x, y, width, height, length,
           color=(0, 0, 0), thickness=1):
    height_2 = int((height - 3 * width) / 2)

    points = []
    points.append((x, y))  # a
    points.append((x, y + height))  # b
    points.append((x + width, y + height))  # c
    points.append((x + width, y + height - width - height_2))  # d
    points.append((x + length, y + height - width - height_2))  # e
    points.append((x + length, y + height - 2 * width - height_2))  # f
    points.append((x + width, y + height - 2 * width - height_2))  # g
    points.append((x + width, y + width))  # h
    points.append((x + length, y + width))  # i
    points.append((x + length, y))  # j
    points.append((x, y))  # k

    image = draw_polygon(image, points, color, thickness)

    points = []
    points.append((x + length, y + int(width / 2)))
    points.append((x + int(width / 2), y + int(width / 2)))
    points.append((x + int(width / 2), y + int(3 * width / 2) + height_2))
    points.append((x + length, y + int(3 * width / 2) + height_2))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    points = []
    points.append((x + int(width / 2), y + int(3 * width / 2) + height_2))
    points.append((x + int(width / 2), y + height - int(width / 2)))

    midcurve = draw_polygon(midcurve, points, color, thickness)

    roi = fill_rectangle(roi, x, y, x + length, y + width, color)
    roi = fill_rectangle(roi, x, y + width, x + width, y + height - 2 * width - height_2, color)
    roi = fill_rectangle(roi, x, y + height - 2 * width - height_2,
                         x + length, y + height - width - height_2, color)
    roi = fill_rectangle(roi, x, y + height - width - height_2,
                         x + width, y + height, color)

    return image, midcurve, roi


def draw_D_curved(image, midcurve, roi, x, y, radius, width,
                  color=(0, 0, 0), thickness=1):
    new_rad = radius + width
    new_width = width * 2

    image = cv2.ellipse(image, center=(x, y), axes=(radius, radius), angle=0,
                        startAngle=0, endAngle=180, color=color, thickness=thickness)
    image = cv2.ellipse(image, center=(x, y), axes=(radius + new_width, radius + new_width),
                        angle=0, startAngle=0, endAngle=180, color=color,
                        thickness=thickness)

    image = cv2.line(image, (x - radius, y), (x + radius, y), color, thickness, cv2.LINE_AA)
    image = cv2.line(image, (x - radius - new_width, y), (x - radius - new_width, y - new_width),
                     color, thickness, cv2.LINE_AA)
    image = cv2.line(image, (x + radius + new_width, y), (x + radius + new_width, y - new_width),
                     color, thickness, cv2.LINE_AA)
    image = cv2.line(image, (x - radius - new_width, y - new_width),
                     (x + radius + new_width, y - new_width),
                     color, thickness, cv2.LINE_AA)

    mid_rad = radius + int(new_width / 2)
    midcurve = cv2.ellipse(midcurve, center=(x, y), axes=(mid_rad, mid_rad), angle=0,
                           startAngle=0, endAngle=180, color=color, thickness=thickness)

    midcurve = cv2.line(midcurve, (x - radius - width, y), (x - radius - width, y - width),
                        color, thickness, cv2.LINE_AA)
    midcurve = cv2.line(midcurve, (x + radius + width, y), (x + radius + width, y - width),
                        color, thickness, cv2.LINE_AA)
    midcurve = cv2.line(midcurve, (x - radius - width, y - width), (x + radius + width, y - width),
                        color, thickness, cv2.LINE_AA)

    roi = cv2.ellipse(roi, center=(x, y), axes=(new_rad, new_rad), angle=0,
                      startAngle=0, endAngle=180, color=color, thickness=new_width)
    roi = cv2.line(roi, (x - radius, y), (x + radius, y), color, thickness, cv2.LINE_AA)
    roi = cv2.line(roi, (x - radius - new_width, y), (x - radius - new_width, y - new_width),
                   color, thickness, cv2.LINE_AA)
    roi = cv2.line(roi, (x + radius + new_width, y), (x + radius + new_width, y - new_width),
                   color, thickness, cv2.LINE_AA)
    roi = cv2.line(roi, (x - radius - new_width, y - new_width),
                   (x + radius + new_width, y - new_width),
                   color, thickness, cv2.LINE_AA)
    roi = fill_rectangle(roi, x - radius - new_width, y - new_width, x + radius + new_width, y, color)

    return image, midcurve, roi


def generate_random(count):
    lh_min = 80
    lh_max = 150

    for shape in shapes.keys():
        draw = shapes[shape]
        for i in range(count):
            if BG_COLOR[0]:
                image = np.ones(IMAGE_SHAPE, dtype=dtype) * 255
                midcurve = np.ones(IMAGE_SHAPE, dtype=dtype) * 255
                roi = np.ones(IMAGE_SHAPE, dtype=dtype) * 255
            else:
                image = np.zeros(IMAGE_SHAPE, dtype=dtype)
                midcurve = np.zeros(IMAGE_SHAPE, dtype=dtype)
                roi = np.zeros(IMAGE_SHAPE, dtype=dtype)

            length = np.random.randint(lh_min, lh_max)
            height = np.random.randint(lh_min, lh_max)
            width_min = 5
            width_max = int(min(length, height) / 3) - 10
            width = np.random.randint(width_min, width_max)
            rotation = np.random.randint(0, 360)
            x = 128 - int(length / 2)
            y = 128 - int(height / 2)
            # x = np.random.randint(20,256-length-10)
            # y = np.random.randint(20,256-height-10)

            image, midcurve, roi = draw(image, midcurve, roi, x, y,
                                        width, length, height,
                                        color=FG_COLOR, thickness=1)

            image, midcurve, roi = rotate(image, midcurve, roi, rotation)

            clubbed_image = np.append(image, midcurve, axis=1)
            clubbed_image = np.append(clubbed_image, roi, axis=1)

            cv2.imwrite(BASE_DIR + 'data/new/v2/' + shape + str(i) + '.png', clubbed_image)
            print(shape + str(i))


shapes = {}
shapes['T'] = draw_T
shapes['I'] = draw_I
shapes['L'] = draw_L
shapes['E'] = draw_E
shapes['C'] = draw_C
shapes['F'] = draw_F

if __name__ == "__main__":
    generate_random(1000)

    '''
    x=128
    y=128
    rad = 50
    width=10

    #im = np.ones(IMAGE_SHAPE,dtype=float)
    #im = cv2.addWeighted(midcurve, 0.5, image, 0.5, 0, im)

    cv2.imwrite('new_data/test.png', clubbed_image)

    im = cv2.imread('new_data/test.png', cv2.IMREAD_UNCHANGED)
    cv2.imshow('a',im)


    
    def draw_rect(image, midcurve, roi, x, y, width, height, length, rotation=0, 
    		   color=(0,0,0), thickness=1, scale=False):
        
        points = []
        points.append( (x,y) )
        points.append( (x+length,y) )
        points.append( (x+length,y+height) )
        points.append( (x+length,y) )
        points.append( (x,y) )
        
        image = draw_polygon(image,points,color,thickness)
        
        points = []
        points.append( (x,y) )
        points.append( (x+length,y) )
        points.append( (x+length,y+height) )
        points.append( (x+length,y) )
        points.append( (x,y) )
    '''
