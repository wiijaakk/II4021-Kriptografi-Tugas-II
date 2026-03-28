import cv2
import numpy as np
import matplotlib.pyplot as plt


def sample_rgb_histogram(video_path, max_frames=48, bins=256, sample_size=(320, 180)):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Video tidak bisa dibuka untuk histogram.")

    hist_r = np.zeros((bins,), dtype=np.float64)
    hist_g = np.zeros((bins,), dtype=np.float64)
    hist_b = np.zeros((bins,), dtype=np.float64)

    processed = 0
    while processed < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Use a fixed-size sampled frame so histogram scale is stable and readable.
        if sample_size is not None:
            frame = cv2.resize(frame, sample_size, interpolation=cv2.INTER_AREA)

        b, g, r = cv2.split(frame)
        hist_b += cv2.calcHist([b], [0], None, [bins], [0, 256]).flatten()
        hist_g += cv2.calcHist([g], [0], None, [bins], [0, 256]).flatten()
        hist_r += cv2.calcHist([r], [0], None, [bins], [0, 256]).flatten()
        processed += 1

    cap.release()

    if processed == 0:
        raise ValueError("Frame video kosong. Histogram tidak dapat dihitung.")

    hist_r /= processed
    hist_g /= processed
    hist_b /= processed

    return {
        "r": hist_r,
        "g": hist_g,
        "b": hist_b,
        "bins": np.arange(0, bins),
        "frames": processed,
    }

def calculate_mse(video1, video2):
    cap1 = cv2.VideoCapture(video1)
    cap2 = cv2.VideoCapture(video2)

    mse_total = 0
    count = 0

    while True:
        ret1, f1 = cap1.read()
        ret2, f2 = cap2.read()

        if not ret1 or not ret2:
            break

        err = np.mean((f1.astype("float") - f2.astype("float")) ** 2)
        mse_total += err
        count += 1

    cap1.release()
    cap2.release()

    return mse_total / count if count > 0 else 0


def calculate_psnr(mse):
    if mse == 0:
        return float('inf')
    return 10 * np.log10((255 ** 2) / mse)


def plot_histogram(video_path, title="Histogram"):
    cap = cv2.VideoCapture(video_path)

    r_vals, g_vals, b_vals = [], [], []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        b, g, r = cv2.split(frame)
        r_vals.extend(r.flatten())
        g_vals.extend(g.flatten())
        b_vals.extend(b.flatten())

    cap.release()

    plt.figure()
    plt.hist(r_vals, bins=256, alpha=0.5, label='R')
    plt.hist(g_vals, bins=256, alpha=0.5, label='G')
    plt.hist(b_vals, bins=256, alpha=0.5, label='B')
    plt.legend()
    plt.title(title)
    plt.show()