import sys
import time
import re
import random


class Virtual_chip8:
    def __init__(self):
        # First 512 bytes - reserved by chip8, so first command location is 512
        self.width = 64
        self.height = 32
        self.pc = 512
        self.i = 0
        self.field = []
        self.memory = []
        self.registers = []
        self.key_inputs = []
        self.stack = []
        self.delay_timer = hex(0)
        self.sound_timer = hex(0)
        self._init_memory()
        self._init_registers()
        self._init_field_()
        self.compare_table = {'cls': '0x00e0',
                              'ret': '0x00ee'}
        self.fonts = ['0xF0', '0x90', '0x90', '0x90', '0xF0',  # 0
                      '0x20', '0x60', '0x20', '0x20', '0x70',  # 1
                      '0xF0', '0x10', '0xF0', '0x80', '0xF0',  # 2
                      '0xF0', '0x10', '0xF0', '0x10', '0xF0',  # 3
                      '0x90', '0x90', '0xF0', '0x10', '0x10',  # 4
                      '0xF0', '0x80', '0xF0', '0x10', '0xF0',  # 5
                      '0xF0', '0x80', '0xF0', '0x90', '0xF0',  # 6
                      '0xF0', '0x10', '0x20', '0x40', '0x40',  # 7
                      '0xF0', '0x90', '0xF0', '0x90', '0xF0',  # 8
                      '0xF0', '0x90', '0xF0', '0x10', '0xF0',  # 9
                      '0xF0', '0x90', '0xF0', '0x90', '0x90',  # A
                      '0xE0', '0x90', '0xE0', '0x90', '0xE0',  # B
                      '0xF0', '0x80', '0x80', '0x80', '0xF0',  # C
                      '0xE0', '0x90', '0x90', '0x90', '0xE0',  # D
                      '0xF0', '0x80', '0xF0', '0x80', '0xF0',  # E
                      '0xF0', '0x80', '0xF0', '0x80', '0x80']  # F

    def _init_registers(self):
        for x in range(16):
            self.registers.append('0x00')

    def _init_memory(self):
        for x in range(4096):
            self.memory.append('0x00')

    def _init_field_(self):
        self.field = []
        for x in range(self.width):
            self.field.append([])
            for y in range(self.height):
                self.field[x].append([])
                self.field[x][y] = '0'

    def print_field(self):
        print()
        representation = ''
        for y in range(self.height):
            for x in range(self.width):
                representation += ' ' + self.field[x][y]
                representation = representation.replace('0b', '')
                representation = representation.replace('0', '.')
                representation = representation.replace('1', '#')
            print(representation)
            representation = ''
        return

    def start(self, file):
        memory_limit = 4096
        counter = 0
        shift = 512
        command = '0x'
        temp_num = ''
        for line in file.readlines():
            for num in line:
                temp_num = hex(num)
                if len(temp_num) < 4:
                    temp_num = '0x0' + temp_num[2]
                self.memory[counter + shift] = temp_num
                counter += 1
        while self.pc < memory_limit:
            command = self.memory[self.pc] + self.memory[self.pc + 1]
            command = command.replace('0x', '')
            command = '0x' + command
            self.compare_with(command)
        return
    # NNN - adress
    # KK - const
    # X, Y - number of register

    def compare_with(self, command):
        if self.compare_table['cls'] == command:
            self.clean_screen(command)
        elif self.compare_table['ret'] == command:
            self.ret(command)
        elif '1' == command[2]:
            self.jp_NNN(command)
        elif '2' == command[2]:
            self.call_NNN(command)
        elif '3' == command[2]:
            self.se_VX_KK(command)
        elif '4' == command[2]:
            self.sne_VX_KK(command)
        elif re.match('0x5.*0', command):
            self.sne_VX_VY(command)
        elif '6' == command[2]:
            self.ld_VX_KK(command)
        elif '7' == command[2]:
            self.add_VX_KK(command)
        elif re.match('0x8.*0', command):
            self.ld_VX_VY(command)
        elif re.match('0x8.*1', command):
            self.or_VX_VY(command)
        elif re.match('0x8.*2', command):
            self.and_VX_VY(command)
        elif re.match('0x8.*3', command):
            self.xor_VX_VY(command)
        elif re.match('0x8.*4', command):
            self.add_VX_VY(command)
        elif re.match('0x8.*5', command):
            self.sub_VX_VY(command)
        elif re.match('0x8.*6', command):
            self.shr_VX(command)
        elif re.match('0x8.*7', command):
            self.subn_VX_VY(command)
        elif re.match('0x8.*e', command):
            self.shl_VX(command)
        elif re.match('0x9.*0', command):
            self.sne_VX_VY(command)
        elif 'a' == command[2]:
            self.ld_I_NNN(command)
        elif 'b' == command[2]:
            self.jp_V0_NNN(command)
        elif 'c' == command[2]:
            self.rnd_VX_KK(command)
        elif 'd' == command[2]:
            self.drw_VX_VY_N(command)
        elif re.match('0xe.*9e', command):
            self.skp_VX(command)
        elif re.match('0xe.*a1', command):
            self.sknp_VX(command)
        elif re.match('0xf.*07', command):
            self.ld_VX_DT(command)
        elif re.match('0xf.*0a', command):
            self.ld_VX_K(command)
        elif re.match('0xf.*15', command):
            self.ld_DT_VX(command)
        elif re.match('0xf.*18', command):
            self.ld_ST_VX(command)
        elif re.match('0xf.*1e', command):
            self.add_I_VX(command)
        elif re.match('0xf.*29', command):
            self.ld_F_VX(command)
        elif re.match('0xf.*33', command):
            self.ld_B_VX(command)
        elif re.match('0xf.*55', command):
            self.ld_I_VX(command)
        elif re.match('0xf.*65', command):
            self.ld_VX_I(command)
        else:
            print("There are no such command {0}!".format(command))
            sys.exit()
        return

    def clean_screen(self, command):
        # clean screen
        self._init_field_()
        self.pc += 2
        return

    def ret(self, command):
        # return
        self.pc = int(self.stack.pop(), 16)
        return

    def jp_NNN(self, command):
        # jump
        self.pc = int(command[3:], 16)
        return

    def call_NNN(self, command):
        # call programm from adress
        first_num = self.memory[int(command[3:], 16)]
        second_num = self.memory[int(command[3:], 16) + 1]
        new_command = first_num + second_num
        new_command = new_command.replace('0x', '')
        new_command = '0x' + new_command
        self.compare_with(new_command)
        self.pc += 2
        self.stack.push(self.pc)
        return

    def se_VX_KK(self, command):
        # skpc instruction if VX==KK
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(command[4:], 16)
        if first_num == second_num:
            self.pc += 4
        else:
            self.pc += 2
        return

    def sne_VX_KK(self, command):
        # skip instruction if VX!=KK
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(command[4:], 16)
        if first_num != second_num:
            self.pc += 4
        else:
            self.pc += 2
        return

    def ld_VX_KK(self, command):
        # load the number KK to register VX
        self.registers[int(command[3], 16)] = hex(int(command[4:], 16))
        self.pc += 2
        return

    def add_VX_KK(self, command):
        # load in VX register the sum of VX and KK
        reg = int(command[3], 16)
        reg_num = int(self.registers[reg], 16)
        num = int(command[4:], 16)
        self.registers[reg] = hex(reg_num + num)
        self.pc += 2
        return

    def ld_VX_VY(self, command):
        # load value from VY register to VX register
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        self.registers[first_reg] = self.registers[second_reg]
        self.pc += 2
        return

    def or_VX_VY(self, command):
        # boolean "or" between VX and VY
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(self.registers[int(command[4], 16)], 16)
        reg = int(command[3], 16)
        bin_or = first_num | second_num
        self.registers[reg] = hex(bin_or)
        self.pc += 2
        return

    def and_VX_VY(self, command):
        # boolean "and" between VX and VY
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(self.registers[int(command[4], 16)], 16)
        reg = int(command[3], 16)
        bin_and = first_num & second_num
        self.registers[reg] = hex(bin_and)
        self.pc += 2
        return

    def xor_VX_VY(self, command):
        # boolean "not or" between VX and VY
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(self.registers[int(command[4], 16)], 16)
        reg = int(command[3], 16)
        bin_xor = first_num | second_num
        self.registers[reg] = hex(bin_xor)
        self.pc += 2
        return

    def add_VX_VY(self, command):
        # VX summing with VY. If result > 255, then VF = 1, else 0.
        # Only smallers 8 bits are saving in VX
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(self.registers[int(command[4], 16)], 16)
        reg = int(command[3], 16)
        sum_res = first_num + second_num
        if sum_res > 255:
            self.registers[15] = '0x01'
            sum_res -= 256
        else:
            self.registers[15] = '0x00'
        self.registers[reg] = hex(sum_res)
        self.pc += 2
        return

    def sub_VX_VY(self, command):
        # VY decrease from VX and the result save in VX.
        # If VX >= VY, then VF = 1, else 0
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(self.registers[int(command[4], 16)], 16)
        reg = int(command[3], 16)
        sub_res = first_num - second_num
        if sub_res >= 0:
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
            sub_res = - sub_res
        self.registers[reg] = hex(sub_res)
        self.pc += 2
        return

    def shr_VX(self, command):
        # The operation of shift to right on 1 bit. Shifted register VX.
        # If smaller bit(very right) of register VX=1, then VF=1, else VF=0
        num = int(self.registers[int(command[3], 16)], 16)
        reg = int(comand[3], 16)
        if num[len(num) - 1] == '1':
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
        num = num >> 1
        self.registers[reg] = hex(num)
        self.pc += 2
        return

    def subn_VX_VY(self, command):
        # If VY >= VX, then VF = 1, else 0.
        # Then VX is decrease from VY and the result save in VX
        first_num = int(self.registers[int(command[3], 16)], 16)
        second_num = int(self.registers[int(command[4], 16)], 16)
        reg = int(command[3], 16)
        subn_res = second_num - first_num
        if subn_res >= 0:
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
            subn_res = -subn_res
        self.registers[reg] = hex(subn_res)
        self.pc += 2
        return

    def shl_VX(self, command):
        # The operation of shift to left on 1 bit. Shifed register VX.
        # If smaller bit(very right) of register VX=1, then VF=1, else VF=0
        num = int(self.registers[int(command[3], 16)], 16)
        reg = int(command[3], 16)
        if num[len(num) - 1] == '1':
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
        num = num << 1
        self.registers[reg] = hex(num)
        self.pc += 2
        return

    def sne_VX_VY(self, command):
        # Skip the next instruction if VX != VY
        first_num = self.registers[int(command[3], 16)]
        second_num = self.registers[int(command[4], 16)]
        if first_num != second_num:
            self.pc += 4
        else:
            self.pc += 2
        return

    def ld_I_NNN(self, command):
        # The value of register I set in NNN.
        self.i = int(command[3:], 16)
        self.pc += 2
        return

    def jp_V0_NNN(self, command):
        # Move to NNN + V0 adress
        self.pc = int(command[3:], 16) + int(self.registers[0], 16)
        return

    def rnd_VX_KK(self, command):
        # Random value (from 0 to 255) & KK
        reg = int(command[3], 16)
        num = int(command[4:], 16)
        self.registers[reg] = hex(random.randint(0, 255) & num)
        self.pc += 2
        return

    def drw_VX_VY_N(self, command):
        # Draw on the screen the sprite.
        # This instruction reads N bytes to adress of register I and
        # draw them in the screen which VX, VY coordinates.
        x = int(self.registers[int(command[3], 16)], 16)
        y = int(self.registers[int(command[4], 16)], 16)
        read_bytes = int(command[5], 16)
        sprite = self.memory[self.i: self.i + read_bytes]
        representation = ''
        px_was_clear = False
        for value in sprite:
            temp = bin(int(value, 16))
            temp = temp.replace('0b', '')
            representation += temp
            while len(representation) < 8:
                representation = '0' + representation
            for i in range(x, min(x + 8, self.width)):
                xor = int(self.field[i][y], 2) ^ int(representation[i - x], 2)
                previous_value = self.field[i][y]
                self.field[i][y] = str(xor)
                if not px_was_clear and previous_value == '1' and self.field[i][y] == '0b0':
                    self.registers[15] = '0x01'
                    px_was_clear = True
            y = min(y + 1, self.height)
            representation = ''
        if not px_was_clear:
            self.registers[15] = '0b00'
        self.print_field()
        self.pc += 2
        return

    def skp_VX(self, command):
        # Skip the next instruction, if key, which adress saves in register VX, push.
        self.pc += 2
        return

    def sknp_VX(self, command):
        # Skip the next instruction, if key, which adress saves in register VX, don't push.
        self.pc += 2
        return

    def ld_VX_DT(self, command):
        # Register VX takes the value of delay timer.
        register = int(command[3], 16)
        self.registers[register] = self.delay_timer
        self.pc += 2
        return

    def ld_VX_K(self, command):
        # Waiting for push a key. When key will be push, save it number in
        # register VX and move to next instruction.
        self.pc += 2
        return

    def ld_DT_VX(self, command):
        # Set the value of delay timer as the value of register VX
        self.delay_timer = self.registers[int(command[5], 16)]
        self.pc += 2
        return

    def ld_ST_VX(self, command):
        # Set the value of sound timer as the value of register VX
        self.sound_timer = self.registers[int(command[5], 16)]
        self.pc += 2
        return

    def add_I_VX(self, command):
        # Set the value of register I as the sum of values I and VX registers
        command_register_num = int(self.registers[int(command[3], 16)], 16)
        command_register_num += self.i
        if command_register_num > 255:
            self.registers[15] = hex(1)
            command_register_num -= 256
        else:
            self.registers[15] = hex(0)
        self.i = hex(command_register_num)
        self.pc += 2
        return

    def ld_F_VX(self, command):
        # Using for output on screen the symbols of standart font size of 4x5 pixels.
        # The command load in register I the adress of the sprite, the value which locate in VX.
        fonts_len = 5
        fonts_value = int(command[3], 16)
        fonts_adress = fonts_len * fonts_value
        self.i = hex(fonts_adress)
        self.pc += 2
        return

    def ld_B_VX(self, command):
        # Save the value of register VX in 2-10 presentation (BCD) in adress I, I+1, I+2
        num = str(int(self.registers[int(command[3], 16)], 16))
        bcd = []
        for digit in num:
            temp = bin(digit)
            temp.replace('0b', '')
            while len(temp) < 4:
                temp = '0' + temp
            bcd.append(temp)
        self.memory[self.i] = bcd[0]
        self.memory[self.i + 1] = bcd[1]
        self.memory[self.i + 2] = bcd[2]
        self.pc += 2
        return

    def ld_I_VX(self, command):
        # Save the values from V0 before VX registers in memory, started from I adress
        for x in range(len(self.registers)):
            self.memory[self.i + x] = self.registers[x]
        self.pc += 2
        return

    def ld_VX_I(self, command):
        # Load the values from V0 before VX registers from memory, started from I adress
        for x in range(16):
            self.registers[x] = self.memory[self.i + x]
        self.pc += 2
        return
