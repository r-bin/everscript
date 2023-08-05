from injector import Injector, inject
_injector = Injector()

from compiler.ast_core import *
from utils.out_utils import *

from rply import LexerGenerator, Token
from rply.token import BaseBox
import re
from textwrap import wrap
import copy
import random
import uuid
from enum import StrEnum

class Object(Function_Base, Calculatable, Memorable):
    def __init__(self, index, flag=None):
        self.index = index
        self.flag = flag

        self.memory = True

    def calculate(self):
        #index = self.resolve(self.index)
        code = self.index.calculate()

        return code
    
    def _code(self):
        index = self.resolve(self.index)
        flag = self.resolve(self.flag)
        
        code = [0x5d] + self._terminate(index.calculate() + [flag.code()])
        code = self._clean_calucatable(code)

        return f"""
{code}     // (5d) IF $2268 & 0x40 THEN UNLOAD OBJ 0 (TODO: verify this)"
        """
    
class FunctionKey(Function_Base):
    value_count:int = 3

    def __init__(self, index):
        self.index = index
        if isinstance(self.index, Param):
            self.index = self.index.eval()
        self.address = 0x928294 + self.index
        
        if (self.index % self.value_count) != 0:
            raise Exception("invalid index (only index%3==0 is allowed")

    def __repr__(self):
        return f"FunctionKey({self.index})"
        
    def eval(self):
        return Range(self.address, self.address + (self.value_count - 1))

    def _code(self):
        code = Word(self.index)
        code.value_count = self.value_count
        code = code.code()

        return code

class Function(Function_Base):
    key:FunctionKey = None

    def __init__(self, name, script, args, function_args=[]):
        self.name = name
        if isinstance(name, Token):
            self.name = self.name.value
        self.script = script
        self.args = args
        self.install = False
        self.address = None
        self.inject = []
        self.terminate = True
        self.async_call = False
        for arg in function_args:
            match arg:
                case _ if isinstance(arg, Arg_Async):
                    self.async_call = True
                case _ if isinstance(arg, Arg_Install):
                    self.install = True
                    self.address = arg.eval()
                    self.terminate = arg.terminate
                case _ if isinstance(arg, Arg_Inject):
                    self.inject.append(arg)
                    self.terminate = arg.terminate

        if self.install and self.terminate:
            self.script += [ End() ]

    def __repr__(self):
        return f"Function('{self.name}', {self.address}, {self.install})"
        
    def _code(self):
        for script in self.script:
            script.params = self.params

        return Function_Code(self.script, '\n').code()

class Arg_Install(BaseBox):
    def __init__(self, address=None, terminate=True):
        self.address = address
        self.terminate = terminate

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
    
class Arg_Async(BaseBox):
    def __init__(self):
        pass

class Address(Function_Base):
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
        address = self.eval()
        address = '{:06X}'.format(address, 'x')
        address = wrap(address, 2)
        
        return ' '.join(reversed(address))

    def eval(self):
        return self.rom2scriptaddr(self.value)

    def count(self):
        return len(self.code_clean().split(" "))

class _Address(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self):
        num = int(self.value.value, 16)
        return num
    
class String(Function_Base):
    def __init__(self, generator, value, install = False):
        self.value = value
        if isinstance(self.value, Token):
            self.value = self.value.value
            self.value = re.sub("\"", "", self.value)
        self.install = install
        self.text_key = None
        self.address = None

        if self.install:
            self.value = RawString(value.value.eval())
            self.value.install = True
            generator.add_string(self, self.value)
            pass

    def __repr__(self):
        return f"String('{self.value}')"
        
    def eval(self):
        return self.value
        
    def _code(self):
        if not self.install:
            code = re.sub("\"", "", self.value)
        else:
            code = Word(self.text_key.index)
            code = code.code()
        return code
        
class RawString(Function_Base):
    def __init__(self, value):
        self.value = value
        self.install = False
        if isinstance(self.value, Token):
            self.value = self.value.value
        elif isinstance(self.value, Param):
            self.value = self.value.value.value

    def __str__(self):
        return f"String('{self.eval()}')"

    def eval(self):
        value = self.value
        value = re.sub("\"", "", value)
        return value
        
    def _code(self):
        code = re.sub("\"", "", self.eval())

        lexer = LexerGenerator()
        lexer.add('END', '\[END\]')
        lexer.add('LF', '\[LF\]')
        lexer.add('HEX', '\[0x[0-9a-f]{2}\]')
        lexer.add('PAUSE', '\[PAUSE:[0-9a-f]{2}\]')
        lexer.add('CHAR', '.')
        lexer = lexer.build()

        code = list(lexer.lex(code))

        def f(c):
            match c:
                case _ if c.name == "CHAR":
                    return c.value.encode('ASCII').hex()
                case _ if c.name == "LF":
                    return "0a"
                case _ if c.name == "END":
                    return "00"
                case _ if c.name == "HEX":
                    return re.sub("\[0x([0-9a-f]{2})\]", r"\1", c.value)
                case _ if c.name == "PAUSE":
                    return "80 " + re.sub("\[PAUSE:([0-9a-f]{2})\]", r"\1", c.value) + " 80"
                case _:
                    raise Exception("invalid char")
        code = [f(c) for c in code]
        code = ' '.join(code) + f" // '{self.value}'"
        return code
        
class Arg(BaseBox):
    def __init__(self, name):
        self.name = name

    def eval(self):
        return self.name
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
        if isinstance(value, Token):
            value = value.value
        self.value = re.sub(":", "", value)

class Call(Function_Base):
    async_call = False
    
    def __init__(self, function, params=[]):
        self.params = params
        if isinstance(function, Function):
            if not function.install:
                self.function = copy.deepcopy(function)
                self.address = function.address
                self.async_call = function.async_call
                for p, a in zip(self.params, function.args):
                    if p.name == None:
                        p.name = a.name
            else:
                self.function = function
                self.address = function.address
                self.async_call = function.async_call
        elif isinstance(function, Param):
            self.function = None
            self.address = function.eval()
        else:
            raise Exception("todo")
        pass

        if self.address == None:
            pass

    def __repr__(self):
        return f"Call({self.address}, {self.function})"
        
    def _code(self):
        if self.function:
            for p, a in zip(self.params, self.function.args):
                p.name = a.name

        if self.function == None or self.function.install:
            address = "xx xx xx"
            if self.address == None and self.function != None: #TODO: should be done by the linker
                self.address = self.function.address
            if self.address != None:
                address = Address(self.address)
                address = address.code()
            else:
                pass

            if self.async_call:
                return f"""
07 {address}      // async  {self}
                """
            else:
                return f"""
29 {address}      // {self}
                """
        
        else:
            return Function_Code(self.function.script, '\n').code(self.params)

class End(Function_Base):
    def eval(self):
        return 0
        
    def _code(self):
        return f"""
00      // (00) END (return)"
        """

class Function_Transition(Function_Base): # TODO
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

class Function_Eval(Function_Base):
    def __init__(self, text):
        self.text = text

    def eval(self):
        return 0
        
    def _code(self):
        return f"""
{self.text.value.code()}        // eval({self.text.value})
        """

class Function_Goto(Function_Base):
    def __init__(self, label=None):
        self.label = label
        self.distance = None

    def eval(self):
        return 0
        
    def _code(self):
        distance = "yy yy"
        if self.distance:
            distance = Word(self.distance).code()

        return f"""
04 {distance}      // goto({self.label}/{distance})
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
        enum = generator.get_identifier(enum_identifier)

        enum_value = re.sub(".*\.", "",  self.identifier)
        value = None
        for v in enum.values:
            if v.name == enum_value:
                value = v.value
                break

        if value == None:
            error = f"Enum value '{enum_value}' does not exist in '{enum_identifier}'"
            raise Exception(error)
        
        self.value = value

    def eval(self):
        return self.value

class If_list(Function_Base, Memorable):
    def __init__(self, list):
        self.list = list

        self.update_memory()

    def update_memory(self, params=[]):
        for script in self.list:
            script.params = self.params

        for element in self.list:
            element.update_memory(params)
            self.inherit_memory(element)

        for element in self.list:
            element.memory = self.memory


    def _code(self):
        self.update_memory(self.params)

        list = []
        if_depleted = False

        if self.memory:
            for element in self.list:
                if self.memory: #TODO: should be redundant
                    list.append(element)
                    list += element.script
                    element.distance = Function_Code(element.script, '\n', params=self.params).count()
                elif element.condition == None:
                    list += element.script
                else:
                    raise Exception("non memory in memory if")
        else:
            for element in self.list:
                if isinstance(element.condition, Memory):
                    raise Exception("memory in non-memory if")
                elif not if_depleted and (element.condition == None or element.eval(self.params)):
                    list.append(element)
                    if_depleted = True
                
        return Function_Code(list, '\n').code(self.params)

class If(Function_Base, Calculatable, Memorable):
    def __init__(self, condition, script):
        self.condition = condition
        self.script = script
        self.distance = None

        self.update_memory()

    def update_memory(self, params=[]):
        self.handle_params(params)
        condition = self.resolve(self.condition)

        if condition:
            if isinstance(condition, UnaryOp):
                self.memory = condition.memory
            if isinstance(condition, Memory):
                self.memory = True
            elif isinstance(condition, BinaryOp):
                self.memory = condition.memory

    def eval(self, params=[]):
        self.update_memory(params)
        condition = self.resolve(self.condition)

        if condition != None:
            condition.params = self.params

        match condition:
            case Word():
                return condition.eval() > 0
            case BinaryOp() | Identifier():
                return condition.eval(self.params)
            case None:
                return True
            case _:
                raise Exception("unknown type for IF condition")

    def _code(self):
        destination = "xx xx"
        if self.distance != None:
            destination = Word(self.distance)
            destination = destination.code()

        condition = self.resolve(self.condition)
        if self.memory and condition:
            code = self.calculate()
            code = self._clean_calucatable(code)
            
            return code
        else:
            return Function_Code(self.script, '\n').code(self.params)
        
    def calculate(self):
        destination = "xx xx"
        if self.distance != None:
            destination = Word(self.distance)
            destination = destination.code()

        code = []

        condition = self.resolve(self.condition)
        condition = condition.calculate()

        opcode = 0x09
        if self.condition.inverted or isinstance(self.condition, UnaryOp): #TODO should be 0x09?
            opcode = 0x08

        code = [opcode] + self._terminate(condition) + [destination]

        return code

        
class Equals(BinaryOp):
    def operator(self):
        return "=="

    def _eval(self):
        return self.left.value.eval() == self.right.value.eval()

    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory) and left.offset == None and left.type == "char":
                code = left.calculate() +  [0x29] + right + [0x22]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "28":
                code = left.calculate() +  [0x29] + right + [0x22]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "28":
                code = left.calculate() +  [0x29] + right + [0x22]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "22":
                code = left.calculate() +  [0x29] + right + [0x22]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "22":
                code = left.calculate() +  [0x29] + right + [0x22]
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code
        
class NotEquals(BinaryOp):
    def operator(self):
        return "!="

    def _eval(self):
        return self.left.value.eval() != self.right.value.eval()

    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory) and left.offset == None and left.type == "char":
                code = left.calculate() +  [0x29] + right + [0x23]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "28":
                code = left.calculate() +  [0x29] + right + [0x23]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "28":
                code = left.calculate() +  [0x29] + right + [0x23]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "22":
                code = left.calculate() +  [0x29] + right + [0x23]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "22":
                code = left.calculate() +  [0x29] + right + [0x23]
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code
    
class GreaterEquals(BinaryOp):
    def operator(self):
        return ">="

    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory) and left.offset == None and left.type == "char":
                code = left.calculate() +  [0x29] + right + [0x21]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "28":
                code = left.calculate() +  [0x29] + right + [0x21]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "28":
                code = left.calculate() +  [0x29] + right + [0x21]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "22":
                code = left.calculate() +  [0x29] + right + [0x21]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "22":
                code = left.calculate() +  [0x29] + right + [0x21]
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code
    
    def _eval(self):
        return self.left.value.eval() >= self.right.value.eval()

class Greater(BinaryOp):
    def operator(self):
        return ">"

    def _eval(self):
        return self.left.value.eval() > self.right.value.eval()

class LowerEquals(BinaryOp):
    def operator(self):
        return "<="

    def _eval(self):
        return self.left.value.eval() <= self.right.value.eval()

class Lower(BinaryOp):
    def operator(self):
        return "<"

    def _eval(self):
        return self.left.value.eval() < self.right.value.eval()
    
class Add(BinaryOp):
    def operator(self):
        return "+"

    def _eval(self):
        return self.left.eval() + self.right.eval()
    
    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory) and left.offset == None and left.type == "28":
                code = [0x0d, left.code(), 0x29] + right + [0x1a]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "22":
                code = [0x08, left.code(), 0x29] + right + [0x1a]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "char":
                code = left.calculate() + [0x29] + right + [0x1a]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "28":
                code = [0x0d] + left.calculate() + [0x29] + right + [0x1a]
            case left if isinstance(left, Memory) and left.offset != None and left.type == "22":
                code = [0x08] + left.calculate() + [0x29] + right + [0x1a]
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code
    
class Sub(BinaryOp):
    def operator(self):
        return "-"

    def _eval(self):
        return self.left.value.eval() - self.right.value.eval()

    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory) and left.offset == None and left.type == "char":
                code = left.calculate() + [0x29] + right + [0x1b]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "28":
                code = [0x0d, left.code(), 0x29] + right + [0x1b]
            case left if isinstance(left, Memory) and left.offset == None and left.type == "22":
                code = [0x08, left.code(), 0x29] + right + [0x1b]
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code
    
class Mul(BinaryOp):
    def operator(self):
        return "*"

    def _eval(self):
        return self.left.value.eval() * self.right.value.eval()

    def _calculate(self, left, right):
        pass

class Div(BinaryOp):
    def operator(self):
        return "/"

    def _eval(self):
        return self.left.value.eval() // self.right.value.eval()

class ShiftRight(BinaryOp):
    def operator(self):
        return ">>"

    def _eval(self):
        return self.left.value.eval() >> self.right.value.eval()

class ShiftLeft(BinaryOp):
    def operator(self):
        return "<<"

    def _eval(self):
        return self.left.value.eval() << self.right.value.eval()
    
class And(BinaryOp):
    def operator(self):
        return "&"

    def _eval(self):
        return self.left.value.eval() & self.right.value.eval()
    
    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory):
                right = self.right
                if isinstance(right, Param):
                    right = right.value
                right = right.eval()

                if right == 0xff:
                    left.count = 1
                else:
                    raise Exception(f"right parameter '${right}' not supported")

                return left
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code
    
class Asign(BinaryOp):
    def operator(self):
        return "="

    def _code(self):
        code = self.calculate(self.params)
        code = self._clean_calucatable(code)

        return code
    
    def _calculate(self, left, right):
        code = []

        match left:
            case left if isinstance(left, Memory) and left.offset == None and left.type == "xx":
                code = [0x18, left.code()] + self._terminate(right)
            case left if isinstance(left, Memory) and left.offset == None and left.type == "28":
                code = [0x19, left.code()] + self._terminate(right)
            case left if isinstance(left, Memory) and left.offset == None and left.type == "22":
                code = [0x18, left.code()] + self._terminate(right)
            case left if isinstance(left, Memory) and left.offset != None:
                code = self._terminate([0x7a] + left.calculate(deref=False)) + self._terminate(right)

            case left if isinstance(left, Object):
                code = self._terminate([0x5c] + left.calculate()) + self._terminate(right)
            case _:
                raise Exception(f"left parameter '${left}' not supported")

        return code

class OrAsign(BinaryOp):
    def operator(self):
        return "|="

    def _code(self):
        raise Exception("not implemented")

class AndAsign(BinaryOp):
    def operator(self):
        return "&="

    def _code(self):
        raise Exception("not implemented")

class Include(BaseBox):
    def __init__(self, generator, path):
        self.generator = generator
        self.path = re.sub("[\'\"]", "", path)

    def eval(self):
        from compiler.lexer import Lexer
        from compiler.parser import Parser

        print(f" - handle import '{self.path}':")

        lexer = Lexer().get_lexer()
        pg = Parser(self.generator)
        pg.parse()
        parser = pg.get_parser()

        script = open(self.path, 'r').read()
        #print(f"{self.path} -> {list(lexer.lex(script))}")
        print(" - lexing code...")
        outUtils = _injector.get(OutUtils)
        outUtils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(script))}"), "lexer_include.txt")
        script = lexer.lex(script)
        print(" - generating objects...")
        script = parser.parse(script)
        print(" - done")

        return script

class Set(Function_Base):
    def __init__(self, memory):
        self.memory = memory

    def _code(self):
        combined = "xx xx"

        memory = self.resolve_param(self.memory)
        if memory:
            address = memory.address
            address -= 0x2258
            address <<=  3

            flag = memory.flag
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
class Unset(Function_Base):
    def __init__(self, memory):
        self.memory = memory

    def _code(self):
        address = self.memory.value.address
        address -= 0x2258
        address <<=  3

        flag = self.memory.value.flag
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

        value = 0x00
        value &= 0b111
        value += 0xb0
        value = '{:02X}'.format(value, 'x')

        return f"""
0c {combined} {value}       // set({self.memory})
        """

class Len(Function_Base):
    def __init__(self, script):
        self.script = script

    def eval(self):
        match self.script:
            case _ if isinstance(self.script, Function_Base):
                script = self.script
                script = Word(script.count())
                
                return script
            case _ if isinstance(self.script, Param):
                script = self.script
                script = script.value
                script = Word(script.count())
                
                return script
            case None:
                return 0
            case _:
                raise Exception(f"unknown type: can't generate code")

    def _code(self):
        match self.script:
            case _ if isinstance(self.script, Function_Base):
                script = self.script
                script = Word(script.count())
                script = script.code()
                return script
            case _:
                raise Exception(f"unknown type: can't generate code")

class Rnd(Function_Base):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def eval(self):
        rnd = random.randint(self.min.eval(), self.max.eval())
        return Word(rnd)

class While(Function_Base):
    def __init__(self, condition, script):
        self.script = script

        self.while_goto_end = Function_Goto()

        self.while_if = If(condition, [])
        self.while_if.distance = Function_Code(script, '\n').count() + self.while_goto_end.count()
        self.memory = self.while_if.memory

        self.list = [self.while_if] + script + [self.while_goto_end]

        self.while_goto_end.distance = -(self.while_if.count() + Function_Code(script, '\n').count() + self.while_goto_end.count())
        pass

    def _code(self):
        for script in self.script:
            script.params = self.params

        code = self.list
        code = Function_Code(code, '\n').code(self.params)

        return code

class Void(BaseBox):
    pass

class StringKey(Function_Base):
    value_count:int = 3

    def __init__(self, index):
        self.index = index
        if isinstance(self.index, Param):
            self.index = self.index.eval()
        self.address = 0x91d000 + self.index
        
        if (self.index % self.value_count) != 0:
            raise Exception("invalid index (only index%3==0 is allowed")

    def __repr__(self):
        return f"StringKey({self.index})"
        
    def eval(self):
        return Range(self.address, self.address + (self.value_count - 1))

    def _code(self):
        code = Word(self.index)
        code.value_count = self.value_count
        code = code.code()

        return code
    
class Range(BaseBox):
    def __init__(self, start, end):
        self.start = start
        if isinstance(self.start, Word):
            self.start = self.start.eval()
        self.end = end
        if isinstance(self.end, Word):
            self.end = self.end.eval()

        if type(self.start) != type(self.end):
            raise Exception("type of start and end don't match")
        
    def __repr__(self):
        return f"Range({self.start}..{self.end})"

    def eval(self):
        list = []
        if isinstance(self.start, StringKey):
            step = self.start.value_count
            for index in range(self.start.index, self.end.index + step, step):
                list.append(StringKey(index))
        elif isinstance(self.start, FunctionKey):
            step = self.start.value_count
            for index in range(self.start.index, self.end.index + step, step):
                list.append(FunctionKey(index))
        elif isinstance(self.start, Memory):
            step = 2
            for address in range(self.start.eval(), self.end.eval() + step, step):
                list.append(Memory(address))
        else:
            raise Exception("unknown type")
        return list

    def count(self):
        return self.end - self.start

    def __add__(self, o):
        if isinstance(o, int):
            return Range(self.start + o, self.end + o)
        else:
            raise Exception("invalid parameter")

class MapEntrance(Function_Base):
    def __init__(self, x, y, direction):
        self.x = x.eval()
        self.y = y.eval()
        self.direction = direction.eval()

class Map(Function_Base):
    class Collection(StrEnum):
        ENTRANCE = "entrance"
        B_TRIGGER = "b_trigger"
        STEPON_TRIGGER = "stepon_trigger"

    class Trigger(StrEnum):
        ENTER = "trigger_enter"

    variant: int = None

    enums: dict[str, Enum] = {}
    enum_entrance: list[MapEntrance] = None
    enum_stepon_trigger: list[Function] = None
    enum_b_trigger: list[Function] = None

    functions: dict[str, Function] = {}
    trigger_enter: Function = None

    def __init__(self, name, params, code, objects):
        if isinstance(name, Token):
            name = name.value
        self.name = name
        self.objects = objects

        if isinstance(params, Token):
            params = params.value
        self.map_index = params[0]
        if isinstance(self.map_index, Param):
            self.map_index = self.map_index.value
        if isinstance(self.map_index, Word):
            self.map_index = self.map_index.value

        self.functions = {c.name: c for c in code if isinstance(c, Function)}
        self.trigger_enter = self._extract_function(self.Trigger.ENTER)

        self.enums = {c.name: c for c in code if isinstance(c, Enum)}
        self.enum_entrance = self._extract_enum(self.Collection.ENTRANCE)
        self.enum_stepon_trigger = self._extract_enum(self.Collection.STEPON_TRIGGER)
        self.enum_b_trigger = self._extract_enum(self.Collection.B_TRIGGER)

        pass
    
    def _extract_function(self, trigger: Trigger):
        if trigger in self.functions.keys():
            return self.functions[trigger]
        else:
            return None
        
    def _extract_enum(self, enum: Collection):
        if enum in self.enums.keys():
            return self.enums[enum]
        else:
            return None
        
    def triggers_stepon(self) -> list:
        return self.enum_to_list(self.enum_stepon_trigger, self.map_data.trigger_step_count)
    
    def triggers_b(self) -> list:
        return self.enum_to_list(self.enum_b_trigger, self.map_data.trigger_b_count)

    def enum_to_list(self, enum:Enum, count:int) -> list:
        triggers = []
        if enum != None:
            triggers = enum.values

        if len(triggers) > count:
            raise Exception(f"invalid trigger count for {enum} ({len(triggers)} > {count})")

        triggers = triggers + [None] * (count - len(triggers))

        return triggers





class MapTransition(Function_Base):
    map: Map = None
    entrance: MapEntrance = None

    def __init__(self, generator, map_name, entrance_name, direction):
        self.map_name = map_name.name
        self.entrance_name = entrance_name.name
        self.direction = direction.value
        if isinstance(self.direction, Word):
            self.direction = self.direction.eval()

        self._generator = generator
        generator.add_map_transition(self)

        pass

    def link(self, map: Map, entrance: MapEntrance):
        self.map = map
        self.entrance = entrance

        pass

    def _code(self):
        if self.map == None or self.entrance == None or self.map.variant == None:
            return f"""
yy // linking required
            """
        else:
            params = [
                self.map.map_index,
                self.entrance.x,
                self.entrance.y,
                self.direction,
                self.entrance.direction
            ]
            params = [Param(None, Word(param, 1)) for param in params]

            function_transition = self._generator.get_function("transition")
            function_transition = Call(function_transition, params)
            function_transition = function_transition

            return Function_Code([
                Asign(Memory(0x2258), Word(self.map.variant)),
                function_transition
            ], '\n').code()
        
# unary operators

class Dead(UnaryOp):
    def _calculate(self, value):
        code = []

        code = value + [0x5c]

        return code
    
class Rand(UnaryOp):
    def _calculate(self, value):
        code = []

        code = [0x2a, 0x29] + value + [0x24]

        return code
    
class RandRange(UnaryOp):
    def _calculate(self, value):
        code = []

        code = value + [0x2b]

        return code
    
class Loot(Function_Base):
    def unwrap_param(self, param):
        if isinstance(param, Param):
            param = param.value

    def __init__(self, generator, object, reward, amount, next):
        self._generator = generator
        self.object = object
        self.reward = reward
        self.amount = amount
        self.next = next
    
        flag = self._generator.get_flag()

        self.object = Object(object, flag)
        self._generator.add_object(self.object)

        self.function = generator.get_function("loot")

    def _code(self):
        params = [Param(None, self.object.flag), Param(None, Word(self.object.index)), self.reward, self.amount, self.next]

        return Call(self.function, params).code(self.params)
class Axe2Wall(Function_Base):
    def unwrap_param(self, param):
        if isinstance(param, Param):
            param = param.value

    def __init__(self, generator, object):
        self._generator = generator
        self.object = object
    
        flag = self._generator.get_flag()

        self.object = Object(object, flag)
        self._generator.add_object(self.object)

        self.function = generator.get_function("axe2_wall")

    def _code(self):
        params = [Param(None, self.object.flag), Param(None, Word(self.object.index))]

        return Call(self.function, params).code(self.params)