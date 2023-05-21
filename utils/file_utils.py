from injector import Injector, inject
_injector = Injector()

import re
import os
from os.path import exists
from textwrap import wrap
import binascii
from pathlib import Path


class FileUtils():
    kilobit = 1024
    megabit = kilobit * kilobit

    header_size = kilobit // 2

    target_size = 4 * megabit
    original_size = 3 * megabit

    target_size_headered = target_size + header_size
    original_size_headerd = original_size + header_size

    def safe_delete(self, file):
        if exists(file):
            size = os.path.getsize(file)

            match(size):
                case self.original_size | self.original_size_headerd | self.target_size | self.target_size_headered:
                    os.remove(file)
                case _:
                    raise Exception(f"failed to delete {file} ({size} != 3/4MB)")
            
    def file2string(self, file):
        file = Path(file)
        
        return file.open().read()
        
    def clean(self, script):
        cleaned_script = re.sub("//.*", "", script)
        cleaned_script = re.sub("[\s]+", " ", cleaned_script)
        cleaned_script = cleaned_script.strip()

        return cleaned_script

    def dump(self, text, file):
        file = Path(file)

        match(file.suffix):
            case ".txt":
                self.dump_txt_raw(text, file)
            case ".ips":
                self.dump_txt_to_ips(text, file)
            case _:
                raise Exception("invalid file type for dumps: '{file.suffix}'")

    def dump_txt_raw(self, text, file):
        text_file = open(file, "w")
        text_file.write(text)
        text_file.close()

    def dump_txt_to_ips(self, code, file):
        with open(file, 'wb') as fout:
            for e in code.split(' '):
                match e:
                    case ("PATCH"|"EOF"):
                        fout.write(e.encode('ASCII'))
                    case _ if len(e) == 2:
                        fout.write(binascii.unhexlify(e))
                    case _:
                        [fout.write(binascii.unhexlify(b)) for b in wrap(e, 2)]

    def tmp_file_name(self, file):
        file = Path(file)
        
        return file.with_stem(f"{file.stem}.tmp")
    
    def prepare_rom(self, file):
        file_size = os.path.getsize(file)

        match(file_size):
            case self.original_size:
                self.extend_rom(file)
            case self.original_size_headerd:
                self.remove_rom_header(file)
                self.extend_rom(file)
            case self.target_size:
                print(" - skipped (rom already prepared)")
            case self.target_size_headered:
                self.remove_rom_header(file)
            case _:
                raise Exception(f"unknown ROM size '{file_size}' (must be exactly {self.original_size}, {self.target_size}, {self.target_size} or {self.target_size_headered})")

    def remove_rom_header(self, file):
        print(" - removing header…")

        file_tmp = self.tmp_file_name(file)
        self.safe_delete(file_tmp)
        os.rename(file, file_tmp)

        with open(file_tmp, 'rb') as f_in:
            f_in.seek(self.header_size)
            rom = f_in.read()
            with open(file, 'wb') as f_out:
                f_out.write(rom)

        self.safe_delete(file_tmp)
    def extend_rom(self, file):
        print(" - extending rom…")

        required_padding = self.target_size - os.path.getsize(file)

        match(required_padding):
            case self.megabit:
                with file.open("ab") as f_inout:
                    f_inout.write(b"\x00" * required_padding)
            case _:
                raise Exception(f"unknown padding length '{required_padding}' (instead of exactly {self.megabit})")


file_utils = _injector.get(FileUtils)