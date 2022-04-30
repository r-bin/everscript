from ast_everscript import *
from itertools import dropwhile
import re
from textwrap import wrap

class Linker():
    def __init__(self, code=[]):
        self.code = code
        self.system = {}

    def link(self):
        self.link_function(self.code)

        for function in self.code:
            self.link_goto(function)

    def link_function(self, code):
        address = 0xb08000

        for function in code:
            if function.address == None:
                function.address = address

            count = sum([e.count() for e in function.script])
            address += count

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
                if distance >= 0:
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
        
        return -1
    