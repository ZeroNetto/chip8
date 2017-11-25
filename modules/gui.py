#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PyQt5 import QtCore
from modules import virtual_chip8


class Gui(QWidget):
    def __init__(self, virtual_chip8):
        super().__init__()
        self.vc8 = virtual_chip8
        self.sell_size = 20
        self.resize(self.sell_size * self.vc8.width,
                    self.sell_size * self.vc8.height)
        self.field = self._init_field()
        self.setLayout(self.field)
        self.setFixedSize(self.sell_size * self.vc8.width,
                          self.sell_size * self.vc8.height)
        self.show()

    def _init_field(self):
        field = QGridLayout()
        field.setContentsMargins(0, 0, 0, 0)
        field.setSpacing(0)
        for x in range(self.vc8.width):
            for y in range(self.vc8.height):
                cell = QLabel()
                cell.setStyleSheet('background-color: black')
                field.addWidget(cell, y, x)
        return field

    def print_field(self):
        """Graphic on screen"""
        for x in range(self.vc8.width):
            for y in range(self.vc8.height):
                sheet = 'background-color: green'
                if self.vc8.field[x][y] == '0':
                    sheet = 'background-color: black'
                cell = self.field.itemAtPosition(y, x).widget()
                if cell.styleSheet() != sheet:
                    cell.setStyleSheet(sheet)
        return

    def keyPressEvent(self, e):
        try:
            self.vc8.pressed_key = chr(e.key()).lower()
        except:
            return
        return
