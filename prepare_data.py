"""
    Prepare Data: populating input images from raw profile data
    Takes raw data from "data/raw/*" files for both, profile shape (shape.dat) as well as midcurve shape (shape.mid)
    Generates raster image files from svg (simple vector graphics)
    Multiple variations are populated using image transformations.
    These images become input for further modeling (stored in "data/input/*")
"""
from keras.preprocessing.image import img_to_array, load_img, array_to_img
from random import shuffle
import PIL
import PIL.ImageOps
import json
import numpy as np
import os
import shutil
import sys
np.set_printoptions(threshold=sys.maxsize)


raw_data_folder = "data/raw"
input_data_folder = "data/input"
pix2pix_data_folder = "data/pix2pix/datasets/pix2pix"

def combine_images(imga, imgb):
    """
    Combines two color image ndarrays side-by-side.
    Ref: https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
    """
    ha,wa = imga.shape[:2]
    hb,wb = imgb.shape[:2]
    max_height = np.max([ha, hb])
    total_width = wa+wb
    new_img = np.zeros(shape=(max_height, total_width))
    new_img[:ha,:wa]=imga
    new_img[:hb,wa:wa+wb]=imgb
    return new_img    
#     images = map(Image.open, [imga,imgb])
#     widths, heights = zip(*(i.size for i in images))
#     total_width = sum(widths)
#     max_height = max(heights)
# 
#     new_im = Image.new('RGB', (total_width, max_height))
# 
#     x_offset = 0
#     for im in images:
#         new_im.paste(im, (x_offset,0))
#         x_offset += im.size[0]    
#     return new_im
    
def generate_pix2pix_dataset(inputdatafolder = input_data_folder, pix2pixdatafolder=pix2pix_data_folder):

    profile_pngs,midcurve_pngs = read_input_image_pairs(inputdatafolder)

    profile_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=(256, 256))) for f in profile_pngs ]
    midcurve_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=(256, 256))) for f in midcurve_pngs ]
    
#     combo_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in combo_pngs_objs])
    profile_pngs_gray_objs = [x[:,:,3] for x in profile_pngs_objs]
    midcurve_pngs_gray_objs = [x[:,:,3] for x in midcurve_pngs_objs]
    
#     combo_pngs_gray_objs = [np.where(x>128, 0, 1) for x in combo_pngs_gray_objs]
        
    combo_pngs = [combine_images(p,m) for p,m in zip(profile_pngs_gray_objs,midcurve_pngs_gray_objs)]

    # shufle them
    shuffle(combo_pngs)
    train_size = int(len(combo_pngs)*0.6)
    val_size = int(len(combo_pngs)*0.2)
    
    train_combo_files = combo_pngs[:train_size]
    val_combo_files = combo_pngs[train_size:train_size+val_size]
    test_combo_files = combo_pngs[train_size+val_size:]

    if os.path.exists(pix2pixdatafolder):
        shutil.rmtree(pix2pixdatafolder,ignore_errors=True)
        
    os.makedirs(pix2pixdatafolder)
    os.makedirs(pix2pixdatafolder+"/train")
    os.makedirs(pix2pixdatafolder+"/val")
    os.makedirs(pix2pixdatafolder+"/test")

    # SAVE into 3 dirs
    for i, arr in enumerate(train_combo_files):
        img = PIL.Image.fromarray(arr.astype('uint8'))
        img = PIL.ImageOps.invert(img)
        filename = pix2pixdatafolder+"/train/" + str(i) + ".jpg"
        img.save(filename)
        
    for i, arr in enumerate(val_combo_files):
        img = PIL.Image.fromarray(arr.astype('uint8'))
        img = PIL.ImageOps.invert(img)
        filename = pix2pixdatafolder+"/val/" + str(i) + ".jpg"
        img.save(filename)

    for i, arr in enumerate(test_combo_files):
        img = PIL.Image.fromarray(arr.astype('uint8'))
        img = PIL.ImageOps.invert(img)
        filename = pix2pixdatafolder+"/test/" + str(i) + ".jpg"
        img.save(filename)
            
    return train_combo_files, val_combo_files,test_combo_files 
    
def get_training_data(datafolder = input_data_folder, size=(100, 100)):
    profile_pngs,midcurve_pngs = read_input_image_pairs(datafolder)
    
    profile_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size)) for f in profile_pngs ]
    midcurve_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size)) for f in midcurve_pngs]

#     profile_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in profile_pngs_objs])
#     midcurve_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in midcurve_pngs_objs])

    profile_pngs_gray_objs = [x[:,:,3] for x in profile_pngs_objs]
    midcurve_pngs_gray_objs =[x[:,:,3] for x in midcurve_pngs_objs]
    
#     profile_pngs_gray_objs = [np.where(x>128, 0, 1) for x in profile_pngs_gray_objs]
#     midcurve_pngs_gray_objs =[np.where(x>128, 0, 1) for x in midcurve_pngs_gray_objs]
        
    # shufle them
    zipped_profiles_midcurves = [(p,m) for p,m in zip(profile_pngs_gray_objs,midcurve_pngs_gray_objs)]
    shuffle(zipped_profiles_midcurves)
    profile_pngs_gray_objs, midcurve_pngs_gray_objs = zip(*zipped_profiles_midcurves)
    
    return profile_pngs_gray_objs, midcurve_pngs_gray_objs

def get_profile_dict(shapename,profiles_dict_list):
    for i in profiles_dict_list:
        if i['ShapeName'] == shapename:
            return i
    profile_dict = {}
    profile_dict['ShapeName'] = shapename
    return profile_dict

def read_dat_files(datafolder=raw_data_folder):
    profiles_dict_list = []
    for file in os.listdir(datafolder):
        if os.path.isdir(os.path.join(datafolder, file)):
            continue
        filename = file.split(".")[0]
        profile_dict = get_profile_dict(filename,profiles_dict_list)        
        if file.endswith(".dat"):
            with open(os.path.join(datafolder, file)) as f:
                profile_dict['Profile'] = [tuple(map(float, i.split('\t'))) for i in f]  
        if file.endswith(".mid"):
            with open(os.path.join(datafolder, file)) as f:
                profile_dict['Midcurve'] = [tuple(map(float, i.split('\t'))) for i in f]
                                
        profiles_dict_list.append(profile_dict)
    return profiles_dict_list

import drawSvg as draw
def create_image_file(fieldname,profile_dict,datafolder=input_data_folder,imgsize=100, isOpenClose=True):
    d = draw.Drawing(imgsize, imgsize, origin='center')
    profilepoints = []
    for tpl in profile_dict[fieldname]:
        profilepoints.append(tpl[0])
        profilepoints.append(tpl[1])
    d.append(draw.Lines(profilepoints[0],profilepoints[1],*profilepoints,close=isOpenClose,fill='none',stroke='black'))
    
    shape = profile_dict['ShapeName']
#     d.saveSvg(datafolder+"/"+shape+'.svg')
    d.savePng(datafolder+"/"+shape+'_'+fieldname+'.png')

def get_original_png_files(datafolder=input_data_folder):
    pngfilenames = []
    for file in os.listdir(datafolder):
        fullpath = os.path.join(datafolder, file)
        if os.path.isdir(fullpath):
            continue
        if file.endswith(".png") and file.find("_rotated_") == -1 and file.find("_translated_")==-1 and file.find("_mirrored_")==-1:
            pngfilenames.append(fullpath)
    return pngfilenames

from PIL import Image
def rotate_images(pngfilenames, angle=90):
    for fullpath in pngfilenames:
        picture= Image.open(fullpath)
        newfilename = fullpath.replace(".png", "_rotated_"+str(angle)+".png")
        picture.rotate(angle).save(newfilename)

def mirror_images(pngfilenames, mode=PIL.Image.TRANSPOSE):
    mirrored_filenames = []
    for fullpath in pngfilenames:
        picture= Image.open(fullpath)
        newfilename = fullpath.replace(".png", "_mirrored_"+str(mode)+".png")
        picture.transpose(mode).save(newfilename)
        mirrored_filenames.append(newfilename)
    return mirrored_filenames
        
def translate_images(pngfilenames, dx=1,dy=1):
    for fullpath in pngfilenames:
        picture= Image.open(fullpath)
        x_shift = dx
        y_shift = dy
        a = 1
        b = 0
        c = x_shift #left/right (i.e. 5/-5)
        d = 0
        e = 1
        f = y_shift #up/down (i.e. 5/-5)
        translate = picture.transform(picture.size, Image.AFFINE, (a, b, c, d, e, f))
#         # Calculate the size after cropping
#         size = (translate.size[0] - x_shift, translate.size[1] - y_shift)
#         # Crop to the desired size
#         translate = translate.transform(size, Image.EXTENT, (0, 0, size[0], size[1]))
        newfilename = fullpath.replace(".png", "_translated_"+str(dx)+"_"+str(dy)+".png")
        translate.save(newfilename)
        
def read_input_image_pairs(datafolder=input_data_folder):
    profile_pngs = []
    midcurve_pngs = []
    for file in os.listdir(datafolder):
        fullpath = os.path.join(datafolder, file)
        if os.path.isdir(fullpath):
            continue
        if file.endswith(".png"):
            if file.find("Profile") != -1:
                profile_pngs.append(fullpath)
            if file.find("Midcurve") != -1:
                midcurve_pngs.append(fullpath)
    profile_pngs = sorted(profile_pngs)
    midcurve_pngs = sorted(midcurve_pngs)
    return profile_pngs,midcurve_pngs
    
def generate_images(datafolder = input_data_folder):
    
    if not os.path.exists(datafolder):
        os.makedirs(datafolder)    
    else:    
        for file in os.listdir(datafolder):
            if file.endswith(".png") and (file.find("_rotated_") != -1 or file.find("_translated_") !=-1):
                print("files already present, not generating...")
                return
                
    print("transformed files not present, generating...")
    profiles_dict_list = read_dat_files()
        
    for profile_dict in profiles_dict_list:
        create_image_file('Profile',profile_dict,datafolder,100,True)
        create_image_file('Midcurve',profile_dict,datafolder,100,False)
        
    pngfilenames = get_original_png_files(datafolder)
    mirrored_filenames_left_right = mirror_images(pngfilenames, PIL.Image.FLIP_LEFT_RIGHT)
    mirrored_filenames_top_bottom = mirror_images(pngfilenames, PIL.Image.FLIP_TOP_BOTTOM)
    mirrored_filenames_transpose = mirror_images(pngfilenames, PIL.Image.TRANSPOSE)
    
    files_list_list = [pngfilenames,mirrored_filenames_left_right,mirrored_filenames_top_bottom,mirrored_filenames_transpose]
    for filelist in files_list_list:
        for angle in range(30,360,30):
            rotate_images(filelist,angle)
            
        for dx in range(5,21,5):
            for dy in range(5,21,5):
                translate_images(filelist,dx,-dy)
            
        
if __name__ == "__main__":
    # generate_images()
    # profile_pngs,midcurve_pngs = read_input_image_pairs()
    generate_pix2pix_dataset()

    
