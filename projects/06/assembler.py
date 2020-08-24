import sys
import os.path

class Assembler:
    def __init__(self, commands):
        self.commands = commands
        self.lables = {}
        self.variables = {}
        self.a = 0

    def define_lables(self):
        line = 0
        for com in self.commands:
            if(com.startswith('(')):
                self.lables[com[1:-1]] = line
                line -= 1
            
            line += 1

    def represents_int(self, symbol):
        if(symbol.isdigit() or (symbol.startswith('-') and symbol[1:].isdigit()) ):
            return True

        return False

    def define_variables(self):
        cur_variable = 16

        for com in self.commands:
            if(com.startswith("@")):
                if(com[1:] in ['R0','R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12','R13','R14','R15']):
                    self.variables[com[1:]] = int(com[2:])
                elif(com[1:] == 'SCREEN'):
                    self.variables["SCREEN"] = 16384
                elif(com[1:]) == "KEYBOARD":
                    self.variables["KEYBOARD"] = 24576
                elif(com[1:] == "SP"):
                    self.variables["SP"] = 0
                elif(com[1:] == "LCL"):
                    self.variables["LCL"] = 1
                elif(com[1:] == "ARG"):
                    self.variables["ARG"] = 2
                elif(com[1:] == "THIS"):
                    self.variables["THIS"] = 3
                elif(com[1:] == "THAT"):
                    self.variables["THAT"] = 4
                elif(com[1:] not in self.lables.keys() and com[1:] not in self.variables.keys() and not self.represents_int(com[1:]) ):
                    self.variables[com[1:]] = cur_variable
                    cur_variable += 1

    def assemble(self):
        self.define_lables()
        self.define_variables()

        hack_code = ""

        for com in self.commands:
            if(com[0] == '@'):
                aoe = (self.a_instruction(com[1:]))
                hack_code += (aoe + '\n')
            elif(com[0] != '('):
                splited_com = com.replace(';', '=').split("=")
                
                dest = ""
                comp = ""
                jump = ""
                if(len(splited_com) == 3):
                    dest = splited_com[0]
                    comp = splited_com[1]
                    jump = splited_com[2]
                elif(";" in com):
                    comp = splited_com[0]
                    jump = splited_com[1]
                elif("=" in com):
                    dest = splited_com[0]
                    comp = splited_com[1]
                
                ae = self.c_instruction(dest, comp, jump)
                hack_code += ae + '\n'
        
        return hack_code
    
    def a_instruction(self, symbol):
        if(symbol in self.lables.keys()):
            num = self.lables[symbol]
        elif(symbol in self.variables.keys()):
            num = self.variables[symbol]
        else:
            num = int(symbol)

        instruction = "0"

        num_in_binary = "{0:b}".format(num)

        for i in range(15 - len(num_in_binary)):
            instruction += '0'
        
        instruction += num_in_binary

        return instruction
    
    def c_instruction(self, dest, comp, jump):
        instruction = "111"

        if(comp == "0"):
            instruction += "0101010"
        elif(comp == "1"):
            instruction += "0111111"
        elif(comp == "-1"):
            instruction += "0111010"
        elif(comp == "D"):
            instruction += "0001100"
        elif(comp == "A"):
            instruction += "0110000"
        elif(comp == "M"):
            instruction += "1110000"
        elif(comp == "!D"):
            instruction += "0001101"
        elif(comp == "!A"):
            instruction += "0110001"
        elif(comp == "!M"):
            instruction += "1110001"
        elif(comp == "-D"):
            instruction += "0001111"
        elif(comp == "-A"):
            instruction += "0110011"
        elif(comp == "-M"):
            instruction += "1110011"
        elif(comp == "D+1"):
            instruction += "0011111"
        elif(comp == "A+1"):
            instruction += "0110111"
        elif(comp == "M+1"):
            instruction += "1110111"
        elif(comp == "D-1"):
            instruction += "0001110"
        elif(comp == "A-1"):
            instruction += "0110010"
        elif(comp == "M-1"):
            instruction += "1110010"
        elif(comp == "D+A"):
            instruction += "0000010"
        elif(comp == "D+M"):
            instruction += "1000010"
        elif(comp == "D-A"):
            instruction += "0010011"
        elif(comp == "D-M"):
            instruction += "1010011"
        elif(comp == "A-D"):
            instruction += "0000111"
        elif(comp == "M-D"):
            instruction += "1000111"
        elif(comp == "D&A"):
            instruction += "0000000"
        elif(comp == "D&M"):
            instruction += "1000000"
        elif(comp == "D|A"):
            instruction += "0010101"
        elif(comp == "D|M"):
            instruction += "1010101"

        if(dest == ""):
            instruction += "000"
        elif(dest == "M"):
            instruction += "001"
        elif(dest == "D"):
            instruction += "010"
        elif(dest == "MD"):
            instruction += "011"
        elif(dest == "A"):
            instruction += "100"
        elif(dest == "AM"):
            instruction += "101"
        elif(dest == "AD"):
            instruction += "110"
        else:
            instruction += "111"

        if(jump == ""):
            instruction += "000"
        elif(jump == "JGT"):
            instruction += "001"
        elif(jump == "JEQ"):
            instruction += "010"
        elif(jump == "JGE"):
            instruction += "011"
        elif(jump == "JLT"):
            instruction += "100"
        elif(jump == "JNE"):
            instruction += "101"
        elif(jump == "JLE"):
            instruction += "110"
        else:
            instruction += "111"

        return instruction

class Parser:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')

    def parse_commands(self):
        commands = []

        line = self.file.readline()
        while(line):
            if( not(line.startswith("//")) and not(line == "\n") ):
                splited_command = line.split("//", 1)
                command = splited_command[0].replace(" ", "").replace('\n', "")
                commands.append(command)
            line = self.file.readline()

        return commands

    def close_file(self):
        self.file.close()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('No file was given')
        exit(-1)

    file_path = sys.argv[1]
    
    file_exists = os.path.isfile(file_path)

    if(file_exists):
        if(file_path.endswith(".asm")):
            parser = Parser(file_path)
            commands = parser.parse_commands()
            parser.close_file()

            assembler = Assembler(commands)
            result = assembler.assemble()

            new_file_path = file_path[:-3] + "hack"

            out_file = open(new_file_path, "w+")
            out_file.write(result);
            out_file.close()
        else:
            print("Wrong file type")
    else:
        print("No such file")

    exit(0)
