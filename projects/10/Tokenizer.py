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
                xml_string += ("<stringConstant> " + tok.rstrip() + " </stringConstant>\n")
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
        self.parsed = ""

    def getResult(self):
        return self.parsed
    
    def compileClass(self):
        self.parsed += "<class>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        while(self.tokens[self.i] == "<keyword> static </keyword>" or self.tokens[self.i] == "<keyword> field </keyword>"):
            self.compileClassVarDec()

        while(self.tokens[self.i] == "<keyword> constructor </keyword>" or self.tokens[self.i] == "<keyword> method </keyword>" or self.tokens[self.i] == "<keyword> function </keyword>"):
            self.compileDeclaration()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.parsed += "</class>\n"

    def compileDeclaration(self):
        self.parsed += "<subroutineDec>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileParameterList()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileBody()

        self.parsed += "</subroutineDec>\n"

    def compileBody(self):
        self.parsed += "<subroutineBody>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        while(self.tokens[self.i] == "<keyword> var </keyword>"):
            self.compileVarDec()
        
        self.compileStatements()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.parsed += "</subroutineBody>\n"

    def compileStatements(self):
        self.parsed += "<statements>\n"

        while( " let " in self.tokens[self.i] or " if " in self.tokens[self.i] or " while " in self.tokens[self.i] or " do " in self.tokens[self.i] or " return " in self.tokens[self.i] ):
            if(" let " in self.tokens[self.i]):
                self.compileLet()
            elif(" if " in self.tokens[self.i]):
                self.compileIf()
            elif(" while " in self.tokens[self.i]):
                self.compileWhile()
            elif(" do " in self.tokens[self.i]):
                self.compileDo()
            elif(" return " in self.tokens[self.i]):
                self.compileReturn()

        self.parsed += "</statements>\n"

    def compileLet(self):
        self.parsed += "<letStatement>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        if(self.tokens[self.i] == "<symbol> [ </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

            self.compileExpression()

            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileExpression()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.parsed += "</letStatement>\n"

    def compileIf(self):
        self.parsed += "<ifStatement>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileExpression()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileStatements()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        if(" else " in self.tokens[self.i]):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

            self.compileStatements()

            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

        self.parsed += "</ifStatement>\n"

    def compileWhile(self):
        self.parsed += "<whileStatement>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileExpression()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileStatements()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.parsed += "</whileStatement>\n"

    def compileDo(self):
        self.parsed += "<doStatement>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        if(self.tokens[self.i] == "<symbol> . </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.compileExpressionList()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1  

        self.parsed += "</doStatement>\n"

    def compileReturn(self):
        self.parsed += "<returnStatement>\n"

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        if(self.tokens[self.i] != "<symbol> ; </symbol>"):
            self.compileExpression()

        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1
        
        self.parsed += "</returnStatement>\n"

    def compileExpressionList(self):
        self.parsed += "<expressionList>\n"

        while(self.tokens[self.i] != "<symbol> ) </symbol>"):
            if(self.tokens[self.i] == "<symbol> , </symbol>"):
                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1

            self.compileExpression()

        self.parsed += "</expressionList>\n"

    def compileExpression(self):
        self.parsed += "<expression>\n"

        self.compileTerm()

        while(self.tokens[self.i].startswith("<symbol>") and (' + ' in self.tokens[self.i] or ' - ' in self.tokens[self.i] or ' * ' in self.tokens[self.i] or ' / ' in self.tokens[self.i] or ' | ' in self.tokens[self.i] or ' = ' in self.tokens[self.i] or ' &amp; ' in self.tokens[self.i] or ' &lt; ' in self.tokens[self.i] or ' &gt; ' in self.tokens[self.i] ) ):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
            self.compileTerm()

        self.parsed += "</expression>\n"

    def compileTerm(self):
        self.parsed += "<term>\n"

        if(self.tokens[self.i] == "<symbol> - </symbol>" or self.tokens[self.i] == "<symbol> ~ </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
            self.compileTerm()
        elif(self.tokens[self.i] == "<symbol> ( </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

            self.compileExpression()

            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
        else:
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1

            if(self.tokens[self.i] == "<symbol> [ </symbol>"):
                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1

                self.compileExpression()

                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1
            elif(self.tokens[self.i] == "<symbol> ( </symbol>"):
                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1

                self.compileExpressionList()

                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1
            elif(self.tokens[self.i] == "<symbol> . </symbol>"):
                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1
                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1
                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1

                self.compileExpressionList()

                self.parsed += self.tokens[self.i] + "\n"
                self.i += 1
        
        self.parsed += "</term>\n"

    def compileVarDec(self):
        self.parsed += "<varDec>\n"
        
        while(self.tokens[self.i] != "<symbol> ; </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
        
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.parsed += "</varDec>\n"

    def compileParameterList(self):
        self.parsed += "<parameterList>\n"

        while(self.tokens[self.i] != "<symbol> ) </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
        
        self.parsed += "</parameterList>\n"

    def compileClassVarDec(self):
        self.parsed += "<classVarDec>\n"
        
        while(self.tokens[self.i] != "<symbol> ; </symbol>"):
            self.parsed += self.tokens[self.i] + "\n"
            self.i += 1
        
        self.parsed += self.tokens[self.i] + "\n"
        self.i += 1

        self.parsed += "</classVarDec>\n"


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('No file was given')
        exit(-1)

    file_path = sys.argv[1]
    
    file_exists = os.path.isfile(file_path)

    if(file_exists):
        if(file_path.endswith(".jack")):
            cleaner = Cleaner(file_path)
            parsed_code = cleaner.clean_commands()
            cleaner.close_file()

            tokenizer = Tokenizer(parsed_code)
            result0 = tokenizer.tokenize()

            new_file_path0 = file_path[:-5] + "Tokenized.xml"

            out_file0 = open(new_file_path0, "w+")
            out_file0.write(result0);
            out_file0.close()

            tokens = result0.split('\n')[1:-2]

            parser = Parser(tokens)
            parser.compileClass()
            result1 = parser.getResult()

            new_file_path1 = file_path[:-5] + "Parsed.xml"

            out_file1 = open(new_file_path1, "w+")
            out_file1.write(result1);
            out_file1.close()
        else:
            print("Wrong file type")
    else:
        print("No such file")