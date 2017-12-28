#!/usr/bin/env python3
import sys
import time
import random
import threading
lock = threading.Lock()


class Virtual_chip8:
    def __init__(self):
        # First 512 bytes - reserved by chip8, so first command location is 512
        self.execution = True
        self.speed = 60
        self.field = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.registers = []
        self.i = 0
        self.memory = []
        self.pc = 512
        self.height = 32
        self.width = 64
        self.shift = 512
        self.memory_limit = 4096
        self.stack = []
        self.basic_commands = {'0x00e0': self.clean_screen,
                               '0x00ee': self.ret}
        self.first_num_commands = {'0x1': self.jp_NNN,
                                   '0x2': self.call_NNN,
                                   '0x3': self.se_VX_KK,
                                   '0x4': self.sne_VX_KK,
                                   '0x6': self.ld_VX_KK,
                                   '0x7': self.add_VX_KK,
                                   '0xa': self.ld_I_NNN,
                                   '0xb': self.jp_V0_NNN,
                                   '0xc': self.rnd_VX_KK,
                                   '0xd': self.drw_VX_VY_N}
        self.first_last_num_commands = {('0x5', '0'): self.se_VX_VY,
                                        ('0x8', '0'): self.ld_VX_VY,
                                        ('0x8', '1'): self.or_VX_VY,
                                        ('0x8', '2'): self.and_VX_VY,
                                        ('0x8', '3'): self.xor_VX_VY,
                                        ('0x8', '4'): self.add_VX_VY,
                                        ('0x8', '5'): self.sub_VX_VY,
                                        ('0x8', '6'): self.shr_VX,
                                        ('0x8', '7'): self.subn_VX_VY,
                                        ('0x8', 'e'): self.shl_VX,
                                        ('0x9', '0'): self.sne_VX_VY}
        self.except_one_num_commands = {('0xe', '9e'): self.skp_VX,
                                        ('0xe', 'a1'): self.sknp_VX,
                                        ('0xf', '07'): self.ld_VX_DT,
                                        ('0xf', '0a'): self.ld_VX_K,
                                        ('0xf', '15'): self.ld_DT_VX,
                                        ('0xf', '18'): self.ld_ST_VX,
                                        ('0xf', '1e'): self.add_I_VX,
                                        ('0xf', '29'): self.ld_F_VX,
                                        ('0xf', '33'): self.ld_B_VX,
                                        ('0xf', '55'): self.ld_I_VX,
                                        ('0xf', '65'): self.ld_VX_I}
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
        self.keys = {'x': '0x00', 'ч': '0x00',
                     '1': '0x01',
                     '2': '0x02',
                     '3': '0x03',
                     'q': '0x04', 'й': '0x04',
                     'w': '0x05', 'ц': '0x05',
                     'e': '0x06', 'у': '0x06',
                     'a': '0x07', 'ф': '0x07',
                     's': '0x08', 'ы': '0x08',
                     'd': '0x09', 'в': '0x09',
                     'z': '0x0a', 'я': '0x0a',
                     'c': '0x0b', 'с': '0x0b',
                     '4': '0x0c',
                     'r': '0x0d', 'к': '0x0d',
                     'f': '0x0e', 'а': '0x0e',
                     'v': '0x0f', 'м': '0x0f'}
        self.pressed_keys = {'0x00': False,
                             '0x01': False,
                             '0x02': False,
                             '0x03': False,
                             '0x04': False,
                             '0x05': False,
                             '0x06': False,
                             '0x07': False,
                             '0x08': False,
                             '0x09': False,
                             '0x0a': False,
                             '0x0b': False,
                             '0x0c': False,
                             '0x0d': False,
                             '0x0e': False,
                             '0x0f': False}
        self._init_memory()
        self._init_registers()
        self._init_field_()

    def _init_registers(self):
        for x in range(16):
            self.registers.append('0x00')

    def _init_memory(self):
        for x in range(4096):
            if x < 80:
                self.memory.append(self.fonts[x])
            else:
                self.memory.append('0x00')

    def _init_field_(self):
        self.field = []
        for x in range(self.width):
            self.field.append([])
            for y in range(self.height):
                self.field[x].append([])
                self.field[x][y] = '0'

    def compare_and_execute(self, command):
        if command in self.basic_commands.keys():
            self.basic_commands[command](command)
        elif (command[:3], command[4:]) in self.except_one_num_commands.keys():
            self.except_one_num_commands[command[:3], command[4:]](command)
        elif (command[:3], command[5]) in self.first_last_num_commands.keys():
            self.first_last_num_commands[(command[:3], command[5])](command)
        elif command[:3] in self.first_num_commands.keys():
            self.first_num_commands[command[:3]](command)
        else:
            print("There are no such command {0}!".format(command))
        return

    def clean_screen(self, command):
        # clean screen
        self._init_field_()
        self.pc += 2
        return

    def ret(self, command):
        # return
        self.pc = self.stack.pop()
        return

    def jp_NNN(self, command):
        # jump
        self.pc = int(command[3:], 16)
        return

    def call_NNN(self, command):
        # call programm from adress
        self.stack.append(self.pc + 2)
        self.pc = int(command[3:], 16)
        return

    def se_VX_KK(self, command):
        # skip instruction if VX==KK
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
        self.registers[int(command[3], 16)] = '0x' + (command[4:])
        self.pc += 2
        return

    def add_VX_KK(self, command):
        # load in VX register the sum of VX and KK
        reg = int(command[3], 16)
        reg_num = int(self.registers[reg], 16)
        num = int(command[4:], 16)
        sum_res = reg_num + num
        if sum_res > 255:
            sum_res -= 256
        hex_res = hex(sum_res)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[reg] = hex_res
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
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        first_num = int(self.registers[first_reg], 16)
        second_num = int(self.registers[second_reg], 16)
        bin_or = first_num | second_num
        hex_res = hex(bin_or)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[first_reg] = hex_res
        self.pc += 2
        return

    def and_VX_VY(self, command):
        # boolean "and" between VX and VY
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        first_num = int(self.registers[first_reg], 16)
        second_num = int(self.registers[second_reg], 16)
        bin_and = first_num & second_num
        hex_res = hex(bin_and)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[first_reg] = hex_res
        self.pc += 2
        return

    def xor_VX_VY(self, command):
        # boolean "not or" between VX and VY
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        first_num = int(self.registers[first_reg], 16)
        second_num = int(self.registers[second_reg], 16)
        bin_xor = first_num ^ second_num
        hex_res = hex(bin_xor)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[first_reg] = hex_res
        self.pc += 2
        return

    def add_VX_VY(self, command):
        # VX summing with VY. If result > 255, then VF = 1, else 0.
        # Only smallers 8 bits are saving in VX
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        first_num = int(self.registers[first_reg], 16)
        second_num = int(self.registers[second_reg], 16)
        sum_res = first_num + second_num
        if sum_res > 255:
            self.registers[15] = '0x01'
            sum_res -= 256
        else:
            self.registers[15] = '0x00'
        hex_res = hex(sum_res)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[first_reg] = hex_res
        self.pc += 2
        return

    def sub_VX_VY(self, command):
        # VY decrease from VX and the result save in VX.
        # If VX >= VY, then VF = 1, else 0
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        first_num = int(self.registers[first_reg], 16)
        second_num = int(self.registers[second_reg], 16)
        sub_res = first_num - second_num
        if sub_res >= 0:
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
            sub_res = -sub_res
        hex_res = hex(sub_res)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[first_reg] = hex_res
        self.pc += 2
        return

    def shr_VX(self, command):
        # The operation of shift to right on 1 bit. Shifted register VX.
        # If smaller bit(very right) of register VX=1, then VF=1, else VF=0
        reg = int(command[3], 16)
        num = bin(int(self.registers[reg], 16))
        if num[len(num) - 1] == '1':
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
        num = int(num, 2) >> 1
        hex_res = hex(num)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[reg] = hex_res
        self.pc += 2
        return

    def subn_VX_VY(self, command):
        # If VY >= VX, then VF = 1, else 0.
        # Then VX is decrease from VY and the result save in VY
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        first_num = int(self.registers[first_reg], 16)
        second_num = int(self.registers[second_reg], 16)
        subn_res = second_num - first_num
        if subn_res >= 0:
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
            subn_res = -subn_res
        hex_res = hex(subn_res)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[first_reg] = hex_res
        self.pc += 2
        return

    def shl_VX(self, command):
        # The operation of shift to left on 1 bit. Shifed register VX.
        # If biggest bit(very left) of register VX=1, then VF=1, else VF=0
        reg = int(command[3], 16)
        num = bin(int(self.registers[reg], 16))
        num = num.replace('0b', '')
        while len(num) < 8:
            num = '0' + num
        if num[0] == '1':
            self.registers[15] = '0x01'
        else:
            self.registers[15] = '0x00'
        num = int(num, 2) << 1
        if num > 255:
            num -= 256
        hex_res = hex(num)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[reg] = hex_res
        self.pc += 2
        return

    def sne_VX_VY(self, command):
        # Skip the next instruction if VX != VY
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        if self.registers[first_reg] != self.registers[second_reg]:
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
        rnd = random.randint(0, 255) & num
        hex_res = hex(rnd)
        if len(hex_res) < 4:
            hex_res = '0x0' + hex_res[len(hex_res) - 1]
        self.registers[reg] = hex_res
        self.pc += 2
        return

    def drw_VX_VY_N(self, command):
        # Draw on the screen the sprite.
        # This instruction reads N bytes to adress of register I and
        # draw them in the screen which VX, VY coordinates.
        read_bytes = int(command[5], 16)
        if read_bytes == 0:
            read_bytes = 16
        x = int(self.registers[int(command[3], 16)], 16)
        y = int(self.registers[int(command[4], 16)], 16)
        sprite = self.memory[self.i: self.i + read_bytes]
        representation = ''
        px_was_clear = False
        for value in sprite:
            temp = bin(int(value, 16))
            temp = temp.replace('0b', '')
            representation = temp
            while len(representation) < 8:
                representation = '0' + representation
            for i in range(x, x + 8):
                previous_value = self.field[i % self.width][y % self.height]
                xor = (int(self.field[i % self.width][y % self.height], 2) ^
                       int(representation[i - x], 2))
                self.field[i % self.width][y % self.height] = str(xor)
                if (not px_was_clear and previous_value == '1' and
                        self.field[i % self.width][y % self.height] == '0'):
                    self.registers[15] = '0x01'
                    px_was_clear = True
            y += 1
        if not px_was_clear:
            self.registers[15] = '0x00'
        self.pc += 2
        return

    def se_VX_VY(self, command):
        # Skip the next instruction, if VX == VY
        first_reg = int(command[3], 16)
        second_reg = int(command[4], 16)
        if self.registers[first_reg] == self.registers[second_reg]:
            self.pc += 4
        else:
            self.pc += 2
        return

    def skp_VX(self, command):
        # Skip the next instruction, if key,
        # which adress saves in register VX is push.
        reg_num = self.registers[int(command[3], 16)]
        if self.pressed_keys[reg_num]:
            self.pc += 4
        else:
            self.pc += 2
        return

    def sknp_VX(self, command):
        # Skip the next instruction, if key,
        # which adress saves in register VX isn't push.
        reg_num = self.registers[int(command[3], 16)]
        if not self.pressed_keys[reg_num]:
            self.pc += 4
        else:
            self.pc += 2
        return

    def ld_VX_DT(self, command):
        # Register VX takes the value of delay timer.
        register = int(command[3], 16)
        temp = hex(self.delay_timer)
        if len(temp) < 4:
            temp = '0x0' + temp[len(temp) - 1]
        self.registers[register] = temp
        self.pc += 2
        return

    def ld_VX_K(self, command):
        # Waiting for push a key. When key will be push, save it number in
        # register VX and move to next instruction.
        reg = int(command[3], 16)
        for key in self.pressed_keys:
            if self.pressed_keys[key]:
                    self.registers[reg] = key
                    self.pc += 2
                    return
        return

    def ld_DT_VX(self, command):
        # Set the value of delay timer as the value of register VX
        self.delay_timer = int(self.registers[int(command[3], 16)], 16)
        self.pc += 2
        return

    def ld_ST_VX(self, command):
        # Set the value of sound timer as the value of register VX
        self.sound_timer = int(self.registers[int(command[3], 16)], 16)
        self.pc += 2
        return

    def add_I_VX(self, command):
        # Set the value of register I as the sum of values I and VX registers
        command_register_num = int(self.registers[int(command[3], 16)], 16)
        self.i += command_register_num
        self.pc += 2
        return

    def ld_F_VX(self, command):
        # Using for output on screen the symbols
        #   of standart font size of 8x5 pixels.
        # The command load in register I the adress of the sprite,
        #   the value which locate in VX.
        fonts_len = 5
        fonts_value = int(self.registers[int(command[3], 16)], 16)
        fonts_adress = fonts_len * fonts_value
        self.i = fonts_adress
        self.pc += 2
        return

    def ld_B_VX(self, command):
        # Save the value of register VX in 2-10 presentation (BCD)
        #   in addresses I (hundreds), I+1(tens), I+2(ones)
        num = str(int(self.registers[int(command[3], 16)], 16))
        while len(num) < 3:
            num = '0' + num
        for digit_id in range(len(num)):
            temp = '0x0' + num[digit_id]
            self.memory[self.i + digit_id] = temp
        self.pc += 2
        return

    def ld_I_VX(self, command):
        # Save the values from V0 to VX registers in memory,
        #   starting from I adress
        x = 0
        num = int(command[3], 16)
        while x <= num:
            self.memory[self.i + x] = self.registers[x]
            x += 1
        self.pc += 2
        return

    def ld_VX_I(self, command):
        # Load the values from V0 to VX registers from memory,
        #   starting from I adress
        x = 0
        num = int(command[3], 16)
        while x <= num:
            self.registers[x] = self.memory[self.i + x]
            x += 1
        self.pc += 2
        return
