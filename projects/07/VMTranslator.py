import sys
import os.path

class Translator:
    def __init__(self, commands, file_name):
        self.commands = commands
        self.static_name = file_name
        self.counter = 0;

    def translate(self):
        result = ""

        for com in self.commands:
            splited_com = com.split(' ')

            if(splited_com[0] == "push"):
                if(splited_com[1] == "constant"):
                    result += "@" + splited_com[2] + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "local"):
                    result += "@" + splited_com[2] + "\nD=A\n@LCL\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "argument"):
                    result += "@" + splited_com[2] + "\nD=A\n@ARG\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "this"):
                    result += "@" + splited_com[2] + "\nD=A\n@THIS\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "that"):
                    result += "@" + splited_com[2] + "\nD=A\n@THAT\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "temp"):
                    result += "@" + splited_com[2] + "\nD=A\n@5\nA=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "static"):
                    result += "@" + self.static_name + '.' + splited_com[2] + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                elif(splited_com[1] == "pointer"):
                    if(splited_com[2] == '0'):
                        result += "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                    else:
                        result += "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            elif(splited_com[0] == "add"):
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=D+M\n@SP\nM=M+1\n"
            elif(splited_com[0] == "sub"):
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=M-D\n@SP\nM=M+1\n"
            elif(splited_com[0] == "neg"):
                result += "@SP\nM=M-1\n@SP\nA=M\nM=-M\n@SP\nM=M+1\n"
            elif(splited_com[0] == "eq"):
                curC = str(self.counter)
                nextC = str(self.counter + 1)
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=M-D\n@SP\nA=M\nD=M\n@EQUAL" + curC + "\nD; JEQ\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@ST"+ nextC +"\n0; JMP\n(EQUAL" + curC + ")\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n(ST" + nextC +")\n"
                self.counter += 1
            elif(splited_com[0] == "lt"):
                curC = str(self.counter)
                nextC = str(self.counter + 1)
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=M-D\n@SP\nA=M\nD=M\n@LESS" + curC + "\nD; JLT\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@ST"+ nextC +"\n0; JMP\n(LESS" + curC + ")\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n(ST" + nextC +")\n"
                self.counter += 1
            elif(splited_com[0] == "gt"):
                curC = str(self.counter)
                nextC = str(self.counter + 1)
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=M-D\n@SP\nA=M\nD=M\n@MORE" + curC + "\nD; JGT\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@ST"+ nextC +"\n0; JMP\n(MORE" + curC + ")\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n(ST" + nextC +")\n"
                self.counter += 1
            elif(splited_com[0] == "and"):
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=D&M\n@SP\nM=M+1\n"
            elif(splited_com[0] == "or"):
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=D|M\n@SP\nM=M+1\n"
            elif(splited_com[0] == "not"):
                result += "@SP\nM=M-1\n@SP\nA=M\nM=!M\n@SP\nM=M+1\n"
            elif(splited_com[0] == "pop"):
                if(splited_com[1] == "local"):
                    result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@" + splited_com[2] + "\nD=A\n@LCL\nA=M+D\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                elif(splited_com[1] == "argument"):
                    result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@" + splited_com[2] + "\nD=A\n@ARG\nA=M+D\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                elif(splited_com[1] == "this"):
                    result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@" + splited_com[2] + "\nD=A\n@THIS\nA=M+D\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                elif(splited_com[1] == "that"):
                    result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@" + splited_com[2] + "\nD=A\n@THAT\nA=M+D\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                elif(splited_com[1] == "temp"):
                    result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@" + splited_com[2] + "\nD=A\n@5\nA=A+D\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                elif(splited_com[1] == "static"):
                    result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@" + self.static_name + '.' + splited_com[2] + "\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                elif(splited_com[1] == "pointer"):
                    if(splited_com[2] == '0'):
                        result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@THIS\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
                    else:
                        result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n@THAT\nD=A\n@R14\nM=D\n@R13\nD=M\n@R14\nA=M\nM=D\n"
        
        result += "(END)\n@END\n0;JMP\n"

        return result


class Parser:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')

    def parse_commands(self):
        commands = []

        line = self.file.readline()
        while(line):
            if( not(line.startswith("//")) and not(line == "\n") ):
                commands.append(line[:-1])
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
        if(file_path.endswith(".vm")):
            parser = Parser(file_path)
            commands = parser.parse_commands()
            parser.close_file()

            translator = Translator(commands, file_path.split('/')[-1][:-3])
            result = translator.translate()

            new_file_path = file_path[:-2] + "asm"

            out_file = open(new_file_path, "w+")
            out_file.write(result);
            out_file.close()
        else:
            print("Wrong file type")
    else:
        print("No such file")
