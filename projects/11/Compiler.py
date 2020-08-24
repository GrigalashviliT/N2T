import sys
import os.path

class Cleaner:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')

    def clean_commands(self):
        parsed_code = ""

        line = self.file.readline()
        while(line):
            if( not(line.lstrip().rstrip().startswith("//")) and  not(line.lstrip().rstrip().startswith("*")) and not(line.lstrip().rstrip().startswith("/**")) and not(line.lstrip().rstrip().startswith("/*")) and not(line == "\n") and not(line == "\t\n") ):
                line = line.split('//')[0]
                parsed_code += (line[:-1].replace('/t', '').rstrip().lstrip())
                parsed_code += ' '

            line = self.file.readline()

        return parsed_code

    def close_file(self):
        self.file.close()

class Tokenizer:
    def __init__(self, parsed_code):
        self.code = parsed_code
        self.keywords = { 'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false','null', 'this', 'let', 'do', 'if', 'else', 'while', "return" }
        self.symbols = { '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~' }

    def tokenize(self):
        xml_string = "<tokens>\n"

        splited_code = self.code.split()
        i = 0

        while( i < len(splited_code) ):
            tok = splited_code[i]

            if(tok.rstrip().lstrip() == ''):
                i += 1
                continue;

            if(tok[-1] == ';' and len(tok) != 1):
                tok = tok[:-1]
                splited_code.insert(i + 1, ';')
            
            while(1):
                if(tok == '' or len(tok) == 1):
                    break

                if( tok[0] == '-'):
                    splited_code.insert(i + 1, tok[1:])
                    tok = tok[0]
                elif(tok[0] == '~'):
                    splited_code.insert(i + 1, tok[1:])
                    tok = tok[0]

                if(tok[-1] == ')'):
                    splited_code.insert(i + 1, ')')
                    tok = tok[:-1]
                    continue
                elif(tok[-1] == '('):
                    splited_code.insert(i + 1, '(')
                    tok = tok[:-1]
                    continue
                elif(tok[-1] == '{'):
                    splited_code.insert(i + 1, '{')
                    tok = tok[:-1]
                    continue
                elif(tok[-1] == '}'):
                    splited_code.insert(i + 1, '}')
                    tok = tok[:-1]
                    continue
                elif(tok[-1] == ','):
                    splited_code.insert(i + 1, ',')
                    tok = tok[:-1]
                    continue
                elif(tok[-1] == ']'):
                    splited_code.insert(i + 1, ']')
                    tok = tok[:-1]
                    continue
                elif(tok[-1] == '['):
                    splited_code.insert(i + 1, '[')
                    tok = tok[:-1]
                    continue
                elif(len(tok) >= 2 and tok[-2] == ','):
                    splited_code.insert(i + 1, ',')
                    splited_code.insert(i + 2, tok[-1])
                    tok = tok[:-2]
                    continue
                elif(len(tok) >= 3 and tok[-3] == ','):
                    splited_code.insert(i + 1, ',')
                    splited_code.insert(i + 2, tok[-2:])
                    tok = tok[:-3]
                    continue

                break;

            if( "." in tok and len(tok) != 1):
                splited_tok = tok.split('.', 1)
                tok = splited_tok[0]
                splited_code.insert(i + 1, splited_tok[1])
                splited_code.insert(i + 1, '.')

            if( "[" in tok and len(tok) != 1):
                splited_tok = tok.split('[', 1)
                tok = splited_tok[0]
                splited_code.insert(i + 1, splited_tok[1])
                splited_code.insert(i + 1, '[')

            if( '(' in tok and len(tok) != 1):
                splited_tok = tok.split('(', 1)
                tok = splited_tok[0]
                splited_code.insert(i + 1, splited_tok[1])
                splited_code.insert(i + 1, '(')
            
            if( '"' in tok and len(tok) != 1 ):
                splited_tok = tok.split('"', 1)

                j = i + 1
                string = splited_tok[1] + " "
                while(j < len(splited_code)):
                    if('"' not in splited_code[j]):
                        string += splited_code[j] + " "
                    else:
                        break
                    
                    del splited_code[j]

                splited_splited_tok = splited_code[j].split('"')
                string += splited_splited_tok[0]
                tok = string
                splited_code[j] = splited_splited_tok[1]

            if(tok.rstrip().lstrip() == ''):
                i += 1
                continue;

            if(tok in self.keywords):
                xml_string += ("<keyword> " + tok + " </keyword>\n")
            elif(tok in self.symbols):
                if(tok != '<' and tok != '>' and tok != '"' and tok != '&'):
                    xml_string += "<symbol> " + tok + " </symbol>\n"
                elif(tok == '<'):
                    xml_string += "<symbol> &lt; </symbol>\n"
                elif(tok == '>'):
                    xml_string += "<symbol> &gt; </symbol>\n"
                elif(tok == '"'):
                    xml_string += "<symbol> &quot; </symbol>\n"
                elif(tok == '&'):
                    xml_string += "<symbol> &amp; </symbol>\n"
            elif(" " in tok):
                xml_string += ("<stringConstant> " + tok + " </stringConstant>\n")
            elif( tok.isdigit() or (len(tok) >= 1 and tok[0] == '-' and tok[1:].isdigit()) ):
                xml_string += ("<integerConstant> " + tok.rstrip() + " </integerConstant>\n")
            else:
                xml_string += ("<identifier> " + tok.rstrip() + " </identifier>\n")

            i += 1

        xml_string += "</tokens>\n"

        return xml_string

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.symbol_table = {}
        self.parsed = ""
        self.class_name = ''
        self.field = 0
        self.static = 0
        self.local = 0
        self.is_method = False
        self.method_name = ''
        self.while_count = 0;
        self.if_count = 0;

    def getResult(self):
        return self.parsed
    
    def compileClass(self):
        self.class_name = self.tokens[self.i + 1].split('>')[1][1:].split('<')[0][:-1]
        self.i += 3

        while(self.tokens[self.i] == "<keyword> static </keyword>" or self.tokens[self.i] == "<keyword> field </keyword>"):
            self.compileClassVarDec()

        while( ( self.i < len(self.tokens) ) and (self.tokens[self.i] == "<keyword> constructor </keyword>" or self.tokens[self.i] == "<keyword> method </keyword>" or self.tokens[self.i] == "<keyword> function </keyword>") ):
            self.compileDeclaration()

    def compileDeclaration(self):
        kind = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
        if(kind == 'method'):
            self.is_method = True
        else:
            self.is_method = False

        self.i += 2
        self.method_name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
        self.local = 0
        self.i += 2

        self.compileParameterList()
        self.i += 1

        self.compileBody(kind)

    def compileBody(self, kind):
        self.i += 1

        while(self.tokens[self.i] == "<keyword> var </keyword>"):
            self.compileVarDec()
        self.parsed += "function " + self.class_name + '.' + self.method_name + " " + str(self.local) + '\n'

        if(kind == 'constructor'):
            self.parsed += "push constant " + str(self.field) + '\n'
            self.parsed += "call Memory.alloc 1\n"
            self.parsed += "pop pointer 0\n"
        elif(kind == 'method'):
            self.parsed += "push argument 0\n"
            self.parsed += "pop pointer 0\n"

        self.compileStatements()
        self.i += 1

    def compileStatements(self):
        while( " let " in self.tokens[self.i] or " if " in self.tokens[self.i] or " while " in self.tokens[self.i] or " do " in self.tokens[self.i] or " return " in self.tokens[self.i] ):
            if(" let " in self.tokens[self.i]):
                self.i += 1
                self.compileLet()
            elif(" if " in self.tokens[self.i]):
                self.i += 1
                self.compileIf()
            elif(" while " in self.tokens[self.i]):
                self.i += 1
                self.compileWhile()
            elif(" do " in self.tokens[self.i]):
                self.i += 1
                self.compileDo()
            elif(" return " in self.tokens[self.i]):
                self.i += 1
                self.compileReturn()

    def compileLet(self):
        name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
        if(self.method_name + '.' + name in self.symbol_table):
            variable = self.symbol_table[self.method_name + '.' + name]
        else:
            variable = self.symbol_table[name]

        kind = variable[0]
        index = variable[2]
        self.i += 1

        if(self.tokens[self.i] == "<symbol> [ </symbol>"):
            self.i += 1
            self.compileExpression()
            self.i += 1

            self.parsed += 'push ' + kind + " " + str(index) + '\n'
            self.parsed += "add\n"
            
            self.i += 1
            self.compileExpression()
            self.i += 1

            self.parsed += 'pop temp 0\n'
            self.parsed += 'pop pointer 1\n'
            self.parsed += 'push temp 0\n'
            self.parsed += 'pop that 0\n'
        else:
            self.i += 1
            self.compileExpression()
            self.i += 1

            self.parsed += 'pop ' + kind + " " + str(index) + '\n'

    def compileIf(self):
        self.i += 1
        self.compileExpression()
        self.i += 2

        if_count = self.if_count
        self.if_count += 1

        self.parsed += 'if-goto TRUE' + str(if_count) + '\n'
        self.parsed += 'goto FALSE' + str(if_count) + '\n'
        self.parsed += 'label TRUE' + str(if_count) + '\n'
        self.compileStatements()
        self.i += 1
        self.parsed += 'goto END_OF_IF' + str(if_count) + '\n'
        self.parsed += 'label FALSE' + str(if_count) + '\n'

        if(" else " in self.tokens[self.i]):
            self.i += 2

            self.compileStatements()
            self.i += 1
        
        self.parsed += 'label END_OF_IF' + str(if_count) + '\n'

    def compileWhile(self):
        while_count = self.while_count
        self.while_count += 1

        self.parsed += 'label WHILE' + str(while_count) + '\n'
        self.i += 1

        self.compileExpression()
        self.parsed += 'not\n'
        self.i += 2

        self.parsed += 'if-goto END_OF_WHILE' + str(while_count) + '\n'
        self.compileStatements()
        self.parsed += 'goto WHILE' + str(while_count) + '\n'
        self.parsed += 'label END_OF_WHILE' + str(while_count) + '\n'
        
        self.i += 1

    def compileDo(self):
        self.compileSubroutine()
        self.parsed += "pop temp 0\n"
        self.i += 1

    def compileReturn(self):

        if(self.tokens[self.i] != "<symbol> ; </symbol>"):
            self.compileExpression()
        else:
            self.parsed += 'push constant 0\n'
        
        self.parsed += "return\n"
        self.i += 1

    def compileExpressionList(self):
        args = 0

        while(self.tokens[self.i] != "<symbol> ) </symbol>"):
            if(self.tokens[self.i] == "<symbol> , </symbol>"):
                self.i += 1
            args += 1
            self.compileExpression()
        
        return args

    def compileExpression(self):
        self.compileTerm()

        while(self.tokens[self.i].startswith("<symbol>") and (' + ' in self.tokens[self.i] or ' - ' in self.tokens[self.i] or ' * ' in self.tokens[self.i] or ' / ' in self.tokens[self.i] or ' | ' in self.tokens[self.i] or ' = ' in self.tokens[self.i] or ' &amp; ' in self.tokens[self.i] or ' &lt; ' in self.tokens[self.i] or ' &gt; ' in self.tokens[self.i] ) ):
            operation = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            self.i += 1
            self.compileTerm()

            if(operation == '*'):
                self.parsed += "call Math.multiply 2\n";
            elif(operation == '/'):
                self.parsed += "call Math.divide 2\n";
            elif(operation == '+'):
                self.parsed += "add\n";
            elif(operation == '-'):
                self.parsed += "sub\n";
            elif(operation == '-'):
                self.parsed += "neg\n";
            elif(operation == '~'):
                self.parsed += "not\n";
            elif(operation == '&amp;'):
                self.parsed += "and\n";
            elif(operation == '|'):
                self.parsed += "or\n";
            elif(operation == '='):
                self.parsed += "eq\n";
            elif(operation == '&gt;'):
                self.parsed += "gt\n";
            elif(operation == '&lt;'):
                self.parsed += "lt\n";

    def compileTerm(self):
        if(self.tokens[self.i] == "<symbol> - </symbol>" or self.tokens[self.i] == "<symbol> ~ </symbol>"):
            operation = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            self.i += 1
            self.compileTerm()
            if(operation == '-'):
                self.parsed += "neg\n";
            else:
                self.parsed += "not\n";
        elif(self.tokens[self.i] == "<symbol> ( </symbol>"):
            self.i += 1
            self.compileExpression()
            self.i += 1
        elif('integerConstant' in self.tokens[self.i]):
            constant = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            self.i += 1

            self.parsed += 'push constant ' + constant + '\n'
        elif('stringConstant' in self.tokens[self.i]):
            constant = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            self.i += 1

            self.parsed += 'push constant ' + str(len(constant)) + '\n'
            self.parsed += "call String.new 1\n"
            for char in constant:
                self.parsed += 'push constant ' + str(ord(char)) + '\n'
                self.parsed += "call String.appendChar 2\n"
        elif('keyword' in self.tokens[self.i]):
            constant = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            self.i += 1

            if(constant == 'this'):
                self.parsed += "push pointer 0\n"
            elif(constant == 'true'):
                self.parsed += "push constant 0\n"
                self.parsed += "not\n"
            elif(constant == 'false'):
                self.parsed += "push constant 0\n"
            elif(constant == 'null'):
                self.parsed += "push constant 0\n"
        else:
            if(self.tokens[self.i + 1] == "<symbol> [ </symbol>"):
                name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
                self.i += 2
                if(self.method_name + '.' + name in self.symbol_table):
                    variable = self.symbol_table[self.method_name + '.' + name]
                else:
                    variable = self.symbol_table[name]
                kind = variable[0]
                index = variable[2]

                self.compileExpression()
                self.i += 1

                self.parsed += "push " + kind + " " + str(index) + "\n"
                self.parsed += "add\n"
                self.parsed += "pop pointer 1\n"
                self.parsed += "push that 0\n"
            elif(self.tokens[self.i + 1] == "<symbol> ( </symbol>" or self.tokens[self.i + 1] == "<symbol> . </symbol>"):
                self.compileSubroutine()
            else:
                name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
                self.i += 1
                if(self.method_name + '.' + name in self.symbol_table):
                    variable = self.symbol_table[self.method_name + '.' + name]
                else:
                    variable = self.symbol_table[name]
                kind = variable[0]
                index = variable[2]

                self.parsed += "push " + kind + " " + str(index) + "\n"
                
    def compileVarDec(self):
        type = self.tokens[self.i + 1].split('>')[1][1:].split('<')[0][:-1]
        self.i += 2
        while(True):
            name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            
            self.symbol_table[self.method_name + '.' + name] = ('local', type, self.local)
            self.local += 1

            self.i += 1
            if(' ; ' in self.tokens[self.i]):
                self.i += 1
                break
            else:
                self.i += 1

    def compileParameterList(self):
        argument = 0

        if(self.is_method):
            self.symbol_table[self.method_name + '.this'] = ('argument', 'Point', 0)
            argument += 1

        while(self.tokens[self.i] != "<symbol> ) </symbol>"):
            type = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            name = self.tokens[self.i + 1].split('>')[1][1:].split('<')[0][:-1]
            self.symbol_table[self.method_name + '.' + name] = ('argument', type, argument)
            argument += 1
            self.i += 2

            if(self.tokens[self.i] == "<symbol> ) </symbol>"):
                break
            else:
                self.i += 1

    def compileClassVarDec(self):
        kind = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
        type = self.tokens[self.i + 1].split('>')[1][1:].split('<')[0][:-1]
        self.i += 2
        while(True):
            name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            if(kind == 'static'):
                self.symbol_table[name] = (kind, type, self.static)
                self.static += 1
            else:
                self.symbol_table[name] = ('this', type, self.field)
                self.field += 1
            
            self.i += 1
            if(' ; ' in self.tokens[self.i]):
                self.i += 1
                break
            else:
                self.i += 1

    def compileSubroutine(self):
        name = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
        self.i += 1
        args = 0

        if(' . ' in self.tokens[self.i]):
            self.i += 1
            subroutine = self.tokens[self.i].split('>')[1][1:].split('<')[0][:-1]
            self.i += 1

            if(name not in self.symbol_table and self.method_name + '.' + name not in self.symbol_table):
                function_name = name + '.' + subroutine
            elif(name in self.symbol_table):
                variable = self.symbol_table[name]

                self.parsed += "push " + variable[0] + ' ' + str(variable[2]) + '\n'
                function_name = variable[1] + '.' + subroutine
                args += 1
            elif(self.method_name + '.' + name in self.symbol_table):
                variable = self.symbol_table[self.method_name + '.' + name]

                self.parsed += "push " + variable[0] + ' ' + str(variable[2]) + '\n'
                function_name = variable[1] + '.' + subroutine
                args += 1
        elif(' ( ' in self.tokens[self.i]):
            function_name = self.class_name + '.' + name
            args += 1
            self.parsed += "push pointer 0\n"
        
        self.i += 1
        args += self.compileExpressionList()
        self.i += 1

        self.parsed += "call " + function_name + ' ' + str(args) + '\n'


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('No file was given')
        exit(-1)

    file_path = sys.argv[1]
    
    file_exists = os.path.isdir(file_path)

    if(file_exists):
        files = [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]
        for file_path in files:
            if(file_path.endswith(".jack")):
                cleaner = Cleaner(file_path)
                parsed_code = cleaner.clean_commands()
                cleaner.close_file()

                tokenizer = Tokenizer(parsed_code)
                result0 = tokenizer.tokenize()

                tokens = result0.split('\n')[1:-2]

                parser = Parser(tokens)
                parser.compileClass()
                result1 = parser.getResult()

                new_file_path1 = file_path[:-5] + ".vm"

                out_file1 = open(new_file_path1, "w+")
                out_file1.write(result1);
                out_file1.close()
            else:
                print("Wrong file type")
    else:
        print("No such directory")