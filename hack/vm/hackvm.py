#!/usr/bin/env python3
import sys

class Parser:
  COMMENT_PREFIXES = ("//", "#", ";")
  
  def __init__(self, filename):
    self.i = 0
    self.current = 0
    try:
      with open(filename) as file:
        self.commands = [
          line.strip()
          for line in file
            if line.strip() and not any(line.lstrip().startswith(prefix) for prefix in self.COMMENT_PREFIXES)
          ]
    except FileNotFoundError:
      raise FileNotFoundError(f"File not found: {self.filename}")

  def next(self):
    return self.current < len(self.commands)

  def advance(self):
    assert self.next(), "next() logic failed" 
    self.current_command = self.commands[self.current]
    self.i = self.current + 1
    self.current += 1

  def command_type(self):
    command = self.current_command.lower()
    if command.startswith("push"):
      return "C_PUSH"
    elif command.startswith("pop"):
      return "C_POP"
    elif command in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
      return "C_ARITHMETIC"
    #TODO: Add implemention for ["C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION", "C_RETURN", "C_CALL"]
    else:
      raise NotImplementedError(f"Command type for '{command}' is not implemented.")

  @property
  def arg1(self):
    ctype = self.command_type()
    if ctype not in ["C_RETURN"]:
      if ctype == "C_ARITHMETIC":
        return self.current_command.split()[0]
      else:
        return self.current_command.split()[1]

  @property
  def arg2(self):
    if self.command_type() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
      return self.current_command.split()[2]

  def parse(self):
    commands = []
    while self.next():
      self.advance()
      a1, a2 = self.arg1, self.arg2
      print(f"{self.command_type()} -> ARG1: '{a1}' | ARG2: '{a2}'")
      commands.append(self.current_command)
    return commands

class VMTranslator:
  def __init__(self, filename):
    self.filename = filename
    self.asm = []

  def write(self):
    output_file = self.filename.replace('.vm', '.asm')
    try:
      with open(output_file, 'w') as file:
        for code in self.asm:
          file.write(code + '\n')
    except IOError as e:
      raise IOError(f"Error writing to file: {output_file}\n{e}")

  def translate(self):
    p = Parser(self.filename)
    try:
      commands = p.parse()
      print(commands)
      # self.write()
    # except SyntaxError as e:
    #   print(f"Syntax Error: {e}")
    #   sys.exit(1)
    except Exception as e:
      print(f"Error: {e}")
      sys.exit(1)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print("Usage: hackvm.py <filename.asm>")
    sys.exit(1)
  try:
    vm = VMTranslator(sys.argv[1])
    vm.translate()
  except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)