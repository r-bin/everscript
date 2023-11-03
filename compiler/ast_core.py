from __future__ import annotations

from rply.token import BaseBox
from rply import Token
import re
from textwrap import wrap

def TODO(message = ""):
    raise Exception(message)

class Calculatable():
    """
    00…2f = opcodes
    30…3f = value 0…f
    40…3f = negative values?
    50…5f = special characters?
    60…6f = value = 10…1f
    """

    def _terminate(self, code:list[int|str|list]):
        code = list(reversed(code))

        termination = Operand("termination")

        for i, c in enumerate(code):
            match c:
                case Opcode() | Operand():
                    code[i] = [c, termination]
                    break
                case str():
                    pass
                case int():
                    code[i] = [c, termination]
                    break
                case list():
                    code[i] = c + [termination]
                    break
                case _:
                    raise Exception("invalid type")

        code = list(reversed(code))

        return code
    
    def _clean_calucatable(self, code, params:list[Param]):
        calculated_code = code

        def stringify(c):
            match c:
                case Opcode() | Operand():
                    return stringify(c.value)
                case int():
                    return '{:02X}'.format(c, 'x')
                case str():
                    return c
                case list():
                    c = [i if isinstance(i, int) else i.value for i in c]
                    return stringify(sum(c))
                case _:
                    raise Exception("invalid type")

        code = list(map(stringify, code))
        code = ' '.join(code)
        code = f"{code} // calculator({calculated_code})"
        if getattr(self, "flatten", None):
            code = f"{code} or {self.flatten(self, params)}"

        return code
    
class Memorable():
    memory = False
    offset = None
    requires_deref = False

    def inherit_memory(self, memorable):
        if isinstance(memorable, Memorable):
            self.memory |= memorable.memory
        else:
            pass
    
    def update(self, params=[]):
        pass
            
class Param(BaseBox):
    def __init__(self, name, value):
        self.name = None
        if isinstance(name, str):
            self.name = name
        elif isinstance(name, Identifier):
            self.name = name.name

        self.value = value

    def __repr__(self):
        return f"Param(name={self.name}, value={self.value})"

    def eval(self, params:list[Param]):
        if isinstance(self.value, Memory):
            return self.value.address.value
        else:
            return self.value.eval(params)

class Identifier(BaseBox):
    def __init__(self, name):
        self.name = name.value

    def __repr__(self):
        return f"Identifier({self.name})"

class Enum(BaseBox):
    def __init__(self, name, values):
        self.name = name.value
        self.values = values

    def eval(self):
        return 0
class Enum_Entry(BaseBox):
    def __init__(self, name, value):
        self.name = name.value
        self.value = value

    def eval(self):
        return self.value.value

class Enum_Call(BaseBox):
    def __init__(self, generator:any, identifier, with_exception=True):
        self._generator = generator

        self.identifier = identifier
        if isinstance(self.identifier, Token):
            self.identifier = self.identifier.value

        enum_identifier = re.sub("\..*", "",  self.identifier)
        enum = self._generator.get_identifier(enum_identifier)

        enum_value = re.sub(".*\.", "",  self.identifier)
        value = None
        for v in enum.values:
            if v.name == enum_value:
                value = v.value
                break

        if with_exception and value == None:
            error = f"Enum value '{enum_value}' does not exist in '{enum_identifier}' ({[entry.name for entry in enum.values]})"
            raise Exception(error)
        
        self.value = value

    def eval(self):
        return self.value

class Function_Base(BaseBox):
    _value_count:int = None

    #cache_code:str = None
    #cache_code_clean:str = None

    def parse_argument_with_type(self, generator:any, argument:any, enum_base:str):
        if isinstance(argument, Param) or isinstance(argument, Identifier):
            if argument.name != None:
                value = argument.name
                value = Enum_Call(generator, f"{enum_base}.{value}")
                value = value.value
            else:
                argument = argument.value
                if isinstance(argument, Word):
                    value = argument
        elif isinstance(argument, Word):
            value = argument
        else:
            TODO()

        return value

    def code(self, params):
        if True: # self.cache_code == None:
            #self.handle_params(params)

            code = self._code(params)
            code = re.sub("\n\s*\n", "", code)
            code = code.strip()

            #if self._valid_code(code):
            #    self.cache_code = code

            return code
        else:
            return self.cache_code
        
    def _valid_code(self, code:str) -> bool:
        code = self._clean_code(code)
        if "xx" in code:
            return False
        if "yy" in code:
            return False
        return True
    
    def _clean_code(self, code:str) -> str:
        code = re.sub("//.*", "", code)
        code = re.sub("[\s]+", " ", code)
        code = code.strip()

        return code
        
    def code_clean(self, params):
        script = self.code(params)
        script = self._clean_code(script)

        return script

    def count(self, params):
        count = self.code_clean(params)
        if len(count) > 0:
            count = count.split(" ")
        count = len(count)

        return count
    
    def force_value_count(self, value_count):
        self._value_count = value_count

    def value_count(self):
        return self._value_count
    
    def resolve(self, value:any, params:list[Param]):
        match value:
            case Identifier():
                return self.resolve_identifier(value, params)
            case Param():
                return self.resolve_param(value, params)
            case _:
                return value

    def resolve_identifier(self, identifier:Identifier, params:list[Param]):
        if not isinstance(identifier, Identifier):
            raise Exception(f"identifier '{identifier}' cannot be resolved")
        
        out = None

        for p in params:
            if p.name == identifier.name:
                out = p.value
                break
            
        return out

    def resolve_param(self, param:Param, params:list[Param]):
        if not isinstance(param, Param):
            raise Exception(f"param '{param}' cannot be resolved")
        
        if param.value != None:
            return param.value
        elif param.name != None:
            for p in params:
                if p.name == param.name:
                    return p.value

        return None
    
    def handle_params(self, params:list[Param], function_params:list[Param]):
        if function_params:
            sp = {x.name : x for x in function_params}
            p = {x.name : x for x in params}
            #test = sp.keys() & p.keys()
            
            for key in sp.keys() & p.keys():
                if sp[key].value == None:
                    sp[key].value = p[key].value

            out_params = [Param(param.name, param.value) for name, param in sp.items()]

            return out_params
        else:
            return params

    def merge_params(self, params:list[Param], function_params:list[Param]):
        fp = {x.name : x for x in function_params}
        p = {x.name : x for x in params}
        
        keys = fp.keys()

        params = [Param(key, fp[key].value if key in fp else p[key].value) for key in keys]

        merged_params = [param for param in params]
        for param in merged_params:
            for p in function_params:
                if param.name == p.name and p.value != None:
                    param.value = p.value

        return merged_params


class Word(Function_Base, Calculatable):
    def __init__(self, value, value_count = 2):
        self.value_original = value
        value = self.resolve(value, [])

        if isinstance(value, int):
            self.value = value
            self._value_count = value_count
        elif isinstance(value, Word):
            self.value = value.eval([])
            self._value_count = value_count
        #elif isinstance(value, Memory) and value.type == "char":
        #    self.value = value.eval([])
        #    self._value_count = 1
        else:
            self.value = int(value.value, 16)

            count = re.sub("[+-]{0,1}0x", "", value.value)
            count = wrap(count, 2)
            count = len(count)
            self._value_count = count

    def __repr__(self):
        return f"Word({self.value_original})"

    def eval(self, params:list[Param]):
        return self.value
        
    def _code(self, params:list[Param]):
        value = self.value

        if value < 0:
            nbits = self.value_count() * 8
            value = (value + (1 << nbits)) % (1 << nbits)

        if self.value_count() == 1:
            value = '{:02X}'.format(value, 'x')
        elif self.value_count() == 2:
            value = '{:04X}'.format(value, 'x')
        elif self.value_count() == 3:
            value = '{:06X}'.format(value, 'x')

        value = re.sub("[+-]{0,1}0x", "", value)
        value = wrap(value, 2)
        
        return ' '.join(reversed(value))
    
    def calculate(self, params:list[Param]):
        i = self.eval(params)

        if i in range(0x0, 0xf):
            i = i & 0x0f
            i = [[Operand("int 0-f"), i]]
        elif i in range(0x10, 0x1f):
            i = (i - 0x10) & 0x0f
            i = [[Operand("int 10-1f"), i]]
        #elif i in range(0xfff0, 0xffff):
        #    i = (i - 0xfff0) & 0x0f
        #    i = [[Operand("int fff0-ffff"), i]]
        else:
            match self.value_count():
                case 1:
                    i = [Operand("unsigned byte"), self.code([])]
                case 2:
                    i = [Operand("word"), self.code([])]
                case _:
                    raise Exception("not supported")

        return i
    
class Memory(Function_Base, Calculatable, Memorable):
    """
    valid addresses:
        00…ff = special characters, like boy, dog, last entity, script owner (larger than required)
        2834… = temp words
        2258… = words
        else = arbitrary access (hack)
    """

    def __init__(self, address=None, flag=None, offset=None):
        self.address = address
        if isinstance(self.address, Word):
            self.address = self.address.eval([])
        elif isinstance(self.address, Param) or isinstance(self.address, Identifier):
            # self.address = self.parse_argument_with_type()
            TODO()
        self.flag = flag
        if isinstance(self.flag, Word):
            self.flag = self.flag.eval([])
        self.offset = offset
        if isinstance(self.offset, Word):
            self.offset = self.offset.eval([])

        self.memory = True
        self._value_count = 2

        self.inverted = False
        self.handle_type()

    def handle_type(self):
        if self.address >= 0x2834:
            self.type = "28"
        elif self.address >= 0x2258:
            self.type = "22"
        elif self.address <= 0xff:
            self.type = "char"
        else:
            self.type = "xx"

    def __repr__(self):
        return f"Memory(address={'{:02X}'.format(self.address, 'x')}/{self.type}, flag={self.flag}, offset={self.offset})"
    
    def eval(self, params:list[Param]):
        return self.address

    def _code(self, params:list[Param]):
        self.handle_type()

        address = self.address
        flag = self.flag
        
        if address >= 0x2834:
            address -= 0x2834
        elif address >= 0x2258:
            address -= 0x2258
        else:
            if address >= 0x2258:
                address -= 0x2258
            else:
                address += 0xDDA8
            self.type = "xx"

        if self.type == "char":
            address = '{:02X}'.format(address, 'x')
            address = wrap(address, 2)
            address = ' '.join(reversed(address))

            return address
        elif not flag:
            address = '{:04X}'.format(address, 'x')
            address = wrap(address, 2)
            address = ' '.join(reversed(address))

            return address
        else:
            address <<=  3

            f = 0
            while  flag > 1:
                flag >>= 1
                f += 1
            flag = f
            flag &= 0b111

            combined = address + flag
            combined = '{:04X}'.format(combined, 'x')
            combined = wrap(combined, 2)
            combined = ' '.join(reversed(combined))

            return combined
        
    def calculate(self, params:list[Param], offset=None, deref=True):
        self.handle_type()

        code = []

        match [self.type, offset, self.flag, self.value_count()]:
            case ["char", None, _, _]:
                code = [self.eval(params)]

            case ["28", None, _, 1]:
                code = [Operand("read temp byte"), self.code(params)]
            case ["28", None, int(), _]:
                code = [Operand("test temp"), self.code(params)]
            case ["28", None, _, _]:
                code = [Operand("read temp word"), self.code(params)]

            case ["22", None, _, 1]:
                code = [Operand("read byte"), self.code(params)]
            case ["22", None, int(), _]:
                code = [Operand("test"), self.code(params)]
            case ["22", None, _, _]:
                code = [Operand("read word"), self.code(params)]

            case ["xx", None, _, 1]:
                code = [Operand("read byte"), self.code(params)]
            case ["xx", None, int(), _]:
                code = [Operand("test"), self.code(params)]
            case ["xx", None, _, _]:
                code = [Operand("read word"), self.code(params)]

            case ["char", _, _, _]:
                code = [self.eval(params), Operand("push")] + Word(offset, 1).calculate([]) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]

            case ["28", _, _, _]:
                code = [Operand("read temp word"), self.code(params), Operand("push")] + Word(offset, 1).calculate([]) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]

            case ["22", _, _, _]:
                code = [Operand("read word"), self.code(params), Operand("push")] + Word(offset, 1).calculate([]) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]

            case _:
                raise Exception("not supported")

        return code

class Function_Code(Function_Base):
    def __init__(self, script, delimiter=' '):
        self.script = script
        self.delimiter = delimiter

    def _code(self, params:list[Param]):
        list = []

        for a in self.script:
            match a:
                case int():
                    list.append('{:02X}'.format(a, 'x')) # TODO
                case Function_Base():
                    list.append(a.code(params))
                case Param():
                    code = self.resolve(a, params)
                    code = code.code(params)
                    list.append(code)
                case str():
                    list.append(a)
                case None:
                    pass
                case _:
                    raise Exception(f"unknown type: can't generate code for:\n{a}")

        code = self.delimiter.join(filter(None, (list)))
        if "xx" in code:
            pass

        return f"""
{code}
        """
class Function_Calculate(Function_Base, Calculatable):
    def __init__(self, script, delimiter=' '):
        self.script = script
        self.delimiter = delimiter

    def _code(self, params:list[Param]):
        list = []

        for a in self.script:
            if isinstance(a, Param):
                a = self.resolve(a, params)
            
            match a:
                case Word():
                    list.append(a.code(params))
                case int():
                    list.append('{:02X}'.format(a, 'x')) # TODO
                case Function_Base():
                    list += a.calculate(params)
                case str():
                    list.append(a)
                case None:
                    pass
                case _:
                    raise Exception(f"unknown type: can't generate code for:\n{a}")

        code = self._terminate(list)
        code = self._clean_calucatable(code, params)
        code = self._clean_code(code)
        if "xx" in code:
            pass

        return f"""
{code}
        """
 
class Operator(Function_Base, Calculatable, Memorable):
    pass

class UnaryOp(Operator):
    def __init__(self, value):
        self.value = value

        if isinstance(value, Param):
            value = value.value

        self.memory = True

    def calculate(self, params:list[Param]):
        #self.handle_params(params)

        value = self.resolve(self.value, params)

        if isinstance(value, Calculatable):
            value = value.calculate(params)

        return self._calculate(value, params)
   
class BinaryOp(Operator):
    params:list[Param]

    def __init__(self, left, right):
        self.left = left
        self.right = right

        self._value_count = 2

        self.update()

        pass

    def update(self, params=[]):
        #self.handle_params(params)
    
        left = self.resolve(self.left, params)
        right = self.resolve(self.right, params)

        self.inherit_memory(left)
        self.inherit_memory(right)

    def eval(self, params:list[Param]):
        left = self.resolve(self.left, params)
        right = self.resolve(self.right, params)

        return self._eval(left, right, params)

    def _code(self, params:list[Param]):
        value = self.eval(params)

        left = self.resolve(self.left, params)
        right = self.resolve(self.right, params)
        
        self._value_count = max(left.value_count(), right.value_count())
        
        if self.value_count() == 1:
            value = '{:02X}'.format(value, 'x')
        elif self.value_count() == 2:
            value = '{:04X}'.format(value, 'x')
        elif self.value_count() == 3:
            value = '{:06X}'.format(value, 'x')

        value = re.sub("[+-]{0,1}0x", "", value)
        value = wrap(value, 2)
        
        return ' '.join(reversed(value))
    
    def calculate(self, params):
        self.update(params)

        left = self.resolve(self.left, params)
        if isinstance(left, Memorable) and left.offset != None and left.memory == False: # TODO: identifier should be detected once the params contain the value
            left.update(params)
            self.update(params)
        if isinstance(left, BinaryOp):
            new_left = left.calculate(params)
            if new_left == None:
                TODO()
            else:
                left = new_left
        
        right = self.resolve(self.right, params)

        estimated_size = None
        match [left, right]:
            case [Memory()|Word(), Memory()|Word()]:
                estimated_size = max(left.value_count(), right.value_count())

        if isinstance(right, BinaryOp) or isinstance(right, UnaryOp) or isinstance(right, Word) or isinstance(right, Memory):
            new_right = right.calculate(params)
            if new_right == None:
                TODO()
            else:
                right = new_right

        if isinstance(self, Memorable) and not self.memory:
            return Word(self.eval(params), estimated_size).calculate(params)
        else:
            return self._calculate(left, right, params)
    
    def flatten(self, x, params:list[Param]):
        if isinstance(x, BinaryOp):
            return self.flatten(x.left, params) + [x.operator()] + self.flatten(x.right, params)
        elif isinstance(x, Param):
            #if not x.value:
            #    sp = {x.name : x for x in params}
            #    x.value = sp[x.name].value
            x = self.resolve(x, params)
            return self.flatten(x, params)
        else:
            return [x]

    def operator(self):
        return ""

class Operand():
    _operands = {
        "nop": 0x00, # noop?

        # _: 0x01, # signed const byte
        "unsigned byte": 0x02, # unsigned const byte

        # _: 0x03, # signed const word
        "word": 0x04, # unsigned const word

        "test": 0x05, # test bit
        "test temp": 0x0a, # test temp bit

        # _: 0x06, # read byte, signed
        "read byte": 0x07, # read byte, unsigned
        "read signed word": 0x08, # read word, signed
        "read word": 0x09, # read word, unsigned
        # _: 0x0b, # read temp byte, signed
        "read temp byte": 0x0c, # read temp byte, unsigned
        "read signed temp word": 0x0d, # read temp word, signed
        "read temp word": 0x0e, # read temp word, unsigned

        # _: 0x0f, # script arg bit, like 05 and 08 but addr is only 8bit

        # _: 0x10, # signed byte script arg
        # _: 0x11, # unsigned byte script arg
        "read signed word arg": 0x12, # signed word script arg
        "read word arg": 0x13, # unsigned word script arg

        # _: 0x14, # boolean invert
        # _: 0x15, # bitwise invert
        # _: 0x16, # flip sign
        
        "*": 0x17, # pull from stack, res = pulled * res
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
        
        "random word": 0x2a, # random word
        
        "randrange": 0x2b, # (random word * $2) >> 16 = randrange[0,$2[
            
        # _: 0x2c, # dialog response
        
        # _: 0x54, # $2 = script data[0x09]
        
        "deref": 0x55, # deref res
        # _: 0x56, # deref res &0xff
        
        # _: 0x57: # (player==dog)
            
        # _: 0x58, # game timer bits 0-15 ($7e0b19..7e0b1a)
        
        # _: 0x59, # bits 16-32 ($7e0b1b..7e0b1c)
        
        # _: 0x5a, # Run shop: buy, get result
        
        # _: 0x5b, # sell
        
        "dead": 0x5c, # Next damage will kill entity
        
        # _: 0x51, # WARN: Invalid sub-instr
        # _: 0x19, # WARN: Invalid sub-instr
        # _: 0x2f, # WARN: Invalid sub-instr
        # _: 0x5d, # WARN: Invalid sub-instr
        # _: 0x5e, # WARN: Invalid sub-instr
        # _: 0x5f # WARN: Invalid sub-instr

        # custom
        "int 0-f": 0x30,
        "int 10-1f": 0x60,
        "int fff0-ffff": 0x40,
        "termination": 0x80
    }

    _opcodes = {
        "if": {
            "22": 0x09,
            "25": 0x1c,
            "28": 0x09
        },
        "if!": {
            "22": 0x08,
            "25": 0x1c,
            "28": 0x08
        },
        "=": {
            "xx": 0x17,
            "22": 0x18,
            "28": 0x19
        },

        "read word": {
            "22": _operands["read word"],
            "28": _operands["read temp word"]
        },
        "test": {
            "22": _operands["test"],
            "28": _operands["test temp"]
        }
    }

    def find_key_by_value(self, value:int) -> str:
        key = self._operands.values().index(value)
        key = self._operands.keys()[key]

        return key

    def find_value_by_key(self, key:str) -> int:
        value = self._operands[key]

        return value

    def __init__(self, value):
        match value:
            case int():
                self.value = value
                self.name = self.find_key_by_value(value)
            case str():
                self.value = self.find_value_by_key(value)
                self.name = value
            case _:
                TODO()

    def __repr__(self):
        return f"Operand({'{:02X}'.format(self.value, 'x')}/{self.name})"
    
class Opcode():
    _opcodes = {
        "call": 0x29,
        "call params": 0xaf,
        "async call": 0x07,
        "async call params": 0xb4,

        "if": 0x09,
        "if!": 0x08,

        "obj": 0x5d,

        "write temp byte": 0x10,
        "write temp word": 0x19,
        "write byte": 0x14,
        "write word": 0x18,
        "write deref": 0x7a,
        "write object": 0x5c,
        "write arg": 0x1a,
    }

    def find_key_by_value(self, value:int) -> str:
        key = self._opcodes.values().index(value)
        key = self._opcodes.keys()[key]

        return key

    def find_value_by_key(self, key:str) -> int:
        value = self._opcodes[key]

        return value

    def __init__(self, value):
        match value:
            case int():
                self.value = value
                self.name = self.find_key_by_value(value)
            case str():
                self.value = self.find_value_by_key(value)
                self.name = value
            case _:
                TODO()

    def __repr__(self):
        return f"Opcode({'{:02X}'.format(self.value, 'x')}/{self.name})"
    
class FunctionVariable():
    def __init__(self, name, constant=False):
        self.name = name
        self.constant = constant