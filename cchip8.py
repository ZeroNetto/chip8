#!/usr/bin/env python3
import sys
import os
import pyaudio
import wave
import time
import threading
import argparse
from sys import platform
from pynput import keyboard
from modules.virtual_chip8 import Virtual_chip8

wf = wave.open(os.path.join('sound\\beep.wav'), 'rb')
pa = pyaudio.PyAudio()
stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                 channels=wf.getnchannels(),
                 rate=wf.getframerate(),
                 output=True)
data = wf.readframes(1024)
vc8 = Virtual_chip8()


def on_press(key):
    try:
        char = key.char
        if char in vc8.keys:
            vc8.pressed_keys[vc8.keys[char]] = True
    except:
        return
    return


def on_release(key):
    try:
        char = key.char
        if char in vc8.keys:
            vc8.pressed_keys[vc8.keys[char]] = False
    except:
        return
    return


def main():
    parser = create_parser()
    parsed_args = parser.parse_args(sys.argv[1:])
    start(parsed_args)
    return


def create_parser():
    parser = argparse.ArgumentParser(
        description='Console version of chip8\n\
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
    try:
        with open(os.path.join(parsed_args.path), 'rb') as file:
            load_memory(file)
    except:
        print('Not correct path {0}'.format(parsed_args.path))
        sys.exit()

    thread_execute = threading.Thread(target=execute,
                                      args=(parsed_args,))
    thread_timers = threading.Thread(target=tick_timers,
                                     args=(parsed_args,))
    listener = keyboard.Listener(on_press=on_press,
                                 on_release=on_release)

    listener.start()
    thread_timers.start()
    thread_execute.start()
    if (not parsed_args.debug and not parsed_args.memory and
            not parsed_args.registers):
        thread_print = threading.Thread(target=print_field)
        thread_print.start()
    return


def execute(parsed_args):
    wait_to_key_command = ('f', '0a')
    prev_pc = vc8.pc
    while vc8.pc < vc8.memory_limit and vc8.execution:
        command = get_command()
        have_pressed_key = False
        while ((command[2], command[4:]) == wait_to_key_command and
                not have_pressed_key):
            time.sleep(0.1)
            for key in vc8.pressed_keys:
                if vc8.pressed_keys[key]:
                    have_pressed_key = True
                    break
        tracing(parsed_args, command)
        vc8.compare_and_execute(command)
        if vc8.pc == prev_pc:
            print('GAME OVER!')
            time.sleep(2)
            vc8.execution = False
            sys.exit()
        else:
            prev_pc = vc8.pc
        if parsed_args.speed > 0:
            time.sleep(0.1 / parsed_args.speed)
    sys.exit()
    return


def load_memory(file):
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


def get_command():
    command = vc8.memory[vc8.pc] + vc8.memory[vc8.pc + 1]
    command = command.replace('0x', '')
    command = '0x' + command
    return command


def tracing(parsed_args, command):
    was_debug = False
    if parsed_args.debug:
        print("PC: {0}, I: {1}, delay: {2}, sound: {3} command: {4}"
              .format(vc8.pc, vc8.i, vc8.delay_timer, vc8.sound_timer,
                      command))
        was_debug = True
    if parsed_args.registers:
        print(vc8.registers)
        was_debug = True
    if parsed_args.memory:
        print(vc8.memory)
        was_debug = True
    if was_debug:
        print_debug_field()
    return


def tick_timers(parsed_args):
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


def print_field():
    while vc8.execution:
        try:
            os.system('cls')
        except:
            os.system('clear')
        for y in range(vc8.height):
            print(get_representation_of_line(y))
        time.sleep(2 / vc8.speed)
    sys.exit()
    return


def print_debug_field():
    print()
    for y in range(vc8.height):
        print(get_representation_of_line(y))
    return


def get_representation_of_line(y):
    representation = ''
    for x in range(vc8.width):
            representation += ' ' + vc8.field[x][y]
            representation = representation.replace('0', '.')
            representation = representation.replace('1', '#')
    return representation

if __name__ == "__main__":
    main()
