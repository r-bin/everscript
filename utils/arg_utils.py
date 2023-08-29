from injector import Injector, inject
_injector = Injector()

import sys, getopt


class ArgUtils():
    version = "1.0.0"

    def parse(self):
        name = "everscript"
        
        example_rom_file = '"Secret of Evermore (U) [!].smc"'
        example_input_file = "<input_file.evs>"
        example_patches_dir = "</additional_patches>"

        class Args():
            executable = sys.executable

            rom_file = None
            input_file = None
            patches_dir = None
            profile = False
            output_dir = "out"
            asm = "asar"
        
        return_args = Args()

        def help():
            print(f"""
Compiler for assembler based scripts, used in the SNES game "Secret of Evermore".
Almost completely based on the results of https://github.com/black-sliver/SoETilesViewer and the work of Black Sliver.

-r, --rom
    Secret of Evermore ROM: English, good dump '[!]', no header ({example_rom_file})
-s, --script, #1
    Contains the code to be compiled into an IPS file and patched into the ROM.
-p, --patches
    Additional patches to be applied.
-o, --out
    Output directory. (Default: "/out")
--asm
    ASM compiler for '.asm' patches. (Default: "asar")
--profile
    Measures the performance of the compiler. Useful for finding problems.
-v, --version
    Current version ({name} - {self.version})

examples:
    {name} --rom {example_rom_file} {example_input_file}                                                rom + script
    {name} --rom {example_rom_file} --script {example_input_file}                                       rom + script
    {name} --rom {example_rom_file} --script {example_input_file} --patches {example_patches_dir}       rom + script + patches
    {name} --rom {example_rom_file} --script {example_input_file} --profile                             profile(rom + script)
            """.strip())
            sys.exit()

        argv = sys.argv
        argv = argv[1:]

        try:
            opts, args = getopt.getopt(argv,"hpr:s:o:",["profile", "rom=", "script=", "patches=", "out=", "asm="])
        except getopt.GetoptError:
            help()

        if len(args) == 1:
            return_args.input_file = args[0]
        else:
            help()

        for opt, arg in opts:
            if opt == "-h":
                help()
            elif opt in ("-v", "--version"):
                print(_version)
                sys.exit()
            elif opt in ("-p", "--profile"):
                return_args.profile = True
            elif opt in ("-r", "--rom"):
                return_args.rom_file = arg
            elif opt in ("-s", "--script"):
                return_args.input_file = arg
            elif opt in ("-p", "--patches"):
                return_args.patches_dir = arg
            elif opt in ("-o", "--out"):
                return_args.output_dir = arg
            elif opt in ("--asm"):
                return_args.asm = arg

        if not return_args.input_file:
            help()

        return return_args
    
arg_utils = _injector.get(ArgUtils)