#!/usr/bin/env python3
import sys
import os
import unittest
import pytest

from modules import virtual_chip8


class Test_commands(unittest.TestCase):
    def test_no_such_command(self):
        command = '0x0000'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 512)

    def test_clean_screen(self):
        command = '0x00e0'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.field[0][0] == '1'
        vc8.compare_and_execute(command)
        if vc8.field[0][0] == '0':
            self.assertTrue(True)
            self.assertEqual(vc8.pc, 514)
        else:
            self.assertFalse(True)

    def test_ret(self):
        command = '0x00ee'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.stack.append(5)
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 5)

    def test_jp_NNN(self):
        command = '0x1111'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, int('111', 16))

    def test_call_NNN(self):
        command = '0x2111'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, int('111', 16))
        self.assertEqual(vc8.stack.pop(), 514)

    def test_se_VX_KK(self):
        command = '0x3100'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 516)

    def test_se_VX_KK_not_equals(self):
        command = '0x3101'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)

    def test_sne_VX_KK(self):
        command = '0x4100'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)

    def test_sne_VX_KK_not_equals(self):
        command = '0x4101'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 516)

    def test_ld_VX_KK(self):
        command = '0x6110'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], '0x10')

    def test_add_VX_KK(self):
        command = '0x7150'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x50'
        res = hex(2 * int('0x50', 16))
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], res)

    def test_add_VX_KK_more_then_255(self):
        command = '0x7150'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0xff'
        res = hex(int('0xff', 16) + int('0x50', 16) - 256)
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], res)

    def test_ld_I_NNN(self):
        command = '0xa150'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.i, int('0x150', 16))

    def test_jp_V0_NNN(self):
        command = '0xb150'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[0] = '0x15'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, int('0x15', 16) + int('150', 16))

    def test_drw_VX_VY_N(self):
        command = '0xd001'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.i = 514
        vc8.memory[514] = '0x01'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.field[7][0], '1')
        self.assertEqual(vc8.registers[15], '0x00')

    def test_drw_VX_VY_N_with_overflow(self):
        command = '0xd001'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.i = 514
        vc8.memory[514] = '0x01'
        vc8.field[7][0] = '1'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.field[7][0], '0')
        self.assertEqual(vc8.registers[15], '0x01')

    def test_se_VX_VY(self):
        command = '0x5000'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 516)

    def test_se_VX_VY_not_equals(self):
        command = '0x5010'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x01'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)

    def test_sne_VX_VY(self):
        command = '0x9000'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)

    def test_sne_VX_VY_not_equals(self):
        command = '0x9010'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x01'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 516)

    def test_ld_VX_VY(self):
        command = '0x8120'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[2] = '0x15'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], vc8.registers[2])

    def test_or_VX_VY(self):
        command = '0x8121'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x10'
        vc8.registers[2] = '0x15'
        exp_result = '0x15'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], exp_result)

    def test_and_VX_VY(self):
        command = '0x8122'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x10'
        vc8.registers[2] = '0x15'
        exp_result = '0x10'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], exp_result)

    def test_xor_VX_VY(self):
        command = '0x8123'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x10'
        vc8.registers[2] = '0x15'
        exp_result = '0x05'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)
        self.assertEqual(vc8.registers[1], exp_result)

    def test_add_VX_VY(self):
        command = '0x8124'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x10'
        vc8.registers[2] = '0x15'
        exp_result = '0x25'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x00')
        self.assertEqual(vc8.pc, 514)

    def test_add_VX_VY_more_then_255(self):
        command = '0x8124'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0xff'
        vc8.registers[2] = '0xff'
        exp_result = '0xfe'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x01')
        self.assertEqual(vc8.pc, 514)

    def test_sub_VX_VY(self):
        command = '0x8125'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x15'
        vc8.registers[2] = '0x10'
        exp_result = '0x05'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x01')
        self.assertEqual(vc8.pc, 514)

    def test_sub_VX_VY_less_then_0(self):
        command = '0x8125'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x15'
        vc8.registers[2] = '0xff'
        exp_result = '0xea'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x00')
        self.assertEqual(vc8.pc, 514)

    def test_shr_VX(self):
        command = '0x8126'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0xfe'
        exp_result = '0x7f'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x00')
        self.assertEqual(vc8.pc, 514)

    def test_shr_VX_with_overflow(self):
        command = '0x8126'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0xff'
        exp_result = '0x7f'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x01')
        self.assertEqual(vc8.pc, 514)

    def test_subn_VX_VY(self):
        command = '0x8127'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x10'
        vc8.registers[2] = '0x15'
        exp_result = '0x05'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x01')
        self.assertEqual(vc8.pc, 514)

    def test_subn_VX_VY_less_then_0(self):
        command = '0x8127'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0xff'
        vc8.registers[2] = '0x15'
        exp_result = '0xea'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x00')
        self.assertEqual(vc8.pc, 514)

    def test_shl_VX(self):
        command = '0x812e'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x1f'
        exp_result = '0x3e'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x00')
        self.assertEqual(vc8.pc, 514)

    def test_shl_VX_with_overflow(self):
        command = '0x812e'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0xfe'
        exp_result = '0xfc'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.registers[15], '0x01')
        self.assertEqual(vc8.pc, 514)

    def test_skp_VX(self):
        command = '0xe19e'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x0e'
        vc8.pressed_keys['0x0e'] = True
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 516)

    def test_skp_VX_not_pressed(self):
        command = '0xe19e'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x0e'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)

    def test_sknp_VX(self):
        command = '0xe1a1'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x0e'
        vc8.pressed_keys['0x0e'] = True
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 514)

    def test_sknp_VX_not_pressed(self):
        command = '0xe1a1'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x0e'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.pc, 516)

    def test_ld_VX_DT(self):
        command = '0xf107'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.delay_timer = 60
        exp_result = '0x3c'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.pc, 514)

    def test_ld_VX_K(self):
        command = '0xf10a'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.pressed_keys['0x0f'] = True
        exp_result = '0x0f'
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[1], exp_result)
        self.assertEqual(vc8.pc, 514)

    def test_ld_DT_VX(self):
        command = '0xf115'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x15'
        exp_result = 21
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.delay_timer, exp_result)
        self.assertEqual(vc8.pc, 514)

    def test_ld_ST_VX(self):
        command = '0xf118'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x15'
        exp_result = 21
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.sound_timer, exp_result)
        self.assertEqual(vc8.pc, 514)

    def test_add_I_VX(self):
        command = '0xf11e'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x15'
        vc8.i = 1
        exp_result = 22
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.i, exp_result)
        self.assertEqual(vc8.pc, 514)

    def test_ld_F_VX(self):
        command = '0xf129'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x0f'
        exp_result = 5 * int('f', 16)
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.i, exp_result)
        self.assertEqual(vc8.pc, 514)

    def test_ld_B_VX(self):
        command = '0xf133'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[1] = '0x15'
        vc8.i = 516
        exp_result = ('0x02', '0x01')
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.memory[vc8.i], '0x00')
        self.assertEqual(vc8.memory[vc8.i + 1], exp_result[0])
        self.assertEqual(vc8.memory[vc8.i + 2], exp_result[1])
        self.assertEqual(vc8.pc, 514)

    def test_ld_I_VX(self):
        command = '0xf255'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.memory[516] = '0x02'
        vc8.memory[517] = '0x01'
        vc8.i = 516
        exp_result = ('0x02', '0x01')
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[0], vc8.memory[516])
        self.assertEqual(vc8.registers[1], vc8.memory[517])
        self.assertEqual(vc8.pc, 514)

    def test_ld_VX_I(self):
        command = '0xf265'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.registers[0] = '0x02'
        vc8.registers[1] = '0x01'
        vc8.i = 516
        exp_result = ('0x02', '0x01')
        vc8.compare_and_execute(command)
        self.assertEqual(vc8.registers[0], vc8.memory[516])
        self.assertEqual(vc8.registers[1], vc8.memory[517])
        self.assertEqual(vc8.pc, 514)

    def test_rnd_VX_KK(self):
        command = '0xc10f'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertTrue(int(vc8.registers[1], 16) >= 0)
        self.assertTrue(int(vc8.registers[1], 16) < 16)

    def test_rnd_VX_KK__zero(self):
        command = '0xc100'
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.compare_and_execute(command)
        self.assertEquals(int(vc8.registers[1], 16), 0)

if __name__ == '__main__':
    unittest.main()
