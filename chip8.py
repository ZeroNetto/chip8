#!/usr/bin/env python3
import sys
import os
import pyaudio
import wave
import threading
import time
import argparse
from modules.virtual_chip8 import Virtual_chip8
from PyQt5.QtWidgets import QApplication
from modules.gui import Gui


wf = wave.open(os.path.join('.\\sound\\beep.wav'), 'rb')
pa = pyaudio.PyAudio()
stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                 channels=wf.getnchannels(),
                 rate=wf.getframerate(),
                 output=True)
data = wf.readframes(1024)


def main():
    parser = create_parser()
    parsed_args = parser.parse_args(sys.argv[1:])
    start(parsed_args)
    return


def create_parser():
    parser = argparse.ArgumentParser(
        description='Graphic version of chip8\n\
                     The list of keys:\n\
                     \r-d\n\
                     \r-r\n\
                     \r-m\n\
                     \r-s\n\
                     \r-ws')
    parser.add_argument('path', type=str,
                        help='path to file')
    parser.add_argument('-d', '--debug',
                        help='print command and counters info',
                        action='store_true')
    parser.add_argument('-r', '--registers',
                        help='print registers info',
                        action='store_true')
    parser.add_argument('-m', '--memory',
                        help='print memory info',
                        action='store_true')
    parser.add_argument('-s', '--speed',
                        type=int,
                        help='change speed of execution in Hz:\
                              if value = 0 - without delay\
                              default = 60Hz',
                        default=60)
    parser.add_argument('-ws', '--without_sound',
                        help='off the sound in games',
                        action='store_true')
    return parser


def start(parsed_args):
    vc8 = Virtual_chip8()
    try:
        with open(os.path.join(parsed_args.path), 'rb') as file:
            load_memory(file, vc8)
    except:
        print('Not correct path {0}'.format(parsed_args.path))
        sys.exit()
    app = QApplication(sys.argv)
    gui = Gui(vc8)

    thread_timers = threading.Thread(target=tick_timers,
                                     args=(vc8, parsed_args))
    thread_execute = threading.Thread(target=execute,
                                      args=(vc8, parsed_args))

    thread_execute.start()
    thread_timers.start()
    sys.exit(app.exec_())
    return


def execute(vc8, parsed_args):
    wait_to_key_command = ('f', '0a')
    prev_pc = vc8.pc
    while vc8.pc < vc8.memory_limit and vc8.execution:
        command = get_command(vc8)
        tracing(vc8, command, parsed_args)
        have_pressed_key = False
        while ((command[2], command[4:]) == wait_to_key_command and
                not have_pressed_key):
            time.sleep(1 / vc8.speed)
            for key in vc8.pressed_keys:
                if vc8.pressed_keys[key]:
                    have_pressed_key = True
                    break
        vc8.compare_and_execute(command)
        if vc8.pc == prev_pc:
            print('GAME OVER!')
            time.sleep(5)
            vc8.execution = False
            sys.exit()
        else:
            prev_pc = vc8.pc
        if parsed_args.speed > 0:
            time.sleep(1 / parsed_args.speed)
    sys.exit()
    return


def load_memory(file, vc8):
    counter = 0
    temp_num = ''
    for line in file.readlines():
        for num in line:
            temp_num = hex(num)
            if len(temp_num) < 4:
                temp_num = '0x0' + temp_num[2]
            vc8.memory[counter + vc8.shift] = temp_num
            counter += 1
    return


def get_command(vc8):
    command = vc8.memory[vc8.pc] + vc8.memory[vc8.pc + 1]
    command = command.replace('0x', '')
    command = '0x' + command
    return command


def tracing(vc8, command, parsed_args):
    if parsed_args.debug:
        print("PC: {0}, I: {1}, delay: {2}, sound: {3} command: {4}"
              .format(vc8.pc, vc8.i, vc8.delay_timer, vc8.sound_timer,
                      command))
    if parsed_args.registers:
        print(vc8.registers)
    if parsed_args.memory:
        print(vc8.memory)
    return


def tick_timers(vc8, parsed_args):
    while vc8.execution:
        if vc8.sound_timer > 0:
            if not parsed_args.without_sound:
                stream.write(data)
            vc8.sound_timer -= 1
        if vc8.delay_timer > 0:
            vc8.delay_timer -= 1
        time.sleep(1 / vc8.speed)
    stream.stop_stream()
    stream.close()
    pa.terminate()
    sys.exit()
    return


if __name__ == "__main__":
    main()
