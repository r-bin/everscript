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

    def prepare_patches(self, directory_in, patches):
        for patch in os.scandir(directory_in):
            patch = Path(patch)

            sub = patch.stem
            if [p for p in patches if sub in patches]:
                shutil.copy(patch, self._patches)

    def _apply_additional_patches(self, file, patches):
        for patch in sorted(os.listdir(patches)):
            patch = Path(os.path.join(patches, patch))

            filename = Path(patch)
            patch_size = os.path.getsize(patch)
            if filename.suffix == ".asm":
                print(f" - applying raw patch {patch.name} ({patch_size})")

                output_dir = "out"

                file_smc = Path(file)
                file_sfc = file_smc.with_suffix('.sfc')
                os.rename(file_smc, file_sfc)
                call_args = ["asar", f"./{output_dir}/patches/{filename.name}", f"./{file_sfc}"]
                call(call_args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                os.rename(file_sfc, file_smc)

        for patch in os.scandir(patches):
            filename = Path(patch)

            if filename.suffix == ".sliver":
                print(f" - converting patch {filename.name} to {filename.with_suffix('.txt').name}")
                with filename.open() as f:
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
                    text_file = open(filename.with_suffix('.txt'), "w")
                    text_file.write(code)
                    text_file.close()

        for patch in os.scandir(patches):
            filename = Path(patch)
            if filename.suffix == ".evs":
                with filename.open() as f:
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
                    print(f" - compiling patch {filename.name} to {filename.with_suffix('.txt').name}")
                    call_args = ["python3.11", f"./everscript.py", f"--out=./{output_dir}/patches/{filename.stem}/", f"{filename}"]

                    if quiet:
                        call(call_args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    else:
                        call(call_args)

                    patch_from = f"./{output_dir}/patches/{filename.stem}/patch.txt"
                    patch_to = f"{filename.with_suffix('.txt')}"
                    shutil.copy(patch_from, patch_to)

        for patch in os.scandir(patches):
            filename = Path(patch)
            if filename.suffix == ".txt":
                with filename.open() as f:
                    p = f.read()
                    p = self.clean(p)

                    self.txt_to_ips(p, filename.with_suffix(".ips"))
                    
        for patch in os.scandir(patches):
            filename = Path(patch)
            if filename.suffix == ".ips":
                self._apply_patch(file, filename)

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

    def _create_rom_diff(self, file_in, file_out):
        patch = None
        with open(file_in, 'rb') as f_in:
            with open(file_out, 'rb') as f_out:
                patch = Patch.create(f_in.read(), f_out.read())

                with open(os.path.join(self._out, "everscript.combined.ips"), 'w+b') as f_patch:
                    f_patch.write(patch.encode())
            
    def patch(self, file_in, patch):
        file_name = os.path.splitext(file_in)
        file_size = os.path.getsize(file_in)

        file_patch = Path(os.path.join(self._out, patch))

        print(f"patching {file_in} ({file_size}) + {file_patch.name} ({os.path.getsize(file_patch)})...")

        target_name = os.path.join(self._out, '.patched'.join(file_name))
        
        shutil.copyfile(file_in, target_name)

        self._extend_rom(target_name)
        self._apply_additional_patches(target_name, self._patches)
        self._apply_patch(target_name, file_patch)

        self._create_rom_diff(file_in, target_name)

        print(f"patched successfully! {file_in} ({file_size}) + {file_patch.name} ({os.path.getsize(file_patch)}) -> {target_name} ({os.path.getsize(target_name)})")

fileUtils = FileUtils()
stringUtils = StringUtils()
objectUtils = ObjectUtils()