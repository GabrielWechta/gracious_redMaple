import ply.yacc as yacc
from symbolTable import SymbolTable

symbol_table = SymbolTable()


class Command:
    def __init__(self, command_type, index=None):
        self.type = command_type
        self.index = index
        self.commands = []


def create_program(commands: Command):
    program = Command("COM_PROGRAM")
    program.commands.append(commands)

    return program


def set_variable(name):
    symbol_table.add(name, "VARIABLE")


def set_const(name):
    symbol_table.add(name, "CONST")


def set_array(name, begin, end):
    if begin > end:
        print("WRONG BEGIN AND END")
        return False

    symbol_table.add(name, "ARRAY", None, begin, end)


def add_command(parent: Command, child: Command):
    parent.commands.append(child)

    return parent


def create_parent_command(command_type, *children):
    parent = Command(command_type)

    for i, child in enumerate(children):
        parent.commands.append(child)

    return parent


def create_value_command(command_type, name):
    if type(name) == int:  # TODO for const. Const's name is well... she. Is it good?
        name = str(name)

    index = symbol_table.get(name)

    if index is None:
        print(f"Variable {name} was not declared.")
        raise Exception
    else:
        value_command = Command(command_type, index)

    return value_command


def create_iterator_command(command_type, name):
    index = symbol_table.get(name)

    if index is not None and symbol_table.dict[index][1] != "ITERATOR":
        print(f"Iterator {name} was declared as VAR or ARR before.")
        raise Exception

    elif index is not None and symbol_table.dict[index][1] == "ITERATOR":
        new_index = symbol_table.get(name)
        iterator_command = Command(command_type, new_index)
        return iterator_command

    elif index is None:
        symbol_table.add(name, "ITERATOR")
        new_index = symbol_table.get(name)
        iterator_command = Command(command_type, new_index)
        return iterator_command


def create_empty_command(command_type):
    return Command(command_type)


""" CLEAN PARSER """
from lex import tokens

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    # TODO maybe if then else??
)

start = 'program'


def p_program(p):
    """program  : DECLARE declarations BEGIN commands END
                | BEGIN commands END"""

    if len(p) == 6:
        p[0] = create_program(p[4])
    elif len(p) == 4:
        p[0] = create_program(p[3])


def p_declarations(p):
    """declarations : declarations COMMA PIDENTIFIER
                    | declarations COMMA PIDENTIFIER LPAREN NUM COLON NUM RPAREN
                    | PIDENTIFIER
                    | PIDENTIFIER LPAREN NUM COLON NUM RPAREN"""

    if len(p) == 4:
        set_variable(p[3])
    elif len(p) == 9:
        set_array(p[3], p[5], p[7])
    elif len(p) == 2:
        set_variable(p[1])
    elif len(p) == 7:
        set_array(p[1], p[3], p[5])


def p_commands(p):
    """commands :
                | commands command """
    #  | commands """

    # TODO possible bug maybe his way?
    if len(p) == 3:
        p[0] = add_command(p[1], p[2])
    elif len(p) == 1:
        p[0] = create_empty_command("COM_COMMANDS")
        # print(p[0], p[1])
        # command = p[1]
        # p[0].commands.append(Command("COM_COMMANDS"))  # ?
        # p[0] = add_command(p[1], Command("COM_COMMANDS"))


def p_command(p):
    """command  : identifier ASSGNOP expression SEMICOLON
                | IF condition THEN commands ELSE commands ENDIF
                | IF condition THEN commands ENDIF
                | WHILE condition DO commands ENDWHILE
                | REPEAT commands UNTIL condition SEMICOLON
                | FOR PIDENTIFIER FROM value TO value DO commands ENDFOR
                | FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR
                | READ identifier SEMICOLON
                | WRITE value SEMICOLON"""

    if p[2] == ":=":
        p[0] = create_parent_command("COM_ASSGNOP", p[1], p[3])
    elif p[1] == "IF" and p[5] == "ELSE":
        p[0] = create_parent_command("COM_IFELSE", p[2], p[4], p[6])
    elif p[1] == "IF" and not p[5] == "ELSE":
        p[0] = create_parent_command("COM_IF", p[2], p[4])
    elif p[1] == "WHILE":
        p[0] = create_parent_command("COM_WHILE", p[2], p[4])
    elif p[1] == "REPEAT":
        p[0] = create_parent_command("COM_REPEAT", p[2], p[4])
    elif p[1] == "FOR" and not p[5] == "DOWNTO":
        p[0] = create_parent_command("COM_FOR", create_iterator_command("COM_PID", p[2]),
                                     create_iterator_command("COM_PID", p[2] + "_fake_iter"), p[4], p[6],
                                     p[8])  # TODO maybe fake iter name should be something like '9i'
    elif p[1] == "FOR" and p[5] == "DOWNTO":
        p[0] = create_parent_command("COM_FORDOWN", create_iterator_command("COM_PID", p[2]),
                                     create_iterator_command("COM_PID", p[2] + "_fake_iter"), p[4], p[6], p[8])
    elif p[1] == "READ":
        p[0] = create_parent_command("COM_READ", p[2])
    elif p[1] == "WRITE":
        p[0] = create_parent_command("COM_WRITE", p[2])


def p_expression(p):
    """expression    : value
                    | value PLUS value
                    | value MINUS value
                    | value TIMES value
                    | value DIVIDE value
                    | value MODULO value"""

    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == "+":
        p[0] = create_parent_command("COM_ADD", p[1], p[3])
    elif p[2] == "-":
        p[0] = create_parent_command("COM_SUB", p[1], p[3])
    elif p[2] == "*":
        p[0] = create_parent_command("COM_MUL", p[1], p[3])
    elif p[2] == "/":
        p[0] = create_parent_command("COM_DIV", p[1], p[3])
    elif p[2] == "%":
        p[0] = create_parent_command("COM_MOD", p[1], p[3])


def p_condition(p):
    """condition    : value EQUAL value
                    | value NOTEQUAL value
                    | value LESSER value
                    | value BIGGER value
                    | value LESSEREQUAL value
                    | value BIGGEREQUAL value"""

    if p[2] == "=":
        p[0] = create_parent_command("COM_EQ", p[1], p[3])
    elif p[2] == "!=":
        p[0] = create_parent_command("COM_NEQ", p[1], p[3])
    elif p[2] == "<":
        p[0] = create_parent_command("COM_LT", p[1], p[3])
    elif p[2] == ">":
        p[0] = create_parent_command("COM_GT", p[1], p[3])
    elif p[2] == "<=":
        p[0] = create_parent_command("COM_LEQ", p[1], p[3])
    elif p[2] == ">=":
        p[0] = create_parent_command("COM_GEQ", p[1], p[3])


def p_value_num(p):
    """value    : NUM"""
    if symbol_table.get(str(p[1])) is None:
        set_const(str(p[1]))
    p[0] = create_value_command("COM_NUM", p[1])


def p_value_identifier(p):
    """value    : identifier"""
    p[0] = p[1]


def p_identifier_pidentifier(p):
    """identifier   : PIDENTIFIER
                    | PIDENTIFIER LPAREN PIDENTIFIER RPAREN"""

    if len(p) == 2:
        p[0] = create_value_command("COM_PID", p[1])
    elif len(p) == 4:
        p[0] = create_parent_command("COM_ARR", create_value_command("COM_PID", p[1]),
                                     create_value_command("COM_PID", p[3]))


def p_identifier_num(p):
    """identifier   : PIDENTIFIER LPAREN NUM RPAREN"""

    p[0] = create_parent_command("COM_ARR", create_value_command("COM_PID", p[1]),
                                 create_value_command("COM_NUM", p[3]))


def p_error(t):
    try:
        print("Syntax error at '%s'" % t.value)
    except:
        pass


parser = yacc.yacc()
data = """
DECLARE
    n,p(2:3)
BEGIN
    READ n;
    REPEAT
        [wdwdds ]
        p:=n/2;
        p:=2*p;
        IF n>=p THEN 
            WRITE 1;
        ELSE 
            WRITE 0;
        ENDIF
        n:=n/2;
    UNTIL n=0;
END
"""

testing_data = """
DECLARE 
    x, y, z, w(9:11)
BEGIN
    x:=2;
    y:=3;
    IF x<y THEN
        z:=x-y;
    ELSE
        z:=y-x;
    ENDIF
END
"""
