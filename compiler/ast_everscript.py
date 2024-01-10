from injector import Injector, inject

from compiler.ast_core import Param
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

class Is(Function_Base):
    def __init__(self, value, type, inverted=False):
        self.value = value
        self.type = type
        self.inverted = inverted

    def is_memory(self, params:list[Param]):
        return False
    
    def eval(self, params:list[Param]):
        value = self.value.resolve(params)
        is_type_of = False
        
        match self.type:
            case "Word":
                is_type_of = isinstance(value, Word)
            case "Memory":
                is_type_of = isinstance(value, Memory)
            case "Arg":
                is_type_of = isinstance(value, Arg)
            case _:
                TODO()

        return is_type_of

    def _code(self, params:list[Param]):
        pass

class RawAddress(Function_Base):
    def __init__(self, value):
        match value:
            case Param():
                self.value = value.resolve([])
            case Memory():
                self.value = value
            case _:
                TODO()

    def calculate(self, params:list[Param], deref=True):
        return Word(self.value.address).calculate(params)

class Deref(Function_Base, Calculatable, Memorable):
    def __init__(self, generator, value, offset):
        self._generator = generator

        self.memory = True
        
        match value:
            case Param()|Identifier():
                self.value = value
            case Memory()|Arg():
                self.value = value
            case Deref():
                self.value = value
            case Word():
                self.value = Memory(value)
            case _:
                TODO(f"value {value} cannot be deref'ed")

        self.offset = self.parse_argument_with_type(self._generator, offset, "ATTRIBUTE")

        if isinstance(self.offset, Word) and self.offset.value_count() != 2:
            self.offset = Word(self.offset, 2)


        if not self.value:
            pass

    def __repr__(self):
        return f"Deref(value={self.value}, offset={self.offset})"

    def is_memory(self, params:list[Param]):
        return True
    
    def eval(self, params:list[Param]):
        value = self.value.resolve(params)

        return value.eval(params)
    
    def value_count(self):
        TODO()
    
    def calculate(self, params:list[Param], deref=True):
        code = None

        value = self.value.resolve(params)

        #if isinstance(self.value, Param):
        #    self.value = self.value.resolve(params)

        match value:
            case Memory():
                code = value.calculate(params, offset=self.offset, deref=deref)
            case Arg():
                code = value.calculate(params, offset=self.offset, deref=deref)
            case Deref():
                code = value.value
                code = code.resolve(params)
                code = code.calculate(params, deref=True)
                code = code + [Operand("push")] + self.offset.calculate(params) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]
            case Word():
                code = Memory(value)
                code = code.calculate(params, offset=self.offset, deref=deref)
                # code = [self.value.code(params)]
            case _:
                TODO()

        return code

    def _code(self, params:list[Param]):
        pass

    def resolve(self, params:list[Param]):
        match [self.value, self.offset]:
            case [Identifier(), _]|[_, Identifier()]:
                value = self.value.resolve(params)
                offset = self.offset.resolve(params)

                deref = Deref(self._generator, value, offset)
            case _:
                deref = self
        
        return deref

class Arg(Function_Base, Calculatable, Memorable):
    def __init__(self, index):
        self.index = index
        self.index = self.index.resolve([])
        self.offset = None

        self.memory = True

    def __repr__(self):
        return f"Arg(index={self.index})"
        
    def is_memory(self, params:list[Param]):
        return True
    
    def calculate(self, params:list[Param], offset=None, deref=False):
        index = self.index.resolve(params)
        index = index.code(params)

        deref |= self.requires_deref

        match [offset]:
            case [None]:
                code = [Operand("read signed word arg"), index]
                if deref:
                    code += [Operand("deref")]
            case [_]:
                code = [Operand("read signed word arg"), index, Operand("push")] + offset.calculate(params) + [Operand("+")]
                if deref:
                    code += [Operand("deref")]
            case _:
                TODO()

        return code

    def _code(self, params:list[Param]):
        index = self.index.resolve(params)
        
        if isinstance(index, int):
            index = Word(index)

        code = index.code(params)

        return code

class Object(Function_Base, Calculatable, Memorable):
    def __init__(self, generator, index, flag=None):
        self.index = index
        # self.index = self.index.resolve([])
        self.flag = flag

        self.memory = True

        self.default_enum = None

    def is_memory(self, params:list[Param]):
        return True
    
    def __repr__(self):
        return f"Object(index={self.index}, flag={self.flag})"
        
    def calculate(self, params:list[Param]):
        index = self.index.resolve(params)
        code = index.calculate(params)

        return code
    
    def _code(self, params:list[Param]):
        index = self.index.resolve(params)
        flag = self.flag.resolve(params)
        
        code = [Opcode("obj")] + self._terminate(index.calculate(params) + [flag.code(params)])
        code = self._clean_calucatable(code, params)

        return f"""
{code}     // (5d) IF $2268 & 0x40 THEN UNLOAD OBJ 0 (TODO: verify this)"
        """
    
class FunctionKey(Function_Base):
    def __init__(self, index):
        self.index = index
        self._value_count = 3
        if isinstance(self.index, Param):
            self.index = self.index.eval([])
        self.address = 0x928294 + self.index
        
        if (self.index % self.value_count()) != 0:
            raise Exception("invalid index (only index%3==0 is allowed")

    def __repr__(self):
        return f"FunctionKey({self.index})"
        
    def eval(self):
        return Range(self.address, self.address + (self.value_count() - 1))

    def _code(self, params:list[Param]):
        code = Word(self.index)
        code._value_count = self.value_count()
        code = code.code()

        return code

class Function(Function_Base):
    key:FunctionKey = None

    def __init__(self, name, script, args, annotations=[]):
        self.name = name
        if isinstance(name, Token):
            self.name = self.name.value
        self.script = script
        self.script = list(filter(lambda item: item is not None, self.script))
        self.args = args
        self.install = False
        self.address = None
        self.inject = []
        self.terminate = True
        self.async_call = False
        self.count_limit = None
        if annotations:
            self.set_annotations(annotations)

    def set_annotations(self, annotations):
        for annotation in annotations:
            match annotation:
                case Annotation_Async():
                    self.async_call = True
                case Annotation_Install():
                    self.install = True
                    self.address = annotation.eval()
                    self.terminate = annotation.terminate
                case Annotation_Inject():
                    self.inject.append(annotation)
                    self.terminate = annotation.terminate
                case Annotation_CountLimit():
                    self.count_limit = annotation.count_limit.eval([])
                case _:
                    TODO()
        
        if self.install and self.terminate:
            #if self.script and not isinstance(self.script[-1], End):
            self.script += [ End() ]

    def __repr__(self):
        return f"Function('name={self.name}', address={self.address}, install={self.install}, args={self.args})"
        
    def _code(self, params:list[Param]):
        out_params = []

        for index, arg in enumerate(self.args):
            out_params.append(Param(arg.name, Arg(Word(index * 2, 1))))

        return Function_Code(self.script, '\n').code(out_params)

class Annotation_Install(BaseBox):
    def __init__(self, address=None, terminate=True):
        self.address = address
        self.terminate = terminate

    def eval(self):
        if self.address != None:
            return self.address.eval([])
        else:
            return None
    
class Annotation_Inject(BaseBox):
    def __init__(self, address, terminate):
        self.address = address
        self.terminate = terminate

    def eval(self, params:list[Param]):
        return self.address.eval(params)
    
class Annotation_Async(BaseBox):
    def __init__(self):
        pass

class Annotation_CountLimit(BaseBox):
    def __init__(self, count_limit):
        self.count_limit = count_limit

class Address(Function_Base):
    def __init__(self, value, length=3):
        self.value = value
        self.length = length

        self.scripts_start_addr = 0x928000

    def __repr__(self):
        if self.value:
            return f"Address({self.value}/{self.eval()})"
        else:
            return f"Address(-)"
    
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
        
    def _code(self, params:list[Param]):
        address = self.eval()
        address = '{:06X}'.format(address, 'x')
        address = wrap(address, 2)
        
        return ' '.join(reversed(address))

    def eval(self):
        return self.rom2scriptaddr(self.value)

    def count(self, params:list[Param]):
        return len(self.code_clean(params).split(" "))

class _Address(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self):
        num = int(self.value.value, 16)
        return num
    
class String(Function_Base):
    def __init__(self, generator, value, install = False):
        self._generator = generator

        self.value = value
        if isinstance(self.value, Token):
            self.value = self.value.value
            self.value = re.sub("\"", "", self.value)
        self.install = install
        self.text_key = None
        self.address = None

    def __repr__(self):
        return f"String('{self.value}')"
        
    def eval(self):
        return self.value

    def count(self, params:list[Param]):
        return RawString(self.value).count(params)
        
    def _code(self, params:list[Param]):
        if not self.text_key:
            code = re.sub("\"", "", self.value)
        else:
            code = Word(self.text_key.index)
            code = code.code([])

        return code
    
class InstalledString(Function_Base):
    def __init__(self, generator, value):
        self._generator = generator
        self.value = value

        self.string_key = None

        self.installed = False

    def _code(self, params:list[Param]):
        value = self.value.resolve(params)

        match value:
            case String():
                if not value.value.endswith("[END]"):
                    value.value += "[END]"

                value = self._generator.add_string(value)

                value = value.code(params)
            #case int():
            #    pass
            case _:
                TODO();

        return value

class RawString(Function_Base):
    def __init__(self, value):
        self.value = value
        self.install = False
        if isinstance(self.value, Token):
            self.value = self.value.value[1:-1]
        elif isinstance(self.value, Param):
            self.value = self.value.value.value

    def __str__(self):
        return f"RawString('{self.eval()}')"

    def eval(self):
        value = self.value
        # value = re.sub("\'", "", value)
        return value
        
    def _code(self, params:list[Param]):
        code = self.eval()

        lexer = LexerGenerator()
        lexer.add('SLOW', '\[SLOW\]')
        lexer.add('LF', '\[LF\]')
        lexer.add('B', '\[B\]')
        lexer.add('END', '\[END\]')
        lexer.add('CHOICE', '\[CHOICE\]')
        lexer.add('MEM1', '\[MEM1\]')
        lexer.add('MEM2', '\[MEM2\]')
        lexer.add('HEX', '\[0x[0-9a-f]{2}\]')
        lexer.add('PAUSE', '\[PAUSE:[0-9a-f]{2}\]')

        lexer.add('…', '\…')
        lexer.add('`', '\`')
        lexer.add('´', '\´')

        lexer.add('CHAR', '.')
        lexer = lexer.build()

        code = list(lexer.lex(code))

        def f(c):
            match c:
                case _ if c.name == "CHAR":
                    return c.value.encode('ASCII').hex()
                case _ if c.name == "…":
                    return '_'.encode('ASCII').hex()
                case _ if c.name == "`":
                    return '{'.encode('ASCII').hex()
                case _ if c.name == "´":
                    return '}'.encode('ASCII').hex()
                case _ if c.name == "SLOW":
                    return "96"
                case _ if c.name == "LF":
                    return "0a"
                case _ if c.name == "B":
                    return "86"
                case _ if c.name == "END":
                    return "00"
                case _ if c.name == "CHOICE":
                    return "0a 8b"
                case _ if c.name == "MEM1":
                    return "a1"
                case _ if c.name == "MEM2":
                    return "a2"
                case _ if c.name == "HEX":
                    return re.sub("\[0x([0-9a-f]{2})\]", r"\1", c.value)
                case _ if c.name == "PAUSE":
                    return "80 " + re.sub("\[PAUSE:([0-9a-f]{2})\]", r"\1", c.value) + " 80"
                case _:
                    raise Exception("invalid char")
        code = [f(c) for c in code]
        code = ' '.join(code) + f" // '{self.value}'"
        return code
        
class FunctionArg(BaseBox):
    def __init__(self, name, enum_base = None):
        self.name = name

        self.enum_base = enum_base

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

class Call(Function_Base, Calculatable):
    async_call = False
    
    def __init__(self, generator, function, params=[]):
        self.generator = generator
        self.params = self._paramify(params)

        match function:
            case Function():
                if not function.install:
                    self.function = function
                    self.address = function.address
                    self.async_call = function.async_call
                    #for p, a in zip(self.params, function.args):
                    #    if p.name == None:
                    #        p.name = a.name
                else:
                    self.function = function
                    self.address = function.address
                    self.async_call = function.async_call
            case Param():
                self.function = None
                self.address = function.eval([])
            case Identifier():
                self.function = function
                self.address = None
            case _:
                TODO()

        if self.address == None:
            pass

    def _paramify(self, params=[]):
        for index, param in enumerate(params):
            if not isinstance(param, Param):
                params[index] = Param(None, param)

        return params

    def __repr__(self):
        return f"Call(address={Address(self.address)}, function={self.function}, params={self.params})"
    
    def calculate(self, address:str, call_params:list[Param], params:list[Param]):
        code = []

        if not call_params:
            match self.async_call:
                case True:
                    code = [Opcode("async call"), address]
                case False:
                    code = [Opcode("call"), address]
        else:
            for param in call_params:
                code += self._terminate(param.value.calculate(params))

            match self.async_call:
                case True:
                    code = [Opcode("async call params"), Word(len(call_params), 1).code(params)] + code + [address]
                case False:
                    code = [Opcode("call params"), Word(len(call_params), 1).code(params)] + code + [address]

        return code
    
    def _code(self, params:list[Param]):
        #params = self.handle_params(params, self.params)

        if self.params and self.function:
            for p, a in zip(self.params, self.function.args):
                if a.enum_base == None:
                    continue

                if p.name == None:
                    continue
                
                value = Enum_Call(self.generator, f"{a.enum_base}.{p.name}", False)

                if value.value == None:
                    continue

                p.name = None
                p.value = value.value

                pass

        # TODO: should be done for all elements
        for param in self.params:
            param = param.resolve(params)
            
            if isinstance(param, Deref):
                param.update(params)
        
        if self.function:
            function = self.function.resolve(params)
        else:
            function = None
            
        out_params = []
        if function:
            out_params = [Param(param.name, param.value.resolve(params) if param.value else None) for param in self.params]

            for param in out_params:
                if param.value == None:
                    for p in params:
                        if param.name == p.name:
                            param.value = p.value

            #params = self.handle_params(params, self.params)

            for p, a in zip(out_params, function.args):
                if p.name != a.name:
                    pass
                p.name = a.name

        if function == None or function.install:
            address = "xx xx xx"
            if self.address == None and function != None: #TODO: should be done by the linker
                self.address = function.address
            if self.address != None:
                address = Address(self.address)
                address = address.code([])
            else:
                pass

            code = self.calculate(address, out_params, params)
            code = self._clean_calucatable(code, params)

            return code
        
        else:
            return Function_Code(function.script, '\n').code(out_params)

class End(Function_Base):
    def eval(self):
        return 0
        
    def _code(self, params:list[Param]):
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

    def _code(self, params:list[Param]):
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
        
    def _code(self, params:list[Param]):
        return f"""
{self.text.value.code(params)}        // eval({self.text.value})
        """

class Function_Goto(Function_Base):
    def __init__(self, label=None):
        self.label = label
        self.distance = None

    def eval(self):
        return 0
        
    def _code(self, params:list[Param]):
        distance = "yy yy"
        if self.distance:
            distance = Word(self.distance).code(params)
        else:
            pass

        return f"""
04 {distance}      // goto({self.label}/{distance})
        """

class If_list(Function_Base, Memorable):
    def __init__(self, if_list):
        self.if_list = if_list


    def is_memory(self, params:list[Param]):
        is_memory = False

        for element in self.if_list:
            is_memory = is_memory or element.is_memory(params)

        return is_memory

    def update_memory(self, params:list[Param]):
        is_memory = False

        for element in self.if_list:
            is_memory = is_memory or element.is_memory(params)

        for element in self.if_list:
            element.forced_memory = is_memory


    def _code(self, params:list[Param]):
        self.update_memory(params)

        if_list = []
        if_depleted = False

        is_memory = self.is_memory(params)

        if is_memory:
            def pad_all_but_last(element:If, is_last:bool):
                script = [element] + element.script
                if not is_last:
                    script += [Jump(None)]

                return script
                                 
            if_count = [Function_Code(pad_all_but_last(element, index == (len(self.if_list) - 1)), '\n').count(params) for index,element in enumerate(self.if_list)]
            if_count.reverse()
            if_count.pop()

            for element in self.if_list:
                count = sum(if_count)
                if count > 0:
                    jump = Jump(count)
                    jump.distance = count
                    script_with_jump = element.script + [jump]
                else:
                    script_with_jump = element.script

                if if_count:
                    if_count.pop()

                if_list.append(element)
                if_list += script_with_jump
                element.distance = Function_Code(script_with_jump, '\n').count(params)
        else:
            for element in self.if_list:
                condition = None
                if element.condition:
                    condition = element.condition.resolve(params)

                if condition != None and condition.is_memory(params):
                    self.update_memory(params)
                    raise Exception("memory in non-memory if")
                elif not if_depleted and (condition == None or element.eval(params)):
                    if_list.append(element)
                    if_depleted = True
                
        return Function_Code(if_list, '\n').code(params)

class If(Function_Base, Calculatable, Memorable):
    def __init__(self, condition, script, if_properties):
        self.forced_memory = False
        
        self.condition = condition
        self.script = script
        self.if_properties = if_properties

        self.distance = None


    def is_memory(self, params:list[Param]):
        condition = False

        if self.condition:
            condition = self.condition.resolve(params)

            condition = condition.is_memory(params)

        return condition

    def update_memory(self, params):
        #self.handle_params(params)

        if self.condition:
            condition = self.condition.resolve(params)

            if isinstance(condition, UnaryOp):
                self.memory = condition.memory
            elif isinstance(condition, Memory):
                self.memory = True
            elif isinstance(condition, BinaryOp):
                self.memory = condition.memory

    def eval(self, params:list[Param]):
        self.update_memory(params)
        condition = self.condition.resolve(params)

        match condition:
            case Word():
                condition = condition.eval(params) > 0
            case BinaryOp()|Identifier()|Is():
                condition = condition.eval(params)
            case None:
                condition = True
            case _:
                raise Exception("unknown type for IF condition")
            
        return condition

    def _code(self, params:list[Param]):
        destination = "xx xx"
        if self.distance != None:
            destination = Word(self.distance)
            destination = destination.code(params)

        condition = None
        if self.condition:
            condition = self.condition.resolve(params)

        if self.forced_memory or self.is_memory(params):
            if condition:
                code = self.calculate(params)
                code = self._clean_calucatable(code, params)
                
                return code
            else:
                return Function_Code([], '\n').code(params) #TODO: else repeated self.script needlessly
        else:
            return Function_Code(self.script, '\n').code(params)
        
    def calculate(self, params:list[Param]):
        destination = "xx xx"
        if self.distance != None:
            destination = Word(self.distance)
            destination = destination.code(params)

        code = []

        condition = self.condition.resolve(params)
        condition = condition.calculate(params)

        inverted = self.if_properties[0]
        if isinstance(self.condition, UnaryOp) and not isinstance(self.condition, Invert):
            inverted = not inverted

        currency_if = False
        if self.condition and isinstance(self.condition, BinaryOp) and self.condition.left:
            condition_left = self.condition.left.resolve(params)
            if condition_left and isinstance(condition_left, Memory) and condition_left.address == 0x2348:
                currency_if = True

        match [inverted, self.if_properties[1]]:
            case [_, True]:
                opcode = None
                match self.condition:
                    case GreaterEquals():
                        opcode = Opcode("if_currency<") # TODO: inverted, should be Opcode("if_currency>=")
                    case Lower():
                        opcode = Opcode("if_currency>=") # TODO: inverted, should be Opcode("if_currency<")
                    case _:
                        TODO()

                left = self.condition.left.resolve(params)
                if not isinstance(left, Memory): # or left.address != 0x2348:
                    TODO()
                left = left.calculate(params)
                right = self.condition.right.resolve(params)
                right = right.calculate(params)
                
                code = [opcode] + self._terminate(left) + self._terminate(right) + [destination]
            case [True, _]:
                opcode = Opcode("if!")
                code = [opcode] + self._terminate(condition) + [destination]
            case [False, _]:
                opcode = Opcode("if")
                code = [opcode] + self._terminate(condition) + [destination]

        return code
        
class And(BinaryOp):
    def operator(self, inverted=False):
        return Operand("&&")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) and right.eval(params)
    
class Or(BinaryOp):
    def operator(self, inverted=False):
        return Operand("||")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) or right.eval(params)
    
class Equals(BinaryOp):
    def operator(self, inverted=False):
        return Operand("==")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) == right.eval(params)
        
class NotEquals(BinaryOp):
    def operator(self, inverted=False):
        return Operand("!=")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) != right.eval(params)
    
class GreaterEquals(BinaryOp):
    def operator(self, inverted=False):
        return Operand(">=")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) >= right.eval(params)
    
class Greater(BinaryOp):
    def operator(self, inverted=False):
        return Operand(">")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) > right.eval(params)
    
class LowerEquals(BinaryOp):
    def operator(self, inverted=False):
        return Operand("<=")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) <= right.eval(params)
    
class Lower(BinaryOp):
    def operator(self, inverted=False):
        return Operand("<")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) < right.eval(params)
    
class Add(BinaryOp):
    def operator(self, inverted=False):
        if not inverted:
            return Operand("+")
        else:
            return Operand("-")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) + right.eval(params)
    
class Sub(BinaryOp):
    def operator(self, inverted=False):
        if not inverted:
            return Operand("-")
        else:
            return Operand("+")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) - right.eval(params)
    
class Mul(BinaryOp):
    def operator(self, inverted=False):
        return Operand("*")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) * right.eval(params)

class Div(BinaryOp):
    def operator(self, inverted=False):
        return Operand("/")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) // right.eval(params)

class ShiftRight(BinaryOp):
    def operator(self, inverted=False):
        return Operand(">>")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) >> right.eval(params)
    
class ShiftLeft(BinaryOp):
    def operator(self, inverted=False):
        return Operand("<<")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) << right.eval(params)
    
class BinaryAnd(BinaryOp):
    def operator(self, inverted=False):
        return Operand("&")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) & right.eval(params)
    
class BinaryOr(BinaryOp):
    def operator(self, inverted=False):
        return Operand("|")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) | right.eval(params)
    
class BinaryXor(BinaryOp):
    def operator(self, inverted=False):
        return Operand("^")

    def _eval(self, left, right, params:list[Param]):
        return left.eval(params) | right.eval(params)

class Asign(BinaryOp):
    def operator(self, inverted=False):
        return "=" # Opcode("=")
    
    def _code(self, params:list[Param]):
        code = self.calculate(params)
        code = self._clean_calucatable(code, params)

        return code
    
    def _calculate(self, left:any, right:any, params:list[Param]):
        code = []
        if not isinstance(right, list):
            right = right.calculate(params)

        match left:
            case Memory():
                match [left.type, left.value_count()]:
                    case ["char", _]:
                        code = left.calculate(params) + self._terminate(right)
                    case ["28", 1]:
                        code = [Opcode("write temp byte"), left.code(params)] + self._terminate(right)
                    case ["28", _]:
                        code = [Opcode("write temp word"), left.code(params)] + self._terminate(right)
                    case ["22"|"xx", 1]:
                        code = [Opcode("write byte"), left.code(params)] + self._terminate(right)
                    case ["22"|"xx", _]:
                        code = [Opcode("write word"), left.code(params)] + self._terminate(right)
                    case _:
                        TODO()
            case Deref():
                code = [Opcode("write deref")] + self._terminate(left.calculate(params, deref=False)) + self._terminate(right)
            case Object():
                code = self._terminate([Opcode("write object")] + left.calculate(params)) + self._terminate(right)
            case Arg():
                code = [Opcode("write arg"), left.code(params)] + self._terminate(right)
            case _:
                TODO()

        return code

class OrAsign(BinaryOp):
    def operator(self, inverted=False):
        return "|="

    def _code(self, params:list[Param]):
        raise Exception("not implemented")

class AndAsign(BinaryOp):
    def operator(self, inverted=False):
        return "&="

    def _code(self, params:list[Param]):
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

    def _code(self, params:list[Param]):
        combined = "xx xx"

        memory = self.memory.resolve(params)
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

    def _code(self, params:list[Param]):
        memory = self.memory.resolve(params)

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

    def _code(self, params:list[Param]):
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
    def __init__(self, condition, script, inverted):
        self.script = script
        self.inverted = inverted

        self.while_goto_end = Function_Goto()

        self.while_if = If(condition, [], [inverted, False])
        self.memory = self.while_if.memory

        self.list = [self.while_if] + script + [self.while_goto_end]

    def _update_condition(self, params:list[Param]):
        self.while_if.distance = Function_Code(self.script, '\n').count(params) + self.while_goto_end.count(params)
        self.while_goto_end.distance = -(self.while_if.count(params) + Function_Code(self.script, '\n').count(params) + self.while_goto_end.count(params))


    def _code(self, params:list[Param]):
        self._update_condition(params)

        code = self.list
        code = Function_Code(code, '\n').code(params)

        return code

class Void(BaseBox):
    pass

class StringKey(Function_Base):
    def __init__(self, index):
        self.index = index
        self._value_count = 3
        if isinstance(self.index, Param):
            self.index = self.index.eval([])
        self.address = 0x91d000 + self.index
        
        if (self.index % self.value_count()) != 0:
            raise Exception("invalid index (only index%3==0 is allowed")

    def __repr__(self):
        return f"StringKey({self.index})"
        
    def eval(self):
        return Range(self.address, self.address + (self.value_count() - 1))

    def _code(self, params:list[Param]):
        code = Word(self.index)
        code._value_count = self.value_count()
        code = code.code(params)

        return code
    
class Range(BaseBox):
    def __init__(self, start, end):
        self.start = start
        if isinstance(self.start, Word):
            self.start = self.start.eval([])
        self.end = end
        if isinstance(self.end, Word):
            self.end = self.end.eval([])

        if type(self.start) != type(self.end):
            raise Exception("type of start and end don't match")
        
    def __repr__(self):
        return f"Range({self.start}..{self.end})"

    def eval(self, params:[Param]):
        list = []
        if isinstance(self.start, StringKey):
            step = self.start.value_count()
            for index in range(self.start.index, self.end.index + step, step):
                list.append(StringKey(index))
        elif isinstance(self.start, FunctionKey):
            step = self.start.value_count()
            for index in range(self.start.index, self.end.index + step, step):
                list.append(FunctionKey(index))
        elif isinstance(self.start, Memory):
            step = 2
            for address in range(self.start.eval(params), self.end.eval(params) + step, step):
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
    def __init__(self, generator, x, y, direction, enter_code):
        self.x = x.eval([])
        self.y = y.eval([])
        self.direction = self.parse_argument_with_type(generator, direction, "DIRECTION")
        self.enter_code = enter_code
        if isinstance(self.enter_code, Param):
            self.enter_code = self.enter_code.value

class Soundtrack(Function_Base):
    def __init__(self, generator, track, volume):
        self.track = self.parse_argument_with_type(generator, track, "MUSIC")
        self.volume = volume

        self._generator = generator
    
    def _code(self, params:list[Param]):
        function_transition = self._generator.get_function("music_enter")
        function_transition = Call(self._generator, function_transition, [self.track, self.volume])
        function_transition = function_transition.code(params)

        return function_transition

class Map(Function_Base):
    class Collection(StrEnum):
        ENTRANCE = "entrance"
        SOUNDTRACK = "soundtrack"
        B_TRIGGER = "b_trigger"
        STEPON_TRIGGER = "stepon_trigger"

    class Trigger(StrEnum):
        ENTER = "trigger_enter"

    variant: int = None

    enums:dict[str, Enum] = {}
    enum_entrance:list[MapEntrance] = None
    enum_soundtrack:list[Soundtrack] = None
    enum_stepon_trigger:list[Function] = None
    enum_b_trigger:list[Function] = None

    functions:dict[str, Function] = {}
    trigger_enter:Function = None

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
        self.enum_soundtrack = self._extract_enum(self.Collection.SOUNDTRACK)
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
    
    def soundtrack(self) -> Soundtrack:
        if self.enum_soundtrack:
            return self.enum_soundtrack.values[0].value
        else:
            return None

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
        self._generator = generator

        self.map_name = map_name.name
        self.entrance_name = entrance_name.name
        self.direction = self.parse_argument_with_type(self._generator, direction, "DIRECTION")

        generator.add_map_transition(self)
        self.scope = generator.current_scope()

    def link(self, map: Map, entrance: MapEntrance):
        self.map = map
        self.entrance = entrance

        pass

    def _code(self, params:list[Param]):
        if self.map == None or self.entrance == None or self.map.variant == None:
            return f"""
yy // linking required
            """
        else:
            entrance_index = [e.value for e in self.map.enum_entrance.values]
            entrance_index = entrance_index.index(self.entrance)

            track_in = self.scope.value
            if track_in:
                track_in = track_in.soundtrack()
            if track_in:
                track_in = track_in.track
                track_in = track_in.eval(params)
            
            track_out = self.map.soundtrack()
            if track_out:
                track_out = self.map.soundtrack().track
                track_out = track_out.eval(params)
            
            if track_in != track_out:
                change_music = True
            else:
                change_music = False

            track_in = self.scope.value
            if track_in:
                track_in = track_in.soundtrack()
            if track_in:
                track_in = track_in.volume
                track_in = track_in.eval(params)
            
            track_out = self.map.soundtrack()
            if track_out:
                track_out = self.map.soundtrack().volume
                track_out = track_out.eval(params)
            

            if track_in != track_out:
                change_volume = True
            else:
                change_volume = False
            
            match [change_music, change_volume]:
                case [True, _]:
                    change_music = Word(0x01)
                case [_, True]:
                    change_music = Word(0x01)

                # TODO: don't restart music if only the volume changes
                #case [True, False]:
                #    change_music = Word(0x01)
                #case [False, True]:
                #    change_music = Word(0x02)
                #case [True, True]:
                #    change_music = Word(0x03)
                
                case _:
                    change_music = Word(0x00)

            call_params = [
                self.map.map_index,
                self.entrance.x,
                self.entrance.y,
                self.direction,
                self.entrance.direction,
                change_music
            ]
            call_params = [Param(None, Word(param, 1)) for param in call_params]

            function_transition = self._generator.get_function("transition")
            function_transition = Call(self._generator, function_transition, call_params)
            function_transition = function_transition

            params = self.merge_params(params, call_params)

            code = Function_Code([
                Asign(Memory(0x23b7), Word(entrance_index)),
                Asign(Memory(0x23b9), Word(self.map.variant)),
                function_transition
            ], '\n').code(params)

            return code

# unary operators

class Dead(UnaryOp):
    def _calculate(self, value:any, params:list[Param]):
        code = []

        code = value + [Operand("dead")]

        return code
    
class Rand(UnaryOp):
    def _calculate(self, value:any, params:list[Param]):
        code = []

        code = [Operand("random word"), Operand("push")] + value + [Operand("&")]

        return code
    
class RandRange(UnaryOp):
    def _calculate(self, value:any, params:list[Param]):
        code = []

        code = value + [Operand("randrange")]

        return code
    
class Invert(UnaryOp):
    def _calculate(self, value:any, params:list[Param]):
        code = []

        code = value + [Operand("!")]

        return code
    
class Loot(Function_Base):
    def unwrap_param(self, param):
        if isinstance(param, Param):
            param = param.value

    def __init__(self, generator, with_kneel_animation:bool, object, reward, amount, next):
        self._generator = generator
        if with_kneel_animation:
            self.animation = Word(0x39, 1)
        else:
            self.animation = Word(0x3a, 1)
        self.object = object
        self.reward = self.parse_argument_with_type(self._generator, reward, "LOOT_REWARD")
        self.amount = amount
        self.next = Word(next)
    
        flag = self._generator.get_flag()

        self.object = Object(self._generator, object, flag)
        self._generator.add_object(self.object)

        self.function = generator.get_function("loot")

    def _code(self, params:list[Param]):
        call_params = [self.animation, self.object.flag, Word(self.object.index), self.reward, self.amount, self.next]

        return Call(self._generator, self.function, call_params).code(params)
    
class Axe2Wall(Function_Base):
    def unwrap_param(self, param):
        if isinstance(param, Param):
            param = param.value

    def __init__(self, generator, object):
        self._generator = generator
        self.object = object
    
        flag = self._generator.get_flag()

        self.object = Object(self._generator, object, flag)
        self._generator.add_object(self.object)

        self.function = generator.get_function("axe2_wall")

    def _code(self, params:list[Param]):
        call_params = [self.object.flag, self.object]

        return Call(self._generator, self.function, call_params).code(params)
    
class Reference(Function_Base):
    def __init__(self, generator, name:any):
        self._generator = generator
        self._scope = generator.current_scope()

        self.name = name
        self.value = None

        match name:
            case Param():
                if name.value:
                    self.value = name.value
                    name = name.value.name

                    self._generator.add_function(self.value, self._generator.current_scope(), reference=True)
                else:
                    name = name.name
            case _:
                pass

        if isinstance(name, Identifier):
            name = name.name

        self._value_count = None

        self.update_reference(name)

    def __repr__(self):
        return f"Reference(name={self.name}, value={self.value})"
    
    def update_reference(self, name:str):
        if not self.value:
            self.value = self._generator.get_function(name, self._scope)
            if self.value:
                self._generator.reference_function(self.value)

    def eval(self, params:list[Param]):
        self.update_reference(self.name)

        match self.value:
            case Function():
                self._value_count = 2

                index = 0xffff
                if self.value.key:
                    index = self.value.key
                    index = index.index
                return index
            case None:
                self._value_count = 2
                self.update_reference(self.name)

                return 0xffff
            case _:
                raise Exception(f"invalid reference {self.value}")
    
    def calculate(self, params:list[Param]):
        code = Word(self.eval(params)).code(params)
        
        return code
    
class Jump(Function_Base):
    def __init__(self, distance:int):
        self.distance = distance

    def _code(self, params:list[Param]):
        code = "xx xx"
        
        if self.distance != None:
            code = Word(self.distance)
            code = code.code(params)

        return f"""
04 {code}       // (04) SKIP 10 (to 0x999907)
        """