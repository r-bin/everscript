from enum import Enum, auto
from ansiwrap import *
import string
from pathlib import Path
from pprint import pprint
from textwrap import wrap
import sys, getopt
import binascii
import os
from io import BytesIO
from copy import copy, deepcopy
import re
from colorama import *

class RomMapping(Enum):
    NO_ROM = "norom"
    HI_ROM = "hirom"
    LO_ROM = "lorom"

def format_command(text):
    return f"{Back.CYAN}; {text}{Back.RESET}"
def format_comment(text):
    return f"{Fore.GREEN}; {text}{Fore.RESET}"
def format_memory(text):
    return f"{Fore.RED}${text}{Fore.RESET}"
def format_rom_memory(text):
    return f"{Fore.RED}${text}{Fore.RESET}"
def format_constant(text):
    return f"{Fore.CYAN}#${text}{Fore.RESET}"
def format_string(text):
    return f"{Fore.CYAN}\"{text}\"{Fore.RESET}"
def format_character(text):
    return f"{Fore.CYAN}'{text}'{Fore.RESET}"

def print_columns(asar_command, comment):
    if False:
        print(f"{asar_command :<50}{comment :<40}")
    else:
        print(asar_command + " " * (50 - ansilen(asar_command)), comment)

class IpsRecord:
    offset = 0
    size = 0
    data = []

    raw = []
    repeat = False

    def __init__(self, offset, size, data):
        self.offset = offset
        self.size = size
        self.data = data

    def __repr__(self):
        formatted_offset = '{:06X}'.format(self.offset)
        return f'IpsRecord[{formatted_offset}] = {self.data}'
    
    def plot(self, commented_out):
        could_be_constant = not self.repeat and len(self.raw) <= 3

        try:
            data_string = self.raw.decode('UTF-8')
            data_string = ''.join(filter(lambda x: x in string.printable, data_string))
            if len(self.raw) != len(data_string):
                raise Exception("different string")
            data_string = repr(data_string)
            data_string = data_string[1:-1]
            could_be_string = not self.repeat and True
        except Exception as exception:
            could_be_string = False

        prefix = ""
        if commented_out:
            prefix += Back.YELLOW
        prefix += " " * 2
        if commented_out:
            prefix += f";{Back.RESET} "

        def indentation():
            indentation = prefix

            if could_be_constant or could_be_string:
                indentation += " " * 2

            return indentation

        if could_be_constant:
            comment = "could be a constant, instead of ASM"
            print_columns(f"{prefix}if 1", format_comment(comment))

            data = int.from_bytes(self.raw, "little")

            match len(self.raw):
                case 1:
                    formatted_data = '{:02X}'.format(data)
                case 2:
                    formatted_data = '{:04X}'.format(data)
                case 3:
                    formatted_data = '{:06X}'.format(data)
                case _:
                    formatted_data = None

            comment = f"TODO (size={self.size})"
            print_columns(f"{indentation()}db {format_constant(formatted_data)}", format_comment(comment))
            if not could_be_string:
                comment = "ASM"
                print_columns(f"{prefix}else", format_comment(comment))

        if could_be_string:
            comment = "could be a string, instead of ASM"
            if could_be_constant:
                print_columns(f"{prefix}elif 0", format_comment(comment))
            else:
                print_columns(f"{prefix}if 1", format_comment(comment))

            comment = f"string \"{data_string}\""

            print_columns(f"{indentation()}db {format_string(data_string)}", format_comment(comment))

            comment = "ASM"
            print_columns(f"{prefix}else", format_comment(comment))

        match self.data:
            case list():
                for asar_command in self.data:
                    data = str(asar_command).split(";")

                    print_columns(indentation() + data[0], ";" + data[1])
            case str():
                if False:
                    data = ", ".join([element.data] * element.size)
                else:
                    data = self.data

                try: # TODO
                    data_string = self.raw.decode('UTF-8')
                    if data_string == '\x00':
                        raise Exception("empty string")

                    comment = f"repeat '{data_string}' (#${data}) size={self.size} times"
                    data = data_string
                    print_columns(f"{indentation()}!i = 1 : while !i < 20 : db {format_character(data_string)} : endwhile", format_comment(comment))
                except Exception as exception:
                    comment = f"repeat #${data} size={self.size} times"
                    print_columns(f"{indentation()}!i = 1 : while !i < 20 : db {format_constant(data)} : endwhile", format_comment(comment))
            case _:
                print("; unknown/broken commands")

        if could_be_constant or could_be_string:
            print(f"{prefix}endif")

class parse_ips:
    debug = False

    patch = None
    elements = []
    mapper = None

    def __init__(self, mapper=RomMapping.NO_ROM):
        self.mapper = mapper

    def snes2asar(self, address):
        match self.mapper:
            case RomMapping.NO_ROM:
                return address
            case RomMapping.LO_ROM:
                raise Exception("TODO")
            case RomMapping.HI_ROM:
                return address + 0x40_0000

    class ASM65816:
        hex = 0
        size = 0
        name = None

        # params
        raw = []
        offset = None
        data = None
        is_const = False
        is_relative = False

        def __init__(self, hex, size, name, m_0=False, data_0=False, is_relative=False):
            self.hex = hex
            self.size = size
            self.name = name

            if m_0 or data_0:
                self.size += 1
            if is_relative:
                self.is_relative = is_relative

        def __repr__(self):
            name = re.sub(" .*", "", self.name)

            comment = binascii.b2a_hex(self.raw).decode('UTF-8')
            comment = wrap(comment, 2)

            comment[0] = f"[{comment[0]}]"
        
            comment = ' '.join(comment)
            comment = f"{comment} (size={self.size}, opcode='{self.name}')"

            if self.data == None and self.size > 1:
                comment = "incomplete command: " + comment
                return f"{name} {Back.RED}??{Back.RESET}{format_comment(comment)}"

            data = self.data
            size = self.size

            if self.is_relative or "label" in self.name:
                data += self.offset
                data += self.size

            match size:
                case 2:
                    formatted_data = '{:02X}'.format(data)
                case 3:
                    formatted_data = '{:04X}'.format(data)
                case 4:
                    formatted_data = '{:06X}'.format(data)
                case _:
                    formatted_data = None
            
            if "#const" in self.name:
                formatted_data = format_constant(f"{formatted_data}")
            else:
                formatted_data = format_memory(f"{formatted_data}")

            if ",Y" in self.name:
                postfix = ",Y"
            elif ",X" in self.name:
                postfix = ",X"
            else:
                postfix = ""

            if not data:
                return f"{name}" + f"{format_comment(comment)}"
            else:
                return f"{name} {formatted_data}{postfix}" + f"{format_comment(comment)}"    

    opcode = {
        0x61: ASM65816(0x61, 2, "ADC (dp,X)"),
        0x63: ASM65816(0x63, 2, "ADC sr,S"),
        0x65: ASM65816(0x65, 2, "ADC dp"),
        0x67: ASM65816(0x67, 2, "ADC [dp]"),
        0x69: ASM65816(0x69, 2, "ADC #const", m_0=True),
        0x6D: ASM65816(0x6D, 3, "ADC addr"),
        0x6F: ASM65816(0x6F, 4, "ADC long"),
        0x71: ASM65816(0x71, 2, "ADC ( dp),Y"),
        0x72: ASM65816(0x72, 2, "ADC (dp)"),
        0x73: ASM65816(0x73, 2, "ADC (sr,S),Y"),
        0x75: ASM65816(0x75, 2, "ADC dp,X"),
        0x77: ASM65816(0x77, 2, "ADC [dp],Y"),
        0x79: ASM65816(0x79, 3, "ADC addr,Y"),
        0x7D: ASM65816(0x7D, 3, "ADC addr,X"),
        0x7F: ASM65816(0x7F, 4, "ADC long,X"),
        0x21: ASM65816(0x21, 2, "AND (dp,X)"),
        0x23: ASM65816(0x23, 2, "AND sr,S"),
        0x25: ASM65816(0x25, 2, "AND dp"),
        0x27: ASM65816(0x27, 2, "AND [dp]"),
        0x29: ASM65816(0x29, 2, "AND #const", m_0=True),
        0x2D: ASM65816(0x2D, 3, "AND addr"),
        0x2F: ASM65816(0x2F, 4, "AND long"),
        0x31: ASM65816(0x31, 2, "AND (dp),Y"),
        0x32: ASM65816(0x32, 2, "AND (dp)"),
        0x33: ASM65816(0x33, 2, "AND (sr,S),Y"),
        0x35: ASM65816(0x35, 2, "AND dp,X"),
        0x37: ASM65816(0x37, 2, "AND [dp],Y"),
        0x39: ASM65816(0x39, 3, "AND addr,Y"),
        0x3D: ASM65816(0x3D, 3, "AND addr,X"),
        0x3F: ASM65816(0x3F, 4, "AND long,X"),
        0x06: ASM65816(0x06, 2, "ASL dp"),
        0x0A: ASM65816(0x0A, 1, "ASL A"),
        0x0E: ASM65816(0x0E, 3, "ASL addr"),
        0x16: ASM65816(0x16, 2, "ASL dp,X"),
        0x1E: ASM65816(0x1E, 3, "ASL addr,X"),
        0x90: ASM65816(0x90, 2, "BCC nearlabel"),
        0xB0: ASM65816(0xB0, 2, "BCS nearlabel"),
        0xF0: ASM65816(0xF0, 2, "BEQ nearlabel"),
        0x24: ASM65816(0x24, 2, "BIT dp"),
        0x2C: ASM65816(0x2C, 3, "BIT addr"),
        0x34: ASM65816(0x34, 2, "BIT dp,X"),
        0x3C: ASM65816(0x3C, 3, "BIT addr,X"),
        0x89: ASM65816(0x89, 2, "BIT #const", m_0=True),
        0x30: ASM65816(0x30, 2, "BMI nearlabel"),
        0xD0: ASM65816(0xD0, 2, "BNE nearlabel"),
        0x10: ASM65816(0x10, 2, "BPL nearlabel"),
        0x80: ASM65816(0x80, 2, "BRA nearlabel"),
        0x00: ASM65816(0x00, 1, "BRK"), # size should be 2
        0x82: ASM65816(0x82, 3, "BRL label"),
        0x50: ASM65816(0x50, 2, "BVC nearlabel"),
        0x70: ASM65816(0x70, 2, "BVS nearlabel"),
        0x18: ASM65816(0x18, 1, "CLC"),
        0xD8: ASM65816(0xD8, 1, "CLD"),
        0x58: ASM65816(0x58, 1, "CLI"),
        0xB8: ASM65816(0xB8, 1, "CLV"),
        0xC1: ASM65816(0xC1, 2, "CMP (dp,X)"),
        0xC3: ASM65816(0xC3, 2, "CMP sr,S"),
        0xC5: ASM65816(0xC5, 2, "CMP dp"),
        0xC7: ASM65816(0xC7, 2, "CMP [dp]"),
        0xC9: ASM65816(0xC9, 2, "CMP #const", m_0=True),
        0xCD: ASM65816(0xCD, 3, "CMP addr"),
        0xCF: ASM65816(0xCF, 4, "CMP long"),
        0xD1: ASM65816(0xD1, 2, "CMP (dp),Y"),
        0xD2: ASM65816(0xD2, 2, "CMP (dp)"),
        0xD3: ASM65816(0xD3, 2, "CMP (sr,S),Y"),
        0xD5: ASM65816(0xD5, 2, "CMP dp,X"),
        0xD7: ASM65816(0xD7, 2, "CMP [dp],Y"),
        0xD9: ASM65816(0xD9, 3, "CMP addr,Y"),
        0xDD: ASM65816(0xDD, 3, "CMP addr,X"),
        0xDF: ASM65816(0xDF, 4, "CMP long,X"),
        0x02: ASM65816(0x02, 2, "COP #const"),
        0xE0: ASM65816(0xE0, 2, "CPX #const", data_0=True),
        0xE4: ASM65816(0xE4, 2, "CPX dp"),
        0xEC: ASM65816(0xEC, 3, "CPX addr"),
        0xC0: ASM65816(0xC0, 2, "CPY #const", data_0=True),
        0xC4: ASM65816(0xC4, 2, "CPY dp"),
        0xCC: ASM65816(0xCC, 3, "CPY addr"),
        0x3A: ASM65816(0x3A, 1, "DEC A"),
        0xC6: ASM65816(0xC6, 2, "DEC dp"),
        0xCE: ASM65816(0xCE, 3, "DEC addr"),
        0xD6: ASM65816(0xD6, 2, "DEC dp,X"),
        0xDE: ASM65816(0xDE, 3, "DEC addr,X"),
        0xCA: ASM65816(0xCA, 1, "DEX"),
        0x88: ASM65816(0x88, 1, "DEY"),
        0x41: ASM65816(0x41, 2, "EOR (dp,X)"),
        0x43: ASM65816(0x43, 2, "EOR sr,S"),
        0x45: ASM65816(0x45, 2, "EOR dp"),
        0x47: ASM65816(0x47, 2, "EOR [dp]"),
        0x49: ASM65816(0x49, 2, "EOR #const", m_0=True),
        0x4D: ASM65816(0x4D, 3, "EOR addr"),
        0x4F: ASM65816(0x4F, 4, "EOR long"),
        0x51: ASM65816(0x51, 2, "EOR (dp),Y"),
        0x52: ASM65816(0x52, 2, "EOR (dp)"),
        0x53: ASM65816(0x53, 2, "EOR (sr,S),Y"),
        0x55: ASM65816(0x55, 2, "EOR dp,X"),
        0x57: ASM65816(0x57, 2, "EOR [dp],Y"),
        0x59: ASM65816(0x59, 3, "EOR addr,Y"),
        0x5D: ASM65816(0x5D, 3, "EOR addr,X"),
        0x5F: ASM65816(0x5F, 4, "EOR long,X"),
        0x1A: ASM65816(0x1A, 1, "INC A"),
        0xE6: ASM65816(0xE6, 2, "INC dp"),
        0xEE: ASM65816(0xEE, 3, "INC addr"),
        0xF6: ASM65816(0xF6, 2, "INC dp,X"),
        0xFE: ASM65816(0xFE, 3, "INC addr,X"),
        0xE8: ASM65816(0xE8, 1, "INX"),
        0xC8: ASM65816(0xC8, 1, "INY"),
        0x4C: ASM65816(0x4C, 3, "JMP addr"),
        0x5C: ASM65816(0x5C, 4, "JMP long"),
        0x6C: ASM65816(0x6C, 3, "JMP (addr)"),
        0x7C: ASM65816(0x7C, 3, "JMP (addr,X)"),
        0xDC: ASM65816(0xDC, 3, "JMP [addr]"),
        0x20: ASM65816(0x20, 3, "JSR addr"),
        0x22: ASM65816(0x22, 4, "JSR long"),
        0xFC: ASM65816(0xFC, 3, "JSR (addr,X))"),
        0xA1: ASM65816(0xA1, 2, "LDA (dp,X)"),
        0xA3: ASM65816(0xA3, 2, "LDA sr,S"),
        0xA5: ASM65816(0xA5, 2, "LDA dp"),
        0xA7: ASM65816(0xA7, 2, "LDA [dp]"),
        0xA9: ASM65816(0xA9, 2, "LDA #const", m_0=True),
        0xAD: ASM65816(0xAD, 3, "LDA addr"),
        0xAF: ASM65816(0xAF, 4, "LDA long"),
        0xB1: ASM65816(0xB1, 2, "LDA (dp),Y"),
        0xB2: ASM65816(0xB2, 2, "LDA (dp)"),
        0xB3: ASM65816(0xB3, 2, "LDA (sr,S),Y"),
        0xB5: ASM65816(0xB5, 2, "LDA dp,X"),
        0xB7: ASM65816(0xB7, 2, "LDA [dp],Y"),
        0xB9: ASM65816(0xB9, 3, "LDA addr,Y"),
        0xBD: ASM65816(0xBD, 3, "LDA addr,X"),
        0xBF: ASM65816(0xBF, 4, "LDA long,X"),
        0xA2: ASM65816(0xA2, 2, "LDX #const", data_0=True),
        0xA6: ASM65816(0xA6, 2, "LDX dp"),
        0xAE: ASM65816(0xAE, 3, "LDX addr"),
        0xB6: ASM65816(0xB6, 2, "LDX dp,Y"),
        0xBE: ASM65816(0xBE, 3, "LDX addr,Y"),
        0xA0: ASM65816(0xA0, 2, "LDY #const", data_0=True),
        0xA4: ASM65816(0xA4, 2, "LDY dp"),
        0xAC: ASM65816(0xAC, 3, "LDY addr"),
        0xB4: ASM65816(0xB4, 2, "LDY dp,X"),
        0xBC: ASM65816(0xBC, 3, "LDY addr,X"),
        0x46: ASM65816(0x46, 2, "LSR dp"),
        0x4A: ASM65816(0x4A, 1, "LSR A"),
        0x4E: ASM65816(0x4E, 3, "LSR addr"),
        0x56: ASM65816(0x56, 2, "LSR dp,X"),
        0x5E: ASM65816(0x5E, 3, "LSR addr,X"),
        0x54: ASM65816(0x54, 3, "MVN srcbk,destbk"),
        0x44: ASM65816(0x44, 3, "MVP srcbk,destbk"),
        0xEA: ASM65816(0xEA, 1, "NOP"),
        0x01: ASM65816(0x01, 2, "ORA (dp,X)"),
        0x03: ASM65816(0x03, 2, "ORA sr,S"),
        0x05: ASM65816(0x05, 2, "ORA dp"),
        0x07: ASM65816(0x07, 2, "ORA [dp]"),
        0x09: ASM65816(0x09, 2, "ORA #const", m_0=True),
        0x0D: ASM65816(0x0D, 3, "ORA addr"),
        0x0F: ASM65816(0x0F, 4, "ORA long"),
        0x11: ASM65816(0x11, 2, "ORA (dp),Y"),
        0x12: ASM65816(0x12, 2, "ORA (dp)"),
        0x13: ASM65816(0x13, 2, "ORA (sr,S),Y"),
        0x15: ASM65816(0x15, 2, "ORA dp,X"),
        0x17: ASM65816(0x17, 2, "ORA [dp],Y"),
        0x19: ASM65816(0x19, 3, "ORA addr,Y"),
        0x1D: ASM65816(0x1D, 3, "ORA addr,X"),
        0x1F: ASM65816(0x1F, 4, "ORA long,X"),
        0xF4: ASM65816(0xF4, 3, "PEA addr"),
        0xD4: ASM65816(0xD4, 2, "PEI (dp)"),
        0x62: ASM65816(0x62, 3, "PER label"),
        0x48: ASM65816(0x48, 1, "PHA"),
        0x8B: ASM65816(0x8B, 1, "PHB"),
        0x0B: ASM65816(0x0B, 1, "PHD"),
        0x4B: ASM65816(0x4B, 1, "PHK"),
        0x08: ASM65816(0x08, 1, "PHP"),
        0xDA: ASM65816(0xDA, 1, "PHX"),
        0x5A: ASM65816(0x5A, 1, "PHY"),
        0x68: ASM65816(0x68, 1, "PLA"),
        0xAB: ASM65816(0xAB, 1, "PLB"),
        0x2B: ASM65816(0x2B, 1, "PLD"),
        0x28: ASM65816(0x28, 1, "PLP"),
        0xFA: ASM65816(0xFA, 1, "PLX"),
        0x7A: ASM65816(0x7A, 1, "PLY"),
        0xC2: ASM65816(0xC2, 2, "REP #const"),
        0x26: ASM65816(0x26, 2, "ROL dp"),
        0x2A: ASM65816(0x2A, 1, "ROL A"),
        0x2E: ASM65816(0x2E, 3, "ROL addr"),
        0x36: ASM65816(0x36, 2, "ROL dp,X"),
        0x3E: ASM65816(0x3E, 3, "ROL addr,X"),
        0x66: ASM65816(0x66, 2, "ROR dp"),
        0x6A: ASM65816(0x6A, 1, "ROR A"),
        0x6E: ASM65816(0x6E, 3, "ROR addr"),
        0x76: ASM65816(0x76, 2, "ROR dp,X"),
        0x7E: ASM65816(0x7E, 3, "ROR addr,X"),
        0x40: ASM65816(0x40, 1, "RTI"),
        0x6B: ASM65816(0x6B, 1, "RTL"),
        0x60: ASM65816(0x60, 1, "RTS"),
        0xE1: ASM65816(0xE1, 2, "SBC (dp,X)"),
        0xE3: ASM65816(0xE3, 2, "SBC sr,S"),
        0xE5: ASM65816(0xE5, 2, "SBC dp"),
        0xE7: ASM65816(0xE7, 2, "SBC [dp]"),
        0xE9: ASM65816(0xE9, 2, "SBC #const", m_0=True),
        0xED: ASM65816(0xED, 3, "SBC addr"),
        0xEF: ASM65816(0xEF, 4, "SBC long"),
        0xF1: ASM65816(0xF1, 2, "SBC (dp),Y"),
        0xF2: ASM65816(0xF2, 2, "SBC (dp)"),
        0xF3: ASM65816(0xF3, 2, "SBC (sr,S),Y"),
        0xF5: ASM65816(0xF5, 2, "SBC dp,X"),
        0xF7: ASM65816(0xF7, 2, "SBC [dp],Y"),
        0xF9: ASM65816(0xF9, 3, "SBC addr,Y"),
        0xFD: ASM65816(0xFD, 3, "SBC addr,X"),
        0xFF: ASM65816(0xFF, 4, "SBC long,X"),
        0x38: ASM65816(0x38, 1, "SEC"),
        0xF8: ASM65816(0xF8, 1, "SED"),
        0x78: ASM65816(0x78, 1, "SEI"),
        0xE2: ASM65816(0xE2, 2, "SEP #const"),
        0x81: ASM65816(0x81, 2, "STA (dp,X)"),
        0x83: ASM65816(0x83, 2, "STA sr,S"),
        0x85: ASM65816(0x85, 2, "STA dp"),
        0x87: ASM65816(0x87, 2, "STA [dp]"),
        0x8D: ASM65816(0x8D, 3, "STA addr"),
        0x8F: ASM65816(0x8F, 4, "STA long"),
        0x91: ASM65816(0x91, 2, "STA (dp),Y"),
        0x92: ASM65816(0x92, 2, "STA (dp)"),
        0x93: ASM65816(0x93, 2, "STA (sr,S),Y"),
        0x95: ASM65816(0x95, 2, "STA _dp_X"),
        0x97: ASM65816(0x97, 2, "STA [dp],Y"),
        0x99: ASM65816(0x99, 3, "STA addr,Y"),
        0x9D: ASM65816(0x9D, 3, "STA addr,X"),
        0x9F: ASM65816(0x9F, 4, "STA long,X"),
        0xDB: ASM65816(0xDB, 1, "STP"),
        0x86: ASM65816(0x86, 2, "STX dp"),
        0x8E: ASM65816(0x8E, 3, "STX addr"),
        0x96: ASM65816(0x96, 2, "STX dp,Y"),
        0x84: ASM65816(0x84, 2, "STY dp"),
        0x8C: ASM65816(0x8C, 3, "STY addr"),
        0x94: ASM65816(0x94, 2, "STY dp,X"),
        0x64: ASM65816(0x64, 2, "STZ dp"),
        0x74: ASM65816(0x74, 2, "STZ dp,X"),
        0x9C: ASM65816(0x9C, 3, "STZ addr"),
        0x9E: ASM65816(0x9E, 3, "STZ addr,X"),
        0xAA: ASM65816(0xAA, 1, "TAX"),
        0xA8: ASM65816(0xA8, 1, "TAY"),
        0x5B: ASM65816(0x5B, 1, "TCD"),
        0x1B: ASM65816(0x1B, 1, "TCS"),
        0x7B: ASM65816(0x7B, 1, "TDC"),
        0x14: ASM65816(0x14, 2, "TRB dp"),
        0x1C: ASM65816(0x1C, 3, "TRB addr"),
        0x04: ASM65816(0x04, 2, "TSB dp"),
        0x0C: ASM65816(0x0C, 3, "TSB addr"),
        0x3B: ASM65816(0x3B, 1, "TSC"),
        0xBA: ASM65816(0xBA, 1, "TSX"),
        0x8A: ASM65816(0x8A, 1, "TXA"),
        0x9A: ASM65816(0x9A, 1, "TXS"),
        0x9B: ASM65816(0x9B, 1, "TXY"),
        0x98: ASM65816(0x98, 1, "TYA"),
        0xBB: ASM65816(0xBB, 1, "TYX"),
        0xCB: ASM65816(0xCB, 1, "WAI"),
        0x42: ASM65816(0x42, 2, "WDM"),
        0xEB: ASM65816(0xEB, 1, "XBA"),
        0xFB: ASM65816(0xFB, 1, "XCE"),
    }

    def validate_patch(self, patch):
        if self.debug:
            print(f"validating patch '{patch}'")

        return True
    
    def read_opcode(self, patch_offset, data, strict=False):
        size = len(data)
        data = BytesIO(data)

        elements = []
        
        while size - data.tell() != 0:
            offset = patch_offset + data.tell()

            raw = opcode = data.read(1)
            opcode = int.from_bytes(opcode, "big")
            if not opcode in self.opcode:
                print(f"invalid opcode {'{:02X}'.format(opcode)}")
            opcode = deepcopy(self.opcode[opcode])
            opcode.offset = self.snes2asar(offset)

            if (size - data.tell()) >= (opcode.size - 1):
                if opcode.size > 1:
                    param = data.read(opcode.size - 1)
                    raw += param
                    param = int.from_bytes(param, "little")
                    opcode.data = param

                opcode.raw = raw
                elements.append(opcode)
            elif not strict:
                data.read(size - data.tell())
                opcode.raw = raw
                elements.append(opcode)
            else:
                raise Exception("invalid opcode")
            
        return elements
    
    def read_name(self, name, file):
        data = file.read(len(name))
        
        data = data.decode("utf-8")

        if self.debug:
            print(f" - parsing name '{data}'=='{name}'?")

        if data == name:
            self.elements.append(data)

            return True
        else:
            # raise Exception(f"invalid header '{data}'")
            pass

    def read_element(self, file, strict=False):
        offset = file.read(3)
        offset = int.from_bytes(offset, "big")
        offset -= 512 # header
        size = file.read(2)
        size = int.from_bytes(size, "big")

        match size:
            case 0:
                size = file.read(2)
                size = int.from_bytes(size, "big")
                raw = data = file.read(1)
                data = binascii.b2a_hex(data).decode('UTF-8')

                element = IpsRecord(offset, size, data)
                element.raw = raw
                element.repeat = True

                self.elements.append(element)
            case _:
                data = file.read(size)

                if self.debug:
                    print(f" - parsing blob '{'{:06X}'.format(offset)}'->'{data}'?")


                try:
                    sub_element = self.read_opcode(offset, data, strict)
                except Exception as exception:
                    sub_element = data

                element = IpsRecord(offset, size, sub_element)
                element.raw = data

                self.elements.append(element)


    def parse(self, patch, strict=False):
        if self.debug:
            print(f"parsing patch '{patch}'")

        self.patch = patch
        self.size = os.path.getsize(patch)

        self.validate_patch(patch)

        with open(patch, "rb") as file:
            self.read_name("PATCH", file)

            while((self.size - file.tell()) > 5):
                self.read_element(file, strict)

                pass

            self.read_name("EOF", file)

    def plot(self, original_rom):
        print(f"analyzing '{self.patch}'…")

        print_columns(self.mapper.value, format_comment("rom mapping"))

        for element in self.elements:
            match element:
                case str():
                    print(format_command(element))
                case IpsRecord():
                    memory = self.snes2asar(element.offset)
                    memory = '{:06X}'.format(memory)
                    raw_memory = '{:06X}'.format(element.offset)
                    
                    comment = f"{element.size} bytes (raw_address=${raw_memory})"

                    print_columns(f"org {format_memory(memory)}", format_comment(comment))

                    if original_rom:
                        if (element.offset + element.size) < os.path.getsize(original_rom):
                            with open(original_rom, "rb") as file:
                                file.seek(element.offset)

                                data = file.read(element.size)

                                sub_elements = self.read_opcode(element.offset, data)

                                original_element = IpsRecord(element.offset, element.size, sub_elements)
                                original_element.raw = data

                                original_element.plot(True)
                        else:
                            indentation = " " * 2
                            print(f"{Back.YELLOW}{indentation}; extension{Back.RESET}")

                    element.plot(False)

                case _:
                    print("; unknown")



def main():
    argv = sys.argv
    argv = argv[1:]

    # ips2asar patch.ips
    # ips2asar --comparison rom.smc patch.ips
    # ips2asar patch.ips

    comparison = None
    strict = False
    mapper = RomMapping.NO_ROM

    try:
        opts, args = getopt.getopt(argv,"hc:sm:",["help", "comparison=", "strict", "mapper="])
    except getopt.GetoptError:
        help()

    if len(args) == 1:
        input_file = args[0]
        input_file = Path(input_file)
    else:
        help()

    for opt, arg in opts:
        if opt == "-h":
            print("help")
        elif opt in ("--comparison", "-c"):
            comparison = arg
            comparison = Path(comparison)
        elif opt in ("--strict", "-s"):
            strict = True
        elif opt in ("--mapper", "-m"):
            mapper = RomMapping(arg.lower())

    parser = parse_ips(mapper)

    parser.parse(input_file, strict)
    parser.plot(comparison)

main()