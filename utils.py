from PIL import Image
import numpy as np

def image_to_bits(img: Image.Image) -> str:
    img = img.convert('RGB')
    byte_arr = np.array(img).flatten()
    return ''.join(format(b, '08b') for b in byte_arr)

def bits_to_image(bits: str, shape) -> Image.Image:
    byte_list = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
    arr = np.array(byte_list, dtype=np.uint8).reshape(shape)
    return Image.fromarray(arr)
