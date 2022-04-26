from rply import ParserGenerator
from ast_everscript import *

class Parser():
    def __init__(self, generator):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            [
                '(', ')', ',', ';', '{', '}', '[', ']', # '\n',
                '=', '==',
                '!', '+', '-', '*', '/', '<<', '>>',
                'WORD', 'ENUM', 'ENUM_CALL', 'STRING',
                'END', 'LABEL_DESTINATION',
                'ELSEIF', 'IF', 'ELSE',
                'FUNCTION_CODE', 'FUNCTION_EVAL', 'FUNCTION_GOTO',
                'FUN_INSTALL', 'FUN_INJECT', 'FUN', 'FUN_IDENTIFIER',
                'FUN_INCLUDE',
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
        @self.pg.production('program : FUN_INCLUDE ( expression )')
        def parse(p):
            path = p[2].value.value

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

        @self.pg.production('expression_entry : expression ;')
        def parse(p):
            element = p[0]

            print(f"expression_entry = {element}")

            return element
        @self.pg.production('expression_list : expression_entry')
        def parse(p):
            list = []
            element = p[0]

            print(f"expression_list = {element}")
            list.append(element)

            return list
            
        @self.pg.production('expression_list : expression_list expression_entry')
        def parse(p):
            list = p[0]
            element = p[1]

            print(f"expression_list = {list} + {element}")
            list.append(element)
            
            return list

        @self.pg.production('expression_entry : label expression_entry')
        def parse(p):
            label = p[0]
            expression = p[1]
            print(f"label = [{label}] {expression}")
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

            function = self.generator.function(name)
            
            print(f"function = {name}()")

            return Call(function, params)

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
        @self.pg.production('memory_flag : [ WORD , WORD ]')
        def parse(p):
            address = Word(p[1])
            flag = Word(p[3])

            return Memory(address, flag)
        @self.pg.production('memory_flag : [ WORD ]')
        def parse(p):
            address = Word(p[1])

            return Memory(address)
        @self.pg.production('memory : [ WORD ]')
        def parse(p):
            address = Word(p[1])

            return Memory(address)

        @self.pg.production('expression : expression == expression')
        @self.pg.production('expression : expression = expression')
        @self.pg.production('expression : expression + expression')
        @self.pg.production('expression : expression - expression')
        @self.pg.production('expression : expression * expression')
        @self.pg.production('expression : expression / expression')
        @self.pg.production('expression : expression << expression')
        @self.pg.production('expression : expression >> expression')
        def parse(p):
            left = p[0]
            operator = p[1]
            right = p[2]
            
            if operator.gettokentype() == '==':
                return Equals(left, right)
            if operator.gettokentype() == '=':
                return Asign(left, right)
            elif operator.gettokentype() == '+':
                return Add(left, right)
            elif operator.gettokentype() == '-':
                return Sub(left, right)
            elif operator.gettokentype() == '*':
                return Mul(left, right)
            elif operator.gettokentype() == '/':
                return Div(left, right)
            elif operator.gettokentype() == '<<':
                return ShiftLeft(left, right)
            elif operator.gettokentype() == '>>':
                return ShiftRight(left, right)
            else:
                raise AssertionError('Oops, this should not be possible!')

        @self.pg.error
        def error_handle_lex(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
