import pathlib
import shutil
import os, subprocess
from os.path import exists
import shutil
import binascii
from textwrap import wrap
from pathlib import Path
import copy
import ujson
import re
import sys, getopt

from ips_util import Patch
from subprocess import call

from rply import LexerGenerator, Token
from rply import ParserGenerator

class FileUtils():
    def file2string(self, file):
        with open(file, 'r') as f:
            return f.read()

class ObjectUtils():
    def deepcopy(self, object):
        if False:
            return copy.deepcopy(object)
        else:
            return ujson.loads(ujson.dumps(object))

class StringUtils():
    def beautify_output(self, output):
        l = []
        m = 0
        for line in output.splitlines():
            s = line.split("//")
            m = max(m, len(s[0]))
            l.append(s)
        
        m = min(m, 27)
        l2 = []
        for line in l:
            if len(line) == 1:
                l2.append(line[0].strip())
            elif not line[0]:
                l2.append("// " + line[1].strip())
            else:
                l2.append(line[0].strip().ljust(m) + "// " + line[1].strip())

        r = '\n'.join(l2)

        r = re.sub("\n([0-9a-fA-F]{6})", r"\n\n\1", r)

        return r

class OutUtils():
    _target_size = 4 * 1024 * 1024
    _original_size = 3 * 1024 * 1024

    _out = "./out"
    _tmp = os.path.join(_out, "tmp")
    _patches = os.path.join(_out, "patches")

    def __init__(self, sub_dir = None):
        if(sub_dir == None):
            self._out = self._parse_out()
        else:
            self._out = os.path.join(self._parse_out(), sub_dir)
            Path(self._out).mkdir(parents=True, exist_ok=True)
        self._tmp = os.path.join(self._out, "tmp")
        self._patches = os.path.join(self._out, "patches")

    def init_out(self):
        self.clean_out()

        Path(self._out).mkdir(parents=True, exist_ok=True)
        Path(self._tmp).mkdir(parents=True, exist_ok=True)
        Path(self._patches).mkdir(parents=True, exist_ok=True)


    def _parse_out(self):
        output_dir = "out"

        argv = sys.argv
        argv = argv[1:]

        try:
            opts, args = getopt.getopt(argv,"hpr:s:o:",["profile", "rom=", "script=", "patches=", "out="])
        except getopt.GetoptError:
            help()

        for opt, arg in opts:
            if opt in ("-o", "--out"):
                output_dir = arg
        
        return output_dir

    def extend_rom(self, file_in, file_out):
        destfile = pathlib.Path(file_out)
        shutil.copyfile(file_in, destfile)

        required_padding = self._target_size - destfile.stat().st_size
        if required_padding > 0:
            with destfile.open("ab") as outfile:
                outfile.write(b"\x00" * required_padding)

    def clean_out(self):        
        if os.path.exists(self._out) and os.path.isdir(self._out):
            shutil.rmtree(self._out)
        os.mkdir(self._out)

    def dump(self, text, file):
        text_file = open(os.path.join(self._out, file), "w")
        text_file.write(text)
        text_file.close()

    def clean(self, script):
        cleaned_script = re.sub("//.*", "", script)
        cleaned_script = re.sub("[\s]+", " ", cleaned_script)
        cleaned_script = cleaned_script.strip()

        return cleaned_script

    def txt_to_ips(self, code, file):
        with open(file, 'wb') as fout:
            for e in code.split(' '):
                match e:
                    case ("PATCH"|"EOF"):
                        fout.write(e.encode('ASCII'))
                    case _ if len(e) == 2:
                        fout.write(binascii.unhexlify(e))
                    case _:
                        [fout.write(binascii.unhexlify(b)) for b in wrap(e, 2)]

    def file(self, script, file): # TODO
        with open(f"{self._out}/{file}", 'wb') as fout:
            for e in script.split(' '):
                match e:
                    case ("PATCH"|"EOF"):
                        fout.write(e.encode('ASCII'))
                    case _ if len(e) == 2:
                        fout.write(binascii.unhexlify(e))
                    case _:
                        [fout.write(binascii.unhexlify(b)) for b in wrap(e, 2)]

    def _safe_delete(self, file):
        if exists(file):
            size = os.path.getsize(file)

            if size == self._target_size or size == self._original_size:
                print(f"removed old file {file} ({size})...")
                os.remove(file)
            else:
                raise Exception(f"failed to delete {file} ({self.size} != {size})")

    def _extend_rom(self, file):
        file_size = os.path.getsize(file)

        if file_size < self._target_size:
            print(f"extending ROM {file} ({file_size} -> {self._target_size})")
            if exists(self._tmp):
                os.rmdir(self._tmp)
            self.extend_rom(file, self._tmp)

        os.remove(file)
        shutil.copyfile(self._tmp, file)
        os.remove(self._tmp)

    def _patch_for_name(self, directory_in, name):
        patch = []

        for file in os.scandir(directory_in):
            file = Path(file)

            if file.stem == name:
                patch.append(file)

        if len(patch) == 1:
            return patch[0]
        else:
            raise Exception(f"multiple files for patch {name} found ({patch})")

    def prepare_rom(self, rom_in):
        if rom_in != None:
            rom_in = Path(rom_in)
            
            target_name = os.path.join(self._out, rom_in.name)
            shutil.copyfile(rom_in, target_name)

            self._extend_rom(target_name)

    def prepare_patches(self, rom_file, directory_in, patches):
        if rom_file != None:
            rom_file = os.path.join(self._out, rom_file)
            rom_file = Path(rom_file)

        for patch in patches:
            patch = self._patch_for_name(directory_in, patch)

            copied_patch = os.path.join(self._patches, patch.name)
            copied_patch = Path(copied_patch)
            shutil.copy(patch, copied_patch)

            match patch.suffix:
                case ".asm":
                    self._prepare_patch_asm(rom_file, self._patches, copied_patch)
                case ".sliver":
                    self._prepare_patch_sliver(rom_file, self._patches, copied_patch)
                case ".evs":
                    self._prepare_patch_evs(rom_file, self._patches, copied_patch)
                case ".txt":
                    self._prepare_patch_txt(rom_file, self._patches, copied_patch)
                case ".ips":
                    self._prepare_patch_ips(rom_file, self._patches, copied_patch)
                case _:
                    raise Exception(f"unknown patch extension for '{patch}'")

    def _prepare_patch_ips(self, rom_file, directory_patch, patch):
        self._apply_patch(rom_file, patch)

    def _prepare_patch_asm(self, rom_file, directory_patch, patch):
        # print(f" - compiling patch {patch} ({os.path.getsize(patch)})")

        tmp_rom = os.path.join(self._patches, patch.stem)
        tmp_rom = Path(tmp_rom)
        tmp_rom = tmp_rom.with_suffix('.sfc')
        shutil.copy(rom_file, tmp_rom)

        call_args = ["asar", patch, tmp_rom]
        call(call_args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        diff = os.path.join(directory_patch, patch.stem)
        diff = Path(tmp_rom)
        diff = tmp_rom.with_suffix('.ips')
        self._create_rom_diff(rom_file, tmp_rom, diff)

        self._prepare_patch_ips(rom_file, directory_patch, diff)
    
    def _prepare_patch_txt(self, rom_file, directory_patch, patch):
        # print(f" - compiling patch {patch} ({os.path.getsize(patch)})")

        with patch.open() as f:
            p = f.read()
            p = self.clean(p)

            patch_ips = patch.with_suffix(".ips")

            self.txt_to_ips(p, patch.with_suffix(".ips"))

            self._prepare_patch_ips(rom_file, directory_patch, patch_ips)

    def _prepare_patch_evs(self, rom_file, directory_patch, patch):
        # print(f" - compiling patch {patch} to {patch.with_suffix('.txt').name} ({os.path.getsize(patch)})")

        with patch.open() as f:
            p = f.read()
            p = self.clean(p)

            argv = sys.argv
            argv = argv[1:]

            input_file = None
            output_dir = "out"

            try:
                opts, args = getopt.getopt(argv,"hpr:s:o:",["profile", "rom=", "script=", "patches=", "out="])
            except getopt.GetoptError:
                help()

            if len(args) == 1:
                input_file = args[0]
            else:
                help()

            for opt, arg in opts:
                if opt in ("-r", "--rom"):
                    rom_file = arg
                elif opt in ("-o", "--out"):
                    output_dir = arg

            quiet = True
            # print(f" - compiling patch {patch.name} to {patch.with_suffix('.txt').name}")
            call_args = ["python3.11", f"./everscript.py", f"--out=./{output_dir}/patches/{patch.stem}/", f"{patch}"]

            if quiet:
                call(call_args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            else:
                call(call_args)

            patch_from = f"./{output_dir}/patches/{patch.stem}/patch.txt"
            patch_to = patch.with_suffix('.txt')
            shutil.copy(patch_from, patch_to)

            self._prepare_patch_txt(rom_file, directory_patch, patch_to)
        
    def _prepare_patch_sliver(self, rom_file, directory_patch, patch):
        print(f" - converting patch {patch.name} to {patch.with_suffix('.txt').name} ({os.path.getsize(patch)})")

        with patch.open() as f:
            code = f.read()
            
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

            # TODO: use dump()
            text_file = open(patch.with_suffix('.txt'), "w")
            text_file.write(code)
            text_file.close()

            self._prepare_patch_txt(rom_file, directory_patch, text_file)

    def _apply_patch(self, file, patch):
        patch_records = Patch.load(patch)
        patch_size = os.path.getsize(patch)

        print(f" - applying patch {patch} ({patch_size})")
        if exists(self._tmp):
            os.remove(self._tmp)
        with open(file, 'rb') as f_in:
            with open(self._tmp, 'w+b') as f_out:
                f_out.write(patch_records.apply(f_in.read()))

        os.remove(file)
        shutil.copyfile(self._tmp, file)
        os.remove(self._tmp)

    def _create_rom_diff(self, file_in, file_out, file_patch):
        patch = None
        with open(file_in, 'rb') as f_in:
            with open(file_out, 'rb') as f_out:
                patch = Patch.create(f_in.read(), f_out.read())

                with open(file_patch, 'w+b') as f_patch:
                    f_patch.write(patch.encode())
            
    def patch(self, file_in, patch):
        file_name = os.path.splitext(file_in)
        file_size = os.path.getsize(file_in)

        file_patch = Path(os.path.join(self._out, patch))

        print(f"patching {file_in} ({file_size}) + {file_patch.name} ({os.path.getsize(file_patch)})...")

        target_name = os.path.join(self._out, file_in)
        
        self._apply_patch(target_name, file_patch)
        self._create_rom_diff(file_in, target_name, os.path.join(self._out, "everscript.combined.ips"))

        print(f"patched successfully! {file_in} ({file_size}) + {file_patch.name} ({os.path.getsize(file_patch)}) -> {target_name} ({os.path.getsize(target_name)})")

fileUtils = FileUtils()
stringUtils = StringUtils()
objectUtils = ObjectUtils()