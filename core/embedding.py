import random
from core.lsb_core import bits_per_pixel


def get_pixel_order(frames, scheme, mode, seed=None):
    # bikin list semua posisi piksel (frame_idx, y, x)
    positions = []
    for f_idx, frame in enumerate(frames):
        h, w = frame.shape[:2]
        for y in range(h):
            for x in range(w):
                positions.append((f_idx, y, x))

    if mode == 'random':
        if seed is None:
            raise ValueError("random mode butuh seed")
        rng = random.Random(seed)
        rng.shuffle(positions)

    return positions


def embed(frames, bits, scheme, mode, seed=None):
    result = [f.copy() for f in frames]
    positions = get_pixel_order(frames, scheme, mode, seed)

    bpp = bits_per_pixel(scheme)
    bit_idx = 0
    total_bits = len(bits)

    for (f_idx, y, x) in positions:
        if bit_idx >= total_bits:
            break

        frame = result[f_idx]
        b = int(frame[y, x, 0])
        g = int(frame[y, x, 1])
        r = int(frame[y, x, 2])

        r_bits, g_bits, b_bits = _scheme_bits(scheme)

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
    positions = get_pixel_order(frames, scheme, mode, seed)

    r_bits, g_bits, b_bits = _scheme_bits(scheme)
    bits = []

    for (f_idx, y, x) in positions:
        if len(bits) >= num_bits:
            break

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
