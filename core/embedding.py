import numpy as np
from core.lsb_core import bits_per_pixel

def get_pixel_order(total_pixels, mode, seed=None):
    indices = np.arange(total_pixels, dtype=np.int64)
    if mode == 'random':
        if seed is None:
            raise ValueError("random mode butuh seed")
        seed_int = int(hash(seed)) % (2**63)
        rng = np.random.default_rng(seed=seed_int)
        rng.shuffle(indices)
    return indices


def _flat_to_coords(flat_idx, pixels_per_frame, width):
    frame_idx = flat_idx // pixels_per_frame
    remainder = flat_idx % pixels_per_frame
    y = remainder // width
    x = remainder % width
    return int(frame_idx), int(y), int(x)


def embed(frames, bits, scheme, mode, seed=None):
    result = [f.copy() for f in frames]
    h, w = frames[0].shape[:2]
    pixels_per_frame = h * w
    total_pixels = pixels_per_frame * len(frames)
    positions = get_pixel_order(total_pixels, mode, seed)
    r_bits, g_bits, b_bits = _scheme_bits(scheme)
    bit_idx = 0
    total_bits = len(bits)
    for flat_idx in positions:
        if bit_idx >= total_bits:
            break
        f_idx, y, x = _flat_to_coords(flat_idx, pixels_per_frame, w)
        frame = result[f_idx]
        b = int(frame[y, x, 0])
        g = int(frame[y, x, 1])
        r = int(frame[y, x, 2])
        for i in range(r_bits):
            if bit_idx >= total_bits:
                break
            r = (r & (0xFF ^ (1 << i))) | (bits[bit_idx] << i)
            bit_idx += 1
        for i in range(g_bits):
            if bit_idx >= total_bits:
                break
            g = (g & (0xFF ^ (1 << i))) | (bits[bit_idx] << i)
            bit_idx += 1
        for i in range(b_bits):
            if bit_idx >= total_bits:
                break
            b = (b & (0xFF ^ (1 << i))) | (bits[bit_idx] << i)
            bit_idx += 1
        result[f_idx][y, x] = [b, g, r]
    return result, bit_idx


def extract(frames, num_bits, scheme, mode, seed=None):
    h, w = frames[0].shape[:2]
    pixels_per_frame = h * w
    total_pixels = pixels_per_frame * len(frames)
    positions = get_pixel_order(total_pixels, mode, seed)
    r_bits, g_bits, b_bits = _scheme_bits(scheme)
    bits = []
    for flat_idx in positions:
        if len(bits) >= num_bits:
            break
        f_idx, y, x = _flat_to_coords(flat_idx, pixels_per_frame, w)
        frame = frames[f_idx]
        b = int(frame[y, x, 0])
        g = int(frame[y, x, 1])
        r = int(frame[y, x, 2])
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
    return bits

def _scheme_bits(scheme):
    from core.video_io import LSB_SCHEMES
    return LSB_SCHEMES[scheme]
