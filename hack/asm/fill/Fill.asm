// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.


(START)
  @i
  M=0
  @j
  M=0
  
  // if not kbd input go back to start
  @KBD
  D=M
  @START
  D;JEQ

(WRTBLK) 
  // check if every pixel is 1
  @i
  D=M
  @SCREEN
  D=D+A
  @24574
  D=D-A
  @BLKEND
  D;JGT
  
  // write pixel to 1
  @i
  D=M
  @SCREEN
  A=A+D
  M=-1
  
  // update iterator
  @1
  D=A
  @i
  M=D+M

  @WRTBLK
  0;JMP

(WRTWHT)
  // check if every pixel is 0
  @j
  D=M
  @SCREEN
  D=D+A
  @24574
  D=D-A
  @WHTEND
  D;JGT
  
  // write pixel to 0
  @j
  D=M
  @SCREEN
  A=A+D
  M=0
  
  // update iterator
  @1
  D=A
  @j
  M=D+M

  @WRTWHT
  0;JMP
 
(BLKEND)
  @KBD
  D=M
  @WRTWHT
  D;JEQ
  
  @BLKEND
  0;JMP

(WHTEND)
  @KBD
  D=M
  @START
  D;JEQ
  
  @WHTEND
  0;JMP

