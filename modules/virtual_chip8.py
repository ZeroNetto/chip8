
class Virtual_chip8:
    def __init__(self):
        self.width = 64
        self.height = 32
        self.field = []
        self.commands = []
        self._init_field_()

    def _init_field_(self):
        self.field = []
        for x in range(self.width):
            self.field.add([])
            for y in range(self.height):
                self.field[x].add([])

    def start(file, self):
        for line in file.readlines():
            compare_with_command(line)
        pass

    def compare_with_command(self):
        pass

    def cls(self):
        # clean screen
        self._init_field_()

    def ret(self):
        # return
        pass

    def jp_NNN(self):
        # jump
        pass

    def call_NNN(self):
        # call programm from adress
        pass

    def se_VX_KK(self):
        # skip instruction if VX==KK
        pass

    def sne_VX_KK(self):
        # skip instruction if VX!=KK
        pass

    def ld_VX_KK(self):
        # load the number KK to register VX
        pass

    def add_VX_KK(self):
        # load in VX register the sum of VX and KK
        pass

    def ld_VX_VY(self):
        # load value from VY register to VX register
        pass

    def or_VX_VY(self):
        # boolean "or" between VX and VY
        pass
    
    def and_VX_VY(self):
        # boolean "and" between VX and VY
        pass
    
    def xor_VX_VY(self):
        # boolean "not or" between VX and VY
        pass
    
    def 