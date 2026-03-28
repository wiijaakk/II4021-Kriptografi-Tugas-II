import hashlib
from core.lsb_core import bytes_to_bits, bits_to_bytes
from core.metadata import build_header, parse_header
from core.embedding import embed as embed_to_frames, extract as extract_from_frames
from core.video_io import read_video, write_video, calculate_capacity
from core.mp4_core import embed_mp4, extract_mp4


def embed(cover_path, payload_info, output_path, scheme, mode, seed=None):
    payload = payload_info['payload']
    header_info = dict(payload_info)
    header_info['mode'] = mode
    header_info['scheme'] = scheme
    header = build_header(header_info)
    full_data = header + payload

    capacity = calculate_capacity(cover_path, scheme)
    if len(full_data) > capacity:
        raise ValueError(f"pesan terlalu besar: {len(full_data)} bytes, kapasitas: {capacity} bytes")

    frames, info = read_video(cover_path)
    bits = bytes_to_bits(full_data)
    
    if scheme == 'mp4-robust':
        modified_frames = embed_mp4(frames, bits)
    else:
        modified_frames, _ = embed_to_frames(frames, bits, scheme, mode, seed)
        
    write_video(output_path, modified_frames, info)


def extract(stego_path, scheme, mode, seed=None):
    frames, info = read_video(stego_path)

    if scheme == 'mp4-robust':
        all_bits = extract_mp4(frames)
        if not all_bits:
            raise ValueError("Tidak ada pesan yang bisa diekstrak dari video ini (mungkin karena kompresi terlalu parah / rusak).")
        # Karena kita baca full sequence, langsung parse aja
        header_bytes = bits_to_bytes(all_bits[:520*8])
        parsed = parse_header(header_bytes)
        all_bytes = bits_to_bytes(all_bits)
        payload = all_bytes[parsed['header_size'] : parsed['header_size'] + parsed['ukuran']]
        return payload, parsed
        
    # extract header dulu, ambil secukupnya buat parse
    # worst case header = 4+1+1+1+1+1+255+1+255 = 520 bytes = 520*8 bits
    max_header_bits = 520 * 8
    header_bits = extract_from_frames(frames, max_header_bits, scheme, mode, seed)
    header_bytes = bits_to_bytes(header_bits)
    parsed = parse_header(header_bytes)

    total_bits = (parsed['header_size'] + parsed['ukuran']) * 8
    all_bits = extract_from_frames(frames, total_bits, scheme, mode, seed)
    all_bytes = bits_to_bytes(all_bits)

    payload = all_bytes[parsed['header_size']:]

    return payload, parsed


def md5(data):
    return hashlib.md5(data).hexdigest()
