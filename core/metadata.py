import struct

SCHEME_TO_CODE = {
    '3-3-2': 0,
    '1-1-1': 1,
    '4-4-4': 2,
}

CODE_TO_SCHEME = {value: key for key, value in SCHEME_TO_CODE.items()}
CODE_TO_SCHEME[3] = '1-1-1'
CODE_TO_SCHEME[4] = '4-4-4'

MODE_TO_CODE = {
    'sequential': 0,
    'random': 1,
}

CODE_TO_MODE = {value: key for key, value in MODE_TO_CODE.items()}


def _resolve_message_type(info):
    if 'message_type' in info:
        message_type = int(info['message_type'])
        if message_type not in (0, 1):
            raise ValueError("message_type harus 0 (teks) atau 1 (file)")
        return message_type

    if 'is_file' in info:
        return 1 if bool(info['is_file']) else 0

    if 'is_text' in info:
        return 0 if bool(info['is_text']) else 1

    return 1

def build_header(info):
    ext = info.get('extension', '').encode()
    nama = info.get('nama_file', '').encode()

    message_type = _resolve_message_type(info)

    mode = info.get('mode', 'sequential')
    if mode not in MODE_TO_CODE:
        raise ValueError(f"Mode sisip tidak dikenal: {mode}")

    scheme = info.get('scheme', '3-3-2')
    if scheme not in SCHEME_TO_CODE:
        raise ValueError(f"Skema LSB tidak dikenal untuk metadata: {scheme}")

    h = struct.pack('>I', info['ukuran'])
    h += bytes([message_type])
    h += bytes([1 if info['is_encrypted'] else 0])
    h += bytes([MODE_TO_CODE[mode]])
    h += bytes([SCHEME_TO_CODE[scheme]])
    h += bytes([len(ext)]) + ext
    h += bytes([len(nama)]) + nama

    return h


def parse_header(data):
    i = 0

    ukuran = struct.unpack('>I', data[i:i+4])[0]
    i += 4

    message_type = data[i]; i += 1
    if message_type not in (0, 1):
        raise ValueError(f"Jenis pesan tidak valid di header: {message_type}")

    is_encrypted = bool(data[i]); i += 1
    mode_code = data[i]; i += 1
    scheme_code = data[i]; i += 1

    if mode_code not in CODE_TO_MODE:
        raise ValueError(f"Mode code tidak dikenal: {mode_code}")

    if scheme_code not in CODE_TO_SCHEME:
        raise ValueError(f"Scheme code tidak dikenal: {scheme_code}")

    ext_len = data[i]; i += 1
    extension = data[i:i+ext_len].decode(); i += ext_len

    nama_len = data[i]; i += 1
    nama_file = data[i:i+nama_len].decode(); i += nama_len

    return {
        'ukuran': ukuran,
        'message_type': message_type,
        'is_text': message_type == 0,
        'is_file': message_type == 1,
        'is_encrypted': is_encrypted,
        'mode': CODE_TO_MODE[mode_code],
        'scheme': CODE_TO_SCHEME[scheme_code],
        'extension': extension,
        'nama_file': nama_file,
        'header_size': i,
    }