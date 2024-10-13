from PIL import Image
from numpy import asarray
import numpy as np

import sys
import os


#  filters
filters = [[[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
            
           [[0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]],

           [[0, 0, 0],
            [1, 0, 1],
            [0, 0, 0]],

           [[1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]],
            
           [[1, 0, 1],
            [0, 0, 0],
            [1, 0, 1],],
           
           [[1, 0, 1],
            [0, 1, 0],
            [1, 0, 1],],
            
           [[1, 1, 0],
            [1, 0, 1],
            [0, 1, 1]],

           [[1, 0, 1],
            [1, 0, 1],
            [1, 0, 1]],


           [[1, 1, 1],
            [0, 1, 0],
            [1, 1, 1]],

           [[1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],],
           
           [[1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],],
]



# base var
help_msg = """Usage:
python dithering.py <input_image_path> <sub_pixel_size> [--invert] [--normalize]
                    [--exposure <exposure>] [--nb-colors <nb_colors>] [...]

Mandatory arguments:
  <input_image_path>: path to input image
  <sub_pixel_size>: integer greater than 2 representing the size of a patch of pixel to dither

Options:
  --invert: inverse the original image

  --normalize: normalize the input image (the brightest pixel will be white and the darkest black)
  --expossure <expossure>: float the sensitivity to brightness (between 0.1 and 10, default = 2)
  --nb-colors <nb_colors>: int greater than 1 and less than 256, the size of the colorspace before dithering (2 = black and whithe, 3 = black, gray, white etc...) (default = 3)
  --rgb-correction <float> <float> <float>: correction factor for RGB components 
  
  --colored: set the output as colored (default is black and white)

  
  
  -h, --help: display this message"""

  

inverse = False
normalize = False
colored = False

number_of_colors = 3
exposure = 2


r_c = 1
g_c = 1
b_c = 1



# parse arg
args = sys.argv[1:]

if '-h' in args or '--help' in args:
    print()
    print(help_msg)
    sys.exit(0)


if len(args) < 2:
    print("\n[!!] not enough arguments\n")
    print(help_msg)
    sys.exit(1)

input_image_path = args[0]

try: 
    compression_ratio = int(args[1])
    if compression_ratio <= 1:
        print("\n[!!] sub_pixel_size must be greater than 2\n")
        print(help_msg)
        sys.exit(1)

except:
    print("\n[!!] dot_size must be an integer\n")
    print(help_msg)
    sys.exit(1)


idx = 2

while idx < len(args):
    arg = args[idx]
    if '--invert' == arg:
        inverse = True

    elif '--normalize' == arg:
        normalize = True

    elif '--colored' == arg:
        colored = True

    elif '--exposure' == arg:
        try:
            exposure = float(args[idx+1])
            
            if exposure < 0.1 or exposure > 10:
                print("\n[!!] exposure must be between 0.1 and 10\n")
                print(help_msg)
                sys.exit(1)
            idx+=1

        except:
            print("\n[!!] exposure must be an float\n")
            print(help_msg)
            sys.exit(1)


    elif '--nb-colors' == arg:
        try:
            number_of_colors = int(args[idx+1])
            
            if number_of_colors < 2 or number_of_colors > 256:
                print("\n[!!] nb-colors must be between 2 and 255\n")
                print(help_msg)
                sys.exit(1)
            idx+=1

        except:
            print("\n[!!] nb-colors must be an int\n")
            print(help_msg)
            sys.exit(1)



    elif '--rgb-correction' == arg:
        try:
            r_c = float(args[idx+1])
            r_c = 1.25**r_c
            idx+=1

        except:
            print("\n[!!] color correction factor must be an float\n")
            print(help_msg)
            sys.exit(1)

        
        
        try:
            g_c = float(args[idx+1])
            g_c = 1.25**g_c
            idx+=1

        except:
            print("\n[!!] color correction factor must be an float\n")
            print(help_msg)
            sys.exit(1)


        try:
            b_c = float(args[idx+1])
            b_c = 1.25**b_c
            idx+=1

        except:
            print("\n[!!] color correction factor must be an float\n")
            print(help_msg)
            sys.exit(1)



    else:
        print(f"\n[!!] unknown argument: {arg}\n")
        print(help_msg)
        sys.exit(1)

    idx += 1 




def compress_img(image, ratio):

    out_shape = image.shape[0]//ratio , image.shape[1]//ratio, image.shape[2]
    out = np.zeros(out_shape)

    for i in range(out_shape[0]):
        for j in range(out_shape[1]):
            if ((j+1)*ratio < image.shape[1] and \
                (i+1)*ratio < image.shape[0]):

                out[i, j] = np.mean(image[i*ratio:(i+1)*ratio, j*ratio:(j+1)*ratio, :], axis=(0, 1))/255
            
            elif ((j+1)*ratio >= image.shape[1]):
                out[i, j] = out[i, j-1]

            elif ((i+1)*ratio >= image.shape[0]):
                out[i, j] = out[i-1, j]
            else:
                out[i, j] = out[i-1, j-1]
    return out


def to_greyscale(image):
    return np.dot(image[...,:3], [0.299, 0.587, 0.114])


def dither(image, ratio):
    out = np.zeros((image.shape[0]*ratio, image.shape[1]*ratio))

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            x = i*ratio
            y = j*ratio

            value = image[i, j]
            value = value**(1/exposure)

            if value < 0.001:
                value = 0


            for k in range(ratio):
                for l in range(ratio):

                        color_id = int(value*(number_of_colors-1))
                        max_color = (color_id+1) /(number_of_colors-1)
                        min_color = (color_id)   /(number_of_colors-1)

                        interval_value = (value-min_color)/(max_color-min_color)
                 
                        idx = interval_value*(len(filters)-1)
                        filter_ = filters[int(idx)]


                        u = int(k/(ratio)*3)
                        v = int(l/(ratio)*3)

                        out[x+k, y+l] =  255*filter_[u][v]     * max_color
                        out[x+k, y+l] += 255*(1-filter_[u][v]) * min_color

    return out



# load image
print("\n[loading image]...", end='', flush=True)
try:
    img = Image.open(input_image_path).convert('RGB')
except:
    print(f"\n[!!] cannot open the file `{input_image_path}`\n")
    print(help_msg)
    sys.exit(1)


shape = img.size
img_array = asarray(img)
print("\r[loading image]: OK")

print("[compressing image]...", end='', flush=True)
compressed_img = compress_img(img_array, compression_ratio)
if inverse:
    compressed_img = 1-compressed_img
if normalize:
    compressed_img -= compressed_img.min()
    compressed_img /=  compressed_img.max()

compressed_img[:, :, 0] = compressed_img[:, :, 0] ** (1 / r_c)
compressed_img[:, :, 1] = compressed_img[:, :, 1] ** (1 / g_c)
compressed_img[:, :, 2] = compressed_img[:, :, 2] ** (1 / b_c)

print("\r[compressing image]: OK")

if colored:
    
    print("[Dithering image]...", end='', flush=True)
    r = compressed_img[:, :, 0] 
    g = compressed_img[:, :, 1]
    b = compressed_img[:, :, 2]

    dr = dither(r, compression_ratio)
    dr = dr.reshape(dr.shape+(1,))
    dg = dither(g, compression_ratio).reshape(dr.shape)
    db = dither(b, compression_ratio).reshape(dr.shape)

    dither_img = np.concatenate([dr, dg, db], axis=-1)
    

    print("\r[Dithering image]: OK")
    
    
    # save image
    print(f"\r[Saving new image]: ...", end='', flush=True)
    img = Image.fromarray(dither_img.astype('uint8'))
    
    # remove ext
    splited =  input_image_path.split('.')
    input_image_path = '.'.join(splited[:-1])
    
    # gen name
    out_path = input_image_path+'_dithered.png'
    i = 1
    while os.path.isfile(out_path):
        out_path = input_image_path+f"_dithered_{i}.png"
        i += 1
    
    img.save(out_path, 'png')
    print(f"\r[Saving new image: ({out_path}) ]: OK")


else:
    print("[Image to grey scale]...", end='', flush=True)
    grey_img = to_greyscale(compressed_img)
    print("\r[Image to grey scale]: OK")

    print("[Dithering image]...", end='', flush=True)
    dither_img = dither(grey_img, compression_ratio) 
    print("\r[Dithering image]: OK")


    # save image
    print(f"\r[Saving new image]: ...", end='', flush=True)
    img = Image.fromarray(dither_img.astype('uint8'))

    # remove ext
    splited =  input_image_path.split('.')
    input_image_path = '.'.join(splited[:-1])

    # gen name
    out_path = input_image_path+'_dithered.png'
    i = 1
    while os.path.isfile(out_path):
        out_path = input_image_path+f"_dithered_{i}.png"
        i += 1

    img.save(out_path, 'png')
    print(f"\r[Saving new image: ({out_path}) ]: OK")