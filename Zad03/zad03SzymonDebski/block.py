import math
from PIL import Image
import numpy as np
from matplotlib import image
from matplotlib import pyplot

CHANNELS = 3
BLK_OFFSET = 4
BLK_SIZE = (BLK_OFFSET ** 2) * CHANNELS

def generate_xor_key():
    max_dec_val = np.iinfo(np.uint8).max
    arr = np.random.randint(max_dec_val + 1, size=BLK_SIZE, dtype=np.uint8)
    arr = np.reshape(arr, (BLK_OFFSET, BLK_OFFSET, CHANNELS))
    return arr


def encrypt_image(flag, output_filename):
    img_name = 'plain.bmp'
    img = Image.open(img_name)
    img_arr = np.asarray(img)
    img_shape = img_arr.shape

    height, width, _ = img_shape
    h_steps = height // BLK_OFFSET
    w_steps = width // BLK_OFFSET
    key_arr = generate_xor_key()
    img_arr_xored = np.empty(img_shape, dtype=np.uint8)
    curr_h = 0
    curr_w = 0


    for ih in range(h_steps):
        for iw in range(w_steps):
            curr_h = ih * BLK_OFFSET
            curr_w = iw * BLK_OFFSET
            img_slice = img_arr[curr_h:curr_h + BLK_OFFSET, curr_w:curr_w + BLK_OFFSET, :]
            img_slice_xored = img_slice ^ key_arr
            if flag:
                key_arr = img_slice_xored
            img_arr_xored[curr_h:curr_h + BLK_OFFSET, curr_w:curr_w + BLK_OFFSET, :] = img_slice_xored

    processed_h = curr_h + BLK_OFFSET
    processed_w = curr_w + BLK_OFFSET
    if processed_h != height or processed_w != width:
        left_h = height - processed_h
        left_w = width - processed_w
        left_slice = key_arr[-left_h:, -left_w:, :]
        img_arr_xored[-left_h:, -left_w:, :] = left_slice

    new_img = Image.fromarray(img_arr_xored)

    new_img.save(output_filename)


encrypt_image(False, 'ecb_crypto.bmp')
encrypt_image(True, 'cbc_crypto.bmp')