from compiler.ast_everscript import *
from itertools import dropwhile
import re
from textwrap import wrap

"""
#memory(
    // base = 0x000000..0x2fffff

    0x000000..0x007fff, // strings = 0xc00000..0xc07f70 (slow)
    0x010000..0x017fff, // strings = 0xc10000..0xc17f70 (slow)
    0x020000..0x027fff, // strings = 0xc20000..0xc27f70 (slow)
    0x030000..0x037fff, // strings = 0xc30000..0xc37f70 (slow)
    // (04..2f unused)

    0x11d000..0x11F32D, // string keys = 0x91d000..0x91F32D (index 0x0000-0x232b, 3 bytes, MSB&80=compressed)

    // ... (unused?)
    0x128000..0x12ffff, // scripts = 0x928000..0x92ffff (fast, room scripts start)
    // ... (room script index, room scripts)
    0x1b8000..0x1bffff, // scripts = 0x9b8000..0x9bffff (fast, room scripts end)
    // ... (00..2f unused?)


    // extension = 0x300000..0x3fffff

    0x300000..0x307fff, // strings extension = 0xb00000..0xb07fff
    // ... (31..3f)
    0x308000..0x30ffff // extension script = 0xb08000..0xb0ffff
    // ... (31..3f)
)
"""
class MemoryManager():
    def __init__(self):
        self.memory = {
            "script": [],
            "text": [],
            "text_key": [],
            "function_key": [],

            "memory": [],
            "flag": []
        }

    def add(self, memory):
        for m in memory:
            if isinstance(m, Word):
                self._add(m)
            elif isinstance(m, Range):
                if isinstance(m.start, StringKey):
                    for string_key in m.eval():
                        self.memory["text_key"].append(string_key)
                elif isinstance(m.start, FunctionKey):
                    for function_key in m.eval():
                        self.memory["function_key"].append(function_key)
                elif isinstance(m.start, Memory):
                    for address in m.eval():
                        self.memory["memory"].append(address)
                    pass
                else:
                    self._add(m)
            elif isinstance(m, StringKey):
                self.memory["text_key"].append(m)
            elif isinstance(m, FunctionKey):
                self.memory["function_key"].append(m)
            elif isinstance(m, Memory):
                self.memory["memory"].append(m)
            else:
                raise Exception(f"unsupported memory: {m}")

    def _split_by_bank(self, memory):
        list = []

        first_bank = memory.start & 0xff0000
        last_bank = memory.end & 0xff0000

        if first_bank == last_bank:
            return [first_bank]
        else:
            step_size = 0x10000
            for bank in range(first_bank, last_bank + step_size, step_size):
                list.append(bank)

        return list

    def _add(self, memory):
        if isinstance(memory, Range):
            for bank in self._split_by_bank(memory):
                self.memory["text"].append(Range(bank, bank + 0x7fff) + 0xc00000)
                self.memory["script"].append(Range(bank + 0x8000, bank + 0xffff) + 0x800000)
        else:
            raise Exception(f"unsupported memory: {memory}")

    def allocate_script(self, count):
        memory = self.memory["script"]
        
        for i, m in enumerate(memory):
            if m.count() > count:
                address = m.start
                self.memory["script"][i] = Range(m.start + count, m.end)
                return address
            else:
                del(memory[i])

        raise Exception("no memory defined/available")
        
    def allocate_text(self, string, text):
        count = text.count()
        text_key = self.memory["text_key"].pop(0)
        memory = self.memory["text"]
        
        for i, m in enumerate(memory):
            if m.count() > count:
                address = m.start
                self.memory["text"][i] = Range(m.start + count, m.end)

                string.address = address
                string.text_key = text_key

                return string
            else:
                del(memory[i])

        raise Exception("no memory defined/available")
    
    def allocate_function_key(self, function):
        function_key = self.memory["function_key"].pop(0)
        
        function.key = function_key
        
    def allocate_memory(self):
        memory = self.memory["memory"].pop(0)
        return memory
    def allocate_flag(self):
        if not self.memory["flag"]:
            memory = self.memory["memory"].pop(0)

            for offset in range(0, 8):
                self.memory["flag"].append(Memory(memory.address, 1 << offset))
            for offset in range(0, 8):
                self.memory["flag"].append(Memory(memory.address + 1, 1 << offset))
            
        flag = self.memory["flag"].pop(0)

        return flag


class MapDataHandler():
    class MapData():
        address_trigger_enter_base = 0x92801b
        address_trigger_enter_size = 5

        address_trigger_offset = 13

        address_trigger_stepon_enter_size = 6
        address_trigger_b_enter_size = 6

        def __init__(self, index, data:int, trigger_step_count:int, trigger_b_count:int, name:str):
            self.index = index
            self.data = data
            self.name = name

            self.trigger_step_count = trigger_step_count
            self.trigger_b_count = trigger_b_count
            self.trigger_enter = self.address_trigger_enter_base + (index * self.address_trigger_enter_size)

        def address_stepon_trigger(self, index:int) -> int:
            address = self.data
            address += self.address_trigger_offset
            address += 2
            address += index * self.address_trigger_stepon_enter_size
            address += 4

            return address
        
        def address_b_trigger(self, index:int) -> int:
            address = self.data
            address += self.address_trigger_offset
            address += 2
            address += self.trigger_step_count * self.address_trigger_stepon_enter_size
            address += 2
            address += index * self.address_trigger_b_enter_size
            address += 4

            return address
        
    map_data:MapData = None

    def __init__(self):
        maps = [
            self.MapData(0x00, 0xabf4f1, 0x08, 0x01, "Omnitopia - Alarm room"),
            self.MapData(0x01, 0xa9e517, 0x04, 0x00, "Prehistoria - Exterior of Blimp's Hut"),
            self.MapData(0x02, 0xacc12d, 0x00, 0x00, "Intro - Mansion Exterior 1965"),
            self.MapData(0x03, 0xaaeaba, 0x00, 0x00, "Intro - Mansion Exterior 1995"),
            self.MapData(0x04, 0xacd00a, 0x02, 0x00, "Antiqua - Crustacia fire pit"),
            self.MapData(0x05, 0xa4d3b4, 0x14, 0x14, "Antiqua - Between 'mids and halls"),
            # …
            self.MapData(0x07, 0xa793e9, 0x0a, 0x0d, "Antiqua - West of Crustacia"),
            # …
            self.MapData(0x15, 0xa0ff33, 0x00, 0x00, "Brian's Test Ground"),
            # …
            self.MapData(0x33, 0xadb50c, 0x02, 0x01, "Strong Heart's Exterior"),
            self.MapData(0x34, 0xadbd79, 0x02, 0x00, "Prehistoria - Strong Heart's Hut"),
            # …
            self.MapData(0x38, 0x9e8000, 0x02, 0x1f, "Prehistoria - South jungle / Start"),
            # …
            self.MapData(0x4f, 0xa99f92, 0x19, 0x10, "Antiqua - East of Crustacia"),
            # …
            self.MapData(0x59, 0xa08000, 0x41, 0x1c, "Prehistoria - Quick sand desert"),
            # …
            self.MapData(0x5b, 0xa78000, 0x05, 0x0b, "Prehistoria - East jungle"),
            self.MapData(0x5c, 0xa8f590, 0x03, 0x04, "Prehistoria - Raptors"),
            # …
            self.MapData(0x6b, 0xa99047, 0x07, 0x00, "Antiqua - Waterfall"),
        ]

        maps = dict([(map.index, map) for map in maps])

        self.maps:dict[self.MapData] = maps

_MapDataHandler = MapDataHandler()

class Linker():
    def __init__(self, code=[]):
        self.code = code
        self.memory_manager = MemoryManager()

    def get_memory_allocation(self):
        text_key = '\n'.join([f"   - [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count(), 'x')}] {m}" for m in self.memory_manager.memory["text_key"]])
        text = '\n'.join([f"   - [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["text"]])
        
        script = '\n'.join([f"   - [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["script"]])

        memory = '\n'.join([f"   -  [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count(), 'x')}] {m}" for m in self.memory_manager.memory["memory"]])
        flag = '\n'.join([f"   - [{'{:04X}'.format(f.address, 'x')}, {'{:04X}'.format(f.count(), 'x')}] {f}" for f in self.memory_manager.memory["flag"]])

        return f"""
unallocated ROM:
  text_key:
{text_key}

  text:
{text}

  script:
{script}

unallocated RAM:
  memory:
{memory}

  flags:
{flag}
        """.strip()

    def link_memory(self):
        return self.memory_manager.allocate_memory()
        
    def link_flag(self):
        return self.memory_manager.allocate_flag()

    def link_string(self, string, text):
        self.memory_manager.allocate_text(string, text)

    def add_memory(self, memory):
        self.memory_manager.add(memory)

    def link_function(self, function):
        if function.address == None:
            count = sum([e.count() for e in function.script])
            address = self.memory_manager.allocate_script(count)

            function.address = address
    
    def link_function_key(self, function:Function):
        if function.key == None:
            self.memory_manager.allocate_function_key(function)


    def link_map_variants(self, maps:list[Map]):
        variants = {}

        for map in maps:
            map.map_data = _MapDataHandler.maps[map.map_index]

            if map.variant == None:
                variant:int = None
                if not map.map_index in variants:
                    variants[map.map_index] = 0
                variant = variants[map.map_index]
                variants[map.map_index] = variants[map.map_index] + 1

                map.variant = variant
                pass

            if map.trigger_enter != None:
                pass # TODO
            

    def link_map_transitions(self, maps:list[Map], map_transitions:list[MapTransition]):
        for map_transition in map_transitions:
            self._link_map_transition(maps, map_transition)
    def _link_map_transition(self, maps:list[Map], map_transition:MapTransition):
        map = next(map for map in maps if map.name == map_transition.map_name)
        entrance:MapEntrance = next(entrance for entrance in map.enum_entrance.values if entrance.name == map_transition.entrance_name).value
        
        map_transition.link(map, entrance)

    def link_call_in_code(self, code:list, all_code=[]):
        for function in code:
            for expression in function.script:
                if isinstance(expression, Call):
                    self.link_call(expression, all_code)
                    if expression.function != None:
                        self.link_call_in_code([expression.function], all_code)

    def link_call(self, call:Call, all_code=[]):
        if call.function != None:
            call.address = call.function.address


        if call.function and call.function.install and call.address == None:
            #TODO: workaround because of diverging id()s
            for c in all_code:
                if call.function != None and call.function.name == c.name:
                    call.address = c.address
                    break

        if call.function and call.function.install and call.address == None:
            raise Exception(f"{call} could not be linked")

    def link_goto(self, function):
        code = function.script

        for expression in code:
            if hasattr(expression, 'label'):
                distance = self._calculate_distance(function, expression)
                if distance:
                    expression.distance = distance
                    print(f"label={expression.label.value}, distance={distance}")

    def _calculate_distance(self, function, start):
        code = list(dropwhile(lambda x: x != start, function.script))
        del code[0]

        distance = 0
        for expression in code:
            if hasattr(expression, 'label_destination') and start.label.value == expression.label_destination.value:
                return distance
            
            distance += expression.count()
        
        return None
    