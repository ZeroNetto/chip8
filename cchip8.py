#!/usr/bin/env python3
import sys
import winsound
import os
import time
import threading
from pynput import keyboard
from modules.virtual_chip8 import Virtual_chip8

vc8 = Virtual_chip8()


def on_press(key):
    if key.char in vc8.keys:
        vc8.pressed_key = key.char
    return


def main():
    if len(sys.argv) < 2:
        print('There are no arguments for start\
                write at least the name of the game')
        sys.exit()
    name = sys.argv[1]
    debug, registers, memory = parse_args(sys.argv)
    start(name, debug, registers, memory)
    return


def parse_args(args):
    debug = False
    registers = False
    memory = False
    for i in range(2, len(args)):
        if args[i].lower() == 'd':
            debug = True
        elif args[i].lower() == 'r':
            registers = True
        elif args[i].lower() == 'm':
            memory = True
        elif args[i].lower() == 'h':
            print('if you want debug then:\
                   print "d" for main info\
                   print "r" for registers info\
                   print "m" for memory info')
            sys.exit()
        else:
            print('There are no such key: {0}'.format(args[i].lower()))
            sys.exit()
    return (debug, registers, memory)


def start(name, debug, registers, memory):
    with open('{0}'.format(name), 'rb') as file:
        load_memory(file)

    thread_execute = threading.Thread(target=execute,
                                      args=(debug, registers, memory))
    thread_timers = threading.Thread(target=tick_timers)
    listener = keyboard.Listener(on_press=on_press)

    listener.start()
    thread_execute.start()
    if not debug and not memory and not registers:
        thread_print = threading.Thread(target=print_field)
        thread_print.start()
    return


def execute(debug, registers, memory):
    wait_to_key_command = ('0xf', '0a')
    drw_command = 'd'
    prev_pc = vc8.pc
    while vc8.pc < vc8.memory_limit and vc8.execution:
        command = get_command()
        key_command = (command[:3], command[4:])
        while (key_command == wait_to_key_command and
                vc8.pressed_key not in vc8.keys):
            time.sleep(1)
        tracing(debug, registers, memory, command)
        vc8.compare_and_execute(command)
        if vc8.pc == prev_pc:
            vc8.execution = False
            time.sleep(2)
            print('GAME OVER!')
            sys.exit()
        else:
            prev_pc = vc8.pc
        #if command[2] == drw_command:
        time.sleep(0.1 / vc8.speed)
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
            winsound.Beep(1000, 100)
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
        time.sleep(1 / vc8.speed)
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
