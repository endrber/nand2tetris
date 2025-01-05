@R0
D=M
@R1
D=D-M
@POS
D;JGT

@R1
D=M
@R2
M=D
@END
D;JMP

(POS)
  @R0
  D=M
  @R2
  M=D

(END)
  @END
  D;JMP
