from rply import ParserGenerator
from compiler.ast_everscript import *

class Parser():
    def __init__(self, generator):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            [
                '..',
                '(', ')', ',', ';', '{', '}', '<', '>', # '[', ']', '\n',
                '==', '>=', '>', '<=', '<', 'OR=', '&=', '=',
                '!', '+', '-', '*', '/', '<<', '>>',
                'TRUE', 'FALSE',
                'WORD', 'ENUM', 'ENUM_CALL', 'STRING',
                'LABEL_DESTINATION', # 'END',
                'ELSEIF', 'IF', 'ELSE',
                'WHILE',
                'FUNCTION_CALL', 'FUNCTION_STRING',
                'FUN_INSTALL', 'FUN_INJECT', 'FUN', 'FUN_IDENTIFIER',
                'FUN_INCLUDE', 'FUN_MEMORY',
                'IDENTIFIER'
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

        self.functions = {
            "eval": (lambda p: Function_Eval(p[2][0])),
            "goto": (lambda p: Function_Goto(p[2][0])),
            "code": (lambda p: Function_Code(p[2])),
            "set": (lambda p: Set(p[2][0])),
            "len": (lambda p: Len(p[2][0]).eval()),
            "rnd": (lambda p: Rnd(p[2][0], p[2][1]).eval()),
            "call": (lambda p: Call(p[2][0], [])),
            "string": (lambda p: String(self.generator, p[2][0], True)),
            "cstring": (lambda p: RawString(p[2][0])),
            "string_key": (lambda p: StringKey(p[2][0])),
            "memory": (lambda p: self.generator.get_memory()),
            "flag": (lambda p: self.generator.get_flag())
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
        @self.pg.production('program : function_list')
        def parse(p):
            return p[0]
        @self.pg.production('program : FUN_INCLUDE ( expression )')
        def parse(p):
            path = p[2].value

            return Include(self.generator, path).eval()

        @self.pg.production('enum : ENUM IDENTIFIER { enum_entry_list }')
        def parse(p):
            name = p[1]
            values = p[3]
            enum = Enum(name, values)

            self.generator.add_enum(enum)

            return enum
        @self.pg.production('enum_entry_list : enum_entry')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('enum_entry_list : enum_entry_list , enum_entry')
        def parse(p):
            return p[0] + [ p[2] ]
        @self.pg.production('enum_entry : IDENTIFIER = expression')
        def parse(p):
            name = p[0]
            value = p[2]

            return Enum_Entry(name, value)

        @self.pg.production('function_list : function')
        def function_list(p):
            list = []
            element = p[0]

            list.append(element)
            self.generator.append(element)

            return list
        @self.pg.production('function_list : function_list function')
        def parse(p):
            list = p[0]
            element = p[1]

            list.append(element)
            self.generator.append(element)

            return list

        @self.pg.production('function : FUN FUN_IDENTIFIER ( arg_list ) { expression_list }')
        def parse(p):
            name = p[1]
            args = p[3]
            code = p[6]

            function = Function(name, code, args)
            
            return function
        @self.pg.production('function : FUN FUN_IDENTIFIER ( ) { expression_list }')
        def parse(p):
            name = p[1]
            code = p[5]
            args = []

            function = Function(name, code, args)
            
            return function
        @self.pg.production('function : function_arg_list FUN FUN_IDENTIFIER ( ) { expression_list }')
        def parse(p):
            function_args = p[0]
            name = p[2]
            args = []
            code = p[6]

            function = Function(name, code, args, function_args)
            
            return function

        @self.pg.production('function_arg_list : function_arg')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('function_arg_list : function_arg_list function_arg')
        def parse(p):
            return p[0] + [ p[1] ]
        @self.pg.production('function_arg : FUN_INJECT ( expression )')
        @self.pg.production('function_arg : FUN_INJECT ( expression , expression )')
        def parse(p):
            address = p[2]
            terminate = True
            if len(p) >= 5 and isinstance(p[4], Word):
                terminate = p[4].eval() == 0

            return Arg_Inject(address, terminate)
        @self.pg.production('function_arg : FUN_INSTALL ( )')
        def parse(p):
            return Arg_Install()
        @self.pg.production('function_arg : FUN_INSTALL ( expression )')
        def parse(p):
            return Arg_Install(p[2])
        @self.pg.production('function_arg : FUN_INSTALL ( expression , expression )')
        def parse(p):
            address = p[2]
            terminate = p[4].eval() > 0

            return Arg_Install(address, terminate)

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

        @self.pg.production('expression : ENUM_CALL')
        def parse(p):
            identifier = p[0]
            enum = Enum_Call(self.generator, identifier)
            return enum.eval()

        @self.pg.production('expression : STRING')
        def parse(p):
            return String(self.generator, p[0])

        @self.pg.production('expression : IDENTIFIER')
        def parse(p):
            return Identifier(p[0])

        @self.pg.production('label : LABEL_DESTINATION')
        def parse(p):
            return Label_Destination(p[0])

        @self.pg.production('expression_entry : IF ( expression ) { expression_list }')
        def parse(p):
            condition = p[2]
            script = p[5]

            return If_list([If(condition, script)])
        @self.pg.production('expression_entry : IF ( expression ) { expression_list } else_list')
        def parse(p):
            condition = p[2]
            script = p[5]
            list = p[7]

            return If_list([If(condition, script)] + list)
        @self.pg.production('else_list : ELSEIF ( expression ) { expression_list }')
        def parse(p):
            condition = p[2]
            script = p[5]

            return [ If(condition, script) ]
        @self.pg.production('else_list : ELSEIF ( expression ) { expression_list } else_list')
        def parse(p):
            condition = p[2]
            script = p[5]
            list = p[7]

            return [ If(condition, script) ] + list
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
            return If(None, p[2])

        @self.pg.production('expression : FUN_IDENTIFIER ( param_list )')
        @self.pg.production('expression : FUN_IDENTIFIER ( )')
        def parse(p):
            name = p[0]
            params = p[2]
            if not isinstance(params, list):
                params = []

            if name.value in self.functions:
                function = self.functions[name.value](p)
                return function
            else:
                function = self.generator.function(name)
            
            return Call(function, params)

        @self.pg.production('expression : FUNCTION_CALL ( expression )')
        def parse(p):
            address = p[2]

            return Call(address, [])
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
            return Arg(p[0].value)

        @self.pg.production('param_list : param')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('param_list : param_list , param')
        def parse(p):
            return p[0] + [ p[2] ]

        @self.pg.production('param : expression')
        def parse(p):
            if isinstance(p[0], Identifier):
                return Param(p[0], None)
            else:
                return Param(None, p[0])

        @self.pg.production('expression : ! expression')
        def parse(p):
            expression = p[1]
            
            expression.inverted = True

            return expression

        @self.pg.production('expression : memory')
        def parse(p):
            return p[0]
        @self.pg.production('memory : memory_flag')
        def parse(p):
            return p[0]
        @self.pg.production('memory_flag : < WORD , WORD >')
        def parse(p):
            address = Word(p[1])
            flag = Word(p[3])

            return Memory(address, flag)
        @self.pg.production('memory : < WORD >')
        def parse(p):
            address = Word(p[1])

            return Memory(address)

        @self.pg.production('expression : param == param')
        @self.pg.production('expression : param >= param')
        @self.pg.production('expression : param > param')
        @self.pg.production('expression : param <= param')
        @self.pg.production('expression : param < param')
        @self.pg.production('expression : param OR= param')
        @self.pg.production('expression : param &= param')
        @self.pg.production('expression : param = param')
        @self.pg.production('expression : param + param')
        @self.pg.production('expression : param - param')
        @self.pg.production('expression : param * param')
        @self.pg.production('expression : param / param')
        @self.pg.production('expression : param << param')
        @self.pg.production('expression : param >> param')
        def parse(p):
            left = p[0]
            operator = p[1]
            right = p[2]

            match operator.gettokentype():
                case '==':
                    return Equals(left, right)
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
                case 'OR=':
                    return OrAsign(left, right)
                case '&=':
                    return AndAsign(left, right)
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
                case _:
                    raise AssertionError('Oops, this should not be possible!')

        @self.pg.production('expression : TRUE')
        def parse(p):
            return Word(1)
        @self.pg.production('expression : FALSE')
        def parse(p):
            return Word(0)

        @self.pg.production('expression_entry : WHILE ( expression ) { expression_list }')
        def parse(p):
            condition = p[2]
            script = p[5]

            return While(condition, script)

        @self.pg.production('expression : expression .. expression')
        def parse(p):
            return Range(p[0], p[2])
            
        @self.pg.production('program : FUN_MEMORY ( param_list )')
        def parse(p):
            memory_list = p[2]
            memory_list = [m.value for m in memory_list]

            self.generator.linker.add_memory(memory_list)

            return Void()

        @self.pg.error
        def error_handle_lex(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
