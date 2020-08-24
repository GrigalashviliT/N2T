// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(INIT)
    @SCREEN
    D=A
    @addressOfScreen
    M=D

    @CHECKFORCLICK
    0;JMP

(DECREASESCREENADDRESS)
    @1
    D=A
    @addressOfScreen
    M=M-D

    @CHECKFORCLICK
    0;JMP

(WHITESCREEN)
    @SCREEN
    D=A
    @addressOfScreen
    D=M-D
    @CHECKFORCLICK
    D;JLT

    @addressOfScreen
    A=M
    M=0

    @DECREASESCREENADDRESS
    0;JMP

(CHECKFORCLICK)
    @KBD
    D=M

    @WHITESCREEN
    D;JEQ

(BLACKSCREEN)
    @1
    D=A
    @addressOfScreen
    M=D+M

    @KBD
    D=A
    @addressOfScreen
    D=D-M
    @DECREASESCREENADDRESS
    D;JLE

    @addressOfScreen
    A=M
    M=-1

    @BLACKSCREEN
    0;JMP

