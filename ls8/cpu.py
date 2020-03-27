"""CPU functionality."""

import sys


ADD = 0b10100000  # Add registry addresses together
# AND = 0b10101000
CALL = 0b1010000  # Jump to subroutine's address
CMP = 0b10100111
DEC = 0b01100110  # Decrement register
# DIV = 0b10100011
HLT = 0b00000001  # Halt the program
INC = 0b01100101  # Increment register
# INT = 0b01010010
# IRET = 0b00010011
JEQ = 0b01010101
# JGE = 0b01011010
# JGT = 0b01010111
# JLE = 0b01011001
# JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
# LD = 0b10000011
LDI = 0b10000010  # Set specific register to specific value
# MOD = 0b10100100
MUL = 0b10100010  # Multiply two registers together and store result in register A
# NOP = 0b00000000
# NOT = 0b01101001
# OR = 0b10101010
POP = 0b01000110  # Pop insturctions off of the stack
# PRA = 0b01001000
PRN = 0b01000111  # Print number
PUSH = 0b01000101  # Push instructions onto the stack
RET = 0b00010001  # Go to return address after subroutine
# SHL = 0b10101100
# SHR = 0b10101101
# ST = 0b10000100
SUB = 0b10100001  # Substract register A from register B and store result in register A
# XOR = 0b10101011

SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[SP] = 0xF4
        self.flag = 0
        self.branchtable = {}
        self.branchtable[CALL] = self.handle_call
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[POP] = self.handle_pop
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.alu_handle_add
        self.branchtable[DEC] = self.alu_handle_dec
        self.branchtable[INC] = self.alu_handle_inc
        self.branchtable[MUL] = self.alu_handle_mul
        self.branchtable[SUB] = self.alu_handle_sub
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self, path):
        """Load a program into memory."""
        try:
            address = 0
            with open(path) as file:
                for line in file:
                    line = line.split('#')[0]
                    line = line.strip()
                    if line == '':
                        continue
                    instruction = int(line, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print('File not found.')
            sys.exit(2)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.flag,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            ir = self.ram[self.pc]  # instruction register
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.branchtable[ir](operand_a, operand_b)
            if not ir >> 4 & 0b0001:
                self.pc += (ir >> 6) + 1

    # General Instructions

    def handle_call(self, a, b):
        # Decrement SP
        self.reg[SP] -= 1

        # Push return address on stack
        return_address = self.pc + 2
        self.ram[self.reg[SP]] = return_address

        # Set PC to value in register
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def handle_hlt(self, *_):
        sys.exit(0)

    def handle_ldi(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b

    def handle_pop(self, reg_num, _):
        # Get value from address pointed to by SP
        val = self.ram[self.reg[SP]]

        # Copy to given register
        self.reg[reg_num] = val

        # Increment SP
        self.reg[SP] += 1

    def handle_prn(self, reg_num, _):
        print(self.reg[reg_num])

    def handle_push(self, reg_num, _):
        # Decrement SP
        self.reg[SP] -= 1

        # Get value in given register
        reg_val = self.reg[reg_num]

        # Copy value to address pointed to by SP
        self.ram[self.reg[SP]] = reg_val

    def handle_ret(self, *_):
        # Pop return address off stack and store it on PC
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def handle_cmp(self, reg_a, reg_b):
        if self.reg[reg_a] < self.reg[reg_b]:
            self.flag = 0b100
        elif self.reg[reg_a] > self.reg[reg_b]:
            self.flag = 0b10
        else:
            self.flag = int(self.reg[reg_a] == self.reg[reg_b])

    def handle_jmp(self, reg_num, _):
        self.pc = self.reg[reg_num]

    def handle_jeq(self, reg_num, _):
        if self.flag & 1:
            self.handle_jmp(reg_num, _)
        else:
            self.pc += 2

    def handle_jne(self, reg_num, _):
        if self.flag & 1 == 0:
            self.handle_jmp(reg_num, _)
        else:
            self.pc += 2

        # ALU Instructions

    def alu_handle_add(self, reg_a, reg_b):
        self.reg[reg_a] += self.reg[reg_b]

    def alu_handle_dec(self, reg_num, _):
        self.reg[reg_num] -= 1

    def alu_handle_inc(self, reg_num, _):
        self.reg[reg_num] += 1

    def alu_handle_mul(self, reg_a, reg_b):
        self.reg[reg_a] *= self.reg[reg_b]

    def alu_handle_sub(self, reg_a, reg_b):
        self.reg[reg_a] -= self.reg[reg_b]
