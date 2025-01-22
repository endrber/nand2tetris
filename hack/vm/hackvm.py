#!/usr/bin/env python3
import sys

def instruction(inst, **kwargs):
  print(inst, kwargs)
  if inst == "A": return f"@{kwargs["address"]}"
  elif inst == "C":
    c_instruction = f"{kwargs['dest']+'=' if kwargs["dest"] is not None else ''}{kwargs['comp']}"
    return c_instruction+f";{kwargs["jump"]}" if "jump" in kwargs else c_instruction
  else: AttributeError(f"'{inst}' not supported")

class VMCommand:
  def to_assembly(self):
    raise NotImplementedError("Must be implemented by subclasses.")

class VMArithmeticCommand(VMCommand):
  def __init__(self, command, arg1):
    self.command = command
    self.arg1 = arg1
    self.label_num = 0
    self.commands = []

  def _sp_op(self, op):
    self.commands.append(instruction(inst="A", address="SP"))
    self.commands.append(instruction(inst="C", dest="M", comp=f"M{op}1"))

  def _comp_to_sp(self, comp):
    self.commands.append(instruction(inst="A", address="SP"))
    self.commands.append(instruction(inst="C", dest="A", comp="M"))
    self.commands.append(instruction(inst="C", dest="M", comp=comp))

  def _sp_to_dest(self, dest):
    self.commands.append(instruction(inst="A", address="SP"))
    self.commands.append(instruction(inst="C", dest="A", comp="M"))
    self.commands.append(instruction(inst="C", dest=dest, comp="M"))

  def _label(self):
    self.label_num += 1
    return 'LABEL'+str(self.label_num)

  def _unary_op(self, comp):
    self._sp_op("-")                     
    self._sp_to_dest('D')           
    self.commands.append(instruction(inst="C", dest="D", comp=comp))        
    self._comp_to_sp('D')           
    self._sp_op("+")                     

  def _binary_op(self, comp):
    self._sp_op("-")
    self._sp_to_dest("D")
    self._sp_op("-")
    self._sp_to_dest("A")
    self.commands.append(instruction(inst="C", dest="D", comp=comp))
    self._sp_op("+")

  def _compare_op(self, jump):
    def jump(comp, jump):
      lbl = self._label()
      self.commands.append(instruction(inst="A", address=label))
      self.commands.append(instruction(inst="C", dest=None, comp=comp, jump=jump))
      return lbl
    self._sp_op("-")                    
    self._sp_to_dest('D')            
    self._sp_op("-")                    
    self._sp_to_dest('A')    
    self.commands.append(instruction(inst="C", dest="D", comp='A-D'))
    label_eq = jump('D', jump)
    self._comp_to_sp('0')
    label_ne = jump('0', 'JMP')   
    self.commands.append(f"('{label_eq}')")           
    self._comp_to_sp('-1')           
    self.commands.append(f"('{label_ne}')")           
    self._sp_op()                      

  def to_assembly(self):
    command = self.arg1.lower()
    if   command == "add": self._binary_op("D+A")
    elif command == "sub": self._binary_op("A-D")
    elif command == 'neg': self._unary_op('-D')
    elif command == 'eq': self._compare_op('JEQ')
    elif command == 'gt': self._compare_op('JGT')
    elif command == 'lt': self._compare_op('JLT')
    elif command == 'and': self._binary_op('D&A')
    elif command == 'or': self._binary_op('D|A')
    elif command == 'not': self._unary_op('!D')
    else: raise Exception(f"{command} to_assembly not found for arithmetic")
    return self.commands

class VMPushPopCommand(VMCommand):
  def __init__(self, command, ctype, arg1, arg2):
    self.command = command
    self.ctype = ctype
    self.arg1 = arg1
    self.arg2 = arg2
    self.commands = []

  def _push(self, seg, idx):
    if seg == "constant":
      self.commands.append(instruction(inst="A", address=str(idx)))
      self.commands.append(instruction(inst="C", dest="D", comp="A"))
      self.commands.append(instruction(inst="A", address="SP"))
      self.commands.append(instruction(inst="C", dest="M", comp="D"))
    else: raise NotImplementedError
  
  def _pop(self, seg, idx):
    raise NotImplementedError

  def to_assembly(self):
    CTYPE = self.ctype
    SEG = self.arg1
    IDX = self.arg2

    if CTYPE == "C_PUSH": self._push(SEG, IDX)
    else: raise NotImplementedError
    return self.commands
        
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
    else: raise NotImplementedError(f"Command type for '{command}' is not implemented.")

  @property
  def arg1(self):
    ctype = self.ctype()
    if ctype not in ["C_RETURN"]:
      if ctype == "C_ARITHMETIC":
        return self.current_command.split()[0].lower()
      else:
        return self.current_command.split()[1].lower()

  @property
  def arg2(self):
    if self.ctype() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
      try:
        return int(self.current_command.split()[2].lower())
      except ValueError:
        return self.current_command.split()[2].lower()

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
      else: raise NotImplemetedError
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
    asm_codegen = [] 
    for command in p.parse():
      asm = command.to_assembly()
      if asm is not None: asm_codegen.append(asm)
    asm = sum(asm, [])
    for a in asm:
      print(a)
    # self.write()

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print("Usage: hackvm.py <filename.asm>")
    sys.exit()
  vm = VMTranslator(sys.argv[1])
  vm.translate()