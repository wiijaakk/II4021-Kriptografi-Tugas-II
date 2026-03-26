import cv2
import numpy as np
from pathlib import Path

LOSSLESS_CODEC = 'RGBA'

LSB_SCHEMES = {
    '1-1-1': (1, 1, 1),
    '3-3-2': (3, 3, 2),
    '4-4-4': (4, 4, 4),
}

def read_video(video_path):
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {video_path}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Tidak bisa membuka video: {video_path}")

    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    info['frame_count'] = len(frames)
    return frames, info


def write_video(output_path, frames, info):
    fourcc = cv2.VideoWriter_fourcc(*LOSSLESS_CODEC)
    writer = cv2.VideoWriter(output_path, fourcc, info['fps'], (info['width'], info['height']))

    if not writer.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*'png ')
        writer = cv2.VideoWriter(output_path, fourcc, info['fps'], (info['width'], info['height']))

    if not writer.isOpened():
        raise ValueError("Gagal membuat video output, codec tidak support")

    for frame in frames:
        writer.write(frame)
    writer.release()


def calculate_capacity(video_path, scheme='3-3-2'):
    if scheme not in LSB_SCHEMES:
        raise ValueError(f"Skema tidak dikenal: {scheme}")

    frames, info = read_video(video_path)
    r, g, b = LSB_SCHEMES[scheme]
    bits_per_pixel = r + g + b
    total_pixels = info['width'] * info['height'] * info['frame_count']
    total_bytes = (total_pixels * bits_per_pixel) // 8

    return total_bytes


def check_capacity(video_path, payload_size_bytes, scheme='3-3-2'):
    return payload_size_bytes <= calculate_capacity(video_path, scheme)
