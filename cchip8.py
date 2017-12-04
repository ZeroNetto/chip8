#!/usr/bin/env python3
import sys
import os
import pyaudio
import wave
import time
import threading
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
    if len(sys.argv) < 2:
        print('There are no arguments for start\
                write at least the path to the game')
        sys.exit()
    path = sys.argv[1]
    debug, registers, memory, without_delay = parse_args(sys.argv)
    start(path, debug, registers, memory, without_delay)
    return


def parse_args(args):
    debug = False
    registers = False
    memory = False
    without_delay = False
    for i in range(2, len(args)):
        if args[i].lower() == 'd':
            debug = True
        elif args[i].lower() == 'r':
            registers = True
        elif args[i].lower() == 'm':
            memory = True
        elif args[i].lower() == 'wd':
            without_delay = True
        elif args[i].lower() == 'h' or args[i].lower() == '--h':
            print('For start you should enter the path to the of game\n\
                   if you want debug then:\n\
                   print "d" for main info\n\
                   print "r" for registers info\n\
                   print "m" for memory info\n\
                   print "wd" for start without delay')
            sys.exit()
        else:
            print('There are no such key: {0}'.format(args[i].lower()))
            sys.exit()
    return (debug, registers, memory, without_delay)


def start(path, debug, registers, memory, without_delay):
    with open(os.path.join(path), 'rb') as file:
        load_memory(file)

    thread_execute = threading.Thread(target=execute,
                                      args=(debug, registers, memory,
                                            without_delay))
    thread_timers = threading.Thread(target=tick_timers)
    listener = keyboard.Listener(on_press=on_press,
                                 on_release=on_release)

    listener.start()
    thread_timers.start()
    thread_execute.start()
    if not debug and not memory and not registers:
        thread_print = threading.Thread(target=print_field)
        thread_print.start()
    return


def execute(debug, registers, memory, without_delay):
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
        tracing(debug, registers, memory, command)
        vc8.compare_and_execute(command)
        if vc8.pc == prev_pc:
            print('GAME OVER!')
            time.sleep(2)
            vc8.execution = False
            sys.exit()
        else:
            prev_pc = vc8.pc
        if not without_delay:
            time.sleep(0.01 / vc8.speed)
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


def tracing(debug, registers, memory, command):
    if debug:
        print("PC: {0}, I: {1}, delay: {2}, sound: {3} command: {4}"
              .format(vc8.pc, vc8.i, vc8.delay_timer, vc8.sound_timer,
                      command))
    if registers:
        print(vc8.registers)
    if memory:
        print(vc8.memory)
    if debug or memory or registers:
        print_debug_field()
    return


def tick_timers():
    while vc8.execution:
        if vc8.sound_timer > 0:
            stream.write(data)
            vc8.sound_timer -= 1
        if vc8.delay_timer > 0:
            vc8.delay_timer -= 1
        time.sleep(1 / vc8.speed)
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
