import os

class A5_1:
    def __init__(self):
        self.reg_x = [0] * 19
        self.reg_y = [0] * 22
        self.reg_z = [0] * 23
        self.keystream = [0] * 228
        self.frame_number = 0

    def initialize(self, key, frame_number):
        self.reg_x = [0] * 19
        self.reg_y = [0] * 22
        self.reg_z = [0] * 23
        for i in range(64):
            self.clock_all((key >> i) & 1)
        for i in range(22):
            self.clock_all((frame_number >> i) & 1)
        for i in range(100):
            self.step_majority()

    def get_keystream_block(self):
        for i in range(228):
            self.keystream[i] = self.step_majority()
        return self.keystream

    def step_majority(self):
        most_common_element = (self.reg_x[8] & self.reg_y[10]) | (self.reg_x[8] & self.reg_z[10]) | (self.reg_y[10] & self.reg_z[10])
        returned_bit = self.reg_x[18]^self.reg_y[21]^self.reg_z[22]
        if(self.reg_x[8] == most_common_element):   
            self.clock_register(self.reg_x, self.reg_x[18] ^ self.reg_x[17] ^ self.reg_x[16] ^ self.reg_x[13])
        if(self.reg_y[10] == most_common_element):
            self.clock_register(self.reg_y, self.reg_y[21] ^ self.reg_y[20])
        if(self.reg_z[10] == most_common_element):
            self.clock_register(self.reg_z, self.reg_z[22] ^ self.reg_z[21] ^ self.reg_z[20] ^ self.reg_z[7])
        return returned_bit

    def clock_register(self, register, input_bit):
        for i in range(len(register)-1, 0, -1):
            register[i] = register[i-1]
        register[0] = input_bit
    
    def clock_all(self, external_bit=0):
        self.clock_register(self.reg_x, self.reg_x[18] ^ self.reg_x[17] ^ self.reg_x[16] ^ self.reg_x[13] ^ external_bit)
        self.clock_register(self.reg_y, self.reg_y[21] ^ self.reg_y[20] ^ external_bit)
        self.clock_register(self.reg_z, self.reg_z[22] ^ self.reg_z[21] ^ self.reg_z[20] ^ self.reg_z[7] ^ external_bit)

class A51Manager:
    def __init__(self, a5_engine, is_text=False, file_path="", extension="", is_encrypted=False, content=None):
        self.engine = a5_engine
        self.is_text = is_text
        self.file_path = file_path
        self.nama_file = os.path.basename(file_path) if file_path else ""
        self.extension = extension
        self.is_encrypted = is_encrypted
        self.content = content

    def bytes_to_bits(self, data):
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 1)
        return bits

    def bits_to_bytes(self, bits):
        result = bytearray()
        for i in range(0, len(bits), 8):
            chunk = bits[i:i+8]
            if len(chunk) < 8:
                break
            byte = 0
            for j, bit in enumerate(chunk):
                byte |= (bit << j)
            result.append(byte)
        return bytes(result)
    
    def process_prepare(self):
        if self.is_text:
            raw_bytes = self.content.encode('utf-8')
            self.extension = ""
        else:
            with open(self.file_path, 'rb') as f:
                raw_bytes = f.read()
            self.extension = self.nama_file.split('.')[-1] if '.' in self.nama_file else ""
        return raw_bytes

    def encrypt_logic(self, raw_bytes, key_int, start_fn=0):
        bit_list = self.bytes_to_bits(raw_bytes)
        while len(bit_list) % 228 != 0:
            bit_list.append(0)
        encrypted_bits = []
        current_fn = start_fn
        for i in range(0, len(bit_list), 228):
            blok = bit_list[i:i+228]
            self.engine.initialize(key_int, current_fn)
            keystream = self.engine.get_keystream_block()
            cipher_blok = [b ^ k for b, k in zip(blok, keystream)]
            encrypted_bits.extend(cipher_blok)
            current_fn += 1
        payload_encrypted = self.bits_to_bytes(encrypted_bits)
        return payload_encrypted
    
    def decrypt_logic(self, encrypted_payload, key_int, original_size, start_fn=0):
        decrypted = self.encrypt_logic(encrypted_payload, key_int, start_fn)
        return decrypted[:original_size]

    def interface(self, key_int):
        raw_bytes = self.process_prepare()
        if self.is_encrypted:
            payload = self.encrypt_logic(raw_bytes, key_int, start_fn=0)
        else:
            payload = raw_bytes
        return{
            "payload": payload,
            "ukuran": len(raw_bytes),
            "nama_file": self.nama_file,
            "extension": self.extension,
            "is_encrypted": self.is_encrypted,
            "is_text": self.is_text
        }