from keras.preprocessing.image import load_img,img_to_array
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg')

img_path = "output/L_Midcurve.png"
img = load_img(img_path, color_mode='rgba', target_size=(100, 100))
print(type(img)) # <class 'PIL.Image.Image'>
img = img.rotate(45)
x = img_to_array(img)
print(type(x)) # <class 'numpy.ndarray'>
print(x.shape) # (100, 100, 4)
x = x[:,:,3]
print(x) 
x = np.where(x>128, 0, 1)
print(x) 

plt.imshow(x) # x/255.
plt.show()

# img = img.convert('1')
# x = img_to_array(img)
# print(type(x)) # <class 'numpy.ndarray'>
# print(x.shape) # (100, 100, 1)
# plt.imshow(x/255.) # doesnt work either
# plt.show() # TypeError: Invalid dimensions for image data

# 
# # import numpy as np
# # img = np.random.rand(224,224,3)
# # plt.imshow(img)
# # plt.show()
# 

# # load and display an image with Matplotlib
# from PIL import Image
#  
# def black_and_white(input_image_path,output_image_path):
#     color_image = Image.open(input_image_path)
#     bw = color_image.convert('1')
#     bw.save(output_image_path)
#  
# if __name__ == '__main__':  
#     black_and_white('output/L_Profile.png',
#         'output/L_bw_Profile.png')