from injector import Injector, inject
_injector = Injector()

from utils.arg_utils import *

import os, subprocess
from subprocess import call


class ProcessUtils():
    def call(self, call_args, quiet):
        # quiet = False
        # args = arg_utils.parse()

        # print(f" - compiling patch {patch.name} to {patch.with_suffix('.txt').name}")

        if quiet:
            call(call_args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:
            call(call_args)
        
        
process_utils = _injector.get(ProcessUtils)