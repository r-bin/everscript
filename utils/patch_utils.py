from injector import Injector, inject
_injector = Injector()

from .parser.patch_handler_asm import *
from .parser.patch_handler_evs import *
from .parser.patch_handler_ips import *
from .parser.patch_handler_sliver import *
from .parser.patch_handler_txt import *

from pathlib import Path
import shutil
import os

class Patch():
    def __init__(self, name, params):
        self.name = name
        self.params = params

class PatchParam():
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Parser():
    def __init__(self):
        self.pg = ParserGenerator(
            [
                'NAME', '(', ')',
                '!', '=', 'VALUE', ',',
            ]
        )

    def parse(self):
        @self.pg.production('patch : NAME ( param_list )')
        def parse(p):
            name = p[0].value
            params = p[2]

            patch = Patch(name, params)

            return patch
        @self.pg.production('patch : NAME')
        def parse(p):
            name = p[0].value

            patch = Patch(name, [])

            return patch
        
        @self.pg.production('param_list : param_list , param')
        def parse(p):
            return p[0] + [ p[2] ]
        @self.pg.production('param_list : param')
        def parse(p):
            return [ p[0] ]

        @self.pg.production('param : ! NAME = VALUE')
        def parse(p):
            name = p[1].value
            value = p[3].value
            return PatchParam(name, value)
        
        @self.pg.error
        def error_handle_lex(token):
            raise ValueError(token)
        
    def get_parser(self):
        return self.pg.build()

class PatchUtils():
    def patch(self, rom_file, patches_in, patches_out, patches):
        self.prepare_patches(rom_file, patches_in, patches_out, patches)

    def parse_parameters(self, patch:str) -> Patch:
        script = patch

        lexer = LexerGenerator()
        lexer.add('(', '\(')
        lexer.add(')', '\)')
        lexer.add('!', '\!')
        lexer.add('NAME', '[a-zA-Z_][a-zA-Z0-9_]+')
        lexer.add('VALUE', '(?<!\!)[$a-zA-Z0-9]+')
        lexer.add('=', '\=')
        lexer.add(',', '\,')

        # ignore whitespace 
        lexer.ignore('[ ]+')

        lexer = lexer.build()
        lexed = lexer.lex(script)

        parser = Parser()
        parser.parse()

        parsed = parser.get_parser().parse(lexed)

        return parsed

    def prepare_patches(self, rom_file, patches_in, patches_out, patches):
        for patch in patches:
            patch = self.parse_parameters(patch)

            patch_in = self._patch_for_name(patches_in, patch.name)

            copied_patch = os.path.join(patches_out, patch_in.name)
            copied_patch = Path(copied_patch)
            shutil.copy(patch_in, copied_patch)

            print(f" - applying patch {patch}", end='')

            patch_handler = None
            match patch_in.suffix:
                case ".asm":
                    patch_handler = _injector.get(PatchHandlerAsm)
                case ".sliver":
                    patch_handler = _injector.get(PatchHandlerSliver)
                case ".evs":
                    patch_handler = _injector.get(PatchHandlerEvs)
                case ".txt":
                    patch_handler = _injector.get(PatchHandlerTxt)
                case ".ips":
                    patch_handler = _injector.get(PatchHandlerIps)
                case _:
                    raise Exception(f"unknown patch extension for '{patch_in}'")
                
            patch_out = patch_handler.prepare_patch(rom_file, patches_out, copied_patch, patch.params)
            
            ips_utils.apply_patch(rom_file, patch_out)

    def _patch_for_name(self, directory_patches, name):
        patch = []

        for file in os.scandir(directory_patches):
            file = Path(file)

            if file.stem == name:
                patch.append(file)

        match len(patch):
            case 0:
                raise Exception(f"no files for patch {name} found ({patch})")
            case 1:
                return patch[0]
            case _:
                raise Exception(f"multiple files for patch {name} found ({patch})")

patch_utils = _injector.get(PatchUtils)