import cv2
import numpy as np
import matplotlib.pyplot as plt

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