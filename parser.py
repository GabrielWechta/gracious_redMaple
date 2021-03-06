""" Parser for jftt compiler, here on the other hand fancy stuff start to happen. """
import sys

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


def set_variable_in_declaration(name):
    """ Function for declaring variables inside DECLARE field. It's special cause it throws exception when same variable is
        being declared twice. """
    if symbol_table.get_symbol_by_name(name) is not None:
        print(f"Double {name} variable declaration", file=sys.stderr)
        sys.exit()  # in this case we programs stops
    else:
        symbol_table.add(name, "VARIABLE")


def set_variable(name):
    """ Function for adding everything approached by parser to symbol table.
        checking if all variables used in program where declared happens in
        symbol_table.check_declaration_sack() """
    if symbol_table.get_symbol_by_name(name) is not None:
        return
    else:
        symbol_table.add(name, "VARIABLE")


def set_const(name):
    symbol_table.add(name, "CONST", int(name), None, None, True)


def set_array(name, begin, end):
    if begin > end:
        print(f"Wrong array {name} declaration.", file=sys.stderr)
        sys.exit()

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
    if type(name) == int:
        name = str(name)

    index = symbol_table.get(name)

    if index is None:
        print(f"Variable {name} was not declared.", file=sys.stderr)
        sys.exit()
    else:
        value_command = Command(command_type, index)

    return value_command


def create_iterator_command(command_type, name):
    index = symbol_table.get(name)

    if index is not None and symbol_table.dict[index][1] == "VARIABLE":
        return

    if index is not None and symbol_table.dict[index][1] != "ITERATOR":
        print(f"Iterator {name} was declared as VAR or ARR before.", file=sys.stderr)
        sys.exit()

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
        set_variable_in_declaration(p[3])
        symbol_table.add_to_declaration_sack(p[3])
    elif len(p) == 9:
        set_array(p[3], p[5], p[7])
    elif len(p) == 2:
        set_variable_in_declaration(p[1])
        symbol_table.add_to_declaration_sack(p[1])
    elif len(p) == 7:
        set_array(p[1], p[3], p[5])


def p_commands(p):
    """commands :
                | commands command """

    if len(p) == 3:
        p[0] = add_command(p[1], p[2])
    elif len(p) == 1:
        p[0] = create_empty_command("COM_COMMANDS")


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
    elif p[1] == "FOR" and p[5] == "TO":
        set_variable(p[2])
        set_variable(p[2] + "_FAKE_iter")
        symbol_table.add_to_declaration_sack(p[2])
        p[0] = create_parent_command("COM_FOR", create_value_command("COM_PID", p[2]),
                                     create_value_command("COM_PID", p[2] + "_FAKE_iter"), p[4], p[6],
                                     p[8])

    elif p[1] == "FOR" and p[5] == "DOWNTO":
        set_variable(p[2])
        set_variable(p[2] + "_FAKE_iter")
        symbol_table.add_to_declaration_sack(p[2])
        p[0] = create_parent_command("COM_FORDOWN", create_value_command("COM_PID", p[2]),
                                     create_value_command("COM_PID", p[2] + "_FAKE_iter"), p[4], p[6], p[8])
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
        set_variable(p[1])
        p[0] = create_value_command("COM_PID", p[1])
    elif len(p) == 5:
        set_variable(p[3])
        if symbol_table.get_symbol_by_name(p[1])[1] != "ARRAY":
            print(f"{p[1]} is not array.", file=sys.stderr)
            sys.exit()
        p[0] = create_parent_command("COM_ARR", create_value_command("COM_PID", p[1]),
                                     create_value_command("COM_PID", p[3]))


def p_identifier_num(p):
    """identifier   : PIDENTIFIER LPAREN NUM RPAREN"""
    if symbol_table.get_symbol_by_name(p[1])[1] != "ARRAY":
        print(f"{p[1]} is not array.", file=sys.stderr)
        sys.exit()
    if symbol_table.get(str(p[3])) is None:
        set_const(str(p[3]))
    p[0] = create_parent_command("COM_ARR", create_value_command("COM_PID", p[1]),
                                 create_value_command("COM_NUM", p[3]))


def p_error(t):
    print("Syntax error at '%s'" % t.value)
    sys.exit()

parser = yacc.yacc()
