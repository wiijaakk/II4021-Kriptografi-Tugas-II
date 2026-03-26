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