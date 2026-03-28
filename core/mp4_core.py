import numpy as np

# Kita perbesar blok jadi 16x16 supaya tahan kompresi ganas MP4 (1 bit disebar ke 256 pixel)
BLOCK_SIZE = 16

# Kita pake Bit paling signifikan ke-7 (Tepat di bawah MSB murni, nilai 64).
# Biar bener bener tahan modifikasi algoritma kompresi.
MASK_BIT = 64

def embed_mp4(frames, full_bits):
    h, w = frames[0].shape[:2]
    max_blocks = (h // BLOCK_SIZE) * (w // BLOCK_SIZE)
    # Header butuh 32 blok (16 bit idx, 16 bit len) plus kita kasih padding 32 bit dummy 
    usable_bits = max_blocks - 64 
    
    result_frames = [f.copy() for f in frames]
    
    bit_idx = 0
    for frame_idx, frame in enumerate(result_frames):
        if bit_idx >= len(full_bits):
            break
            
        chunk = full_bits[bit_idx : bit_idx + usable_bits]
        bit_idx += len(chunk)
        
        # Bikin marker yg super safety: Index dan Panjang
        header_idx = [(frame_idx >> i) & 1 for i in range(16)]
        header_len = [(len(chunk) >> i) & 1 for i in range(16)]
        
        # Tambah dummy padding di depan biar ga kena distorsi awal frame
        dummy = [0] * 32
        
        frame_data = dummy + header_idx + header_len + chunk
        
        # Proses sisip ke blok 16x16
        idx = 0
        for y in range(0, h - BLOCK_SIZE + 1, BLOCK_SIZE):
            for x in range(0, w - BLOCK_SIZE + 1, BLOCK_SIZE):
                if idx >= len(frame_data):
                    break
                
                bit = frame_data[idx]
                
                # Copy 1 bit tersebut ke 256 piksel
                for by in range(BLOCK_SIZE):
                    for bx in range(BLOCK_SIZE):
                        b = int(frame[y+by, x+bx, 0])
                        # Reset bit dulu baru set
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
        
        # Ekstrak data per blok 16x16 pakai Majority Vote
        for y in range(0, h - BLOCK_SIZE + 1, BLOCK_SIZE):
            for x in range(0, w - BLOCK_SIZE + 1, BLOCK_SIZE):
                vote_1 = 0
                for by in range(BLOCK_SIZE):
                    for bx in range(BLOCK_SIZE):
                        b = int(frame[y+by, x+bx, 0])
                        if (b & MASK_BIT) != 0:
                            vote_1 += 1
                            
                if vote_1 > (BLOCK_SIZE * BLOCK_SIZE) / 2:
                    bits.append(1)
                else:
                    bits.append(0)
                    
        # Skip 32 bit padding dummy
        bits = bits[32:]
                    
        if len(bits) < 32:
            continue
            
        frame_idx = 0
        for i in range(16):
            frame_idx |= (bits[i] << i)
            
        data_len = 0
        for i in range(16, 32):
            # Rumus (i - 16) yang awal justru yang BENAR, sumpah.
            data_len |= (bits[i] << (i - 16))
            
        if data_len > 0 and data_len <= (len(bits) - 32):
            extracted_chunks[frame_idx] = bits[32 : 32 + data_len]
            
    sorted_keys = sorted(extracted_chunks.keys())
    full_bits = []
    for k in sorted_keys:
        full_bits.extend(extracted_chunks[k])
        
    return full_bits


