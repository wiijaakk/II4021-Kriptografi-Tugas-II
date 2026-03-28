from core.A5_1 import A5_1, A51Manager
engine = A5_1()
manager = A51Manager(engine)
raw = b"1234567890" # 10 bytes
print("Original len:", len(raw))

enc = manager.encrypt_logic(raw, 12345)
print("Encrypted len (should be padded):", len(enc))

# Assume extraction takes only first 10 bytes
extracted_part = enc[:10]

# Now let's decrypt just the extracted part
engine_dec = A5_1()
manager_dec = A51Manager(engine_dec)
dec = manager_dec.encrypt_logic(extracted_part, 12345)
print("Decrypted len:", len(dec))
print("Decrypted (first 10):", dec[:10])

