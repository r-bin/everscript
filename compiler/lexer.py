from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('SIGNED', 'signed(?=\ )')
        self.lexer.add('T_NONE', 'None')
        self.lexer.add('T_BYTE', 'Byte')
        self.lexer.add('T_WORD', 'Word')
        self.lexer.add('T_MEMORY', 'Memory')
        self.lexer.add('T_FUNCTION', 'Function')
        self.lexer.add('T_ARG', 'Arg')
        self.lexer.add('IS', 'is(?=\ )')
        self.lexer.add('!IS', '!is(?=\ )')

        self.lexer.add('VAL', 'val(?=\ )')
        self.lexer.add('VAR', 'var(?=\ )')
        
        self.lexer.add('STRING', '\".*?\"')
        self.lexer.add('STRING_RAW', '\'.*?\'')

        self.lexer.add('\n', '\n')
        self.lexer.add(';', ';')
        self.lexer.add('..', '\.\.')

        self.lexer.add('AND', '\&\&')
        self.lexer.add('OR', '\|\|')

        self.lexer.add('OR=', '\|\=')
        self.lexer.add('&=', '\&\=')
        self.lexer.add('==', '\=\=')
        self.lexer.add('!=', '\!\=')
        self.lexer.add('<=', '\<\=')
        self.lexer.add('>=', '\>\=')
        self.lexer.add('=', '\=')
        self.lexer.add('<<=', '\<\<\=')
        self.lexer.add('>>=', '\>\>\=')
        self.lexer.add('*=', '\*\=')
        self.lexer.add('/=', '\/\=')
        self.lexer.add('-=', '\-\=')
        self.lexer.add('+=', '\+\=')
        self.lexer.add('++', '\+\+')
        self.lexer.add('--', '\-\-')
        
        self.lexer.add('(', '\(')
        self.lexer.add(')', '\)')
        self.lexer.add(',', '\,')
        self.lexer.add('{', '\{')
        self.lexer.add('}', '\}')
        self.lexer.add('[', '\[')
        self.lexer.add(']', '\]')
        self.lexer.add('<', '\<(?!\<)')
        self.lexer.add('>', '\>(?!\>)')
        
        self.lexer.add('~', '\~(?!=)')
        self.lexer.add('!', '\!(?!=)')
        self.lexer.add('+', '\+(?= )')
        self.lexer.add('-', '\-(?= )')
        self.lexer.add('*', '\*')
        self.lexer.add('/', '\/')
        self.lexer.add('<<', '\<\<')
        self.lexer.add('>>', '\>\>')
        self.lexer.add('B_AND', '\&(?![\&\=])')
        self.lexer.add('B_OR', '\|(?![\|\=])')
        self.lexer.add('B_XOR', '\^')

        self.lexer.add('INVERT_WORD', '\-(?=\()')
        
        self.lexer.add('>', '\>')
        self.lexer.add('<', '\<')

        self.lexer.add('TRUE', 'True(?![a-zA-Z_])')
        self.lexer.add('FALSE', 'False(?![a-zA-Z_])')
        #self.lexer.add('ADDRESS', '0[xX][0-9a-fA-F]{6}')
        self.lexer.add('WORD', '[\+\-]{0,1}0[xX][0-9a-fA-F]+')
        self.lexer.add('WORD_DECIMAL', '[\+\-]{0,1}0[dD][0-9]+')
        #self.lexer.add('word', '[0-9]+')
        self.lexer.add('ENUM_CALL', '[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z][a-zA-Z0-9_]*')
        #self.lexer.add('ENUM_IDENTIFIER', '[a-zA-Z][a-zA-Z0-9]+')

        #self.lexer.add('END', 'return')
        self.lexer.add('LABEL_DESTINATION', '[A-Z][A-Z_]*:')
        #self.lexer.add('LABEL_JUMP', '[A-Z][A-Z_]*')

        self.lexer.add('ENUM', 'enum(?!\()')
        self.lexer.add('ELSEIF!', 'else if!(?=\()')
        self.lexer.add('ELSEIF', 'else if(?=\()')
        self.lexer.add('IF_CURRENCY', 'if_currency(?=\()')
        self.lexer.add('IF!', 'if!(?=\()')
        self.lexer.add('IF', 'if(?=\()')
        self.lexer.add('ELSE', 'else(?=\s*\{)')
        
        self.lexer.add('WHILE!', 'while!(?=\()')
        self.lexer.add('WHILE', 'while(?=\()')

        self.lexer.add('@', '@')
        self.lexer.add(':', ':')
        self.lexer.add('?', '\?')

        self.lexer.add('FUN_INCLUDE', '#include(?=\()')
        self.lexer.add('FUN_MEMORY', '#memory(?=\()')
        self.lexer.add('FUN_PATCH', '#patch(?=\()')

        self.lexer.add('MEMORY', 'memory(?=\()')
        self.lexer.add('OBJECT', 'object(?=\[)')
        self.lexer.add('ARG', 'arg(?=\[)')
        self.lexer.add('SCRIPT', 'script(?=\[)')
        self.lexer.add('TIME', 'time(?=\[)')

        self.lexer.add('FUN', 'fun(?=\ )')
        self.lexer.add('NAME_IDENTIFIER', '[a-z_][a-z0-9][a-z0-9_]*(?=\()')
        self.lexer.add('MAP', 'map(?=\ )')
        self.lexer.add('AREA', 'area(?=\ )')
        self.lexer.add('GROUP', 'group(?=\ )')
        
        self.lexer.add('IDENTIFIER', '[a-zA-Z_][a-zA-Z0-9_]*(?![\(\{])')

        # ignore whitespace 
        self.lexer.ignore('[ \t\r\f\v\n]+|\/\/.*\n')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()