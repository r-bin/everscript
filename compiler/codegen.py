from compiler.ast_everscript import *

from itertools import dropwhile
import numpy as np
import re
import binascii
from textwrap import wrap
from enum import StrEnum

class Scope(BaseBox):
    class Type(StrEnum):
        DEFAULT = "DEFAULT"
        MAP = "MAP"
        OBJECT = "OBJECT"

    type: Type = Type.DEFAULT
    name: str = None
    identifier: dict[str, any] = {}

    def __init__(self, type: Type | BaseBox = Type.DEFAULT):
        if isinstance(type, BaseBox):
            type = self.Type(type.name)

        self.type = type
        self.identifier = {} #TODO should be optional, but seems to be required

class _Splice():
    def __init__(self, list, element=None):
        self.list = np.array(list)
        self.element = element
        self.index = np.where(self.list == self.element)

    def before(self):
        return list[:self.index]

    def after(self):
        return list[self.index:]
        
    def until(self):
        return self.before() + self.element

    def starting(self):
        return self.after() + self.element

class CodeGen():
    wipe_strings = False

    def __init__(self, linker):
        print(f"CodeGen.init()")
        self.linker = linker

        self.scopes: list[Scope] = [Scope()]

        self.code: list[Function] = []
        self.system = {}

        self.strings = []
        self.memory = []
        self.flags = []
        self.patches = []
        self.maps = []
        self.exits = []

    def get_memory_allocation(self):
        strings = []
        for s in self.strings:
            strings.append(f"   - [{'{:06X}'.format(s.text_key.address, 'x')}, {'{:04X}'.format(s.text_key.count(), 'x')}] {s.text_key}")
            strings.append(f"   - [{'{:06X}'.format(s.address, 'x')}, {'{:04X}'.format(s.value.count(), 'x')}] {s}")
        strings = '\n'.join(strings)
        memory = '\n'.join([f"   - [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count(), 'x')}] {m}" for m in self.memory])
        flag = '\n'.join([f"   - [{'{:04X}'.format(f.address, 'x')}, {'{:04X}'.format(f.count(), 'x')}] {f}" for f in self.flags])

        return f"""
{self.linker.get_memory_allocation()}

allocated ROM:
  strings:
{strings}

  scripts:
    TODO

allocated RAM:
  memory:
{memory}

  flags:
{flag}
        """.strip()

    def get_memory(self):
        memory = self.linker.link_memory()

        self.memory.append(memory)
    def get_flag(self):
        memory = self.linker.link_flag()

        self.flags.append(memory)

    def add_patch(self, patch_name):
        self.patches.append(patch_name)

    def add_string(self, string, text):
        self.linker.link_string(string, text)

        self.strings.append(string)

    def add_function(self, function: Function): #TODO
        #self.code += f"<address> {expression.count()}\n"
        
        if function.install == False:
            self.system[function.name.value] = function
        else:
            self.code.append(function)
    
    def get_function(self, name): #TODO
        if name.value in self.system:
            return self.system[name.value]

        for function in self.code:
            if function.name == name:
                return function
        
        raise Exception(f"function '{name}' is not defined: {self.code}")

    def add_map(self, map):
        self.maps.append(map)

    def add_exit(self, exit):
        self.exits.append(exit)

    def generate(self):
        list = []

        if self.wipe_strings:
            list.append(self._wipe_strings())

        self.linker.link_function(self.code)
        self.linker.link_map(self.maps)
        self.linker.link_call(self.code)

        for function in self.code:
            list.append(self._generate(function))

        for map in self.maps:
            list.append(self._generate_map(map))

        for string in self.strings:
            list.append(self._generate_string(string))

        header = ["PATCH"]
        footer = ["EOF"]
        
        return '\n'.join(header + list + footer)

    def _wipe_strings(self):
        list = []

        address = 0x11d000
        count = 0
        repeat = 0x232D
        code = "00"

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} {'{:04X}'.format(repeat, 'x')} // address={address} count={count} repeat={repeat} name='wipe texts'"]
        footer = []

        list += header + [code] + footer

        address = 0x000000
        code = RawString("aya[END]")
        count = code.count()
        code = code.code()

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name='default text'"]
        footer = []

        list += header + [code] + footer

        return '\n'.join(list)

    def _generate_map(self, map: Map):
        list = []

        if map.trigger_enter != None:
            name = map.trigger_enter.name
            address = map.map_data.trigger_enter
            count = 3

            code = map.trigger_enter.address
            code = Address(code).code()

            if address >= 0xC00000: # TODO
                address -= 0xC00000
            elif address >= 0x800000: # TODO
                address -= 0x800000
            elif address >= 0x400000: # TODO
                address -= 0x400000

            header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={name}"]
            footer = []

            list += header + [code] + footer

        return '\n'.join(list)
        

    def _generate_string(self, string):
        list = []

        name = '{:04X}'.format(string.text_key.index, 'x')
        address = string.text_key.address
        count = string.text_key.count()
        code = string.address
        code -= 0xc00000
        code = Word((code & 0xffff) + ((code & 0x7f8000) >> 1))
        code.value_count = 3
        code = code.code()

        if address >= 0xC00000: # TODO
            address -= 0xC00000
        elif address >= 0x800000: # TODO
            address -= 0x800000
        elif address >= 0x400000: # TODO
            address -= 0x400000

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={name}"]
        footer = []

        list += header + [code] + footer

        name = string.value
        address = string.address
        count = string.value.count()
        code = string.value.code()

        if address >= 0xC00000: # TODO
            address -= 0xC00000
        elif address >= 0x800000: # TODO
            address -= 0x800000
        elif address >= 0x400000: # TODO
            address -= 0x400000

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={name}"]
        footer = []

        list += header + [code] + footer

        return '\n'.join(list)

    def _generate(self, function: Function):
        code = function.script
        address = function.address
        count = sum([e.count() for e in code])

        list = []

        list += self._inject(function)
        self.linker.link_goto(function)

        if address >= 0xC00000: # TODO
            address -= 0xC00000
        elif address >= 0x800000: # TODO
            address -= 0x800000
        elif address >= 0x400000: # TODO
            address -= 0x400000

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={function.name}"]
        footer = []

        list += header + [e.code() for e in code] + footer

        return '\n'.join(list)

    def _inject(self, function):
        list = []

        for inject in function.inject:
            list.append(self._inject_function(function, inject))

        return list

    def _inject_function(self, function, inject):
        if inject == None:
            return []
        
        address = inject.eval()
        call = Call(function)
        count = call.count()
        if function.terminate:
            count += 1 # TODO
        
        script = [call.code()]
        if function.terminate:
            script += [ End().code() ]
        else:
            pass

        code = Function_Code(script).script

        if address >= 0xC00000: # TODO
            address -= 0xC00000
        elif address >= 0x800000: # TODO
            address -= 0x800000
        elif address >= 0x400000: # TODO
            address -= 0x400000

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={function.name}"]
        footer = []

        return '\n'.join(header + code + footer)

    def push_scope(self, scope: Scope) -> None:
        self.scopes.append(scope)
    def pop_scope(self) -> Scope:
        if len(self.scopes) <= 1:
            raise Exception("default scope cannot be popped")
        
        return self.scopes.pop()
    def _current_scope(self) -> Scope:
        return self.scopes[-1]
    def _all_identifiers(self) -> dict[str, any]:
        all_identifiers: dict[str, any] = {}

        for scope in self.scopes:
            for identifier, value in scope.identifier.items():
                all_identifiers[identifier] = value

        return all_identifiers

    def set_identifier(self, identifier: str, value: any) -> None:
        if isinstance(identifier, Token):
            identifier = identifier.value

        if identifier in self._current_scope().identifier:
            raise Exception(f"redeclaration of identifier '${identifier}'")

        self._current_scope().identifier[identifier] = value

    def get_identifier(self, identifier: str) -> any:
        all_identifiers = self._all_identifiers()

        if not identifier in all_identifiers:
            raise Exception(f"Enum '{identifier}' does not exist!")
        
        return all_identifiers[identifier]