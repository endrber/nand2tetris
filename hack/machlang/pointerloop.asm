@R1
D=M
@R0
D=D+M
@n
M=D

(LOOP)
  @R0
  D=M
  @n
  D=D-M
  @END
  D;JGE

  @R0
  A=M
  M=-1

  @R0
  D=M
  M=D+1

  @LOOP
  0;JMP

(END)
  @END
  0;JMP
