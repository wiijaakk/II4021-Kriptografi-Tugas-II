from core.A5_1 import A5_1, A51Manager
engine = A5_1()
manager = A51Manager(engine)

def encrypt_logic_nopad(self, raw_bytes, key_int, start_fn=0):
    bit_list = self.bytes_to_bits(raw_bytes)
    # NO PADDING!
    encrypted_bits = []
    current_fn = start_fn
    for i in range(0, len(bit_list), 228):
        blok = bit_list[i:i+228]
        self.engine.initialize(key_int, current_fn)
        keystream = self.engine.get_keystream_block()
        cipher_blok = [b ^ k for b, k in zip(blok, keystream)]
        encrypted_bits.extend(cipher_blok)
        current_fn += 1
    return self.bits_to_bytes(encrypted_bits)

A51Manager.encrypt_logic = encrypt_logic_nopad

raw = b"1234567890" # 10 bytes
print("Original len:", len(raw))

enc = manager.encrypt_logic(raw, 12345)
print("Encrypted len (no pad):", len(enc))

dec = manager.encrypt_logic(enc, 12345)
print("Decrypted len (no pad):", len(dec))
print("Decrypted:", dec)

