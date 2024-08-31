// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

@i
M=0
@R2
M=0

@R1
D=M
@END
D;JEQ

@R0
D=M
@END
D;JEQ

(LOOP)   
  @i
  D=M
  @R1
  D=D-M
  @END
  D;JGE

  @R0
  D=M
  @R2
  M=D+M
  @i
  M=M+1
  @LOOP
  0;JMP

(END)
  @END
  D;JEQ
