// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.


(START)
  @i
  M=0
  @j
  M=0
  
  @KBD
  D=M
  @START
  D;JEQ

(LOOP)
  @KBD
  D=M
  @START
  D;JEQ
  
  @i
  D=M
  @SCREEN
  D=D+A
  @24574
  D=D-A
  @END
  D;JGT

  @i
  D=M
  @SCREEN
  A=A+D
  M=-1
  
  @32
  D=A
  @i
  M=D+M

  @LOOP
  0;JMP

(WHITE)
  @j
  D=M
  @SCREEN
  D=D+A
  @24574
  D=D-A
  @END2
  D;JGT

  @j
  D=M
  @SCREEN
  A=A+D
  M=0
  
  @32
  D=A
  @j
  M=D+M

  @WHITE
  0;JMP
 
(END)
  @KBD
  D=M
  @WHITE
  D;JEQ
  
  @END
  0;JMP

(END2)
  @KBD
  D=M
  @START
  D;JEQ
  
  @END2
  0;JMP

