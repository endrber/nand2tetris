#!/usr/bin/env python3
import sys

DEST_TABLE = {
  '':    '000',
  'M':   '001',
  'D':   '010',
  'MD':  '011',
  'A':   '100',
  'AM':  '101',
  'AD':  '110',
  'AMD': '111'
}

JUMP_TABLE = {
  '':    '000',
  'JGT': '001',
  'JEQ': '010',
  'JGE': '011',
  'JLT': '100',
  'JNE': '101',
  'JLE': '110',
  'JMP': '111'
}

COMP_TABLE = {
  '0':   '0101010',
  '1':   '0111111',
  '-1':  '0111010',
  'D':   '0001100',
  'A':   '0110000',
  '!D':  '0001101',
  '!A':  '0110001',
  '-D':  '0001111',
  '-A':  '0110011',
  'D+1': '0011111',
  'A+1': '0110111',
  'D-1': '0001110',
  'A-1': '0110010',
  'D+A': '0000010',
  'D-A': '0010011',
  'A-D': '0000111',
  'D&A': '0000000',
  'D|A': '0010101',
  'M':   '1110000',
  '!M':  '1110001',
  '-M':  '1110011',
  'M+1': '1110111',
  'M-1': '1110010',
  'D+M': '1000010',
  'D-M': '1010011',
  'M-D': '1000111',
  'D&M': '1000000',
  'D|M': '1010101'
}

VALID_SYMBOL_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.$:")

class SymbolTable:
  def __init__(self):
    self.table = {
      'SP': 0,
      'LCL': 1,
      'ARG': 2,
      'THIS': 3,
      'THAT': 4,
      **{f'R{i}': i for i in range(16)},
      'SCREEN': 16384,
      'KBD': 24576
    }
    self.next_address = 16

  def add(self, symbol, address=None):
    if symbol not in self.table:
      if address is not None:
        self.table[symbol] = address
      else: 
        self.table[symbol] = self.next_address
        self.next_address += 1

  def get(self, symbol):
    return self.table.get(symbol)

  def contains(self, symbol):
    return symbol in self.table

class Instruction:
  def to_binary(self):
    raise NotImplementedError("Must be implemented by subclasses.")

class AInstruction(Instruction):
  def __init__(self, symbol, line_number):
    self.symbol = symbol
    self.line_number = line_number

  def to_binary(self, symbol_table):
    address = None
    if self.symbol.isdigit():
      address = int(self.symbol)
    else:
      if not is_valid_symbol(self.symbol):
        raise SyntaxError(f"Line {self.line_number}: Invalid symbol '{self.symbol}' in A-instruction.")
      if not symbol_table.contains(self.symbol):
        symbol_table.add(self.symbol)
      address = symbol_table.get(self.symbol)
    if address is None or address < 0 or address > 32767:
      raise ValueError(f"Line {self.line_number}: Invalid address '{self.symbol}'.")
    return '0' + f'{address:015b}'

class CInstruction(Instruction):
  def __init__(self, dest, comp, jump, line_number):
    self.dest = dest
    self.comp = comp
    self.jump = jump
    self.line_number = line_number

  def to_binary(self):
    if self.comp not in COMP_TABLE:
      raise SyntaxError(f"Line {self.line_number}: Invalid comp mnemonic '{self.comp}'.")
    if self.dest not in DEST_TABLE:
      raise SyntaxError(f"Line {self.line_number}: Invalid dest mnemonic '{self.dest}'.")
    if self.jump not in JUMP_TABLE:
      raise SyntaxError(f"Line {self.line_number}: Invalid jump mnemonic '{self.jump}'.")
    return '111' + COMP_TABLE[self.comp] + DEST_TABLE[self.dest] + JUMP_TABLE[self.jump]

class LInstruction(Instruction):
  def __init__(self, symbol, line_number):
    self.symbol = symbol
    self.line_number = line_number

  def to_binary(self):
    return None  # Labels do not translate to binary code

def is_valid_symbol(symbol):
  return symbol and all(c in VALID_SYMBOL_CHARS for c in symbol[0:]) and not symbol[0].isdigit()

class Parser:
  def __init__(self, lines):
    self.lines = lines
    self.current_line = 0
    self.line_number = 0

  def has_more_commands(self):
    return self.current_line < len(self.lines)

  def advance(self):
    if self.has_more_commands():
      self.current_command = self.lines[self.current_line]
      self.line_number = self.current_line + 1
      self.current_line += 1
    else:
      self.current_command = None

  def instruction_type(self):
    command = self.current_command
    if command.startswith('@'):
      return 'A_INSTRUCTION'
    elif command.startswith('(') and command.endswith(')'):
      return 'L_INSTRUCTION'
    else:
      return 'C_INSTRUCTION'

  def parse(self):
    instructions = []
    while self.has_more_commands():
      self.advance()
      command = self.current_command
      if not command or command.startswith('//'):
        continue
      command = command.split('//')[0].strip()
      if not command:
        continue
      inst_type = self.instruction_type()
      if inst_type == 'A_INSTRUCTION':
        symbol = command[1:].strip()
        if not symbol:
          raise SyntaxError(f"Line {self.line_number}: Missing symbol in A-instruction.")
        instructions.append(AInstruction(symbol, self.line_number))
      elif inst_type == 'L_INSTRUCTION':
        symbol = command[1:-1].strip()
        if not is_valid_symbol(symbol):
          raise SyntaxError(f"Line {self.line_number}: Invalid label '{symbol}'.")
        instructions.append(LInstruction(symbol, self.line_number))
      elif inst_type == 'C_INSTRUCTION':
        dest, comp, jump = self.parse_c_instruction(command)
        instructions.append(CInstruction(dest, comp, jump, self.line_number))
      else:
        raise SyntaxError(f"Line {self.line_number}: Unknown instruction type.")
    return instructions

  def parse_c_instruction(self, command):
    if '=' in command:
      dest, rest = command.split('=', 1)
      dest = dest.strip()
    else:
      dest, rest = '', command
    if ';' in rest:
      comp, jump = rest.split(';', 1)
      comp, jump = comp.strip(), jump.strip()
    else:
      comp, jump = rest.strip(), ''
    if not comp:
      raise SyntaxError(f"Line {self.line_number}: Missing comp field in C-instruction.")
    return dest, comp, jump

class Assembler:
  def __init__(self, filename):
    self.filename = filename
    self.symbol_table = SymbolTable()
    self.instructions = []
    self.machine_code = []

  def read_file(self):
    try:
      with open(self.filename) as file:
        lines = [line.rstrip('\n') for line in file]
      return lines
    except FileNotFoundError:
      raise FileNotFoundError(f"File not found: {self.filename}")

  def construct_labels(self, instructions):
    line_number = 0
    for instruction in instructions:
      if isinstance(instruction, LInstruction):
        if self.symbol_table.contains(instruction.symbol):
          raise SyntaxError(f"Line {instruction.line_number}: Label '{instruction.symbol}' redefined.")
        self.symbol_table.add(instruction.symbol, line_number)
      else:
        line_number += 1

  def gen_machine_code(self, instructions):
    for instruction in instructions:
      if isinstance(instruction, LInstruction):
        continue
      if isinstance(instruction, AInstruction):
        binary = instruction.to_binary(self.symbol_table)
      elif isinstance(instruction, CInstruction):
        binary = instruction.to_binary()
      else:
        raise ValueError("Unknown instruction type.")
      self.machine_code.append(binary)

  def write_output(self):
    output_file = self.filename.replace('.asm', '.hack')
    try:
      with open(output_file, 'w') as file:
        for code in self.machine_code:
          file.write(code + '\n')
    except IOError as e:
      raise IOError(f"Error writing to file: {output_file}\n{e}")

  def assemble(self):
    lines = self.read_file()
    parser = Parser(lines)
    try:
      instructions = parser.parse()
      self.construct_labels(instructions) # first pass
      self.gen_machine_code(instructions) # second pass
      self.write_output()
    except SyntaxError as e:
      print(f"Syntax Error: {e}")
      sys.exit(1)
    except Exception as e:
      print(f"Error: {e}")
      sys.exit(1)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print("Usage: hackasm.py <filename.asm>")
    sys.exit(1)
  try:
    assembler = Assembler(sys.argv[1])
    assembler.assemble()
  except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)