from rply import ParserGenerator

from compiler.ast_everscript import *
from compiler.codegen import Scope
from compiler.codegen import CodeGen

class Parser():
    def __init__(self, generator:CodeGen):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            [
                'VAL', 'VAR',
                'T_BYTE', 'T_WORD', 'T_MEMORY', 'T_ARG',
                'IS', '!IS',
                'SIGNED',
                '..',
                '(', ')', ',', ';', '{', '}', '<', '>', '[', ']', #'\n',
                '!', 'AND', 'OR',
                '==', '!=', '>=', '>', '<=', '<', 'OR=', '&=', '=', '<<=', '>>=', '*=', '/=', '-=', '+=', '++', '--',
                '!', '+', '-', '*', '/', '<<', '>>', 'B_AND', 'B_OR', 'B_XOR',
                'INVERT_WORD',
                'TRUE', 'FALSE',
                'WORD', 'WORD_DECIMAL', 'ENUM', 'ENUM_CALL', 'STRING', 'STRING_RAW',
                'LABEL_DESTINATION', # 'END',
                'ELSEIF!', 'ELSEIF', 'IF_CURRENCY', 'IF!', 'IF', 'ELSE',
                'WHILE', 'WHILE!',
                'FUNCTION_CALL', 'FUNCTION_STRING',
                '@', ':', 'FUN', 'NAME_IDENTIFIER', 'MAP', 'AREA', 'GROUP',
                'FUN_INCLUDE', 'FUN_MEMORY', 'FUN_PATCH',
                'OBJECT', 'ARG', 'SCRIPT', 'TIME', 'IDENTIFIER',
            ],

            # A list of precedence rules with ascending precedence, to
            # disambiguate ambiguous production rules.
            precedence = [
                ('left', ['+', '-']),
                ('left', ['*', '/', 'B_AND'])
            ]
        )
        
        def parse_memory(p):
            memory = Memory()
            self.generator.add_memory(memory)
            return memory
        def parse_flag(p):
            memory = Memory(None, 0x00)
            self.generator.add_memory(memory)
            return memory

        self.native_functions = {
            "throw": (lambda p: EverScriptException(p[2][0])),
            "eval": (lambda p: Function_Eval(p[2][0])),
            "goto": (lambda p: Function_Goto(p[2][0])),
            "code": (lambda p: Function_Code(p[2])),
            "calculate": (lambda p: Function_Calculate(p[2])),
            "set": (lambda p: Set(p[2][0])),
            "unset": (lambda p: Unset(p[2][0])),
            "len": (lambda p: Len(p[2][0]).eval()),
            "rnd": (lambda p: Rnd(p[2][0], p[2][1]).eval()),
            "call": (lambda p: Call(self.generator, p[2][0], [])),
            "install_string": (lambda p: InstalledString(self.generator, p[2][0])),
            "string_key": (lambda p: StringKey(p[2][0])),
            "function_key": (lambda p: FunctionKey(p[2][0])),
            "memory": (lambda p: self.generator.get_memory()),
            "memory_tmp": (lambda p: self.generator.current_scope().allocate_memory()),
            "flag": (lambda p: self.generator.get_flag()),
            "flag_tmp": (lambda p: self.generator.current_scope().allocate_flag()),
            "reference": (lambda p: Reference(self.generator, p[2][0])),
            "deref": (lambda p: Deref(self.generator, p[2][0], None)),
            "_address": (lambda p: RawAddress(p[2][0])),

            # object
            "_loot": (lambda p: Loot(self.generator, True, p[2][0], p[2][1], p[2][2], p[2][3])),
            "_loot_chest": (lambda p: Loot(self.generator, False, p[2][0], p[2][1], p[2][2], Word(0x00))),
            "_axe2_wall": (lambda p: Axe2Wall(self.generator, p[2][0])),

            # late link
            "entrance": (lambda p: MapEntrance(self.generator, p[2][0], p[2][1], p[2][2], p[2][3] if len(p[2])>=4 else None)),
            "soundtrack": (lambda p: Soundtrack(self.generator, p[2][0], p[2][1])),
            "map_transition": (lambda p: MapTransition(self.generator, p[2][0], p[2][1], p[2][2])),

            # unary operators
            "dead": (lambda p: Dead(p[2][0])),
            "rand": (lambda p: Rand(p[2][0])),
            "randrange": (lambda p: RandRange(p[2][0])),
        }

        self.generator = generator

    def parse(self):
        @self.pg.production('program_list : program_list program')
        def parse(p):
            return p[0] + [ p[1] ]
        @self.pg.production('program_list : program')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('program : enum')
        @self.pg.production('program : object_map')
        @self.pg.production('program : area')
        @self.pg.production('program : group')
        @self.pg.production('program : function')
        def parse(p):
            return p[0]
        @self.pg.production('program : FUN_INCLUDE ( expression )')
        def parse(p):
            path = p[2].value

            return Include(self.generator, path).eval()

        # maps
        @self.pg.production('scope : MAP')
        @self.pg.production('scope : AREA')
        def parse(p):
            scope = Scope(self.generator, p[0])

            self.generator.push_scope(scope)

            return scope
        
        @self.pg.production('area : scope NAME_IDENTIFIER ( ) { program_list } ;')
        def parse(p):
            name = p[1]
            code = p[5]

            scope = self.generator.pop_scope()

            scope.value = None

            self.generator.set_identifier(name, None)
            
            return code
        
        @self.pg.production('group : GROUP NAME_IDENTIFIER ( ) { program_list } ;')
        def parse(p):
            name = p[1]
            code = p[5]

            return code
        
        @self.pg.production('object_map : scope NAME_IDENTIFIER ( param_list ) { program_list } ;')
        def parse(p):
            name = p[1]
            params = p[3]
            code = p[6]

            scope = self.generator.pop_scope()

            map = Map(self.generator, name, params, code, scope.objects)
            scope.value = map

            self.generator.set_identifier(name, map)
            self.generator.add_map(map)
            
            return map
        
        @self.pg.production('expression : expression : IDENTIFIER')
        def parse(p):
            expression = p[0]
            default_enum = p[2]

            match expression:
                case Object():
                    expression.default_enum = default_enum
                case _:
                    TODO()

            return expression

        @self.pg.production('expression : VAL IDENTIFIER = expression')
        @self.pg.production('expression : VAR IDENTIFIER = expression')
        def parse(p):
            constant = p[0].gettokentype() == "VAL"
            name = p[1].value
            value = p[3]

            function_variable = FunctionVariable(name, value, constant)

            scope = self.generator.current_scope()

            self.generator.set_identifier(name, function_variable)

            return function_variable
        
        @self.pg.production('expression : INVERT_WORD ( expression )')
        def parse(p):
            value = p[2]

            match value:
                case Word():
                    value = Word(-value.value)
                case _:
                    value = Inverted(value)

            return value
        
        @self.pg.production('expression : expression IS type')
        @self.pg.production('expression : expression !IS type')
        def parse(p):
            value = p[0]
            type = p[2].value
            inverted = p[1]

            match inverted.gettokentype():
                case 'IS':
                    inverted = False
                case '!IS':
                    inverted = True
                case _:
                    TODO()

            return Is(value, type, inverted)

        @self.pg.production('expression : SIGNED expression')
        def parse(p):
            expression = p[1]
            if isinstance(expression, Arg):
                expression.signed = True
            else:
                TODO()

            return expression
        
        @self.pg.production('expression : OBJECT [ expression ]')
        def parse(p):
            index = p[2]
            if isinstance(index, Token):
                index = Word(index)

            return Object(self.generator, index)
        
        @self.pg.production('expression : ARG [ expression ]')
        def parse(p):
            index = p[2]
            if isinstance(index, Token):
                index = Word(index)

            return Arg(index)
        
        @self.pg.production('expression : SCRIPT [ expression ]')
        def parse(p):
            index = p[2]
            if isinstance(index, Token):
                index = Word(index)

            return Script(index)
        
        @self.pg.production('expression : TIME [ expression ]')
        def parse(p):
            index = p[2]
            if isinstance(index, Token):
                index = Word(index)

            return Time(index)
        
        # enum
        @self.pg.production('enum : ENUM IDENTIFIER { enum_entry_list , }')
        @self.pg.production('enum : ENUM IDENTIFIER { enum_entry_list }')
        def parse(p):
            name = p[1]
            values = p[3]
            enum = Enum(name, values)

            self.generator.set_identifier(name.value, enum)

            return enum
        @self.pg.production('enum_entry_list : enum_entry')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('enum_entry_list : enum_entry_list , enum_entry')
        def parse(p):
            return p[0] + [ p[2] ]
        @self.pg.production('enum_entry : IDENTIFIER = expression')
        @self.pg.production('enum_entry : IDENTIFIER = function')
        def parse(p):
            name = p[0]
            value = p[2]

            return Enum_Entry(name, value)

        # functions
        @self.pg.production('function : FUN NAME_IDENTIFIER ( arg_list ) { expression_list }')
        def parse(p):
            name = p[1]
            args = p[3]
            code = p[6]

            function = Function(name, code, args)
            self.generator.add_function(function)

            return function
        @self.pg.production('function : FUN NAME_IDENTIFIER ( ) { expression_list }')
        def parse(p):
            name = p[1]
            code = p[5]
            args = []

            function = Function(name, code, args)
            self.generator.add_function(function)
            
            return function
        @self.pg.production('function : annotation_list function')
        def parse(p):
            args = p[0]
            function = p[1]

            function.set_annotations(args)

            # TODO: var/val
            # scope = self.generator.pop_scope()
            # scope.value = function
            
            return function
        @self.pg.production('function : { expression_list }')
        def parse(p):
            name = "anonymous"
            args = []
            code = p[1]

            function = Function(name, code, args)
            self.generator.add_function(function)

            return function
        @self.pg.production('function : { expression_list }')
        def parse(p):
            name = "anonymous"
            args = []
            code = p[1]

            function = Function(name, code, args)
            self.generator.add_function(function)
            
            return function

        @self.pg.production('annotation_list : annotation')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('annotation_list : annotation_list annotation')
        def parse(p):
            return p[0] + [ p[1] ]
        @self.pg.production('annotation : @ NAME_IDENTIFIER ( )')
        @self.pg.production('annotation : @ NAME_IDENTIFIER ( param_list )')
        def parse(p):
            name = p[1]
            name = name.value
            params = p[3]
            if not isinstance(params, list):
                params = []

            # TODO: var/val
            # if name == "install":
            #     scope = Scope(self.generator, "NATIVE_FUNCTION")
            #     self.generator.push_scope(scope)

            match [name, len(params)]:
                case ["install", 0]:
                    return Annotation_Install()
                case ["install", 1]:
                    return Annotation_Install(params[0])
                case ["install", 2]:
                    return Annotation_Install(params[0], params[1].eval([]) > 0)
                
                case ["inject", 1]:
                    return Annotation_Inject(params[0], True)
                case ["inject", 2]:
                    return Annotation_Inject(params[0], params[1].eval() == 0)
                
                case ["async", 0]:
                    return Annotation_Async()
                
                case ["count_limit", 1]:
                    return Annotation_CountLimit(params[0])
                
                case _:
                    raise Exception(f"invalid annotation {name}")

        @self.pg.production('expression_entry : expression ;')
        def parse(p):
            element = p[0]

            return element
        @self.pg.production('expression_list : expression_entry')
        def parse(p):
            list = []
            element = p[0]

            list.append(element)

            return list
            
        @self.pg.production('expression_list : expression_list expression_entry')
        def parse(p):
            list = p[0]
            element = p[1]

            list.append(element)
            
            return list

        @self.pg.production('expression_entry : label expression_entry')
        def parse(p):
            label = p[0]
            expression = p[1]
            expression.label_destination = label
            return expression

        @self.pg.production('expression : WORD')
        def parse(p):
            return Word(p[0])
        
        @self.pg.production('expression : WORD_DECIMAL')
        def parse(p):
            return Word(p[0], is_decimal=True)

        @self.pg.production('expression : ENUM_CALL')
        def parse(p):
            identifier = p[0]
            enum = Enum_Call(self.generator, identifier)
            return enum.eval()

        @self.pg.production('expression : STRING')
        def parse(p):
            return String(self.generator, p[0])
        @self.pg.production('expression : STRING_RAW')
        def parse(p):
            return RawString(p[0])

        @self.pg.production('expression : IDENTIFIER')
        def parse(p):
            return Identifier(p[0])
        
        @self.pg.production('expression : function')
        def parse(p):
            function = p[0]

            return function

        @self.pg.production('label : LABEL_DESTINATION')
        def parse(p):
            return Label_Destination(p[0])

        @self.pg.production('if : IF')
        def parse(p):
            return [False, False]
        @self.pg.production('if : IF!')
        def parse(p):
            return [True, False]
        @self.pg.production('if : IF_CURRENCY')
        def parse(p):
            return [False, True]
        @self.pg.production('elseif : ELSEIF')
        def parse(p):
            return [False, False]
        @self.pg.production('elseif : ELSEIF!')
        def parse(p):
            return [True, False]
        
        @self.pg.production('expression_entry : if ( expression ) { expression_list }')
        def parse(p):
            if_properties = p[0]
            condition = p[2]
            script = p[5]

            return If_list([If(condition, script, if_properties)])
        @self.pg.production('expression_entry : if ( expression ) { expression_list } else_list')
        def parse(p):
            if_properties = p[0]
            condition = p[2]
            script = p[5]
            list = p[7]

            return If_list([If(condition, script, if_properties)] + list)
        @self.pg.production('else_list : elseif ( expression ) { expression_list }')
        def parse(p):
            if_properties = p[0]
            condition = p[2]
            script = p[5]

            return [ If(condition, script, if_properties) ]
        @self.pg.production('else_list : elseif ( expression ) { expression_list } else_list')
        def parse(p):
            if_properties = p[0]
            condition = p[2]
            script = p[5]
            list = p[7]

            return [ If(condition, script, if_properties) ] + list
        @self.pg.production('else_list : else')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('else_list : else_list else')
        def parse(p):
            return p[0] + [ p[1] ]
        @self.pg.production('else_list : else_list else_list')
        def parse(p):
            return p[0] + p[1]
        @self.pg.production('else : ELSE { expression_list }')
        def parse(p):
            return If(None, p[2], [False, False])
        
        @self.pg.production('expression : NAME_IDENTIFIER ( param_list )')
        @self.pg.production('expression : NAME_IDENTIFIER ( )')
        def parse(p):
            name = p[0]
            params = p[2]
            if not isinstance(params, list):
                params = []

            if name.value in self.native_functions:
                function = self.native_functions[name.value](p)
                return function
            else:
                function = self.generator.get_function(name)
            
            if function:
                return Call(self.generator, function, params)
            else:
                return Call(self.generator, Identifier(name), params)

        @self.pg.production('expression : FUNCTION_CALL ( expression )')
        def parse(p):
            address = p[2]

            return Call(self.generator, address, [])
        @self.pg.production('expression : FUNCTION_STRING ( expression )')
        def parse(p):
            string = p[2]

            return String(string, True)

        @self.pg.production('arg_list : arg')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('arg_list : arg_list , arg')
        def parse(p):
            return p[0] + [ p[2] ]
        @self.pg.production('arg : IDENTIFIER')
        def parse(p):
            return FunctionArg(p[0].value)
        @self.pg.production('arg : IDENTIFIER : IDENTIFIER')
        def parse(p):
            return FunctionArg(p[0].value, p[2].value)

        @self.pg.production('param_list : param')
        def parse(p):
            param = p[0]
            param_list = [ param ]

            return param_list
        @self.pg.production('param_list : param_list , param')
        def parse(p):
            param = p[2]
            param_list = p[0] + [ param ]

            return param_list

        @self.pg.production('param : expression')
        def parse(p):
            param = p[0]

            if isinstance(param, Identifier):
                return Param(param, None)
            else:
                return Param(None, param)

        @self.pg.production('expression : memory')
        def parse(p):
            return p[0]
        @self.pg.production('memory : memory_flag')
        def parse(p):
            return p[0]
        @self.pg.production('memory_flag : < expression , expression >')
        def parse(p):
            address = Word(p[1])
            flag = Word(p[3])

            return Memory(address, flag)
        
        @self.pg.production('expression :  expression [ expression ]')
        def parse(p):
            expression = p[0]
            offset = p[2]
            if isinstance(offset, Token):
                offset = Word(offset, 2)

            return Deref(self.generator, expression, offset)

        @self.pg.production('type : T_BYTE')
        @self.pg.production('type : T_WORD')
        @self.pg.production('type : T_MEMORY')
        @self.pg.production('type : T_ARG')
        def parse(p):
            return p[0]

        @self.pg.production('memory : ( type ) memory')
        def parse(p):
            data_type = p[1]
            memory = p[3]

            match data_type.gettokentype():
                case 'T_BYTE':
                    memory.force_value_count(1)
                case 'T_WORD':
                    memory.force_value_count(1)
                case _:
                    TODO()

            return memory

        @self.pg.production('memory : < expression >')
        def parse(p):
            address = Word(p[1], 2)

            return Memory(address)
        @self.pg.production('memory : < IDENTIFIER >')
        def parse(p):
            character = p[1]

            address = Enum_Call(self.generator, f"CHARACTER.{character.value}")
            address = address.value

            return Memory(address)

        @self.pg.production('expression : ! expression')
        def parse(p):
            return Invert(p[1])
        
        @self.pg.production('expression : param ++')
        @self.pg.production('expression : param --')
        def parse(p):
            left = p[0]
            operator = p[1]

            match operator.gettokentype():
                case '++':
                    return Asign(left, Add(left, Word(1)))
                case '--':
                    return Asign(left, Sub(left, Word(1)))
                
                case _:
                    raise AssertionError('Oops, this should not be possible!')

        @self.pg.production('expression : param AND param')
        @self.pg.production('expression : param OR param')
        @self.pg.production('expression : param == param')
        @self.pg.production('expression : param != param')
        @self.pg.production('expression : param >= param')
        @self.pg.production('expression : param > param')
        @self.pg.production('expression : param <= param')
        @self.pg.production('expression : param < param')
        @self.pg.production('expression : param OR= param')
        @self.pg.production('expression : param &= param')
        @self.pg.production('expression : param = param')
        @self.pg.production('expression : param <<= param')
        @self.pg.production('expression : param >>= param')
        @self.pg.production('expression : param *= param')
        @self.pg.production('expression : param /= param')
        @self.pg.production('expression : param -= param')
        @self.pg.production('expression : param += param')
        @self.pg.production('expression : param + param')
        @self.pg.production('expression : param - param')
        @self.pg.production('expression : param * param')
        @self.pg.production('expression : param / param')
        @self.pg.production('expression : param << param')
        @self.pg.production('expression : param >> param')
        @self.pg.production('expression : param B_AND param')
        @self.pg.production('expression : param B_OR param')
        @self.pg.production('expression : param B_XOR param')
        def parse(p):
            left = p[0]
            operator = p[1]
            right = p[2]

            match operator.gettokentype():
                case 'AND':
                    return And(left, right)
                case 'OR':
                    return Or(left, right)
                case '==':
                    return Equals(left, right)
                case '!=':
                    return NotEquals(left, right)
                case '>=':
                    return GreaterEquals(left, right)
                case '>':
                    return Greater(left, right)
                case '<=':
                    return LowerEquals(left, right)
                case '<':
                    return Lower(left, right)
                
                case '=':
                    return Asign(left, right)
                case '<<=':
                    return Asign(left, ShiftLeft(left, right))
                case '>>=':
                    return Asign(left, ShiftRight(left, right))
                case '*=':
                    return Asign(left, Mul(left, right))
                case '/=':
                    return Asign(left, Div(left, right))
                case '-=':
                    return Asign(left, Sub(left, right))
                case '+=':
                    return Asign(left, Add(left, right))
                case 'OR=':
                    return Asign(left, Or(left, right))
                case '&=':
                    return Asign(left, And(left, right))
                
                case '+':
                    return Add(left, right)
                case '-':
                    return Sub(left, right)
                case '*':
                    return Mul(left, right)
                case '/':
                    return Div(left, right)
                case '<<':
                    return ShiftLeft(left, right)
                case '>>':
                    return ShiftRight(left, right)
                case 'B_AND':
                    return BinaryAnd(left, right)
                case 'B_OR':
                    return BinaryOr(left, right)
                case 'B_XOR':
                    return BinaryXor(left, right)
                
                case _:
                    raise AssertionError('Oops, this should not be possible!')

        @self.pg.production('expression : TRUE')
        def parse(p):
            return Word(1)
        @self.pg.production('expression : FALSE')
        def parse(p):
            return Word(0)

        @self.pg.production('while : WHILE')
        def parse(p):
            return False
        @self.pg.production('while : WHILE!')
        def parse(p):
            return True
        
        @self.pg.production('expression_entry : while ( expression ) { expression_list }')
        def parse(p):
            inverted = p[0]
            condition = p[2]
            script = p[5]

            return While(condition, script, inverted)

        @self.pg.production('expression : expression .. expression')
        def parse(p):
            return Range(p[0], p[2])
            
        @self.pg.production('program : FUN_MEMORY ( param_list )')
        def parse(p):
            memory_list = p[2]
            memory_list = [m.value for m in memory_list]

            self.generator.linker.add_memory(memory_list)

            return Void()
        
        @self.pg.production('program : FUN_PATCH ( param_list , )')
        @self.pg.production('program : FUN_PATCH ( param_list )')
        def parse(p):
            patch_list = p[2]
            patch_list = [m.value.value for m in patch_list]

            for patch_name in patch_list:
                self.generator.add_patch(patch_name)

            return Void()
        
        @self.pg.production('expression : ( expression )')
        def parse(p):
            term = p[1]

            return term

        @self.pg.error
        def error_handle_lex(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
