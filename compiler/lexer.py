"""EverScript lexer.

Wraps `rply`'s :class:`~rply.LexerGenerator` with all token definitions for
the EverScript language.  Call :meth:`Lexer.get_lexer` once to obtain a
compiled lexer instance, then reuse it for every file.

Token ordering matters in rply: rules are tried in the order they are added
and the first match wins.  Compound operators (``<<=``, ``>>=``, etc.) must
be added **before** their component characters (``<``, ``>``, etc.).
"""

from rply import LexerGenerator


class Lexer:
    """Builds and caches the EverScript token rule set.

    Typical usage::

        lexer = Lexer().get_lexer()
        tokens = list(lexer.lex(source_text))
    """

    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        """Register all EverScript token rules with the underlying LexerGenerator.

        Rules are added in priority order — longest / most specific patterns
        first.  The ignore rule at the end strips whitespace and ``//`` line
        comments.

        Notable design choices:

        - ``SIGNED``, ``IS``, ``IN``, ``VAL``, ``VAR`` etc. use a
          look-ahead ``(?=\ )`` so they only match when followed by a space,
          preventing accidental matches inside identifiers.
        - Compound assignment operators (``<<=``, ``>>=``, ``*=``, …) are
          registered before their component characters.
        - ``<`` and ``>`` use a negative look-ahead (``(?!<)``, ``(?!>)``) to
          avoid shadowing ``<<`` and ``>>``.
        - ``NAME_IDENTIFIER`` matches lower-case function call heads
          (``name(…)``); ``IDENTIFIER`` covers everything else.
        """
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
        # Only exact triple-slash comments are doc comments. Longer slash
        # separators (////...) should stay regular ignored comments.
        self.lexer.add('DOC_COMMENT', r'///(?!/)[^\n]*')
        self.lexer.add('/', r'\/(?!\/)')
        self.lexer.add('<<', r'\<\<')
        self.lexer.add('>>', r'\>\>')
        self.lexer.add('B_AND', r'\&(?![\&\=])')
        self.lexer.add('B_OR', r'\|(?![\|\=])')
        self.lexer.add('B_XOR', r'\^')

        self.lexer.add('INVERT_WORD', r'\-(?=\()')

        # The unconditional '<' and '>' rules below are unreachable: the
        # look-ahead versions above already cover every case.  Removed.
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

        self.lexer.add('#IF', '#if')
        self.lexer.add('#ENDIF', '#endif')

        self.lexer.add('MEMORY', r'memory(?=\()')
        self.lexer.add('OBJECT', r'object(?=\[)')
        self.lexer.add('ARG', r'arg(?=\[)')
        self.lexer.add('SCRIPT', r'script(?=\[)')
        self.lexer.add('TIME', r'time(?=\[)')

        self.lexer.add('FUN', r'fun(?=\ )')
        # NAME_IDENTIFIER matches a lower-case identifier immediately followed
        # by '(' — i.e. a function call head.  Requires at least one char after
        # the leading [a-z_] so that single-char names like f( are also matched.
        self.lexer.add('NAME_IDENTIFIER', r'[a-z_][a-z0-9_]*(?=\()')
        self.lexer.add('MAP', r'map(?=\ )')
        self.lexer.add('AREA', r'area(?=\ )')
        self.lexer.add('GROUP', r'group(?=\ )')
        
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*(?![\(\{])')

        # Ignore whitespace and regular line comments. Exact /// lines are left
        # for DOC_COMMENT; 4+ slash separators fall back here as normal comments.
        self.lexer.ignore(r'[ \t\r\f\v\n]+|\/\/(?:\/{2,}[^\n]*|(?!\/)[^\n]*)\n?')

    def get_lexer(self):
        """Build and return the compiled rply lexer.

        Call this once and reuse the result.  Calling it multiple times
        re-registers all token rules and builds a fresh lexer, which is
        expensive.

        Returns:
            A compiled rply ``Lexer`` instance ready for :meth:`lex` calls.
        """
        self._add_tokens()
        return self.lexer.build()