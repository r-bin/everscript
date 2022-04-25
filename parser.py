from rply import ParserGenerator
from ast_everscript import *
import copy

class Parser():
    def __init__(self, generator):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            [
                '(', ')', ',', ';', '{', '}', '[', ']', # '\n',
                '=', '==',
                'WORD', 'ENUM', 'ENUM_CALL', 'STRING',
                'END', 'LABEL_DESTINATION',
                'ELSEIF', 'IF', 'ELSE',
                'FUNCTION_CODE', 'FUNCTION_EVAL', 'FUNCTION_GOTO',
                'FUN_INSTALL', 'FUN_INJECT', 'FUN', 'FUN_IDENTIFIER',
                'IDENTIFIER'
            ]
        )

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

            print(f"function_list = {element}")
            list.append(element)
            self.generator.append(element)

            return list
        @self.pg.production('function_list : function_list function')
        def parse(p):
            list = p[0]
            element = p[1]

            print(f"function_list = {list} + {element}")
            list.append(element)
            self.generator.append(element)

            return list

        @self.pg.production('function : FUN FUN_IDENTIFIER ( arg_list ) { expression_list }')
        def parse(p):
            name = p[1]
            args = p[3]
            code = p[6]

            function = Function(name, code, args)
            print(f"function = {name}({args}) = {len(code)}")

            return function
        @self.pg.production('function : FUN FUN_IDENTIFIER ( ) { expression_list }')
        def parse(p):
            name = p[1]
            code = p[5]
            args = []

            function = Function(name, code, args)
            print(f"function = {name}({args}) = {len(code)}")

            return function
        @self.pg.production('function : function_arg_list FUN FUN_IDENTIFIER ( ) { expression_list }')
        def parse(p):
            function_args = p[0]
            name = p[2]
            args = []
            code = p[6]

            function = Function(name, code, args, function_args)
            print(f"function = {name} () = {len(code)}")

            return function

        @self.pg.production('function_arg_list : function_arg')
        def parse(p):
            return [ p[0] ]
        @self.pg.production('function_arg_list : function_arg_list function_arg')
        def parse(p):
            return p[0] + [ p[1] ]
        @self.pg.production('function_arg : FUN_INJECT ( expression )')
        def parse(p):
            return Arg_Inject(p[2])
        @self.pg.production('function_arg : FUN_INSTALL ( )')
        def parse(p):
            return Arg_Install()
        @self.pg.production('function_arg : FUN_INSTALL ( expression )')
        def parse(p):
            return Arg_Install(p[2])

        @self.pg.production('expression_list : expression ;')
        def parse(p):
            list = []
            element = p[0]

            print(f"expression_list = {element}")
            list.append(element)

            return list
            
        @self.pg.production('expression_list : expression_list expression ;')
        def parse(p):
            list = p[0]
            element = p[1]

            print(f"expression_list = {list} + {element}")
            list.append(element)
            
            return list

        @self.pg.production('expression_list : expression_list expression_list')
        def parse(p):
            list = p[0]
            elements = p[1]

            print(f"expression_list = {list} + {elements}")
            list = list + elements
            
            return list

        @self.pg.production('expression : label expression')
        def parse(p):
            print(f"label = [{p[0]}] {p[1]}")
            p[1].label_destination = p[0]
            return p[1]
        @self.pg.production('expression_list : label expression_list')
        def parse(p):
            label = p[0]
            list = p[1]
            expression = p[1][0]
            print(f"label = [{label}] {expression}")
            expression.label_destination = label
            return list

        @self.pg.production('expression : expression == expression')
        def parse(p):
            left = p[0]
            right = p[2]
            return Equals(left, right)

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
            return String(p[0])

        @self.pg.production('expression : IDENTIFIER')
        def parse(p):
            return Identifier(p[0])

        @self.pg.production('label : LABEL_DESTINATION')
        def parse(p):
            return Label_Destination(p[0])

        @self.pg.production('expression : FUNCTION_CODE ( param_list )')
        def parse(p):
            return Function_Code(p[2])

        @self.pg.production('expression : FUNCTION_EVAL ( expression )')
        def parse(p):
            return Function_Eval(p[2])

        @self.pg.production('expression : FUNCTION_GOTO ( expression )')
        def parse(p):
            return Function_Goto(p[2])
            
        @self.pg.production('expression : IF ( expression ) { expression_list }')
        def parse(p):
            condition = p[2]
            script = p[5]

            return If_list([If(condition, script)])
        @self.pg.production('expression : IF ( expression ) { expression_list } else_list')
        def parse(p):
            condition = p[2]
            script = p[5]
            list = p[7]

            return If_list([If(condition, script)] + list)
        @self.pg.production('else_list : ELSEIF ( expression ) { expression_list }')
        def parse(p):
            condition = p[2]
            script = [ p[5] ]

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

        @self.pg.production('expression_list : FUN_IDENTIFIER ( param_list ) ;')
        @self.pg.production('expression_list : FUN_IDENTIFIER ( ) ;')
        def parse(p):
            name = p[0]
            params = p[2]
            if not isinstance(params, list):
                params = []

            generator = self.generator
            function = self.generator.function(name)
            
            print(f"function = {name}()")

            if function.install:
                return [ Call(function) ]
            else:
                for p, a in zip(params, function.args):
                    p.name = a.name

                function = copy.deepcopy(function)
                return function.code(params)
            
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

        @self.pg.production('expression : memory')
        def parse(p):
            return p[0]
        @self.pg.production('memory : [ WORD , WORD ]')
        def parse(p):
            address = Word(p[1])
            flag = Word(p[3])

            return Memory(address, flag)

        @self.pg.error
        def error_handle_lex(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
