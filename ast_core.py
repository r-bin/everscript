from rply.token import BaseBox
import re
from textwrap import wrap

class Function_Base(BaseBox):
    params = []

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

class BinaryOp(Function_Base):
    def __init__(self, left, right):
        self.left = left
        self.right = right

        self.value_count = 2
    
    def eval(self):
        self.left.params = self.params
        self.right.params = self.params

        if self.params:
            sp = {x.name : x for x in self.params}
            if isinstance(self.left, Param) and self.left.name != None:
                self.left.value = sp[self.left.name].value
            if isinstance(self.right, Param) and self.right.name != None:
                self.right.value = sp[self.right.name].value

        return self._eval()

    def _code(self):
        value = self.eval()
        self.value_count = max(self.left.value.value_count, self.right.value.value_count)
        
        if self.value_count == 1:
            value = '{:02X}'.format(value, 'x')
        elif self.value_count == 2:
            value = '{:04X}'.format(value, 'x')
        elif self.value_count == 3:
            value = '{:06X}'.format(value, 'x')

        value = re.sub("0x", "", value)
        value = wrap(value, 2)
        
        return ' '.join(reversed(value))
    
    def flatten(self, x):
        if isinstance(x, BinaryOp):
            return self.flatten(x.left) + [x.operator()] + self.flatten(x.right)
        elif isinstance(x, Param):
            if not x.value:
                sp = {x.name : x for x in self.params}
                x.value = sp[x.name].value
            return self.flatten(x.value)
        else:
            return [x]

    def operator(self):
        return ""

class Word(Function_Base):
    def __init__(self, value):
        if isinstance(value, int):
            self.value_original = value
            self.value = value
            self.value_count = 2
        else:
            self.value_original = value
            self.value = int(value.value, 16)

            count = re.sub("0x", "", value.value)
            count = wrap(count, 2)
            count = len(count)
            self.value_count = count

    def __repr__(self):
        return f"Word({self.value_original})"

    def eval(self):
        return self.value
        
    def _code(self):
        value = self.value

        if value < 0:
            nbits = self.value_count * 8
            value = (value + (1 << nbits)) % (1 << nbits)

        if self.value_count == 1:
            value = '{:02X}'.format(value, 'x')
        elif self.value_count == 2:
            value = '{:04X}'.format(value, 'x')
        elif self.value_count == 3:
            value = '{:06X}'.format(value, 'x')

        value = re.sub("0x", "", value)
        value = wrap(value, 2)
        
        return ' '.join(reversed(value))
    
class Memory(Function_Base):
    def __init__(self, address=None, flag=None):
        self.address = address
        if isinstance(self.address, Word):
            self.address = self.address.eval()
        self.flag = flag
        if isinstance(self.flag, Word):
            self.flag = self.flag.eval()
        self.inverted = False
        self.type = "xx"

    def __repr__(self):
        return f"Memory(address={self.address}, flag={self.flag})"
    
    def eval(self):
        return self.address

    def _code(self):
        address = self.address
        flag = self.flag
        
        if address >= 0x2834:
            address -= 0x2834
            self.type = "28"
        elif address >= 0x2258:
            address -= 0x2258
            self.type = "24"
        else:
            if address >= 0x2258:
                address -= 0x2258
            else:
                address += 0xDDA8
            self.type = "xx"

        if not flag:
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

class Param(BaseBox):
    def __init__(self, name, value):
        self.name = None
        if name != None:
            self.name = name.value
        self.value = value

    def __repr__(self):
        return f"Param(name={self.name}, value={self.value})"

    def eval(self):
        if isinstance(self.value, Memory):
            return self.value.address.value
        elif isinstance(self.value, Word):
            return self.value.value
        else:
            return self.value.eval()

class Function_Code(Function_Base):
    def __init__(self, script, delimiter=' '):
        self.script = script
        self.delimiter = delimiter

    def _code(self):
        list = []

        for a in self.script:
            match a:
                case _ if isinstance(a, int):
                    list.append('{:02X}'.format(a, 'x')) # TODO
                case _ if isinstance(a, Function_Base):
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
                        list.append(a.value.code(self.params))
                case _ if isinstance(a, str):
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
