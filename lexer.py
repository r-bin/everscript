from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('\n', '\n')
        self.lexer.add(';', ';')

        self.lexer.add('(', '\(')
        self.lexer.add(')', '\)')
        self.lexer.add(',', '\,')
        self.lexer.add('{', '\{')
        self.lexer.add('}', '\}')
        self.lexer.add('[', '\[')
        self.lexer.add(']', '\]')
        
        self.lexer.add('==', '\=\=')
        self.lexer.add('=', '\=')
        
        self.lexer.add('!', '\!')

        #self.lexer.add('ADDRESS', '0[xX][0-9a-fA-F]{6}')
        self.lexer.add('WORD', '0[xX][0-9a-fA-F]+')
        #self.lexer.add('word', '[0-9]+')
        self.lexer.add('STRING', '\".*\"')
        self.lexer.add('ENUM_CALL', '[a-zA-Z_][a-zA-Z0-9_]+\.[a-zA-Z][a-zA-Z0-9_]+')
        #self.lexer.add('ENUM_IDENTIFIER', '[a-zA-Z][a-zA-Z0-9]+')

        self.lexer.add('END', 'return')
        self.lexer.add('LABEL_DESTINATION', '[A-Z][A-Z_]*:')
        #self.lexer.add('LABEL_JUMP', '[A-Z][A-Z_]*')

        self.lexer.add('ENUM', 'enum(?!\()')
        self.lexer.add('ELSEIF', 'else if(?=\()')
        self.lexer.add('IF', 'if(?=\()')
        self.lexer.add('ELSE', 'else(?=\s*\{)')

        self.lexer.add('FUNCTION_EVAL', 'eval(?=\()')
        self.lexer.add('FUNCTION_GOTO', 'goto(?=\()')
        self.lexer.add('FUNCTION_CODE', 'code(?=\()')
        
        self.lexer.add('FUN_INSTALL', '@install(?=\()')
        self.lexer.add('FUN_INJECT', '@inject(?=\()')

        self.lexer.add('FUN', 'fun(?=\ )')
        self.lexer.add('FUN_IDENTIFIER', '[a-z_][a-z0-9_]+(?=\()')
        
        self.lexer.add('IDENTIFIER', '[a-zA-Z_][a-zA-Z0-9_]*(?![\(\{])')

        # ignore whitespace 
        self.lexer.ignore('[ \t\r\f\v\n]+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()