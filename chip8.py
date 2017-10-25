import sys
from modules import virtual_chip8


def main():
    name = sys.argv()
    file = open(name, 'rb')
    vc8 = virtual_chip8()
    vc8.start(file)


if __name__ == "__main__":
    main()
