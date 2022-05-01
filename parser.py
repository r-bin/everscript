from rply import ParserGenerator
from ast_everscript import *

class Parser():
    def __init__(self, generator):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            [
                '(', ')', ',', ';', '{', '}', '[', ']', '<', '>', # '\n',
                '==', '>=', '>', '<=', '<', 'OR=', '&=', '=',
                '!', '+', '-', '*', '/', '<<', '>>',
                'TRUE', 'FALSE',
                'WORD', 'ENUM', 'ENUM_CALL', 'STRING',
                'END', 'LABEL_DESTINATION',
                'ELSEIF', 'IF', 'ELSE',
                'FUNCTION_CODE', 'FUNCTION_EVAL', 'FUNCTION_GOTO', 'FUNCTION_SET', 'FUNCTION_LEN', 'FUNCTION_RND', 'FUNCTION_CALL',
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
                terminate = p[4].eval()

            return Arg_Inject(address, terminate)
        @self.pg.production('function_arg : FUN_INSTALL ( )')
        def parse(p):
            return Arg_Install()
        @self.pg.production('function_arg : FUN_INSTALL ( expression )')
        def parse(p):
            return Arg_Install(p[2])

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
        @self.pg.production('expression : FUNCTION_SET ( expression )')
        def parse(p):
            return Set(p[2])
            
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
            
            return Call(function, params)

        @self.pg.production('expression : FUNCTION_CALL ( expression )')
        def parse(p):
            address = p[2]

            return Call(address, [])

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

        @self.pg.production('expression : expression == expression')
        @self.pg.production('expression : expression >= expression')
        @self.pg.production('expression : expression > expression')
        @self.pg.production('expression : expression <= expression')
        @self.pg.production('expression : expression < expression')
        @self.pg.production('expression : expression OR= expression')
        @self.pg.production('expression : expression &= expression')
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

        @self.pg.production('expression : FUNCTION_LEN ( expression )')
        def parse(p):
            return Len(p[2]).eval()

        @self.pg.production('expression : FUNCTION_RND ( expression , expression )')
        def parse(p):
            return Rnd(p[2], p[4]).eval()

        @self.pg.production('expression : TRUE')
        def parse(p):
            return Word(1)
        @self.pg.production('expression : FALSE')
        def parse(p):
            return Word(0)

        @self.pg.error
        def error_handle_lex(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
