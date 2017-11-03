import sys
from modules import virtual_chip8


def main():
    name = sys.argv[1]
    with open('{0}'.format(name), 'rb') as file:
        vc8 = virtual_chip8.Virtual_chip8()
        vc8.start(file)
    return


if __name__ == "__main__":
    main()
