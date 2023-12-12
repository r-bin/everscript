from compiler.ast_everscript import *

from itertools import dropwhile
import numpy as np
import re
import binascii
from textwrap import wrap
from enum import StrEnum
from typing import Callable

from compiler.linker import Linker

class Scope(BaseBox):
    class Type(StrEnum):
        DEFAULT = "DEFAULT"
        MAP = "MAP"
        AREA = "AREA"
        OBJECT = "OBJECT"
        NATIVE_FUNCTION = "NATIVE_FUNCTION"

    type:Type = Type.DEFAULT
    name:str = None
    value:any = None
    temp_memory:list[Memory] = None
    temp_flag:list[Memory] = None
    temp_vars = None

    def __init__(self, generator, type:Type|BaseBox = Type.DEFAULT):
        self._generator = generator

        if isinstance(type, BaseBox):
            type = self.Type(type.name)

        self.type = type
        self.identifier:dict[str,any] = {}
        self.objects:dict[str,Object] = []
        self.functions:dict[Function] = {}

        self._update_memory()

    def _update_memory(self) -> None:
        if not self.temp_memory:
            self.temp_memory = [m for m in self._generator.linker.memory_manager.memory["memory"]["28"]]
            self.temp_memory = list(reversed(self.temp_memory))

        if not self.temp_flag:
            self.temp_flag = []

        if not self.temp_vars:
            self.temp_vars = []

            if self.type == self.Type.NATIVE_FUNCTION:
                for index in range(00, 30, 2): #TODO: arg33 exists
                    self.temp_vars.append(Arg(index))
                    
                # self.temp_vars = list(reversed(self.temp_vars))

    def allocate_memory(self) -> Memory:
        self._update_memory()

        memory = self.temp_memory
        memory = list(reversed(memory))
        memory = self.temp_memory.pop()

        return memory
    
    def allocate_flag(self) -> Memory:
        self._update_memory()

        if not self.temp_flag:
            memory = self.allocate_memory()
            flags = []

            for offset in range(0, 8):
                flags.append(Memory(memory.address, 1 << offset))
            for offset in range(0, 8):
                flags.append(Memory(memory.address + 1, 1 << offset))
            
            # flags = list(reversed(flags))

            self.temp_flag = flags

        flag = self.temp_flag.pop(0)

        return flag

    def allocate_var(self, name, constant) -> FunctionVariable:
        if self.type == self.Type.NATIVE_FUNCTION:
            value = self.temp_vars.pop()

            function_variable = FunctionVariable(self._generator, name, value, constant)

            self._generator.set_identifier(function_variable.name, value)

            return function_variable
        else:
            pass

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
        self.linker:Linker = linker

        self.scopes:list[Scope] = [Scope(self)]

        self.code:list[Function] = []
        self.system = {}

        self.strings = []
        self.map_transitions:list[MapTransition] = []
        self.memory = []
        self.flags = []
        self.patches = []
        self.maps = []
        self.exits = []

    def push_scope(self, scope:Scope) -> None:
        self.scopes.append(scope)
    def pop_scope(self) -> Scope:
        if len(self.scopes) <= 1:
            raise Exception("default scope cannot be popped")
        
        return self.scopes.pop()
    def current_scope(self) -> Scope:
        return self.scopes[-1]
    def base_scope(self) -> Scope:
        return self.scopes[0]
    def _all_identifiers(self) -> dict[str,any]:
        all_identifiers:dict[str, any] = {}

        for scope in self.scopes:
            for identifier, value in scope.identifier.items():
                all_identifiers[identifier] = value

        return all_identifiers

    def get_memory_allocation(self):
        strings = []
        for s in self.strings:
            strings.append(f"   - [{'{:06X}'.format(s.text_key.address, 'x')}, {'{:04X}'.format(s.text_key.count([]), 'x')}] {s.text_key}")
            strings.append(f"   - [{'{:06X}'.format(s.address, 'x')}, {'{:04X}'.format(s.count([]), 'x')}] {s}")
        strings = '\n'.join(strings)
        memory = '\n'.join([f"   - [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.memory])
        flag = '\n'.join([f"   - [{'{:04X}'.format(f.address, 'x')}, {'{:04X}'.format(f.count([]), 'x')}] {f}" for f in self.flags])

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

    def get_memory(self) -> Memory:
        memory = self.linker.link_memory()

        self.memory.append(memory)

        return memory
    def get_flag(self) -> Memory:
        memory = self.linker.link_flag()

        self.flags.append(memory)

        return memory

    def add_patch(self, patch_name):
        self.patches.append(patch_name)

    def add_string(self, string:String):
        for s in self.strings:
            if s.value == string.value:
                return s

        self.linker.link_string(string)

        self.strings.append(string)

        return string

    def add_map_transition(self, map_transition:MapTransition):
        self.map_transitions.append(map_transition)

    def add_function(self, function:Function, scope:Scope=None):
        if not scope:
            scope = self.current_scope()

        scope.functions[function.name] = function
        
        self.code.append(function)
    
    def get_function(self, name, scope=None, with_exception=False): #TODO
        if isinstance(name, Token):
            name = name.value
        elif isinstance(name, Param):
            name = name.name

        function = None
        for scope in reversed(self.scopes):
            if name in scope.functions.keys():
                function = scope.functions[name]
                break

        if function:
            return function
        
        if scope: #TODO: returns the wrong scope
            if name in scope.functions.keys():
                function = scope.functions[name]

        
        for f in self.code:
            if f.name == name:
                return f #TODO: returns the last method with the same name, not necessarily from the same scope
        
        if with_exception:
            filterd_functions = [f.name for f in self.code if f.name != "anonymous"]
            raise Exception(f"function '{name}' is not defined: {filterd_functions}")
        
        return None

    def add_map(self, map):
        self.maps.append(map)

    def add_exit(self, exit):
        self.exits.append(exit)

    def generate(self):
        output = []

        if self.wipe_strings:
            output.append(self._wipe_strings())

        # map.variant
        self.linker.link_map_variants(self.maps)
        # map_transition()
        self.linker.link_map_transitions(self.maps, self.map_transitions)
        
        # function.count() -> function.address
        for function in self.code:
            self.linker.link_function(function)
        # call()
        self.linker.link_call_in_code(self.code, self.code)

        # fun f() {}
        for function in self.code:
            if function.install:
                output.append(self._generate_function(function))

        variants = self.get_map_variants()
        if variants:
            output.append(self._generate_map())

            function_keys = [function for function in self.code if function.key != None]
            function_keys.sort(key=lambda k: k.key.index)
            for function in function_keys:
                output.append(self._generate_function_key(function))

        # string()
        for string in self.strings:
            output.append(self._generate_string(string))

        header = ["PATCH"]
        footer = ["EOF"]
        
        return '\n'.join(header + output + footer)

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
    
    def _generate_map_trigger(self, map_data, maps:list[Map], count:int, enum_triggers:Callable[[Map], Enum_Entry|Function], address_triggers:Callable) -> list[str]:
        code_list = []

        function_nop = self.get_function("_trigger_nop")

        def append_trigger(code_list, address, code, name):
            count = 2
            
            code = code.index
            code = Word(code)
            code = code.code([])

            if address >= 0xC00000: # TODO
                address -= 0xC00000
            elif address >= 0x800000: # TODO
                address -= 0x800000
            elif address >= 0x400000: # TODO
                address -= 0x400000

            header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name='{name}'"]
            footer = []

            code_list += header + [code] + footer


        if len(maps) == 1:
            map = maps[0]

            triggers = enum_triggers(map)
            
            for index in range(count):
                name = "anonymous"
                function = triggers[index] or function_nop
                if isinstance(function, Enum_Entry):
                    name = function.name
                    function = function.value

                if isinstance(function, Function):
                    self.code.append(function)
                    self.linker.link_function(function)
                    self.linker.link_function_key(function)
                    code_list.append(self._generate_function(function))

                    code = function.key
                else:
                    self.linker.link_function(function.function)
                    self.linker.link_function_key(function.function)

                    code = function.function.key

                name = f"maps[{map_data.index}, {map.name}].trigger[{index}, {name}]"

                append_trigger(code_list, address_triggers(index), code, name)
        else:
            for index in range(count):
                name = "misc" #TODO
                name = f"maps[{map_data.index}, {'/'.join([map.name for map in maps])}].trigger[{index}, {name}]"

                code_triggers = []

                for map in maps:
                    function = enum_triggers(map)[index]
                    match function:
                        case Function():
                            pass
                        case Enum_Entry():
                            function = function.value
                        # case Loot():
                        #     function = function.value
                        case None:
                            function = function_nop
                        case _:
                            TODO()

                    if not isinstance(function, Call):
                        function = Call(self, function)
                    else:
                        pass

                    test = If(
                            Equals(Param(None, Memory(0x23b9)), Param(None, Word(map.variant))),
                            [function],
                            [False, False]
                        )
                    code_triggers.append(test)
                    
                code_triggers = If_list(code_triggers)
                code_triggers = [code_triggers]

                function = Function("test", code_triggers, [], [Annotation_Install()])
                self.code.append(function)
                self.linker.link_function(function)
                self.linker.link_function_key(function)
                code_list.append(self._generate_function(function))
                
                code = function.key

                append_trigger(code_list, address_triggers(index), code, name)
                
        return code_list
    
    def _late_generate(self, function:Function, link_key:bool, scope:Scope=None):
        self.add_function(function, scope)
        self.linker.link_function(function)
        self.linker.link_call_in_code([function], self.code)

        if link_key:
            self.linker.link_function_key(function)

        return self._generate_function(function)

    def _generate_map(self):
        output = []

        variants = self.get_map_variants()
        
        function_nop = Function("_trigger_nop", [], [], [Annotation_Install()])
        output.append(self._late_generate(function_nop, True, self.base_scope()))

        def _prepare_trigger_enter(map:Map, function:Function) -> Function:
            objects = [object for object in map.objects]
            soundtrack = map.soundtrack()

            entrances = [e.value for e in map.enum_entrance.values]
            code_transition_in = []
            for entrance in entrances:
                entrance_index = [e.value for e in map.enum_entrance.values]
                entrance_index = entrance_index.index(entrance)

                entrance_code = entrance.enter_code

                if entrance_code:
                    code = If(
                        Equals(Param(None, Memory(0x23b7)), Param(None, Word(entrance_index))),
                        [entrance_code],
                        [False, False]
                    )

                    code_transition_in.append(code)

            code_transition_in = If_list(code_transition_in)

            function_enter = Function("_trigger_enter", 
                [soundtrack] + objects + [code_transition_in] + [Call(self, function)], [], [Annotation_Install()])
            
            return function_enter
        def _generate_trigger_enter(output:list[str], map:Map, function:Function):
            function_enter = _prepare_trigger_enter(map, function)
            output.append(self._late_generate(function_enter, False))

            return function_enter

        for map_data, maps in variants.items():
            address:int = None

            if len(maps) == 1:
                map = maps[0]

                name = f"maps[{map_data.index}, {map.name}].{map.trigger_enter.name}()"
                #code = map.trigger_enter.address
                code = _generate_trigger_enter(output, map, map.trigger_enter)
                code = code.address
                pass
            else:
                name = f"maps[{map_data.index}, {'/'.join([map.name for map in maps])}].trigger_enter()"
                code_enter = []

                for map in maps:
                    code = map.trigger_enter
                    code = _generate_trigger_enter(output, map, code)
                    test = If(
                            Equals(Param(None, Memory(0x23b9)), Param(None, Word(map.variant))),
                            [Call(self, code)],
                            [False, False]
                        )
                    code_enter.append(test)

                code_enter = If_list(code_enter)
                code_enter = [code_enter]

                function_enter = Function("test", code_enter, [], [Annotation_Install()])
                self.code.append(function_enter)
                self.linker.link_function(function_enter)
                output.append(self._generate_function(function_enter))
                
                code = function_enter.address

            address = map_data.trigger_enter
            count = 3

            code = Address(code).code([])

            address = self.correct_address(address)

            header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name='{name}'"]
            footer = []

            output += header + [code] + footer

            triggers = [map.enum_b_trigger for map in maps]
            triggers = [len(enum.values) if enum != None else 0 for enum in triggers]
            triggers = sum(triggers)
            if triggers > 0:
                output += self._generate_map_trigger(map_data, maps, map_data.trigger_b_count, (lambda map: map.triggers_b()), map_data.address_b_trigger)

            triggers = [map.enum_stepon_trigger for map in maps]
            triggers = [len(enum.values) if enum != None else 0 for enum in triggers]
            triggers = sum(triggers)
            if triggers > 0:
                output += self._generate_map_trigger(map_data, maps, map_data.trigger_step_count, (lambda map: map.triggers_stepon()), map_data.address_stepon_trigger)

        return '\n'.join(output)
        
    def correct_address(self, address:int)->int:
        if address >= 0xC00000: # TODO
            address -= 0xC00000
        elif address >= 0x800000: # TODO
            address -= 0x800000
        elif address >= 0x400000: # TODO
            address -= 0x400000
            
        if address > (4 * 1024 * 1024):
            TODO()

        return address

    def _generate_string(self, string):
        list = []

        name = '{:04X}'.format(string.text_key.index, 'x')
        address = string.text_key.address
        count = string.text_key.count([])
        code = string.address
        code -= 0xc00000
        code = Word((code & 0xffff) + ((code & 0x7f8000) >> 1))
        code._value_count = 3
        code = code.code([])

        address = self.correct_address(address)

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name='{name}'"]
        footer = []

        list += header + [code] + footer

        name = string.value
        address = string.address
        code = RawString(string.value)
        count = code.count([])
        code = code.code([])

        address = self.correct_address(address)

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={name}"]
        footer = []

        list += header + [code] + footer

        return '\n'.join(list)

    def _generate_function(self, function:Function):
        code = function.code([])
        address = function.address
        count = function.count([])
        if function.count_limit and not function.inject and count > function.count_limit:
            raise Exception(f"function '{function.name}' (count={count}) violated @count_limit({function.count_limit}) ")

        list = []

        list += self._inject(function)
        self.linker.link_goto(function)

        address = self.correct_address(address)

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name='{function.name}()'"]
        footer = []

        list += header + [code] + footer

        return '\n'.join(list)

    def _generate_function_key(self, function:Function):
        code = function.address
        if not code:
            function.install = True
            self._late_generate(function, True)
            code = function.address
            pass
        code = [Address(code)]
        address = function.key.address
        count = sum([e.count([]) for e in code])

        list = []

        address = self.correct_address(address)

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name='{function.key}->{function.name}()'"]
        footer = []

        list += header + [e.code([]) for e in code] + footer

        return '\n'.join(list)

    def _inject(self, function):
        list = []

        for inject in function.inject:
            list.append(self._inject_function(function, inject))

        return list

    def _inject_function(self, function, inject):
        if inject == None:
            return []
        
        address = inject.eval([])
        call = Call(self, function)
        count = call.count([])
        if function.terminate:
            count += 1 # TODO
        
        script = [call.code([])]
        if function.terminate:
            script += [ End().code([]) ]
        else:
            pass

        code = Function_Code(script).script

        address = self.correct_address(address)

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // address={address} count={count} name={function.name}"]
        footer = []

        return '\n'.join(header + code + footer)

    def set_identifier(self, identifier:str, value:any) -> None:
        if isinstance(identifier, Token):
            identifier = identifier.value

        if identifier in self.current_scope().identifier:
            raise Exception(f"redeclaration of identifier '${identifier}'")

        self.current_scope().identifier[identifier] = value

    def get_identifier(self, identifier:str) -> any:
        all_identifiers = self._all_identifiers()

        if not identifier in all_identifiers:
            raise Exception(f"Enum '{identifier}' does not exist!")
        
        return all_identifiers[identifier]

    def add_object(self, object:Object) -> None:
        self.current_scope().objects.append(object)
    
    def get_map_variants(self) -> dict[int, list[Map]]:
        variants:dict[int, list[Map]] = {}

        for map in self.maps:
            key = map.map_data #map.map_index

            if map.variant == None or key == None:
                raise Exception("map need to be linked first")
        
            if not key in variants:
                variants[key] = []

            variants[key].append(map)

        return variants
    
    def reference_function(self, function:Function):
        if isinstance(function, Param):
            function = function.value
        self.linker.link_function_key(function)

        return function.key