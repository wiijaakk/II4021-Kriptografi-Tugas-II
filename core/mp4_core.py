import numpy as np

BLOCK_SIZE = 16  # 1 bit disebar ke 16x16 = 256 piksel biar tahan kompresi
MASK_BIT = 64    # bit ke-7, cukup kuat tahan H.264 tapi perubahannya ga keliatan

def embed_mp4(frames, full_bits):
    h, w = frames[0].shape[:2]
    max_blocks = (h // BLOCK_SIZE) * (w // BLOCK_SIZE)
    usable_bits = max_blocks - 64  # sisain 64 blok buat header + dummy padding
    
    result_frames = [f.copy() for f in frames]
    
    bit_idx = 0
    for frame_idx, frame in enumerate(result_frames):
        if bit_idx >= len(full_bits):
            break
            
        chunk = full_bits[bit_idx : bit_idx + usable_bits]
        bit_idx += len(chunk)
        
        header_idx = [(frame_idx >> i) & 1 for i in range(16)]
        header_len = [(len(chunk) >> i) & 1 for i in range(16)]
        dummy = [0] * 32  # padding di depan biar distorsi awal frame ga ngereject data
        
        frame_data = dummy + header_idx + header_len + chunk
        
        idx = 0
        for y in range(0, h - BLOCK_SIZE + 1, BLOCK_SIZE):
            for x in range(0, w - BLOCK_SIZE + 1, BLOCK_SIZE):
                if idx >= len(frame_data):
                    break
                
                bit = frame_data[idx]
                
                for by in range(BLOCK_SIZE):
                    for bx in range(BLOCK_SIZE):
                        b = int(frame[y+by, x+bx, 0])
                        if bit == 1:
                            frame[y+by, x+bx, 0] = b | MASK_BIT
                        else:
                            frame[y+by, x+bx, 0] = b & ~MASK_BIT
                idx += 1
                
    return result_frames

def extract_mp4(frames):
    h, w = frames[0].shape[:2]
    extracted_chunks = {}
    
    for frame in frames:
        bits = []
        
        for y in range(0, h - BLOCK_SIZE + 1, BLOCK_SIZE):
            for x in range(0, w - BLOCK_SIZE + 1, BLOCK_SIZE):
                vote_1 = 0
                for by in range(BLOCK_SIZE):
                    for bx in range(BLOCK_SIZE):
                        b = int(frame[y+by, x+bx, 0])
                        if (b & MASK_BIT) != 0:
                            vote_1 += 1
                
                # majority vote
                if vote_1 > (BLOCK_SIZE * BLOCK_SIZE) / 2:
                    bits.append(1)
                else:
                    bits.append(0)
                    
        bits = bits[32:]  # skip dummy padding
                    
        if len(bits) < 32:
            continue
            
        frame_idx = 0
        for i in range(16):
            frame_idx |= (bits[i] << i)
            
        data_len = 0
        for i in range(16, 32):
            data_len |= (bits[i] << (i - 16))
            
        if data_len > 0 and data_len <= (len(bits) - 32):
            extracted_chunks[frame_idx] = bits[32 : 32 + data_len]
            
    sorted_keys = sorted(extracted_chunks.keys())
    full_bits = []
    for k in sorted_keys:
        full_bits.extend(extracted_chunks[k])
        
    return full_bits