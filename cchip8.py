#!/usr/bin/env python3
import sys
import winsound
import os
import time
import threading
from pynput import keyboard
from modules.virtual_chip8 import Virtual_chip8

wait_to_key_command = ('f', '0a')
vc8 = Virtual_chip8()
threads = []


def on_press(key):
    key = str(key)
    vc8.pressed_key = key


def main():
    if len(sys.argv) < 2:
        print('There are no arguments for start\
                write at least the name of the game')
        sys.exit()
    name = sys.argv[1]
    debug, registers, memory = parse_args(sys.argv)
    with open('{0}'.format(name), 'rb') as file:
        start(file, debug, registers, memory)
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
            print('There are no such command: {0}'.format(args[i].lower()))
            sys.exit()
    return (debug, registers, memory)


def start(file, debug, registers, memory):
    load_memory(file)

    thread_execute = threading.Thread(target=execute,
                                      args=(debug, registers, memory))
    thread_print = threading.Thread(target=print_field)
    listener = keyboard.Listener(on_press=on_press)

    thread_execute.start()
    thread_print.start()
    listener.start()

    threads.append(thread_execute)
    threads.append(thread_print)
    threads.append(listener)
    return


def execute(debug, registers, memory):
    prev_pc = vc8.pc
    while vc8.pc < vc8.memory_limit:
        command = get_command()
        key_command = (command[0], command[2:])
        while (key_command == wait_to_key_command and
                vc8.pressed_key not in vc8.keys):
            time.sleep(1)
        treat_tick(debug, registers, memory, command)
        vc8.compare_and_execute(command)
        if vc8.pc == prev_pc:
            time.sleep(2)
            print('GAME OVER!')
            for thread in threads:
                sys.exit(thread)
        else:
            prev_pc = vc8.pc
        time.sleep(1 / vc8.speed)
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


def treat_tick(debug, registers, memory, command):
    if vc8.sound_timer > 0:
        winsound.Beep(1000, 100)
        vc8.sound_timer -= 1
    if vc8.delay_timer > 0:
        vc8.delay_timer -= 1
    if debug:
        print("PC: {0}, I: {1}, delay: {2}, sound: {3} command: {4}"\
              .format(vc8.pc, vc8.i, vc8.delay_timer, vc8.sound_timer,
                      command))
    if registers:
        print(vc8.registers)
    if memory:
        print(vc8.memory)
    return


def print_field():
    try:
        os.system('cls')
    except:
        os.system('clear')
    representation = ''
    for y in range(vc8.height):
        for x in range(vc8.width):
            representation += ' ' + vc8.field[x][y]
            representation = representation.replace('0b', '')
            representation = representation.replace('0', '.')
            representation = representation.replace('1', '#')
        print(representation)
        representation = ''
    return

if __name__ == "__main__":
    main()
