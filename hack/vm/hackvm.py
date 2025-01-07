#!/usr/bin/env python3
import sys

class VMCommand:
  def to_assembly(self):
    raise NotImplementedError("Must be implemented by subclasses.")

class VMArithmeticCommand(VMCommand):
  def __init__(self, command, arg1):
    self.command = command
    self.arg1 = arg1

  def to_assembly(self):
    raise NotImplementedError

class VMPushPopCommand(VMCommand):
  def __init__(self, command, ctype, arg1, arg2):
    self.command = command
    self.ctype = ctype
    self.arg1 = arg1
    self.arg2 = arg2

  def to_assembly(self):
    raise NotImplementedError

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

  def ctype(self):
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
    ctype = self.ctype()
    if ctype not in ["C_RETURN"]:
      if ctype == "C_ARITHMETIC":
        return self.current_command.split()[0]
      else:
        return self.current_command.split()[1]

  @property
  def arg2(self):
    if self.ctype() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
      try:
        return int(self.current_command.split()[2])
      except ValueError:
        return self.current_command.split()[2]

  def parse(self):
    commands = []
    while self.next():
      self.advance()
      arg1, arg2 = self.arg1, self.arg2
      ctype = self.ctype()
      if ctype == "C_ARITHMETIC":
        commands.append(VMArithmeticCommand(self.current_command, arg1))
      elif ctype in ["C_PUSH", "C_POP"]:
        commands.append(VMPushPopCommand(self.current_command, ctype, arg1, arg2))
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
      for command in commands:
        print(command, command.to_assembly())
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