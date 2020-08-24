import sys
import os.path

class Translator:
    def __init__(self, commands, file_name, end):
        self.commands = commands
        self.static_name = file_name
        self.counter = 0
        self.end = end

    def translate(self):
        result = ""
        self.counter += 1;

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
            elif(splited_com[0] == "label"):
                result += "(" + splited_com[1] + ")\n"
            elif(splited_com[0] == "goto"):
                result += "@" + splited_com[1] + "\n0;JMP\n"
            elif(splited_com[0] == "if-goto"):
                result += "@SP\nM=M-1\n@SP\nA=M\nD=M\n@" + splited_com[1] + "\nD;JNE\n"
            elif(splited_com[0] == "function"):
                result += "(" + splited_com[1] + ")\n"
                for i in range(int(splited_com[2])):
                    result += "@SP\nA=M\nM=0\n@SP\nM=M+1\n"
            elif(splited_com[0] == "call"):
                result += "@Return" + str(self.counter) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@SP\nD=M\n@" + str(int(splited_com[2]) + 5) + "\nD=D-A\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@" + splited_com[1] + "\n0;JMP\n(Return" + str(self.counter) + ")\n";
                self.counter += 1;
            elif(splited_com[0] == "return"):
                result += "@LCL\nD = M\n@R14\nM = D\n@5\nD = A\n@R14\nD = M - D\nA = D\nD = M\n@R15\nM = D\n@0\nD=A\n@ARG\nA=M\nD=D+A\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n@R14\nM=M-1\nA=M\nD=M\n@THAT\nM=D\n@R14\nM=M-1\nA=M\nD=M\n@THIS\nM=D\n@R14\nM=M-1\nA=M\nD=M\n@ARG\nM=D\n@R14\nM=M-1\nA=M\nD=M\n@LCL\nM=D\n@R15\nA=M\n0;JMP\n"
        
        if(self.end == 1):
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
                splited_command = line.split("//", 1)
                command = splited_command[0].replace('\n', "").replace('\t', '').rstrip()
                commands.append(command)
            line = self.file.readline()

        return commands

    def close_file(self):
        self.file.close()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        file_path = os.getcwd();
    else:
        file_path = sys.argv[1]

    if(file_path[-1] == '/'):
        file_path = file_path[:-1]
    
    file_exists = os.path.isfile(file_path)

    if(os.path.isdir(file_path)):
        whole_result = ""
        whole_result += "@256\nD=A\n@SP\nM=D\n"
        whole_result += "@Return0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@SP\nD=M\n@" + str(5) + "\nD=D-A\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@Sys.init\n0;JMP\n(Return0)\n";
        files = [f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]
        for f in files:
            if(f.endswith(".vm")):
                parser = Parser(file_path + '/' +  f)
                commands = parser.parse_commands()
                parser.close_file()

                translator = Translator(commands, f[:-3], 0)
                result = translator.translate()

                whole_result += result

        whole_result += "(END)\n@END\n0;JMP\n"

        new_file_path = file_path + '/' + file_path.split('/')[-1] + ".asm"

        out_file = open(new_file_path, "w+")
        out_file.write(whole_result);
        out_file.close()
    elif(file_exists):
        if(file_path.endswith(".vm")):
            parser = Parser(file_path)
            commands = parser.parse_commands()
            parser.close_file()

            translator = Translator(commands, file_path.split('/')[-1][:-3], 1)
            result = translator.translate()

            new_file_path = file_path[:-2] + "asm"

            out_file = open(new_file_path, "w+")
            out_file.write(result);
            out_file.close()
        else:
            print("Wrong file type")
    else:
        print("No such file")