"""
test_manual.py
jalankan: python test_manual.py

simulasi flow lengkap tanpa GUI dan tanpa modul kripto beneran.
nanti kalau modul kripto udah jadi, tinggal ganti bagian dummy crypto.
"""

import cv2
import numpy as np
import tempfile
import os
import hashlib

from core.video_io import LOSSLESS_CODEC
from core.stego import embed, extract


def make_cover_video(path, width=640, height=480, n_frames=30, fps=30):
    w = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*LOSSLESS_CODEC), fps, (width, height))
    for _ in range(n_frames):
        frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        w.write(frame)
    w.release()


def md5(data):
    return hashlib.md5(data).hexdigest()


# ── dummy kripto ──────────────────────────────────────────
# nanti ini diganti sama output beneran dari modul kripto
# sekarang pura-pura aja payload udah diproses

def dummy_kripto_output(pesan, nama_file='', extension='', is_text=False, is_encrypted=False):
    # kalau nanti udah ada modul kripto beneran:
    # payload = kripto.encrypt(pesan, kunci) kalau is_encrypted
    # sekarang langsung return raw
    return {
        'payload': pesan,
        'ukuran': len(pesan),
        'nama_file': nama_file,
        'extension': extension,
        'is_encrypted': is_encrypted,
        'is_text': is_text,
    }


# ── test cases ────────────────────────────────────────────

def test(label, pesan, nama_file, extension, is_text, scheme, mode, seed=None):
    cover = tempfile.mktemp(suffix='.avi')
    output = tempfile.mktemp(suffix='.avi')
    make_cover_video(cover)

    payload_info = dummy_kripto_output(pesan, nama_file, extension, is_text)

    try:
        # simulasi user klik embed di GUI
        embed(cover, payload_info, output, scheme, mode, seed)

        # simulasi user klik extract di GUI
        result, meta = extract(output, scheme, mode, seed)

        ok = md5(pesan) == md5(result)
        status = 'PASS' if ok else 'FAIL'
        print(f'[{status}] {label}')
        if not ok:
            print(f'       expected : {pesan[:30]}')
            print(f'       got      : {result[:30]}')
    except Exception as e:
        print(f'[ERROR] {label} → {e}')
    finally:
        os.unlink(cover)
        if os.path.exists(output):
            os.unlink(output)


if __name__ == '__main__':
    print('====== TEST MANUAL ======\n')

    # pesan teks
    test('teks pendek, sequential, 3-3-2',
         b'halo ini pesan teks', '', '', True, '3-3-2', 'sequential')

    test('teks pendek, random, 3-3-2',
         b'halo ini pesan teks', '', '', True, '3-3-2', 'random', seed='kuncirahasia')

    # file pdf simulasi
    pdf_dummy = b'%PDF-1.4 ' + os.urandom(2000)
    test('file pdf, sequential, 3-3-2',
         pdf_dummy, 'laporan.pdf', 'pdf', False, '3-3-2', 'sequential')

    test('file pdf, random, 3-3-2',
         pdf_dummy, 'laporan.pdf', 'pdf', False, '3-3-2', 'random', seed='abc123')

    # file exe simulasi
    exe_dummy = os.urandom(3000)
    test('file exe, sequential, 1-1-1',
         exe_dummy, 'program.exe', 'exe', False, '1-1-1', 'sequential')

    # skema 4-4-4
    test('teks, sequential, 4-4-4',
         b'test skema kapasitas besar', '', '', True, '4-4-4', 'sequential')

    # pesan besar
    besar = os.urandom(10000)
    test('file besar 10kb, sequential, 3-3-2',
         besar, 'bigfile.bin', 'bin', False, '3-3-2', 'sequential')

    # capacity reject
    print()
    print('--- capacity check ---')
    cover = tempfile.mktemp(suffix='.avi')
    output = tempfile.mktemp(suffix='.avi')
    make_cover_video(cover, n_frames=1)
    payload_info = dummy_kripto_output(os.urandom(999999), 'gede.bin', 'bin', False)
    try:
        embed(cover, payload_info, output, '3-3-2', 'sequential')
        print('[FAIL] capacity check harusnya reject')
    except ValueError as e:
        print(f'[PASS] capacity check → {e}')
    finally:
        os.unlink(cover)
        if os.path.exists(output):
            os.unlink(output)

    print('\n====== SELESAI ======')