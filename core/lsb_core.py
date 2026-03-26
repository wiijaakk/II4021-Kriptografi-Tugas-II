import numpy as np
from video_io import LSB_SCHEMES

# fungsi untuk embed bits ke fram video, return frame yang sudah dimodif + jumlah bit yang berhasil diembed
def embed_bits_to_frame(frame, bits, scheme, start_idx=0): 
    r_bits, g_bits, b_bits = LSB_SCHEMES[scheme]
    result = frame.copy()
    height, width = frame.shape[:2]
    
    bit_idx = 0
    total_bits = len(bits)
    pixel_idx = 0

    for y in range(height):
        for x in range(width):
            if pixel_idx < start_idx:
                pixel_idx += 1
                continue
            if bit_idx >= total_bits:
                return result, bit_idx

            b, g, r = int(result[y, x, 0]), int(result[y, x, 1]), int(result[y, x, 2])

            # embed ke R
            for i in range(r_bits):
                if bit_idx >= total_bits:
                    break
                r = (r & (0xFF ^ (1 << i))) | (bits[bit_idx] << i)
                bit_idx += 1

            # embed ke G
            for i in range(g_bits):
                if bit_idx >= total_bits:
                    break
                g = (g & (0xFF ^ (1 << i))) | (bits[bit_idx] << i)
                bit_idx += 1

            # embed ke B
            for i in range(b_bits):
                if bit_idx >= total_bits:
                    break
                b = (b & (0xFF ^ (1 << i))) | (bits[bit_idx] << i)
                bit_idx += 1

            result[y, x] = [b, g, r]
            pixel_idx += 1

    return result, bit_idx


# fungsi untuk ekstrak bits dari frame video, return list of bits yang berhasil diekstrak
def extract_bits_from_frame(frame, num_bits, scheme, start_idx=0):
    r_bits, g_bits, b_bits = LSB_SCHEMES[scheme]
    height, width = frame.shape[:2]

    bits = []
    pixel_idx = 0

    for y in range(height):
        for x in range(width):
            if pixel_idx < start_idx:
                pixel_idx += 1
                continue
            if len(bits) >= num_bits:
                return bits

            b, g, r = frame[y, x]

            for i in range(r_bits):
                if len(bits) >= num_bits:
                    break
                bits.append((r >> i) & 1)

            for i in range(g_bits):
                if len(bits) >= num_bits:
                    break
                bits.append((g >> i) & 1)

            for i in range(b_bits):
                if len(bits) >= num_bits:
                    break
                bits.append((b >> i) & 1)

            pixel_idx += 1

    return bits


def bytes_to_bits(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_bytes(bits):
    result = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8:
            break
        byte = 0
        for j, bit in enumerate(chunk):
            byte |= (bit << j)
        result.append(byte)
    return bytes(result)


def bits_per_pixel(scheme):
    r, g, b = LSB_SCHEMES[scheme]
    return r + g + b


def pixels_needed(num_bits, scheme):
    bpp = bits_per_pixel(scheme)
    return (num_bits + bpp - 1) // bpp
