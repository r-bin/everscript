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
                elif isinstance(m.start, Memory):
                    for address in m.eval():
                        self.memory["memory"].append(address)
                    pass
                else:
                    self._add(m)
            elif isinstance(m, StringKey):
                self.memory["text_key"].append(m)
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

class Linker():
    def __init__(self, code=[]):
        self.code = code
        self.memory_manager = MemoryManager()

    def get_memory_allocation(self):
        text_key = '\n'.join([f"   - [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count(), 'x')}] {m}" for m in self.memory_manager.memory["text_key"]])
        text = '\n'.join([f"   - [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["text"]])
        
        script = '\n'.join([f"   - [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["script"]])

        memory = '\n'.join([f"   -  [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["memory"]])
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

    def link(self):
        self.link_function(self.code)

        for function in self.code:
            self.link_goto(function)

    def link_function(self, code):
        for function in code:
            if function.address == None:
                count = sum([e.count() for e in function.script])
                address = self.memory_manager.allocate_script(count)

                function.address = address

    def link_call(self, code):
        for function in code:
            for expression in function.script:
                if isinstance(expression, Call):
                    self._link_call(code, expression)

    def _link_call(self, code, call):
        for function in code:
            if call.function != None and function.name == call.function.name:
                call.address = function.address

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
    