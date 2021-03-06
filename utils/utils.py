import pathlib
import shutil
import os
from os.path import exists
import shutil
import binascii
from textwrap import wrap
from pathlib import Path
import copy
import ujson
import re

from ips_util import Patch

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
                os.remove(self._tmp)
            self.extend_rom(file, self._tmp)

        os.remove(file)
        shutil.copyfile(self._tmp, file)
        os.remove(self._tmp)

    def _apply_additional_patches(self, file, directory):
        patches = os.path.join(self._out, "patches")
        shutil.copytree(directory, patches)

        for patch in os.scandir(patches):
            filename = Path(patch)
            if filename.suffix == ".txt": 
                with filename.open() as f:
                    p = f.read()

                    self.txt_to_ips(p, filename.with_suffix(".ips"))
                    
        for patch in os.scandir(patches):
            filename = Path(patch)
            if filename.suffix == ".ips":
                self._apply_patch(file, filename)

    def _apply_patch(self, file, patch):
        patch_records = Patch.load(patch)
        patch_size = os.path.getsize(patch)

        print(f"applying patch {patch} ({patch_size})")
        if exists(self._tmp):
            os.remove(self._tmp)
        with open(file, 'rb') as f_in:
            with open(self._tmp, 'w+b') as f_out:
                f_out.write(patch_records.apply(f_in.read()))

        os.remove(file)
        shutil.copyfile(self._tmp, file)
        os.remove(self._tmp)
            
    def patch(self, file_in, patch, patches):
        file_name = os.path.splitext(file_in)
        file_size = os.path.getsize(file_in)

        print(f"patching {file_in} ({file_size}) + {patch} ({os.path.getsize(patch)})...")

        target_name = os.path.join(self._out, '.patched'.join(file_name))
        
        shutil.copyfile(file_in, target_name)

        self._extend_rom(target_name)
        if patches:
            self._apply_additional_patches(target_name, "./patches")
        self._apply_patch(target_name, patch)

        print(f"patched successfully! {file_in} ({file_size}) + {patch} ({os.path.getsize(patch)}) -> {target_name} ({os.path.getsize(target_name)})")

fileUtils = FileUtils()
stringUtils = StringUtils()
objectUtils = ObjectUtils()
outUtils = OutUtils()