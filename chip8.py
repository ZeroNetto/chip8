#!/usr/bin/env python3
import sys
import pyaudio
import wave
import threading
import time
from modules.virtual_chip8 import Virtual_chip8
from PyQt5.QtWidgets import QApplication
from modules.gui import Gui

wf = wave.open('sound\\beep.wav', 'rb')
pa = pyaudio.PyAudio()
stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                 channels=wf.getnchannels(),
                 rate=wf.getframerate(),
                 output=True)
data = wf.readframes(1024)


def main():
    if len(sys.argv) < 2:
        print('There are no arguments for start\
                write at least the name of the game')
        sys.exit()
    name = sys.argv[1]
    debug, registers, memory, without_delay = parse_args(sys.argv)
    start(name, debug, registers, memory, without_delay)
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
            print('if you want debug then:\n\
                   print "d" for main info\n\
                   print "r" for registers info\n\
                   print "m" for memory info\n\
                   print "wd" for start without delay')
            sys.exit()
        else:
            print('There are no such key: {0}'.format(args[i].lower()))
            sys.exit()
    return (debug, registers, memory, without_delay)


def start(name, debug, registers, memory, without_delay):
    vc8 = Virtual_chip8()
    with open('games_for_chip8\{0}'.format(name), 'rb') as file:
        load_memory(file, vc8)
    app = QApplication(sys.argv)
    gui = Gui(vc8)

    thread_timers = threading.Thread(target=tick_timers,
                                     args=(vc8,))
    thread_execute = threading.Thread(target=execute,
                                      args=(vc8, debug, registers, memory,
                                            without_delay))

    thread_execute.start()
    thread_timers.start()
    sys.exit(app.exec_())
    return


def execute(vc8, debug, registers, memory, without_delay):
    wait_to_key_command = ('f', '0a')
    prev_pc = vc8.pc
    while vc8.pc < vc8.memory_limit and vc8.execution:
        command = get_command(vc8)
        tracing(vc8, debug, registers, memory, command)
        have_pressed_key = False
        while ((command[2], command[4:]) == wait_to_key_command and
                not have_pressed_key):
            time.sleep(0.1)
            for key in vc8.pressed_keys:
                if vc8.pressed_keys[key]:
                    have_pressed_key = True
                    break
        vc8.compare_and_execute(command)
        if vc8.pc == prev_pc:
            vc8.execution = False
            time.sleep(5)
            print('GAME OVER!')
            sys.exit()
        else:
            prev_pc = vc8.pc
        if not without_delay or command[2] == 'd':
            time.sleep(0.01 / vc8.speed)
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


def tracing(vc8, debug, registers, memory, command):
    if debug:
        print("PC: {0}, I: {1}, delay: {2}, sound: {3} command: {4}"
              .format(vc8.pc, vc8.i, vc8.delay_timer, vc8.sound_timer,
                      command))
    if registers:
        print(vc8.registers)
    if memory:
        print(vc8.memory)
    return


def tick_timers(vc8):
    while vc8.execution:
        if vc8.sound_timer > 0:
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
