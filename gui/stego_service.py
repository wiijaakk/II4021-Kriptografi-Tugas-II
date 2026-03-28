from pathlib import Path

from core.metadata import build_header
from core.stego import embed as stego_embed
from core.stego import extract as stego_extract
from core.video_io import calculate_capacity
from gui.crypto_util import decrypt_bytes, encrypt_bytes


def _parse_a51_key(key_text):
    key_text = (key_text or "").strip()
    if not key_text:
        raise ValueError("Key A5/1 wajib diisi.")

    try:
        return int(key_text)
    except ValueError as exc:
        raise ValueError("Key A5/1 harus berupa bilangan bulat.") from exc


def _resolve_seed(mode, stego_key):
    mode = (mode or "").strip().lower()
    stego_key = (stego_key or "").strip()

    if mode not in ("sequential", "random"):
        raise ValueError("Mode harus sequential atau random.")

    if mode == "random" and not stego_key:
        raise ValueError("Mode random wajib mengisi stego-key.")

    return stego_key if mode == "random" else None


def _build_payload_bytes(payload_type, text_payload, file_payload_path):
    payload_type = (payload_type or "").strip().lower()

    if payload_type == "text":
        text_payload = (text_payload or "").strip()
        if not text_payload:
            raise ValueError("Payload text tidak boleh kosong.")

        return text_payload.encode("utf-8"), "", "", True

    if payload_type == "file":
        file_payload_path = (file_payload_path or "").strip()
        if not file_payload_path:
            raise ValueError("Payload file belum dipilih.")

        file_path = Path(file_payload_path)
        if not file_path.exists() or not file_path.is_file():
            raise ValueError("File payload tidak ditemukan.")

        raw = file_path.read_bytes()
        extension = file_path.suffix.lstrip(".")
        return raw, file_path.stem, extension, False

    raise ValueError("Jenis payload tidak valid.")


def _estimate_total_bytes(payload_info, mode, scheme):
    header_info = dict(payload_info)
    header_info["mode"] = mode
    header_info["scheme"] = scheme
    header = build_header(header_info)
    return len(header) + len(payload_info["payload"])


def _estimate_encrypted_size(raw_size_bytes):
    total_bits = int(raw_size_bytes) * 8
    block_bits = 228
    block_count = (total_bits + block_bits - 1) // block_bits
    return (block_count * block_bits) // 8


def embed_payload(
    cover_video,
    output_video,
    payload_type,
    text_payload,
    file_payload_path,
    a51_key,
    mode,
    scheme,
    stego_key,
    encrypt_enabled=True,
):
    cover_video = (cover_video or "").strip()
    output_video = (output_video or "").strip()
    scheme = (scheme or "").strip()

    if not cover_video:
        raise ValueError("Cover video wajib diisi.")
    if not output_video:
        raise ValueError("Path output video wajib diisi.")

    seed = _resolve_seed(mode, stego_key)
    raw_payload, nama_file, extension, is_text = _build_payload_bytes(
        payload_type,
        text_payload,
        file_payload_path,
    )

    estimated_payload_size = len(raw_payload)
    if encrypt_enabled:
        estimated_payload_size = _estimate_encrypted_size(len(raw_payload))

    estimate_info = {
        "ukuran": estimated_payload_size,
        "nama_file": nama_file,
        "extension": extension,
        "is_encrypted": bool(encrypt_enabled),
        "is_text": is_text,
    }

    # biar validate capacity dulu sebelum jalan
    needed_bytes = _estimate_total_bytes({"payload": b"\x00" * 0, **estimate_info}, mode, scheme)
    needed_bytes += estimated_payload_size
    available_bytes = calculate_capacity(cover_video, scheme)
    if needed_bytes > available_bytes:
        raise ValueError(
            f"Kapasitas tidak cukup. Butuh {needed_bytes} bytes, tersedia {available_bytes} bytes."
        )

    payload_bytes = raw_payload
    if encrypt_enabled:
        key_int = _parse_a51_key(a51_key)
        payload_bytes = encrypt_bytes(raw_payload, key_int)

    payload_info = {
        "payload": payload_bytes,
        "ukuran": len(payload_bytes),
        "nama_file": nama_file,
        "extension": extension,
        "is_encrypted": bool(encrypt_enabled),
        "is_text": is_text,
    }

    stego_embed(cover_video, payload_info, output_video, scheme, mode, seed)

    return {
        "payload_info": payload_info,
        "needed_bytes": needed_bytes,
        "available_bytes": available_bytes,
    }


def _decode_text_payload(payload):
    text = payload.decode("utf-8", errors="replace")
    return text.rstrip("\x00")


def _default_output_name(meta):
    base = meta.get("nama_file") or "extracted_payload"
    extension = (meta.get("extension") or "").strip()
    if extension:
        return f"{base}.{extension}"
    return base


def extract_payload(stego_video, a51_key, stego_key, mode, scheme):
    stego_video = (stego_video or "").strip()
    if not stego_video:
        raise ValueError("Stego video wajib diisi.")

    seed = _resolve_seed(mode, stego_key)
    payload, meta = stego_extract(stego_video, scheme, mode, seed)

    if meta.get("is_encrypted"):
        key_int = _parse_a51_key(a51_key)
        payload = decrypt_bytes(payload, key_int)

    result = {
        "meta": meta,
        "payload": payload,
        "is_text": bool(meta.get("is_text")),
    }

    if result["is_text"]:
        result["text"] = _decode_text_payload(payload)
    else:
        result["default_filename"] = _default_output_name(meta)

    return result