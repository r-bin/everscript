from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('SIGNED', r'signed(?=\ )')
        self.lexer.add('T_NONE', 'None')
        self.lexer.add('T_BYTE', 'Byte')
        self.lexer.add('T_WORD', 'Word')
        self.lexer.add('T_MEMORY', 'Memory')
        self.lexer.add('T_FUNCTION', 'Function')
        self.lexer.add('T_ARG', 'Arg')
        self.lexer.add('IS', r'is(?=\ )')
        self.lexer.add('!IS', r'!is(?=\ )')

        self.lexer.add('VAL', r'val(?=\ )')
        self.lexer.add('VAR', r'var(?=\ )')
        
        self.lexer.add('STRING', r'".*?"')
        self.lexer.add('STRING_RAW', r"'.*?'")

        self.lexer.add('\n', '\n')
        self.lexer.add(';', ';')
        self.lexer.add('..', r'\.\.')

        self.lexer.add('IN', r'in(?=\ )')

        self.lexer.add('AND', r'\&\&')
        self.lexer.add('OR', r'\|\|')

        self.lexer.add('OR=', r'\|\=')
        self.lexer.add('&=', r'\&\=')
        self.lexer.add('==', r'\=\=')
        self.lexer.add('!=', r'\!\=')
        self.lexer.add('<=', r'\<\=')
        self.lexer.add('>=', r'\>\=')
        self.lexer.add('=', r'\=')
        self.lexer.add('<<=', r'\<\<\=')
        self.lexer.add('>>=', r'\>\>\=')
        self.lexer.add('*=', r'\*\=')
        self.lexer.add('/=', r'\/\=')
        self.lexer.add('-=', r'\-\=')
        self.lexer.add('+=', r'\+\=')
        self.lexer.add('++', r'\+\+')
        self.lexer.add('--', r'\-\-')
        
        self.lexer.add('(', r'\(')
        self.lexer.add(')', r'\)')
        self.lexer.add(',', r'\,')
        self.lexer.add('{', r'\{')
        self.lexer.add('}', r'\}')
        self.lexer.add('[', r'\[')
        self.lexer.add(']', r'\]')
        self.lexer.add('<', r'\<(?!\<)')
        self.lexer.add('>', r'\>(?!\>)')
        
        self.lexer.add('~', r'\~(?!=)')
        self.lexer.add('!', r'\!(?!=)')
        self.lexer.add('+', r'\+(?= )')
        self.lexer.add('-', r'\-(?= )')
        self.lexer.add('*', r'\*')
        self.lexer.add('/', r'\/')
        self.lexer.add('<<', r'\<\<')
        self.lexer.add('>>', r'\>\>')
        self.lexer.add('B_AND', r'\&(?![\&\=])')
        self.lexer.add('B_OR', r'\|(?![\|\=])')
        self.lexer.add('B_XOR', r'\^')

        self.lexer.add('INVERT_WORD', r'\-(?=\()')
        
        self.lexer.add('>', r'\>')
        self.lexer.add('<', r'\<')

        self.lexer.add('TRUE', r'True(?![a-zA-Z_])')
        self.lexer.add('FALSE', r'False(?![a-zA-Z_])')
        #self.lexer.add('ADDRESS', '0[xX][0-9a-fA-F]{6}')
        self.lexer.add('WORD', r'[\+\-]{0,1}0[xX][0-9a-fA-F]+')
        self.lexer.add('WORD_DECIMAL', r'[\+\-]{0,1}0[dD][0-9]+')
        #self.lexer.add('word', '[0-9]+')
        self.lexer.add('ENUM_CALL', r'[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z][a-zA-Z0-9_]*')
        #self.lexer.add('ENUM_IDENTIFIER', '[a-zA-Z][a-zA-Z0-9]+')

        #self.lexer.add('END', 'return')
        self.lexer.add('LABEL_DESTINATION', '[A-Z][A-Z_]*:')
        #self.lexer.add('LABEL_JUMP', '[A-Z][A-Z_]*')

        self.lexer.add('ENUM', r'enum(?!\()')
        self.lexer.add('ELSEIF!', r'else if!(?=\()')
        self.lexer.add('ELSEIF', r'else if(?=\()')
        self.lexer.add('IF_CURRENCY', r'if_currency(?=\()')
        self.lexer.add('IF!', r'if!(?=\()')
        self.lexer.add('IF', r'if(?=\()')
        self.lexer.add('ELSE', r'else(?=\s*\{)')
        
        self.lexer.add('WHILE!', r'while!(?=\()')
        self.lexer.add('WHILE', r'while(?=\()')
        self.lexer.add('FOR', r'for(?=\()')

        self.lexer.add('@', '@')
        self.lexer.add(':', ':')
        self.lexer.add('?', r'\?')

        self.lexer.add('FUN_INCLUDE', r'#include(?=\()')
        self.lexer.add('FUN_MEMORY', r'#memory(?=\()')
        self.lexer.add('FUN_PATCH', r'#patch(?=\()')
        self.lexer.add('FUN_PATCH', r'#patch(?=\()')  # TODO: duplicate token — remove one

        self.lexer.add('#IF', '#if')
        self.lexer.add('#ENDIF', '#endif')

        self.lexer.add('MEMORY', r'memory(?=\()')
        self.lexer.add('OBJECT', r'object(?=\[)')
        self.lexer.add('ARG', r'arg(?=\[)')
        self.lexer.add('SCRIPT', r'script(?=\[)')
        self.lexer.add('TIME', r'time(?=\[)')

        self.lexer.add('FUN', r'fun(?=\ )')
        self.lexer.add('NAME_IDENTIFIER', r'[a-z_][a-z0-9][a-z0-9_]*(?=\()')
        self.lexer.add('MAP', r'map(?=\ )')
        self.lexer.add('AREA', r'area(?=\ )')
        self.lexer.add('GROUP', r'group(?=\ )')
        
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*(?![\(\{])')

        # ignore whitespace 
        self.lexer.ignore(r'[ \t\r\f\v\n]+|\/\/.*\n')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()