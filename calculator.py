from numpy import isin
from ast_core import *

from textwrap import wrap
import re

_instructions = {
    "nop": 0x00, # noop?

    # _: 0x01, # signed const byte
    # _: 0x02, # unsigned const byte

    # _: 0x03, # signed const word
    "word": 0x04, # unsigned const word

    # _: 0x05, # test bit
    # _: 0x0a, # test temp bit

    # _: 0x06, # read byte, signed
    # _: 0x07, # read byte, unsigned
    "read word": 0x08, # read word, signed
    "read signed word": 0x09, # read word, unsigned
    # _: 0x0b, # read temp byte, signed
    # _: 0x0c, # read temp byte, unsigned
    "read temp word": 0x0d, # read temp word, signed
    # _: 0x0e, # read temp word, unsigned

    # _: 0x0f, # script arg bit, like 05 and 08 but addr is only 8bit

    # _: 0x10, # signed byte script arg
    # _: 0x11, # unsigned byte script arg
    # _: 0x12, # signed word script arg
    # _: 0x13, # unsigned word script arg

    # _: 0x14, # boolean invert
    # _: 0x15, # bitwise invert
    # _: 0x16, # flip sign
    # _: 0x17, # pull from stack, res = pulled * res

    "/": 0x18, # pulled / res
    "+": 0x1a, # pulled + res
    "-": 0x1b, # pulled - res
    "<<": 0x1c, # pulled << res
    ">>": 0x1d, # pulled >> res
    "<": 0x1e, # pulled < res (signed)
    ">": 0x1f, # pulled > res (signed)
    "<=": 0x20, # pulled <= res (signed)
    ">=": 0x21, # pulled >= res (signed)
    "==": 0x22, # pulled == res
    "!=": 0x23, # pulled != res
    "&": 0x24, # pulled & res
    "|": 0x25, # pulled | res
    "^": 0x26, # pulled ^ res
    "||": 0x27, # pulled || res
    "&&": 0x28, # pulled && res

    "push": 0x29, # push to stack
    
    # _: 0x2a, # random word
    
    # _: 0x2b, # (random word * $2) >> 16 = randrange[0,$2[
        
    # _: 0x2c, # dialog response
    
    # _: 0x54, # $2 = script data[0x09]
    
    # _: 0x55, # deref res
    # _: 0x56, # deref res &0xff
    
    # _: 0x57: # (player==dog)
        
    # _: 0x58, # game timer bits 0-15 ($7e0b19..7e0b1a)
    
    # _: 0x59, # bits 16-32 ($7e0b1b..7e0b1c)
    
    # _: 0x5a, # Run shop: buy, get result
    
    # _: 0x5b, # sell
    
    # _: 0x5c, # Next damage will kill entity
    
    # _: 0x51, # WARN: Invalid sub-instr
    # _: 0x19, # WARN: Invalid sub-instr
    # _: 0x2f, # WARN: Invalid sub-instr
    # _: 0x5d, # WARN: Invalid sub-instr
    # _: 0x5e, # WARN: Invalid sub-instr
    # _: 0x5f # WARN: Invalid sub-instr
}

_types =  {
    "24": 0x18,
    "25": 0x1c,
    "28": 0x19
}

_offsets =  {
    "last": 0x80,
    "0-f": 0x30,
    "10-1f": 0x60,
    "fff0-ffff": 0x40
}

_operators = {
    "if": {
        "24": 0x09,
        "25": 0x1c,
        "28": 0x09
    },
    "=": {
        "24": 0x18,
        "28": 0x19
    },

    "read word": {
        "24": _instructions["read word"],
        "28": _instructions["read temp word"]
    }
}

class _Address(Function_Base):
    def __init__(self, address):
        self.address = address
        self.type = None
        
        self._code()

    def _code(self):
        code = self.address
        
        if code >= 0x2834:
            code -= 0x2834
            self.type = "28"
        elif code >= 0x2258:
            code -= 0x2258
            self.type = "24"
        code = '{:04X}'.format(code, 'x')
        code = wrap(code, 2)
        code = ' '.join(reversed(code))

        return code

class Calculator(Function_Base):
    def __init__(self, instruction=[]):
        self.instruction = instruction

        self.type = None
        self.left = None
        self.right = None

    def eval(self):
        out = []

        instruction = "="
        operator = None

        header = []
        footer = []

        while self.instruction:
            i = self.instruction.pop(0)

            if i in _operators:
                operator = i

                if i == "if":
                    self.add_instruction(out, "read signed word")
                    footer.append("xx xx")
                elif i == "=":
                    pass
                else:
                    raise Exception("unknown operator")
            if i in _instructions:
                if instruction == "+":
                    self.add_instruction(footer, _instructions["push"])
                instruction = _instructions[i]

                self.add_instruction(footer, i)
            elif isinstance(i, Memory) or isinstance(i, str) and re.match("<0x[0-9a-fA-F]+>", i):
                i = _Address(i.address.eval())
                
                if not self.left:
                    if instruction in _operators:
                        self.add_instruction(out, _operators[instruction][i.type])
                    else:
                        self.add_instruction(out, i.type)
                    self.left = i
                    self.type = _types[i.type]
                elif not self.right:
                    self.add_instruction(out, _operators["read word"][i.type])

                    self.right = i
                    self.type = _types[i.type]
                else:
                    raise Exception("todo")
                out.append(i)
            elif isinstance(i, Word) or isinstance(i, str) and re.match("0x[0-9a-fA-F]", i):
                word = i
                i = i.eval()

                if i in range(0x0, 0xf):
                    i = 0x30 + (i & 0x0f)
                elif i in range(0x10, 0x1f):
                    i = 0x60 + ((i - 0x10) & 0x0f)
                elif i in range(0xfff0, 0xffff):
                    i = 0x40 + ((i - 0xfff0) & 0x0f)
                else:
                    i = word

                if isinstance(i, Word):
                    self.add_instruction(out, _instructions["word"])
                elif self.right:
                    self.add_instruction(out, _instructions["push"])
                self.add_instruction(out, i)

        out = header + out + list(reversed(footer))

        for i, e in reversed(list(enumerate(out))):
            if isinstance(e, int):
                out[i] |= 0x80
                break

        return out

    def add_instruction(self, out, instruction):
        if instruction in _instructions:
            instruction = _instructions[instruction]
        
        out.append(instruction)
    
    def code(self):
        script = self.eval()
        script = Function_Code(script)
        script = script.code()

        return script