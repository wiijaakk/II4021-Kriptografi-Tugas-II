from core.A5_1 import A5_1, A51Manager

def encrypt_bytes(data_bytes, key_int):
    engine = A5_1()
    manager = A51Manager(engine)
    return manager.encrypt_logic(data_bytes, key_int)

def decrypt_bytes(data_bytes, key_int):
    engine = A5_1()
    manager = A51Manager(engine)
    return manager.encrypt_logic(data_bytes, key_int)