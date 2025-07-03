import numpy as np
from PIL import Image
from utils import image_to_bits, bits_to_image

def get_range(d):
    ranges = [(0,7), (8,15), (16,31), (32,63), (64,127), (128,255)]
    for r in ranges:
        if r[0] <= d <= r[1]:
            return r
    return (0, 0)

def embed_image_in_image(cover_img: Image.Image, secret_img: Image.Image) -> Image.Image:
    cover_img = cover_img.convert('RGB')
    secret_bits = image_to_bits(secret_img) + '1111111111111110'

    r, g, b = cover_img.split()
    r, g, b = np.array(r).flatten(), np.array(g).flatten(), np.array(b).flatten()

    idx = 0
    channels = [r, g, b]
    for c in channels:
        for i in range(0, len(c)-1, 2):
            if idx >= len(secret_bits):
                break
            p1, p2 = c[i], c[i+1]
            d = abs(p2 - p1)
            r_min, r_max = get_range(d)
            n = int(np.floor(np.log2(r_max - r_min + 1)))
            if idx + n > len(secret_bits):
                break
            bits = secret_bits[idx:idx+n]
            dec = int(bits, 2)
            new_d = r_min + dec
            diff = new_d - d
            p2 = p2 + diff if p2 >= p1 else p2 - diff
            c[i+1] = np.clip(p2, 0, 255)
            idx += n

    h, w = cover_img.size
    r_img = Image.fromarray(r.reshape((w, h)).astype(np.uint8))
    g_img = Image.fromarray(g.reshape((w, h)).astype(np.uint8))
    b_img = Image.fromarray(b.reshape((w, h)).astype(np.uint8))
    return Image.merge('RGB', (r_img, g_img, b_img))

def extract_image_from_image(stego_img: Image.Image, secret_shape) -> Image.Image:
    stego_img = stego_img.convert('RGB')
    r, g, b = stego_img.split()
    r, g, b = np.array(r).flatten(), np.array(g).flatten(), np.array(b).flatten()

    channels = [r, g, b]
    secret_bits = ''
    for c in channels:
        for i in range(0, len(c)-1, 2):
            p1, p2 = c[i], c[i+1]
            d = abs(p2 - p1)
            r_min, r_max = get_range(d)
            n = int(np.floor(np.log2(r_max - r_min + 1)))
            m = d - r_min
            bits = format(m, f'0{n}b')
            secret_bits += bits
            if '1111111111111110' in secret_bits:
                break
        if '1111111111111110' in secret_bits:
            break
    secret_bits = secret_bits.split('1111111111111110')[0]
    return bits_to_image(secret_bits, secret_shape)

def embed_text_in_image(cover_img: Image.Image, secret_text: str) -> Image.Image:
    cover_img = cover_img.convert('RGB')
    secret_bits = ''.join(format(ord(c), '08b') for c in secret_text) + '1111111111111110'

    r, g, b = cover_img.split()
    r, g, b = np.array(r).flatten(), np.array(g).flatten(), np.array(b).flatten()

    idx = 0
    channels = [r, g, b]
    for c in channels:
        for i in range(0, len(c)-1, 2):
            if idx >= len(secret_bits):
                break
            p1, p2 = c[i], c[i+1]
            d = abs(p2 - p1)
            r_min, r_max = get_range(d)
            n = int(np.floor(np.log2(r_max - r_min + 1)))
            if idx + n > len(secret_bits):
                break
            bits = secret_bits[idx:idx+n]
            dec = int(bits, 2)
            new_d = r_min + dec
            diff = new_d - d
            p2 = p2 + diff if p2 >= p1 else p2 - diff
            c[i+1] = np.clip(p2, 0, 255)
            idx += n

    h, w = cover_img.size
    r_img = Image.fromarray(r.reshape((w, h)).astype(np.uint8))
    g_img = Image.fromarray(g.reshape((w, h)).astype(np.uint8))
    b_img = Image.fromarray(b.reshape((w, h)).astype(np.uint8))
    return Image.merge('RGB', (r_img, g_img, b_img))

def extract_text_from_image(stego_img: Image.Image) -> str:
    stego_img = stego_img.convert('RGB')
    r, g, b = stego_img.split()
    r, g, b = np.array(r).flatten(), np.array(g).flatten(), np.array(b).flatten()

    channels = [r, g, b]
    secret_bits = ''

    for c in channels:
        for i in range(0, len(c)-1, 2):
            p1, p2 = c[i], c[i+1]
            d = abs(p2 - p1)
            r_min, r_max = get_range(d)
            n = int(np.floor(np.log2(r_max - r_min + 1)))
            m = d - r_min
            bits = format(m, f'0{n}b')
            secret_bits += bits

            # Jika penanda akhir ditemukan, berhenti
            if '1111111111111110' in secret_bits:
                break
        if '1111111111111110' in secret_bits:
            break

    # Potong bit sampai sebelum EOF marker
    secret_bits = secret_bits.split('1111111111111110')[0]

    # Konversi ke teks hanya jika genap 8 bit
    text = ''
    for i in range(0, len(secret_bits), 8):
        byte = secret_bits[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))

    return text