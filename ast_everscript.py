from ast_core import *
from calculator import *
from utils import Utils

from rply import LexerGenerator, Token
from rply.token import BaseBox
import re
from textwrap import wrap
import copy
import random
import uuid

utils = Utils()

class Function(Function_Base):
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
                    self.terminate = arg.terminate
                case _ if isinstance(arg, Arg_Inject):
                    self.inject.append(arg)
                    self.terminate = arg.terminate

        if self.install and self.terminate:
            self.script += [ End() ]

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
    
class String(Function_Base):
    def __init__(self, value, c_string = False):
        self.value = value
        self.c_string = c_string

    def __str__(self):
        return f"String({self.value.value})"

    def eval(self):
        return self.value.value
        
    def _code(self):
        if isinstance(self.value, Token):
            code = re.sub("\"", "", self.value.value)
        elif not self.c_string:
            code = re.sub("\"", "", self.value.eval())
        else:
            code = re.sub("\"", "", self.value.eval())

            lexer = LexerGenerator()
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
                    case _ if c.name == "HEX":
                        return re.sub("\[0x([0-9a-f]{2})\]", r"\1", c.value)
                    case _ if c.name == "PAUSE":
                        return "80 " + re.sub("\[PAUSE:([0-9a-f]{2})\]", r"\1", c.value) + " 80"
                    case _:
                        raise Exception("invalid char")
            code = [f(c) for c in code]
            code = ' '.join(code) + f" // '{self.value.value}'"
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
    def __init__(self, function, params=[]):
        self.params = params
        if isinstance(function, Function):
            self.function = copy.deepcopy(function)
            self.address = function.address
            for p, a in zip(self.params, function.args):
                p.name = a.name
        elif isinstance(function, Param):
            self.function = None
            self.address = function.eval()
        else:
            raise Exception("todo")
        
    def _code(self):
        if self.function == None or self.function.install:
            address = "xx xx xx"
            if self.address != None:
                address = Address(self.address)
                address = address.code()

            return f"""
29 {address}      // call({self.address})
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
        distance = "xx xx"
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

class If_list(Function_Base):
    def __init__(self, list):
        self.list = list
        self.memory = False

        for element in self.list:
            if element.memory:
                self.memory = True
                break

        for element in self.list:
            element.memory = self.memory

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

class If(Function_Base):
    def __init__(self, condition, script):
        self.condition = condition
        self.script = script
        self.distance = None
        self.memory = False

        if isinstance(condition, Memory):
            self.memory = True
        elif isinstance(condition, BinaryOp) and isinstance(condition.left.value, Memory):
            self.memory = True

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
            destination = Word(self.distance)
            destination = destination.code()

        if self.memory and self.condition:
            if isinstance(self.condition, BinaryOp):
                code = self.condition.flatten(self.condition)
            else:
                code = [self.condition]
            code = ["if"] + code + [destination]
            code = f"{Calculator(list(code)).code()} // Calculator({code})"
            return code
        else:
            return Function_Code(self.script, '\n').code(self.params)
        
class Equals(BinaryOp):
    def operator(self):
        return "=="

    def _eval(self):
        return self.left.value.eval() == self.right.value.eval()

class GreaterEquals(BinaryOp):
    def operator(self):
        return ">="

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
        return self.left.value.eval() + self.right.value.eval()

class Sub(BinaryOp):
    def operator(self):
        return "-"

    def _eval(self):
        return self.left.value.eval() - self.right.value.eval()

class Mul(BinaryOp):
    def operator(self):
        return "*"

    def _eval(self):
        return self.left.value.eval() * self.right.value.eval()

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

class Asign(BinaryOp):
    def operator(self):
        return "="

    def _code(self):
        code = self.flatten(self)
        code = f"{Calculator(code).code()} // Calculator({code})"
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
        utils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(script))}"), "lexer_include.txt")
        script = lexer.lex(script)
        print(" - generating objects...")
        script = parser.parse(script)
        print(" - done")

        return script

class Set(Function_Base):
    def __init__(self, memory):
        self.memory = memory

    def _code(self):
        address = self.memory.value.address.eval()
        address -= 0x2258
        address <<=  3

        flag = self.memory.value.flag.eval()
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

class Len(Function_Base):
    def __init__(self, script):
        self.script = script

    def eval(self):
        match self.script:
            case _ if isinstance(self.script, Function_Base):
                script = self.script
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

class Range(BaseBox):
    def __init__(self, start, end):
        self.start = start
        if isinstance(self.start, Word):
            self.start = self.start.eval()
        self.end = end
        if isinstance(self.end, Word):
            self.end = self.end.eval()
        
    def __repr__(self):
        return f"Range({self.start}..{self.end})"

    def count(self):
        return self.end - self.start

    def __add__(self, o):
        if isinstance(o, int):
            return Range(self.start + o, self.end + o)
        else:
            raise Exception("invalid parameter")

class Void(BaseBox):
    pass