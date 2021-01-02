import ply.yacc as yacc

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

    print("program")

def p_declarations(p):
    """declarations : declarations COMMA PIDENTIFIER
                    | declarations COMMA PIDENTIFIER LPAREN NUM COLON NUM RPAREN
                    | PIDENTIFIER
                    | PIDENTIFIER LPAREN NUM COLON NUM RPAREN"""

    print("declarations")

def p_commands(p):
    """commands : commands command
                | command"""

    print("commands")

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

    print("command")

def p_expression(p):
    """expression    : value
                    | value PLUS value
                    | value MINUS value
                    | value TIMES value
                    | value DIVIDE value
                    | value MODULO value"""

    print("expression")


def p_condition(p):
    """condition    : value EQUAL value
                    | value NOTEQUAL value
                    | value LESSER value
                    | value BIGGER value
                    | value LESSEREQUAL value
                    | value BIGGEREQUAL value"""

    print("condition")

def p_value(p):
    """value    : NUM
                | identifier"""

    print("value")

def p_identifier(p):
    """identifier   : PIDENTIFIER
                    | PIDENTIFIER LPAREN PIDENTIFIER RPAREN
                    | PIDENTIFIER LPAREN NUM RPAREN"""

    print("identifier")

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

result = parser.parse(data)
print(result)