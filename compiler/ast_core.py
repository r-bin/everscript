from __future__ import annotations

from rply.token import BaseBox
from rply import Token
import re
from textwrap import wrap
from enum import IntEnum
from typing import Any

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
                case Word():
                    return stringify(c.value)
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

    def is_memory(self, params:list[Param]):
        return False

    def inherit_memory(self, memorable):
        if isinstance(memorable, Memorable):
            self.memory |= memorable.memory
        else:
            pass
    
    def update(self, params=[]):
        pass
      
class Resolvable():
    def resolve(self, params:list[Param], with_exception:bool=True):
        value = None

        match self:
            case Identifier():
                value = self.resolve_identifier(self, params)
            case Param():
                value = self.resolve_param(self, params)
            case BinaryOp():
                value = self.__class__(self.left.resolve(params), self.right.resolve(params))
                return value
            case UnaryOp():
                value = self.__class__(self.value.resolve(params))
                return value
            case _:
                return self
            
        if value:
            return value.resolve(params)
        elif with_exception:
            value = self.resolve_param(self, params)
            raise Exception(f"{self} could not be resolved with params: {params}")
        else:
            return None

    def resolve_identifier(self, identifier:Identifier, params:list[Param]):
        if not isinstance(identifier, Identifier):
            raise Exception(f"identifier '{identifier}' cannot be resolved")
        
        out = None

        for p in params:
            if p.name == identifier:
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

class Param(BaseBox, Resolvable):
    name: Identifier|None
    value: Any
    nullable: bool

    def __init__(self, name:Identifier, value:Any, nullable:bool=False):
        name = name
        if isinstance(name, Token):
            name = name.value
        self.name = name
        
        self.value = value

        self.nullable = nullable

    def __repr__(self):
        return f"Param(name={self.name}, value={self.value})"

    def eval(self, params:list[Param]):
        if isinstance(self.value, Memory):
            return self.value.address.value
        else:
            return self.value.eval(params)

class Identifier(BaseBox, Resolvable):
    def __init__(self, name, nullable=False):
        self.name = name.value
        self.nullable = nullable

    def __eq__(self, other):
        match other:
            case None:
                return False
            case str():
                return self.name == other
            case Token():
                return self.name == other.value
            case Identifier():
                #return super().__eq__(other)
                return self.name == other.name
        
        raise Exception("invalid Identifier comparison")

    def __contains__(self, key):
        return key in self.numbers
    
    def __hash__(self):
        return hash(self.name)
    
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

        if isinstance(value, Memory):
            value.hint.append(self.name)

    def eval(self):
        return self.value.value

class Enum_Call(BaseBox):
    def __init__(self, generator:any, identifier, base=None, with_exception=True):
        self._generator = generator

        identifier = identifier
        if isinstance(identifier, Token):
            identifier = identifier.value
        elif isinstance(identifier, Param):
            identifier = identifier.name
        if isinstance(identifier, Identifier):
            identifier = identifier.name

        if isinstance(base, Token):
            base = base.value

        if "." in identifier:
            if base:
                raise Exception(f"invalid enum call: {identifier} + {base}")
            
            self.base = re.sub("\..*", "",  identifier)
            self.identifier = re.sub(".*\.", "",  identifier)
        else:
            self.base = base
            self.identifier = identifier

        enum = self._generator.get_identifier(self.base)

        value = None
        for v in enum.values:
            if v.name == self.identifier:
                value = v.value
                break

        if with_exception and value == None:
            error = f"Enum value '{self.identifier}' does not exist in '{self.base}' ({[entry.name for entry in enum.values]})"
            raise Exception(error)
        
        self.value = value

    def eval(self):
        return self.value

class Function_Base(BaseBox, Resolvable):
    _value_count:int|None = None

    cacheable:bool = False
    cache_code:str|None = None

    def __init__(self, raw=None):
        self.raw = raw

    def parse_argument_with_type(self, generator:Any, argument:Param|Identifier, enum_base:str):
        if isinstance(argument, Param) or isinstance(argument, Identifier):
            if argument.name != None:
                value = argument.name
                if isinstance(value, Identifier):
                    value = value.name
                value = Enum_Call(generator, value, enum_base)
                value = value.value
            else:
                argument = argument.value
                if isinstance(argument, Word):
                    value = argument
        elif isinstance(argument, Word):
            value = argument
        else:
            value = argument
            # TODO("this does not seem to work")

        return value

    def code(self, params):
        if self.cacheable and self.cache_code != None:
            return self.cache_code
        else:
            #self.handle_params(params)

            code = self._code(params)
            code = re.sub("\n\s*\n", "", code)
            code = code.strip()

            if self._valid_code(code):
                self.cache_code = code

            return code
            
        
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

class EverScriptException(Function_Base):
    def __init__(self, description):
        self.description = description

    def _code(self, params:list[Param]):
        TODO(self.description)

class Word(Function_Base, Calculatable):
    def __init__(self, value, value_count=2, is_decimal=False):
        self.value_original = value
        match value:
            case Token()|int():
                value = value
            case _:
                value = value.resolve([])

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
            if is_decimal:
                value = re.sub("0[dD]", "", value.value)
                self.value = int(value)
                
                if self.value > 0xff or len(value) >= 4:
                    self._value_count = 2
                else:
                    self._value_count = 1
            else:
                self.value = int(value.value, 16)

                count = re.sub("[+-]{0,1}0x", "", value.value)
                count = wrap(count, 2)
                count = len(count)
                self._value_count = count

    def __repr__(self):
        return f"Word({self.value_original})"

    def is_memory(self, params:list[Param]):
        return False
    
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

        value = ' '.join(reversed(value))
        
        return value
    
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
            if self.value_count() == None:
                if self.value > 0xff:
                    self.force_value_count(2)
                else:
                    self.force_value_count(1)

            match [self.value_count(), self.value >= 0x00]:
                case [1, True]:
                    i = [Operand("byte"), self.code([])]
                case [2, True]:
                    i = [Operand("word"), self.code([])]
                case [1, False]:
                    i = [Operand("signed byte"), self.code([])]
                case [2, False]:
                    i = [Operand("signed word"), self.code([])]
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

    def __init__(self, address=None, flag=None, size=2, offset=None):
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
        if size not in [1, 2]:
            TODO()
        self._value_count = size
        self.sram = False

        self.inverted = False
        self.handle_type()

        self.hint = []

    def handle_type(self):
        if self.address >= 0x2834:
            self.type = "28"
        #elif self.address >= 0x2500: # TODO
        #    self.type = "22"
        elif self.address >= 0x2258:
            self.type = "22"
            if not self.address in range(0x2463, 0x2512):
                self.sram = True
        elif self.address <= 0xff:
            self.type = "char"
        else:
            self.type = "xx"

    def __repr__(self):
        return f"Memory(address={'{:02X}'.format(self.address, 'x')}/{self.type}, flag={self.flag}, size={self.value_count()}, offset={self.offset}, hint={self.hint})"
    
    def is_memory(self, params:list[Param]):
        return True
    
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
                code = [self.eval(params), Operand("push")] + offset.calculate([]) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]

            case ["28", _, _, _]:
                code = [Operand("read temp word"), self.code(params), Operand("push")] + offset.calculate([]) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]

            case ["22"|"xx", _, _, _]:
                code = [Operand("read word"), self.code(params), Operand("push")] + offset.calculate([]) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]

            case _:
                raise Exception("not supported")

        return code

class Memory_Alloc(Function_Base, Calculatable, Memorable):
    class MemorySize(IntEnum):
        FLAG = 0
        BYTE = 1
        WORD = 2
    
    class MemoryType(IntEnum):
        SRAM = 0
        RAM = 1
        TEMP_RESERVED = 2
        TEMP = 3

    def __init__(self, generator:any, size, type):
        self._generator = generator

        size = self.parse_argument_with_type(self._generator, size, "MEMORY_SIZE")
        size = size.eval([])
        size = self.MemorySize(size)
        self.size = size

        type = self.parse_argument_with_type(self._generator, type, "MEMORY_TYPE")
        type = type.eval([])
        type = self.MemoryType(type)
        self.type = type

        if self.type == self.MemoryType.TEMP:
            self.memory = self._generator.current_scope().get_memory(self.size, self.type)
        else:
            self.memory = self._generator.get_memory(self.size, self.type)


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
                    code = a.resolve(params)
                    code = code.code(params)
                    list.append(code)
                case str():
                    list.append(a)
                case FunctionVariable():
                    param = Param(a.name, a.value)
                    params.append(param)
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
    def __init__(self, script, delimiter=' ', raw=None):
        self.raw = raw
        
        self.script = script
        self.delimiter = delimiter

    def _code(self, params:list[Param]):
        list = []

        for a in self.script:
            a = a.resolve(params)
            
            match a:
                case Word():
                    list += a.calculate(params)
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

    def is_memory(self, params:list[Param]):
        return True
    def calculate(self, params:list[Param]):
        #self.handle_params(params)

        value = self.value.resolve(params)

        if isinstance(value, Calculatable):
            value = value.calculate(params)

        return self._calculate(value, params)
   
class BinaryOp(Operator):
    params:list[Param]

    def __init__(self, left, right):
        self.left = left
        self.right = right

        self._value_count = 2


        pass

    def is_memory(self, params:list[Param]):
        left = self.left.resolve(params)
        left = left.is_memory(params)

        right = self.right.resolve(params)
        right = right.is_memory(params)

        return left or right
    
    def update(self, params=[]):
        #self.handle_params(params)
    
        left = self.left.resolve(params)
        right = self.right.resolve(params)

        self.inherit_memory(left)
        self.inherit_memory(right)

    def eval(self, params:list[Param]):
        left = self.left.resolve(params)
        if not left:
            raise Exception(f"in {self}.{self.left} does not exist")
        right = self.right.resolve(params)
        if not right:
            raise Exception(f"in {self}.{self.right} does not exist")

        return self._eval(left, right, params)

    def _code(self, params:list[Param]):
        value = self.eval(params)

        left = self.left.resolve(params)
        right = self.right.resolve(params)
        
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
        left = self.left.resolve(params)
        if isinstance(left, Memorable):
            left.update(params)
        
        right = self.right.resolve(params)
        if isinstance(right, Memorable):
            right.update(params)

        self.update(params)

        estimated_size = None
        match [left, right]:
            case [Memory()|Word(), Memory()|Word()]:
                estimated_size = max(left.value_count(), right.value_count())
            case [Memory()|Word(), _]:
                estimated_size = left.value_count()
            case [_, Memory()|Word()]:
                estimated_size = right.value_count()

        if isinstance(self, Memorable) and not self.is_memory(params):
            return Word(self.eval(params), estimated_size).calculate(params)
        else:
            return self._calculate(left, right, params)
    
    def _calculate(self, left:any, right:any, params:list[Param]):
        operator = self.operator()
        invert = False

        return left.calculate(params) + [Operand("push")] + right.calculate(params) + [operator]
    
    def flatten(self, x, params:list[Param]):
        if isinstance(x, BinaryOp):
            return self.flatten(x.left, params) + [x.operator()] + self.flatten(x.right, params)
        elif isinstance(x, Param):
            #if not x.value:
            #    sp = {x.name : x for x in params}
            #    x.value = sp[x.name].value
            x = x.resolve(params)
            return self.flatten(x, params)
        else:
            return [x]

    def operator(self, inverted=False) -> Operand:
        TODO()

class Operand():
    _operands = {
        "nop": 0x00, # noop?

        "signed byte": 0x01, # signed const byte
        "byte": 0x02, # unsigned const byte

        "signed word": 0x03, # signed const word
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

        "!": 0x14, # boolean invert
        "~": 0x15, # bitwise invert
        "-x": 0x16, # flip sign
        
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
        
        "script9": 0x54, # $2 = script data[0x09]
        
        "deref": 0x55, # deref res
        # _: 0x56, # deref res &0xff
        
        # _: 0x57: # (player==dog)
            
        "time0": 0x58, # game timer bits 0-15 ($7e0b19..7e0b1a)
        
        "time2": 0x59, # bits 16-32 ($7e0b1b..7e0b1c)
        
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
        "if_currency>=": 0x8e,
        "if_currency<": 0x8f,

        "obj": 0x5d,

        "write temp byte": 0x11,
        "write temp word": 0x19,
        "write temp flag": 0x0d,
        "write byte": 0x14,
        "write word": 0x18,
        "write deref": 0x7a,
        "write object": 0x5c,
        "write arg": 0x1a,
        "write flag": 0x0c,
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
    def __init__(self, name, value=None, constant=False):
        self.name = name
        self.value = value
        self.constant = constant