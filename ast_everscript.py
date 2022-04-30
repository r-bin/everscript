from lib2to3.pytree import Base
import math
from rply.token import BaseBox
import re
from textwrap import wrap
import copy
import random

class _Function_Base(BaseBox):
    params = []

    def call(self, args):
        return 

    def code(self, params=[]):
        if self.params:
            sp = {x.name : x for x in self.params}
            p = {x.name : x for x in params}
            for key in sp.keys() & p.keys():
                sp[key].value = p[key].value
        else:
            self.params = params

        code = self._code()
        code = re.sub("\n\s*\n", "", code)
        code = code.strip()

        return code
        
    def code_clean(self):
        script = self.code(self.params)
        script = re.sub("//.*", "", script)
        script = re.sub("[\s]+", " ", script)
        script = script.strip()

        return script

    def count(self):
        count = self.code_clean()
        if len(count) > 0:
            count = count.split(" ")
        count = len(count)

        return count

class Function(_Function_Base):
    def __init__(self, name, script, args, function_args=[]):
        self.name = name
        self.script = script
        self.args = args
        self.install = False
        self.address = None
        self.inject = []
        self.terminate = True
        for arg in function_args:
            match arg:
                case _ if isinstance(arg, Arg_Install):
                    self.install = True
                    self.address = arg.eval()
                case _ if isinstance(arg, Arg_Inject):
                    self.inject.append(arg)
                    self.terminate = arg.terminate

        if self.install:
            self.script += [ End() ]

    def _code(self):
        for script in self.script:
            script.params = self.params

        return Function_Code(self.script, '\n').code()

class Function_Code(_Function_Base):
    def __init__(self, script, delimiter=' '):
        self.script = script
        self.delimiter = delimiter

    def _code(self):
        list = []

        for a in self.script:
            match a:
                case _ if isinstance(a, int):
                    list.append('{:02X}'.format(a, 'x')) # TODO
                case _ if isinstance(a, _Function_Base):
                    list.append(a.code(self.params))
                case _ if isinstance(a, Param):
                    if a.value == None:
                        code = "xx"
                        for param in self.params:
                            if param.name == a.name:
                                code = param.value.code()
                                break
                        if code == "xx":
                            pass
                        list.append(code)
                    else:
                        list.append(a.value.code())
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

class Arg_Install(BaseBox):
    def __init__(self, address=None):
        self.address = address

    def eval(self):
        if self.address != None:
            return self.address.eval()
        else:
            return None
    
class Arg_Inject(BaseBox):
    def __init__(self, address, terminate):
        self.address = address
        self.terminate = terminate

    def eval(self):
        return self.address.eval()

class Address(_Function_Base):
    def __init__(self, value, length=3):
        self.value = value
        self.length = length

        self.scripts_start_addr = 0x928000

    def print(self):
        return {'{:08X}'.format(self.value, 'x')} # TODO pattern

    def rom2scriptaddr(self, romaddr):
        address = romaddr & ~(0x8000)
        address -= (self.scripts_start_addr & ~(0x8000))
        address = (address&0x007fff) + ((address&0x1ff0000)>>1)

        test = f"{'{:08X}'.format(romaddr, 'x')}->{'{:08X}'.format(address, 'x')}"

        return address

    def script2romaddr(self, scriptaddr):
        address = self.scripts_start_addr + (scriptaddr&0x007fff) + ((scriptaddr&0xff8000)<<1)

        test = f"{'{:08X}'.format(scriptaddr, 'x')}->{'{:08X}'.format(address, 'x')}"

        return address
        
    def _code(self):
        address = self.rom2scriptaddr(self.value)
        address = '{:06X}'.format(address, 'x')
        address = wrap(address, 2)
        
        return ' '.join(reversed(address))

    def count(self):
        return len(self.code_clean().split(" "))

class _Address(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self):
        num = int(self.value.value, 16)
        return num

class Word(_Function_Base):
    def __init__(self, value):
        self.value_original = value

        if isinstance(value, int):
            self.value = value
            self.count = 2
        else:
            self.value = int(value.value, 16)

            count = re.sub("0x", "", value.value)
            count = wrap(count, 2)
            count = len(count)
            self.count = count

    def eval(self):
        return self.value
        
    def _code(self):
        if self.count == 1:
            value = '{:02X}'.format(self.value, 'x')
        elif self.count == 2:
            value = '{:04X}'.format(self.value, 'x')
        elif self.count == 3:
            value = '{:06X}'.format(self.value, 'x')

        value = re.sub("0x", "", value)
        value = wrap(value, 2)
        
        return ' '.join(reversed(value))
        
class String(_Function_Base):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value.value
        
    def _code(self):
        code = re.sub("\"", "", self.value.value)
        return code
        
class Arg(BaseBox):
    def __init__(self, name):
        self.name = name

    def eval(self):
        return self.name
class Param(BaseBox):
    def __init__(self, name, value):
        self.name = None
        if name != None:
            self.name = name.value
        self.value = value

    def eval(self):
        return self.value.value

class Label_Jump(BaseBox):
    def __init__(self, value):
        self.value = value.value

    def eval(self):
        num = -1
        if self.value == "TEST":
            num = 1
        return num

class Label_Destination(BaseBox):
    def __init__(self, value):
        self.value = re.sub(":", "", value.value)

    def eval(self):
        num = -1
        if self.value == "TEST:":
            num = 1
        return num

class Call(_Function_Base):
    def __init__(self, function, params=[]):
        self.params = params
        if isinstance(function, Function):
            self.function = copy.deepcopy(function)
            self.address = function.address
            for p, a in zip(self.params, function.args):
                p.name = a.name
        else:
            self.function = None
            self.address = function.eval()
        
    def _code(self):
        if self.function == None or self.function.install:
            address = "xx xx xx"
            if self.address != None:
                address = Address(self.address)
                address = address.code()

            return f"""
// call({self.address})
29 {address}      // (29) CALL 0x92de75 Some cinematic script (used multiple times)"
            """
        
        else:
            return Function_Code(self.function.script, '\n').code(self.params)

class End(_Function_Base):

    def eval(self):
        return 0
        
    def _code(self):
        return f"""
00      // (00) END (return)"
        """

class Function_Transition(_Function_Base): # TODO
    def __init__(self, map, x, y, direction):
        self.map = map
        self.x = x
        self.y = y
        self.direction = direction

    def eval(self):
        return 0

    def _code(self):
        if hasattr(self, 'label_destination'):
            prefix = f"{self.label_destination.value}: "
        else:
            prefix = ""

        return f"""
// {prefix}transition({self.map.eval()},{self.direction.eval()})
27                  // (27) Fade-out screen (WRITE $0b83=0x8000)
a3 00               // (a3) CALL \"Fade-out / stop music\" (0x00)
22 {'{:02X}'.format(self.x.eval(), 'x')} {'{:02X}'.format(self.y.eval(), 'x')} {'{:02X}'.format(self.map.eval(), 'x')} 00      // (22) CHANGE MAP = 0x34 @ [ 0x0090 | 0x0118 ]: \"Prehistoria - Strong Heart's Hut\""
        """

class Function_Eval(_Function_Base):
    def __init__(self, script):
        self.script = script

    def eval(self):
        return 0
        
    def _code(self):
        return f"""
{self.script.code()}        // eval({self.script.value.value})
        """

class Function_Goto(_Function_Base):
    def __init__(self, label):
        self.label = label
        self.distance = -1

    def eval(self):
        return 0
        
    def _code(self):
        address = "xx xx"
        if self.distance >= 0:
            address = f"{'{:02X}'.format(self.distance, 'x')} 00"

        return f"""
// goto({self.label.value})
04 {address}      // (04) SKIP 4 (to 0x9385d4)"
        """

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
    def __init__(self, generator, identifier):
        self.identifier = identifier.value

        enum_identifier = re.sub("\..*", "",  self.identifier)
        enum = generator.get(enum_identifier)

        enum_value = re.sub(".*\.", "",  self.identifier)
        for v in enum.values:
            if v.name == enum_value:
                value = v.value
                break

        self.value = value

    def eval(self):
        return self.value

class Identifier(BaseBox):
    def __init__(self, value):
        self.value = value.value

    def eval(self):
        # TODO
        for param in self.params:
            if param.name == self.value:
                return param.value.eval()

        raise Exception("undefined parameter")

class If_list(_Function_Base):
    def __init__(self, list):
        self.list = list
        self.memory = False

        for element in self.list:
            if isinstance(element.condition, Memory):
                self.memory = True
            elif isinstance(element.condition, BinaryOp) and isinstance(element.condition.left, Memory):
                self.memory = True

    def _code(self):
        for script in self.list:
            script.params = self.params

        list = []
        if_depleted = False

        if not self.memory:
            for element in self.list:
                if isinstance(element.condition, Memory):
                    raise Exception("memory in non-memory if")
                elif not if_depleted and (element.condition == None or element.eval()):
                    list.append(element)
                    if_depleted = True
        else:
            for element in self.list:
                if self.memory:
                    list.append(element)
                    list += element.script
                    element.distance = Function_Code(element.script, '\n').count()
                elif element.condition == None:
                    list += element.script
                else:
                    raise Exception("non memory in memory if")
                
        return Function_Code(list, '\n').code(self.params)

class If(_Function_Base):
    def __init__(self, condition, script):
        self.condition = condition
        self.script = script
        self.distance = None

    def eval(self):
        if self.condition != None:
            self.condition.params = self.params

        match self.condition:
            case _ if isinstance(self.condition, Word):
                return self.condition.eval() > 0
            case _ if isinstance(self.condition, BinaryOp):
                return self.condition.eval()
            case None:
                return True
            case _:
                raise Exception("unknown type for IF condition")

    def _code(self):
        destination = "xx xx"
        if self.distance != None:
            destination = '{:04X}'.format(self.distance, 'x')
            destination = wrap(destination, 2)
            destination = ' '.join(reversed(destination))

        if isinstance(self.condition, Memory):
            address = self.condition.address.eval()
            address -= 0x2258
            address <<=  3

            flag = self.condition.flag.eval()
            f = 0
            while  flag > 1:
                flag >>= 1
                f += 1
            flag = f
            flag &= 0b111
            
            combined = address + flag
            #combined -= 1 # TODO
            combined = '{:04X}'.format(combined, 'x')
            combined = wrap(combined, 2)
            combined = ' '.join(reversed(combined))

            invert = self.condition.inverted
            if invert:
                command = 0x08
            else:
                raise Exception("only inverted memory checks are allowed")
            command = '{:02X}'.format(command, 'x')
            
            type = 0x85
            type = '{:02X}'.format(type, 'x')

            if_mode = "if"
            if self.condition == None:
                if_mode = "else"
            
            if invert:
                if_mode += "(!memory)"
            else:
                if_mode += "(memory)"

            return f"""
{command} {type} {combined} {destination}       // {if_mode} jump {self.distance}
            """
        elif isinstance(self.condition, BinaryOp) and isinstance(self.condition.left, Memory):
            address = self.condition.left.address.eval()
            address -= 0x2834
            address = '{:04X}'.format(address, 'x')
            address = wrap(address, 2)
            address = ' '.join(reversed(address))

            value = self.condition.right.eval()
            value -= 1
            value &= 0b111
            value += 0x30
            value = '{:02X}'.format(value, 'x')

            return f"""
09 0e {address} 29 {value} a2 {destination}       // if() jump
            """
        else:
            return Function_Code(self.script, '\n').code(self.params)
        

class BinaryOp(_Function_Base):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def _code(self):
        address = self.eval()
        address = '{:04X}'.format(address, 'x')
        address = wrap(address, 2)
        
        return ' '.join(reversed(address))

class Equals(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() == self.right.eval()

class GreaterEquals(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() >= self.right.eval()

class Greater(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() > self.right.eval()

class LowerEquals(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() <= self.right.eval()

class Lower(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() < self.right.eval()
    
class Add(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() + self.right.eval()
class Sub(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() - self.right.eval()

class Mul(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() * self.right.eval()
class Div(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() / self.right.eval()
class ShiftRight(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() >> self.right.eval()
class ShiftLeft(BinaryOp):
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        return self.left.eval() << self.right.eval()

class Asign(BinaryOp):
    def _code(self):
        memory = self.left.address.eval()
        memory -= 0x2258
        memory = '{:04X}'.format(memory, 'x')
        memory = wrap(memory, 2)
        memory = ' '.join(reversed(memory))

        value = self.right
        if isinstance(value, Identifier):
            p = {x.name : x for x in self.params}
            value = p[value.value].value
        value = value.eval()
        if value <= 0xf:
            value &= 0xf
            value += 0xb0
            value = '{:02X}'.format(value, 'x')
        else:
            value = '{:04X}'.format(value, 'x')
            value = wrap(value, 2)
            value = ' '.join(reversed(value))
            value = f"84 {value}"


        return  f"""
18 {memory} {value}       // memory({self.left.address.value}) = {self.right.value}
            """
class OrAsign(BinaryOp):
    def _code(self):
        raise Exception("not implemented")
class AndAsign(BinaryOp):
    def _code(self):
        raise Exception("not implemented")

class Memory(BaseBox):
    def __init__(self, address, flag=None):
        self.address = address
        self.flag = flag

class Include(BaseBox):
    def __init__(self, generator, path):
        self.generator = generator
        self.path = re.sub("[\'\"]", "", path)

    def eval(self):
        from lexer import Lexer
        from parser import Parser

        print(f" - handle import '${self.path}':")

        lexer = Lexer().get_lexer()
        pg = Parser(self.generator)
        pg.parse()
        parser = pg.get_parser()

        script = open(self.path, 'r').read()
        #print(f"{self.path} -> {list(lexer.lex(script))}")
        print(" - lexing code...")
        script = lexer.lex(script)
        print(" - generating objects...")
        script = parser.parse(script)
        print(" - done")

        return script

class Set(_Function_Base):
    def __init__(self, memory):
        self.memory = memory

    def _code(self):
        address = self.memory.address.eval()
        address -= 0x2258
        address <<=  3

        flag = self.memory.flag.eval()
        f = 0
        while  flag > 1:
            flag >>= 1
            f += 1
        flag = f
        flag &= 0b111
        
        combined = address + flag
        #combined -= 1 # TODO
        combined = '{:04X}'.format(combined, 'x')
        combined = wrap(combined, 2)
        combined = ' '.join(reversed(combined))

        value = 0x01
        value &= 0b111
        value += 0xb0
        value = '{:02X}'.format(value, 'x')

        return f"""
0c {combined} {value}       // set({self.memory})
        """

class Len(_Function_Base):
    def __init__(self, script):
        self.script = script

    def eval(self):
        match self.script:
            case _ if isinstance(self.script, _Function_Base):
                script = self.script
                script = Word(script.count())
                
                return script
            case None:
                return 0
            case _:
                raise Exception(f"unknown type: can't generate code")

    def _code(self):
        match self.script:
            case _ if isinstance(self.script, _Function_Base):
                script = self.script
                script = Word(script.count())
                script = script.code()
                return script
            case _:
                raise Exception(f"unknown type: can't generate code")

class Rnd(_Function_Base):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def eval(self):
        rnd = random.randint(self.min.eval(), self.max.eval())
        return Word(rnd)
