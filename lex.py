""" Lexer program for jftt compiler.
    nothing fancy, everything as typical lexer.
    """

import ply.lex as lex

# List of token names.
tokens = ("DECLARE", "BEGIN", "IF", "THEN", "ELSE", "ENDIF", "WHILE", "DO", "ENDWHILE", "END",
          "REPEAT", "UNTIL", "FOR", "FROM", "TO", "ENDFOR", "DOWNTO", "READ", "WRITE",
          "ASSGNOP", "PLUS", "MINUS", "TIMES", "DIVIDE", "MODULO",
          "LPAREN", "RPAREN",
          "NOTEQUAL", "EQUAL", "LESSEREQUAL", "BIGGEREQUAL", "LESSER", "BIGGER",
          "NUM", "PIDENTIFIER",
          "COMMA", "SEMICOLON", "COLON"
          )

""" SIMPLE TOKENS """
def t_DECLARE(t):
    r'DECLARE'
    return t
def t_BEGIN(t):
    r'BEGIN'
    return t
def t_IF(t):
    r'IF'
    return t
def t_THEN(t):
    r'THEN'
    return t
def t_ELSE(t):
    r'ELSE'
    return t
def t_ENDIF(t):
    r'ENDIF'
    return t
def t_WHILE(t):
    r'WHILE'
    return t
def t_DOWNTO(t):
    r'DOWNTO'
    return t
def t_DO(t):
    r'DO'
    return t
def t_ENDWHILE(t):
    r'ENDWHILE'
    return t
def t_REPEAT(t):
    r'REPEAT'
    return t
def t_UNTIL(t):
    r'UNTIL'
    return t
def t_FOR(t):
    r'FOR'
    return t
def t_FROM(t):
    r'FROM'
    return t
def t_TO(t):
    r'TO'
    return t
def t_ENDFOR(t):
    r'ENDFOR'
    return t
def t_READ(t):
    r'READ'
    return t
def t_WRITE(t):
    r'WRITE'
    return t
def t_END(t):
    r'END'
    return t

""" NOT SIMPLE TOKENS """
def t_ASSGNOP(t):
    r':='
    t.value = ':='
    return t

def t_PLUS(t):
    r'\+'
    t.value = '+'
    return t

def t_MINUS(t):
    r'-'
    t.value = '-'
    return t

def t_TIMES(t):
    r'\*'
    t.value = '*'
    return t

def t_DIVIDE(t):
    r'/'
    t.value = '/'
    return t

def t_MODULO(t):
    r'%'
    t.value = '%'
    return t

def t_LPAREN(t):
    r'\('
    t.value = '('
    return t

def t_RPAREN(t):
    r'\)'
    t.value = ')'
    return t

def t_NOTEQUAL(t):
    r'!\='
    t.value = '!='
    return t

def t_EQUAL(t):
    r'='
    t.value = '='
    return t

def t_LESSEREQUAL(t):
    r'\<\='
    t.value = '<='
    return t

def t_BIGGEREQUAL(t):
    r'\>\='
    t.value = '>='
    return t

def t_LESSER(t):
    r'\<'
    t.value = '<'
    return t

def t_BIGGER(t):
    r'\>'
    t.value = '>'
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_PIDENTIFIER(t):
    r'[_a-z]+'
    return t

def t_COMMA(t):
    r','
    return t

def t_SEMICOLON(t):
    r';'
    return t

def t_COLON(t):
    r':'
    return t

def t_COMMENT(t):
    r'\[(.|[\n])*?\]'
    # return t
    pass

""" STANDARD TOKENS """
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

""" BUILDING LEXER """
lexer = lex.lex()

