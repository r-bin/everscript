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
            self.temp_memory = [m for m in self._generator.linker.memory_manager.memory["memory"]["temp"]]
            self.temp_memory.sort(key=lambda x: x.address)

        if not self.temp_flag:
            self.temp_flag = []

        if not self.temp_vars:
            self.temp_vars = []

            if self.type == self.Type.NATIVE_FUNCTION:
                for index in range(00, 30, 2): #TODO: arg33 exists
                    self.temp_vars.append(Arg(index))
                    
                # self.temp_vars = list(reversed(self.temp_vars))

    def get_memory(self, size, type) -> Memory:
        self._update_memory()

        memory_list = self.temp_memory
        size = size.value

        if size == 0:
            if not self.temp_flag:
                memory = memory_list.pop(0)

                for offset in range(0, 8):
                    self.temp_flag.append(Memory(memory.address, 1 << offset))
                
            flag = self.temp_flag.pop(0)

            return flag
        elif size == 1:
            m = memory_list.pop(0)

            return m
        elif size == 2:
            m2 = None
            for i, m in enumerate(memory_list, start=0):
                if m2 == None:
                    m2 = m
                    continue
                else:
                    if m2.address == m.address - 1:
                        del memory_list[i + 1]
                        del memory_list[i]

                        m.force_value_count(2)
                        return m
                    else:
                        m2 = m

        raise Exception("invalid memory allocation")
    
    def allocate_memory(self) -> Memory:
        self._update_memory()

        memory = self.temp_memory
        memory = self.temp_memory.pop(0)

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
        self.dependencies:list[Function] = []
        self.map_code:list[Function] = []
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
        function_keys = '\n'.join([f"   - [{m.key}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.linker.linked_methods])
        memory = '\n'.join([f"   - [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.memory])
        flag = '\n'.join([f"   - [{'{:04X}'.format(f.address, 'x')}, {'{:04X}'.format(f.count([]), 'x')}] {f}" for f in self.flags])

        return f"""
{self.linker.get_memory_allocation()}

allocated ROM:
  strings:
{strings}

  function keys:
{function_keys}

  scripts:
    TODO

allocated RAM:
  memory:
{memory}

  flags:
{flag}
        """.strip()

    def get_memory(self, size, type) -> Memory:
        memory = self.linker.link_memory(size, type)

        self.memory.append(memory)

        return memory
    def get_flag(self, type:str) -> Memory:
        memory = self.linker.link_flag(type)

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

    def add_function(self, function:Function, scope:Scope=None, reference:bool=False):
        if not scope:
            scope = self.current_scope()

        scope.functions[function.name] = function
        
        self.code.append(function)

        if reference:
            self.reference_function(function)
    def add_map_function(self, function:Function, scope:Scope=None, reference:bool=False):
        if not scope:
            scope = self.current_scope()

        self.map_code.append(function)

        if reference:
            self.reference_function(function)

    def add_dependency(self, function:Function):
        if isinstance(function, Param):
            function = function.value

        if not function in self.dependencies:
            function.weak = False
            self.dependencies += [function]

            for code in self.flatten_script(function.script):
                if isinstance(code, Call) and not code.address:
                    f = code.function
                    if isinstance(f, Identifier):
                        f = self.get_function(f.name)

                    if f and f.install:
                        self.add_dependency(f)
    
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

    def flatten_script(self, list):
        l = []

        for code in list:
            if not isinstance(code, If_list):
                l.append(code)
            else:
                for c in code.if_list:
                    l += self.flatten_script(c.script)

        return l

    def generate(self):
        output = []

        if self.wipe_strings:
            output.append(self._wipe_strings())

        # link maps
        self.linker.link_map_variants(self.maps)
        self.linker.link_map_transitions(self.maps, self.map_transitions)
        
        output.append("\n// map variants")
        variants = self.get_map_variants()
        if variants:
            self._generate_map()

        # link functions
        installed_functions = [function for function in self.code if function.install and not function.weak]
        for function in installed_functions:
            self.linker.link_function(function)

        for function in self.map_code:
            self.linker.link_function(function)

        self.dependencies = list(set(self.dependencies) - set(installed_functions))
        for function in self.dependencies:
            self.linker.link_dependency(function)

        # generate functions
        output.append("\n// functions")
        for function in installed_functions:
            output.append(self._generate_function(function))
        output.append("\n// map functions")
        for function in self.map_code:
            output.append(self._generate_function(function))
        output.append("\n// dependencies")
        for function in self.dependencies:
            output.append(self._generate_function(function))

        output.append("\n// function indicies")
        function_keys = [function for function in self.code if isinstance(function.key, FunctionKey)]
        function_keys.sort(key=lambda k: k.key.index)
        for function in function_keys:
            output.append(self._generate_function_key(function))

        output.append("\n// map indicies")
        map_function_keys = [function for function in self.map_code if isinstance(function.map_key, MapKey)]
        for function in map_function_keys:
            output.append(self._generate_function_map_key(function))

        output.append("\n// dependency indicies")
        dependencies_keys = [function for function in self.dependencies if not function in function_keys and function.key != None]
        dependencies_keys.sort(key=lambda k: k.key.index)
        for function in dependencies_keys:
            output.append(self._generate_function_key(function))

        # string()
        output.append("\n// strings")
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

        function_nop = self.get_function("nop")

        def _generate_trigger(key_address, function:Function, name):
            function.map_key = MapKey(key_address, True)
            self.linker.link_function_key(function)
            function.name = name
            function.install = True

            self.add_map_function(function)

        if len(maps) == 1:
            map = maps[0]

            triggers = enum_triggers(map)
            
            for index in range(count):
                name = "anonymous"
                function = triggers[index] or function_nop
                if isinstance(function, Enum_Entry):
                    function = function.value
                if isinstance(function, Call):
                    function = function.function

                name = f"maps[{map_data.index}, {map.name}].trigger[{index}, {name}]"

                key_address = address_triggers(index)
                _generate_trigger(key_address, function, name)
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
                            Equals(Param(None, Memory(0x244b, size=1)), Param(None, Word(map.variant))),
                            [function],
                            [False, False]
                        )
                    code_triggers.append(test)
                    
                code_triggers = If_list(code_triggers)
                code_triggers = [code_triggers]

                function = Function("test", code_triggers, [], [Annotation_Install()])
                function.name = name

                key_address = address_triggers(index)
                _generate_trigger(key_address, function, name)
    
    def _generate_map(self):
        variants = self.get_map_variants()

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
                        Equals(Param(None, Memory(0x244c, size=1)), Param(None, Word(entrance_index))),
                        [entrance_code],
                        [False, False]
                    )

                    code_transition_in.append(code)

            code_transition_in = If_list(code_transition_in)

            function_enter = Function("_trigger_enter", 
                [Asign(Memory(0x244a, size=1), Word(map.map_index)), Asign(Memory(0x244b, size=1), Word(map.variant))] + [soundtrack] + objects + [code_transition_in] + [Call(self, function)], [], [Annotation_Install()])
            
            return function_enter
        def _generate_trigger_enter(map:Map, function:Function, name):
            function.map_key = MapKey(map.map_data.trigger_enter)
            self.linker.link_function_key(function)

            self.add_map_function(function)

        for map_data, maps in variants.items():
            address:int = None

            if len(maps) == 1:
                map = maps[0]

                _generate_trigger_enter(map, _prepare_trigger_enter(map, map.trigger_enter), f"maps[{map_data.index}, {map.name}].{map.trigger_enter.name}()")
            else:
                name = f"maps[{map_data.index}, {'/'.join([map.name for map in maps])}].trigger_enter()"
                code_enter = []

                for map in maps:
                    function_enter = _prepare_trigger_enter(map, map.trigger_enter)
                    test = If(
                            Equals(Param(None, Memory(0x244b, size=1)), Param(None, Word(map.variant))),
                            [Call(self, function_enter)],
                            [False, False]
                        )
                    code_enter.append(test)

                code_enter = If_list(code_enter)
                code_enter = [code_enter]

                function_enter = Function("test", code_enter, [], [Annotation_Install()])
                _generate_trigger_enter(map, function_enter, f"test")

            triggers = [map.enum_b_trigger for map in maps]
            triggers = [len(enum.values) if enum != None else 0 for enum in triggers]
            triggers = sum(triggers)
            if triggers > 0:
                self._generate_map_trigger(map_data, maps, map_data.trigger_b_count, (lambda map: map.triggers_b()), map_data.address_b_trigger)

            triggers = [map.enum_stepon_trigger for map in maps]
            triggers = [len(enum.values) if enum != None else 0 for enum in triggers]
            triggers = sum(triggers)
            if triggers > 0:
                self._generate_map_trigger(map_data, maps, map_data.trigger_step_count, (lambda map: map.triggers_stepon()), map_data.address_stepon_trigger)
        
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

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // count='{count}' function='{function}'"]
        footer = []

        list += header + [code] + footer

        return '\n'.join(list)

    def _generate_function_key(self, function:Function):
        code = function.address
        code = [Address(code)]

        address = function.key.address
        count = sum([e.count([]) for e in code])

        list = []

        address = self.correct_address(address)

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // count={count} name='{function.key}->{function}'"]
        footer = []

        list += header + [e.code([]) for e in code] + footer

        return '\n'.join(list)

    def _generate_function_map_key(self, function:Function):
        list = []
        
        list += [self._generate_function_key(function)]

        indirect = function.map_key.indirect_call

        code = None
        if indirect:
            code = [Word(function.key.index)]
        else:
            code = function.address
            #code = self.correct_address(code)
            code = [Address(code)]

        address = function.map_key.address
        count = sum([e.count([]) for e in code])


        address = self.correct_address(address)

        if indirect:
            comment = f"function='{function.map_key}->{function.key}->{function}'"
        else:
            comment = f"function='{function.map_key}->{function}'"

        header = [f"{'{:06X}'.format(address, 'x')} {'{:04X}'.format(count, 'x')} // count={count} {comment}'"]
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
        if inject.terminate:
            count += 1 # TODO
        
        script = [call.code([])]
        if inject.terminate:
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
    
    def reference_function(self, function:Function, link_key=True):
        if not function.key:
            function.weak = False

            self.add_dependency(function)
            self.linker.link_function_key(function)