from injector import Injector, inject
_injector = Injector()

from utils.file_utils import *
from .patch_handler import PatchHandler
from .patch_handler_txt import PatchHandlerTxt

from pathlib import Path
import shutil
import os
from os.path import exists
from rply import LexerGenerator, Token
from rply import ParserGenerator


class PatchHandlerSliver(PatchHandler):
    @inject
    def __init__(self, patch_handler_txt: PatchHandlerTxt):
        self._patch_handler_txt = patch_handler_txt

    def prepare_patch(self, rom_file, directory_patch, patch, params=[]):
        # print(f" - converting patch {patch.name} to {patch.with_suffix('.txt').name} ({os.path.getsize(patch)})")

        code = self._parse_file(patch)

        file_out = patch.with_suffix('.txt')
        file_utils.dump(code, file_out)

        return self._patch_handler_txt.prepare_patch(rom_file, directory_patch, file_out)

    def _parse_file(self, file):
            code = file_utils.file2string(file)
            
            class Lexer():
                def __init__(self):
                    self.lexer = LexerGenerator()

                def _add_tokens(self):
                    self.lexer = LexerGenerator()
                    self.lexer.add('ADDRESS', '@0x[0-9a-f]+')
                    self.lexer.add('WORD', '[0-9a-f]{2}')
                    self.lexer.add('END', '@')

                    self.lexer.ignore('[ \t\r\f\v\n]+|\/\/.*\n|#set|#endif|#ifndef.*$')

                def get_lexer(self):
                    self._add_tokens()
                    return self.lexer.build()

            lexer = Lexer().get_lexer()
            lexed = lexer.lex(code)

            class Patch:
                def __init__(self, list):
                    self.list = list

                def eval(self):
                    code = ""
                    
                    code += "PATCH"
                    code += "\n\n"

                    for m in self.list:
                        address = m.address
                        address = address.value
                        address = address.replace('@', '')
                        address = int(address, 16)
                        
                        if address >= 0xC00000: # TODO
                            address -= 0xC00000
                        elif address >= 0x800000: # TODO
                            address -= 0x800000
                        elif address >= 0x400000: # TODO
                            address -= 0x400000
                                    
                        code += f"{'{:06x}'.format(address, 'x')} {'{:04x}'.format(m.count, 'x')}\n"
                        code += m.eval()
                        code += "\n"

                    code += "\n\n"
                    code += "EOF"

                    return code


            class Method:
                def __init__(self, address, code):
                    self.address = address
                    self.code = code
                    self.count = len(code)

                def eval(self):
                    code = ""
                    
                    code = ' '.join(c.value for c in self.code)
                    return code

            class Parser():
                def __init__(self):
                    self.pg = ParserGenerator(
                        # A list of all token names accepted by the parser.
                        [
                            'ADDRESS', 'WORD', 'END'
                        ]
                    )
                
                def parse(self):

                    @self.pg.production('PATCH : METHOD_LIST')
                    def parse(p):
                        return Patch(p[0])
                    
                    @self.pg.production('METHOD_LIST : METHOD')
                    def parse(p):
                        return [ p[0] ]
                    @self.pg.production('METHOD_LIST : METHOD_LIST METHOD')
                    def parse(p):
                        return p[0] + [ p[1] ]
                    
                    @self.pg.production('METHOD : ADDRESS CODE END')
                    def parse(p):
                        return Method(p[0], p[1])
                    @self.pg.production('METHOD : ADDRESS CODE')
                    def parse(p):
                        return Method(p[0], p[1])
                    
                    @self.pg.production('CODE : CODE WORD')
                    def parse(p):
                        return p[0] + [ p[1] ]
                    @self.pg.production('CODE : WORD')
                    def parse(p):
                        return [ p[0] ]
                    
                    @self.pg.error
                    def error_handle_lex(token):
                        raise ValueError(token)
                    
                def get_parser(self):
                    return self.pg.build()
                    
            pg = Parser()
            pg.parse()
            parser = pg.get_parser()

            code = parser.parse(lexed)
            code = code.eval()

            return code