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

            "memory": {"sram":[], "ram":[], "temp":[]},
            "flag": {"sram":[], "ram":[], "temp":[]},
        }

    def add(self, memory):
        for m in memory:
            if isinstance(m, Word):
                self._add(m)
            elif isinstance(m, Range):
                match m.start:
                    case StringKey() | FunctionKey() | Memory():
                        self.add(m.eval([]))
                    #case Memory():
                    #    self.memory["memory"][m.start.type].append(m)
                    case _:
                        self._add(m)
            elif isinstance(m, StringKey):
                self.memory["text_key"].append(m)
            elif isinstance(m, FunctionKey):
                self.memory["function_key"].append(m)
            elif isinstance(m, Memory):
                match [m.sram, m.type]:
                    case [True, _]:
                        memory_list = self.memory["memory"]["sram"]
                    case [_, "22"]:
                        memory_list = self.memory["memory"]["ram"]
                    case [_, "28"]:
                        memory_list = self.memory["memory"]["temp"]
                    case [_, _]:
                        TODO()
                
                memory_list.append(m)
                # memory_list.sort(key=lambda x: x.address)
                memory_list.sort(key=lambda x: x.address, reverse=m.type=="28")
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

        raise Exception("no memory defined/available (script)")
        
    def allocate_text(self, string:String):
        count = string.count([])
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

        raise Exception("no memory defined/available (text)")
    
    def allocate_function_key(self, function):
        function_key = self.memory["function_key"].pop(0)
        
        function.key = function_key
        
    def allocate_memory(self, size, type):
        match type.value:
            case 0:
                memory_type = "sram"
            case 1:
                memory_type = "ram"
            case 2:
                memory_type = "temp"
            case _:
                TODO()

        memory_list = self.memory["memory"][memory_type]
        size = size.value

        if size == 0:
            if not self.memory["flag"][memory_type]:
                memory = self.memory["memory"][memory_type].pop(0)

                for offset in range(0, 8):
                    self.memory["flag"][memory_type].append(Memory(memory.address, 1 << offset))
                
            flag = self.memory["flag"][memory_type].pop(0)

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
                    if (m2.address == m.address - 1) or (m2.address == m.address + 1): # TODO
                        del memory_list[i + 1]
                        del memory_list[i]

                        m.force_value_count(2)
                        return m
                    else:
                        m2 = m

        raise Exception("invalid memory allocation")


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
            self.MapData(0x06, 0x9c8000, 0x1b, 0x14, "Antiqua - Outside of 'mids"),
            self.MapData(0x07, 0xa793e9, 0x0a, 0x0d, "Antiqua - West of Crustacia"),
            self.MapData(0x08, 0xa5b42e, 0x05, 0x05, "Antiqua - Nobilia, Square"),
            self.MapData(0x09, 0xa9bde6, 0x03, 0x00, "Antiqua - Nobilia, Square during Aegis fight"),
            self.MapData(0x0a, 0x9faaeb, 0x0b, 0x3a, "Antiqua - Nobilia, Market"),
            self.MapData(0x0b, 0xa6964a, 0x0a, 0x0c, "Antiqua - Nobilia, Palace grounds"),
            self.MapData(0x0c, 0xad9f83, 0x04, 0x02, "Antiqua - Nobilia, Inn"),
            self.MapData(0x0d, 0xa9d82a, 0x08, 0x00, "Gothica - Ebon Keep Hall (Stairs, behind Verm)"),
            self.MapData(0x0e, 0xacc8b8, 0x02, 0x01, "Gothica - Ebon Keep Dining Room"),
            self.MapData(0x0f, 0xaac915, 0x02, 0x02, "Gothica - Ebon Keep West Room (Naris)"),
            self.MapData(0x10, 0xadc553, 0x02, 0x00, "Gothica - Ebon Keep Stained Glass Hallway"),
            self.MapData(0x11, 0xabbd82, 0x02, 0x00, "Gothica - Ebon Keep Queen's Room"),
            self.MapData(0x12, 0xa58000, 0x02, 0x0d, "Gothica - Ebon Keep sewers"),
            self.MapData(0x13, 0xacb18d, 0x04, 0x01, "Gothica - Between Ebon Keep sewers, Dark Forest and Swamp"),
            self.MapData(0x14, 0xabd077, 0x02, 0x03, "Gothica - Ebon Keep Tinker's Room"),
            self.MapData(0x15, 0xa0ff33, 0x00, 0x00, "Brian's Test Ground"),
            self.MapData(0x16, 0xa38000, 0x2a, 0x18, "Prehistoria - BBM"),
            self.MapData(0x17, 0xac9955, 0x08, 0x0c, "Prehistoria - Bug room 2"),
            self.MapData(0x18, 0xab8ad2, 0x03, 0x02, "Prehistoria - Thraxx' room"),
            self.MapData(0x19, 0xa48000, 0x05, 0x13, "Gothica - Chessboard"),
            self.MapData(0x1a, 0xa8e53c, 0x04, 0x01, "Gothica - Below chessboard"),
            self.MapData(0x1b, 0xa68000, 0x13, 0x00, "Antiqua - Desert of Doom"),
            self.MapData(0x1c, 0xa7e153, 0x06, 0x14, "Antiqua - Nobilia, North of Market"),
            self.MapData(0x1d, 0xa7f396, 0x00, 0x00, "Antiqua - Nobilia, Arena (Vigor Fight)"),
            self.MapData(0x1e, 0xacde7c, 0x01, 0x09, "Antiqua - Nobilia, Arena Holding Room"),
            self.MapData(0x1f, 0xa8d4ca, 0x02, 0x00, "Gothica - Doubles room in forest"),
            self.MapData(0x20, 0xace592, 0x02, 0x00, "Gothica - Timberdrake room in forest"),
            self.MapData(0x21, 0xacf37c, 0x02, 0x00, "Gothica - Dark forest entrance (save point)"),
            self.MapData(0x22, 0xa1c650, 0x11, 0x09, "Gothica - Dark Forest"),
            self.MapData(0x23, 0xacb96b, 0x06, 0x03, "Antiqua - Halls SW"),
            self.MapData(0x24, 0xa3bc84, 0x1d, 0x07, "Antiqua - Halls NW"),
            self.MapData(0x25, 0xa4b92d, 0x0d, 0x14, "Prehistoria - Fire Eyes' Village"),
            self.MapData(0x26, 0xadcee5, 0x01, 0x03, "Prehistoria - West area with Defend"),
            self.MapData(0x27, 0xa6d67a, 0x03, 0x1e, "Prehistoria - Mammoth Graveyard"),
            self.MapData(0x28, 0xa1a38f, 0x20, 0x02, "Antiqua - Halls Collapsing Bridge"),
            self.MapData(0x29, 0xa7bb53, 0x20, 0x02, "Antiqua - Halls main room"),
            self.MapData(0x2a, 0xaa98b5, 0x01, 0x00, "Antiqua - Halls Boss Room"),
            self.MapData(0x2b, 0xa7ce91, 0x02, 0x11, "Antiqua - Outside of halls"),
            self.MapData(0x2c, 0xac911f, 0x02, 0x00, "Antiqua - Halls SE"),
            self.MapData(0x2d, 0xa28000, 0x12, 0x05, "Antiqua - Halls NE"),
            self.MapData(0x2e, 0xadc8ba, 0x01, 0x02, "Antiqua - Blimp's Cave"),
            self.MapData(0x2f, 0xa0cd23, 0x06, 0x14, "Antiqua - Horace's camp"),
            self.MapData(0x30, 0xaaa4f5, 0x08, 0x07, "Antiqua - Crustacia inside pirate ship"),
            self.MapData(0x31, 0xacd757, 0x00, 0x00, "Intro - Podunk 1965"),
            self.MapData(0x32, 0xada585, 0x00, 0x00, "Intro - Podunk 1995"),
            self.MapData(0x33, 0xadb50c, 0x02, 0x01, "Strong Heart's Exterior"),
            self.MapData(0x34, 0xadbd79, 0x01, 0x03, "Prehistoria - Strong Heart's Hut"),
            self.MapData(0x35, 0xaad4ab, 0x05, 0x0a, "Act1 Quicksand, Bugmuck and Volcano caves + Act2 West Alchemy Cave"),
            self.MapData(0x36, 0xa3f774, 0x02, 0x04, "Prehistoria - Both fire pits (one room)"),
            self.MapData(0x37, 0x9dbcf3, 0x0c, 0x16, "Gothica - Gomi's Tower"),
            self.MapData(0x38, 0x9e8000, 0x02, 0x1f, "Prehistoria - South jungle / Start"),
            self.MapData(0x39, 0xaca984, 0x02, 0x00, "Gothica - Ebon Keep Fire pit"),
            self.MapData(0x3a, 0xadab68, 0x02, 0x00, "Antiqua - Nobilia, Fire pit"),
            self.MapData(0x3b, 0xa2c0a8, 0x04, 0x22, "Prehistoria - Volcano Room 2"),
            self.MapData(0x3c, 0xa2a161, 0x15, 0x19, "Prehistoria - Volcano Room 1"),
            self.MapData(0x3d, 0xa39eca, 0x27, 0x00, "Prehistoria - Pipe maze"),
            self.MapData(0x3e, 0xa98000, 0x0c, 0x0e, "Prehistoria - Side rooms of pipe maze "),
            self.MapData(0x3f, 0xaabd2c, 0x01, 0x00, "Prehistoria - Volcano Boss Room"),
            self.MapData(0x40, 0xab8000, 0x02, 0x00, "Gothica - Swamp south of Gomi's Tower"),
            self.MapData(0x41, 0xa5e6be, 0x04, 0x17, "Prehistoria - North jungle"),
            self.MapData(0x42, 0xa9f1d1, 0x1c, 0x02, "Omnitopia - Reactor room and Reactor control"),
            self.MapData(0x43, 0xaba9f5, 0x01, 0x06, "Omnitopia - Control room"),
            self.MapData(0x44, 0xaaf592, 0x02, 0x01, "Omnitopia - Greenhouse (dark or both?)"),
            self.MapData(0x45, 0xabebf5, 0x02, 0x00, "Omnitopia - Secret boss room"),
            self.MapData(0x46, 0xa6eb36, 0x05, 0x03, "Omnitopia - Professor's lab and ship area, (also?) Intro"),
            self.MapData(0x47, 0xaa8c6d, 0x01, 0x07, "Omnitopia - Storage room"),
            self.MapData(0x48, 0x9fd4e3, 0x38, 0x35, "Omnitopia - Metroplex tunnels (rimsalas, spheres)"),
            self.MapData(0x49, 0xa4ee2d, 0x0d, 0x00, "Omnitopia - Junkyard (Landing spot)"),
            self.MapData(0x4a, 0xa3da2c, 0x02, 0x08, "Omnitopia - Final Boss Room"),
            self.MapData(0x4b, 0xa0a80a, 0x32, 0x20, "Antiqua - Oglin cave"),
            self.MapData(0x4c, 0xab958d, 0x02, 0x0a, "Antiqua - Nobilia, Fountain and snake statues"),
            self.MapData(0x4d, 0xad8669, 0x00, 0x00, "Antiqua - Nobilia, Inside palace (Horace cutscene)"),
            self.MapData(0x4e, 0xaab123, 0x02, 0x00, "Gothica - Ivor Tower, west alley (market)"),
            self.MapData(0x4f, 0xa99f92, 0x19, 0x10, "Antiqua - East of Crustacia"),
            self.MapData(0x50, 0xa5fd60, 0x00, 0x00, "Prehistoria - Sky above Volcano"),
            self.MapData(0x51, 0xa9aed7, 0x09, 0x19, "Prehistoria - Village Huts and Blimp's Hut"),
            self.MapData(0x52, 0xacfa2d, 0x01, 0x00, "Prehistoria - Top of Volcano"),
            self.MapData(0x53, 0xabe2f9, 0x00, 0x00, "Antiqua - Act2 Start Cutscene"),
            self.MapData(0x54, 0xaa8000, 0x07, 0x03, "Omnitopia - Shops"),
            self.MapData(0x55, 0x9ed770, 0x2f, 0x18, "Antiqua - 'mids bottom level (Dog start)"),
            self.MapData(0x56, 0xa6c154, 0x06, 0x18, "Antiqua - 'mids top level (Boy start)"),
            self.MapData(0x57, 0xa7a7a2, 0x15, 0x0b, "Antiqua - 'mids basement level (Tiny)"),
            self.MapData(0x58, 0xad8cbb, 0x05, 0x00, "Antiqua - 'mids boss room (Rimsala)"),
            self.MapData(0x59, 0xa08000, 0x41, 0x1c, "Prehistoria - Quick sand desert"),
            self.MapData(0x5a, 0xad9309, 0x01, 0x02, "Prehistoria - Acid rain guy"),
            self.MapData(0x5b, 0xa78000, 0x05, 0x11, "Prehistoria - East jungle"),
            self.MapData(0x5c, 0xa8f590, 0x03, 0x04, "Prehistoria - Raptors"),
            self.MapData(0x5d, 0xabd9ce, 0x07, 0x00, "Gothica - Ebon Keep Courtyard (South of Verm)"),
            self.MapData(0x5e, 0xacec95, 0x0a, 0x00, "Gothica - Ebon Keep Front Room (Verm)"),
            self.MapData(0x5f, 0xadb961, 0x04, 0x00, "Gothica - Ebon Keep Verm side rooms"),
            self.MapData(0x60, 0xadcc0b, 0x01, 0x03, "Gothica - Ebon Keep Storage Room"),
            self.MapData(0x61, 0xa8b3a9, 0x00, 0x00, "Opening - Scrolling over Machine"),
            self.MapData(0x62, 0xa0f130, 0x09, 0x00, "Gothica - Ivor Tower, west square (trailers)"),
            self.MapData(0x63, 0xad8000, 0x02, 0x00, "Gothica - Ivor Tower, inside trailers"),
            self.MapData(0x64, 0xadb0aa, 0x02, 0x00, "Antiqua - Cave entrance under 'mids"),
            self.MapData(0x65, 0x9d8000, 0x1d, 0x22, "Prehistoria - Swamp (main area)"),
            self.MapData(0x66, 0xa8c44e, 0x07, 0x13, "Prehistoria - West of swamp"),
            self.MapData(0x67, 0x9eabdf, 0x0d, 0x2a, "Prehistoria - Bugmuck exterior"),
            self.MapData(0x68, 0xa6abe2, 0x0d, 0x00, "Antiqua - Crustacia exterior"),
            self.MapData(0x69, 0xa18000, 0x1f, 0x21, "Prehistoria - Volcano path"),
            self.MapData(0x6a, 0xac88e1, 0x00, 0x00, "Antiqua - Act2 Start Cutscene - waterfall"),
            self.MapData(0x6b, 0xa99047, 0x07, 0x00, "Antiqua - Waterfall"),
            self.MapData(0x6c, 0xabc707, 0x01, 0x01, "Gothica - SE of Ivor Tower (Well)"),
            self.MapData(0x6d, 0xabb3bc, 0x00, 0x00, "Antique - Aquagoth Room"),
            self.MapData(0x6e, 0xa8a2f4, 0x09, 0x00, "Gothica - Ivor Tower Hall"),
            self.MapData(0x6f, 0xaadfdf, 0x02, 0x02, "Gothica - Ivor Tower Dining Room"),
            self.MapData(0x70, 0xa9cb12, 0x0a, 0x00, "Gothica - Ivor Tower Exterior Bridges and Balconies"),
            self.MapData(0x71, 0x9f8000, 0x39, 0x20, "Gothica - Ivor Tower East Room + Kitchen"),
            self.MapData(0x72, 0xa88000, 0x13, 0x12, "Gothica - Ivor Tower East Upper Floor"),
            self.MapData(0x73, 0x9cf0c2, 0x1c, 0x00, "Gothica - Ivor Tower Dog Maze Underground"),
            self.MapData(0x74, 0xa49d43, 0x20, 0x01, "Gothica - Ebon Keep and Ivory Tower dungeon + pipe room"),
            self.MapData(0x75, 0xad9947, 0x02, 0x00, "Gothica - Ivor Tower Stariwell to dungeon"),
            self.MapData(0x76, 0x9dea4e, 0x02, 0x14, "Gothica - South of Ivor Tower (Gate)"),
            self.MapData(0x77, 0xaba009, 0x03, 0x00, "Gothica - Ivor Tower Puppet Show / Mungola"),
            self.MapData(0x78, 0xaca178, 0x04, 0x00, "Gothica - Ivor Tower Queen's Room"),
            self.MapData(0x79, 0xa5cdd9, 0x04, 0x08, "Gothica - Ivor Tower Sewers"),
            self.MapData(0x7a, 0xadc17d, 0x02, 0x00, "Gothica - Ivor Tower Sewers Exterior (landing spot)"),
            self.MapData(0x7b, 0xa59a21, 0x08, 0x07, "Gothica - Ebon Keep and Ivor Tower Exterior Bottom Half"),
            self.MapData(0x7c, 0xa2dfcb, 0x0b, 0x00, "Gothica - Ebon Keep and Ivor Tower Exterior Top Half"),
            self.MapData(0x7d, 0xa1e7e2, 0x0c, 0x15, "Gothica - Ebon Keep and Ivor Tower Interior"),
            self.MapData(0x7e, 0xa89236, 0x01, 0x11, "Omnitopia - Jail"),
        ]

        maps = dict([(map.index, map) for map in maps])

        self.maps:dict[self.MapData] = maps

_MapDataHandler = MapDataHandler()

class Linker():
    def __init__(self, code=[]):
        self.code = code
        self.memory_manager = MemoryManager()
        self.linked_methods = []

    def get_memory_allocation(self):
        text_key = '\n'.join([f"   - [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.memory_manager.memory["text_key"]])
        text = '\n'.join([f"   - [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["text"]])
        
        script = '\n'.join([f"   - [{'{:04X}'.format(m.start, 'x')}, {'{:04X}'.format(m.end - m.start, 'x')}] {m}" for m in self.memory_manager.memory["script"]])

        memory_sram = '\n'.join([f"   -  [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.memory_manager.memory["memory"]["sram"]])
        memory_ram = '\n'.join([f"   -  [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.memory_manager.memory["memory"]["ram"]])
        memory_temp = '\n'.join([f"   -  [{'{:04X}'.format(m.address, 'x')}, {'{:04X}'.format(m.count([]), 'x')}] {m}" for m in self.memory_manager.memory["memory"]["temp"]])
        flag_sram = '\n'.join([f"   - [{'{:04X}'.format(f.address, 'x')}, {'{:04X}'.format(f.count([]), 'x')}] {f}" for f in self.memory_manager.memory["flag"]["sram"]])
        flag_ram = '\n'.join([f"   - [{'{:04X}'.format(f.address, 'x')}, {'{:04X}'.format(f.count([]), 'x')}] {f}" for f in self.memory_manager.memory["flag"]["ram"]])

        return f"""
unallocated ROM:
  text_key:
{text_key}

  text:
{text}

  script:
{script}

unallocated RAM:
  SRAM:
{memory_sram}

  RAM:
{memory_ram}

  TEMP:
{memory_temp}

  flags SRAM:
{flag_sram}

  flags RAM:
{flag_ram}
        """.strip()

    def link_memory(self, size, type) -> Memory:
        return self.memory_manager.allocate_memory(size, type)
        
    def link_flag(self, type:str) -> Memory:
        return self.memory_manager.allocate_flag(type)

    def link_string(self, string:String):
        self.memory_manager.allocate_text(string)

    def add_memory(self, memory):
        self.memory_manager.add(memory)

    def link_function(self, function:Function):
        if not function.install:
            raise  Exception(f"function '{function.name}' cannot be linked")
    
        function.weak = False
        
        if not function.address:
            count = function.count([])
            address = self.memory_manager.allocate_script(count)

            function.address = address
    def link_dependency(self, function:Function):
        if not function.install:
            raise  Exception(f"dependency '{function.name}' cannot be linked")

        self.link_function(function)
    
    def link_function_key(self, function:Function):
        if function.key == None:
            self.memory_manager.allocate_function_key(function)
            self.linked_methods.append(function)


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
        map = next((map for map in maps if map.name == map_transition.map_name), None)
        if map == None:
            raise Exception(f"entrance '{map_transition.entrance_name}' could not find '{map_transition.map_name}.{map_transition.entrance_name}'")
        entrance = [entrance for entrance in map.enum_entrance.values if entrance.name == map_transition.entrance_name]
        if len(entrance) != 1:
            raise Exception(f"entrance '{map_transition.entrance_name}' could not be found in map '{map.name}' ({[entrance.name for entrance in map.enum_entrance.values]})")
        entrance:MapEntrance = entrance[0].value
        
        map_transition.link(map, entrance)

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
    