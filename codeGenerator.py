from parser import Command, parser, symbol_table


class codeCommand:
    def __init__(self, cc_type: str, args=None, block=None):
        self.type = cc_type
        self.args = []
        self.block = block


class codeProgram:
    def __init__(self):
        self.code_commands = []
        self.label = 1

    def __str__(self):
        table = ""
        for command in self.code_commands:
            table += command.type + " " + str(command.args) + "\n"
        return table

    def add_code_command(self, cc_type):
        code_command = codeCommand(cc_type)
        code_command.block = -1
        self.code_commands.append(code_command)

    def add_arg_to_current_command(self, arg):
        self.code_commands[-1].args.append(arg)

    def bad_inequality(self):
        if self.code_commands[-1] == "CODE_JLT" or self.code_commands[-1] == "CODE_JGT":
            return True
        else:
            return False

    def switch_condition_at_current_command(self):
        current_type = self.code_commands[-1].type

        if current_type == "CODE_JNEQ":
            self.code_commands[-1].type = "CODE_JEQ"
        elif current_type == "CODE_JEQ":
            self.code_commands[-1].type = "CODE_JNEQ"

        elif current_type == "CODE_JGEQ":
            self.code_commands[-1].type = "CODE_JLT"
        elif current_type == "CODE_JLEQ":
            self.code_commands[-1].type = "CODE_JGT"

        elif current_type == "CODE_JGT":
            self.code_commands[-1].type = "CODE_JLEQ"
        elif current_type == "CODE_JLT":
            self.code_commands[-1].type = "CODE_JGEQ"

    def set_type_of_current_command(self, cc_type):
        self.code_commands[-1].type = cc_type

    def change_jump_destination_at_current_command(self, dest):
        self.code_commands[-1].args[0] = dest

    def add_label(self, label_value):
        code_command = codeCommand("CODE_LABEL")
        code_command.block = -1
        code_command.args.append(label_value)
        self.code_commands.append(code_command)


code_program = codeProgram()


def transform_tree_r(command: Command):
    if not command:  # to check
        return

    if command.type == "COM_ASSGNOP":
        code_program.add_code_command("CODE_COPY")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_NUM":
        code_program.add_arg_to_current_command(command.index)
        # code_program.add_arg_to_current_command(None)

    elif command.type == "COM_PID":
        code_program.add_arg_to_current_command(command.index)
        # code_program.add_arg_to_current_command(None)

    elif command.type == "COM_ARR":
        # code_program.add_code_command("CODE_ARR")
        code_program.add_arg_to_current_command(command.commands[0].index)
        code_program.add_arg_to_current_command(command.commands[1].index)

    elif command.type == "COM_ADD":
        code_program.add_code_command("CODE_ADD")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_SUB":
        code_program.add_code_command("CODE_SUB")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_MUL":
        code_program.add_code_command("CODE_MUL")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_DIV":
        code_program.add_code_command("CODE_DIV")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_MOD":
        code_program.add_code_command("CODE_MOD")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_IF":
        label_exit = code_program.label
        code_program.label += 1
        label_tmp = label_exit

        code_program.add_code_command("CODE_UNKNOWN")
        code_program.add_arg_to_current_command(label_tmp)
        code_program.add_arg_to_current_command(-1)
        transform_tree_r(command.commands[0])

        if code_program.bad_inequality():
            code_program.switch_condition_at_current_command()
            label_exit = code_program.label
            code_program.label += 1
            code_program.add_code_command("CODE_JUMP")
            code_program.add_arg_to_current_command(label_exit)
            code_program.add_label(label_tmp)

        transform_tree_r(command.commands[1])  # this is happening if true
        code_program.add_label(label_exit)

    elif command.type == "COM_IFELSE":
        label_else = code_program.label
        code_program.label += 1
        label_exit = code_program.label
        code_program.label += 1
        label_tmp = label_exit

        code_program.add_code_command("CODE_UNKNOWN")
        code_program.add_arg_to_current_command(label_tmp)
        code_program.add_arg_to_current_command(-1)  # ?
        transform_tree_r(command.commands[0])

        if code_program.bad_inequality():
            code_program.switch_condition_at_current_command()
            label_else = code_program.label
            code_program.label += 1
            code_program.add_code_command("CODE_JUMP")
            code_program.add_arg_to_current_command(label_else)
            code_program.add_label(label_tmp)

        transform_tree_r(command.commands[1])  # this is happening if true
        code_program.add_code_command("CODE_JUMP")
        code_program.add_arg_to_current_command(label_exit)
        code_program.add_label(label_else)

        transform_tree_r(command.commands[2])
        code_program.add_label(label_exit)

    elif command.type == "COM_WHILE":
        label_start = code_program.label
        code_program.label += 1
        label_exit = code_program.label
        code_program.label += 1
        label_tmp = label_exit

        code_program.add_label(label_start)
        code_program.add_code_command("CODE_UNKNOWN")
        code_program.add_arg_to_current_command(label_tmp)
        code_program.add_arg_to_current_command(-1)  # ?
        transform_tree_r(command.commands[0])

        if code_program.bad_inequality():
            code_program.switch_condition_at_current_command()
            label_exit = code_program.label
            code_program.label += 1
            code_program.add_code_command("CODE_JUMP")
            code_program.add_arg_to_current_command(label_exit)
            code_program.add_label(label_tmp)

        transform_tree_r(command.commands[1])
        code_program.add_code_command("CODE_JUMP")
        code_program.add_arg_to_current_command(label_start)
        code_program.add_label(label_exit)

    elif command.type == "COM_REPEAT":
        label_start = code_program.label
        code_program.label += 1

        code_program.add_label(label_start)

        transform_tree_r(command.commands[0])

        code_program.add_code_command("CODE_UNKNOWN")
        code_program.add_arg_to_current_command(label_start)
        code_program.add_arg_to_current_command(-1)
        transform_tree_r(command.commands[1])

        if code_program.bad_inequality():
            code_program.switch_condition_at_current_command()
            label_exit = code_program.label
            code_program.label += 1
            code_program.change_jump_destination_at_current_command(label_exit)
            code_program.add_code_command("CODE_JUMP")
            code_program.add_arg_to_current_command(label_start)
            code_program.add_label(label_exit)

    elif command.type == "COM_FOR":
        label_start = code_program.label
        code_program.label += 1
        label_exit = code_program.label
        code_program.label += 1

        code_program.add_code_command("CODE_COPY")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[2])

        code_program.add_code_command("CODE_COPY")
        transform_tree_r(command.commands[1])
        transform_tree_r(command.commands[3])

        code_program.add_code_command("CODE_INC")
        transform_tree_r(command.commands[1])

        code_program.add_code_command("CODE_SUB")
        transform_tree_r(command.commands[1])
        # transform_tree_r(command.commands[1]) # TODO is it necessary?
        transform_tree_r(command.commands[2])

        code_program.add_label(label_start)

        code_program.add_code_command("CODE_JZERO")
        code_program.add_arg_to_current_command(label_exit)
        code_program.add_arg_to_current_command(-1)
        transform_tree_r(command.commands[1])

        transform_tree_r(command.commands[4])

        code_program.add_code_command("CODE_INC")
        transform_tree_r(command.commands[0])

        code_program.add_code_command("CODE_DEC")
        transform_tree_r(command.commands[1])

        code_program.add_code_command("CODE_JUMP")
        code_program.add_arg_to_current_command(label_start)

        code_program.add_label(label_exit)

    elif command.type == "COM_FORDOWN":
        label_start = code_program.label
        code_program.label += 1
        label_exit = code_program.label
        code_program.label += 1

        code_program.add_code_command("CODE_COPY")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[2])

        code_program.add_code_command("CODE_COPY")
        transform_tree_r(command.commands[1])
        transform_tree_r(command.commands[2])

        code_program.add_code_command("CODE_INC")
        transform_tree_r(command.commands[1])

        code_program.add_code_command("CODE_SUB")
        transform_tree_r(command.commands[1])
        transform_tree_r(command.commands[1])
        transform_tree_r(command.commands[3])

        code_program.add_label(label_start)

        code_program.add_code_command("CODE_JZERO")
        code_program.add_arg_to_current_command(label_exit)
        code_program.add_arg_to_current_command(-1)
        transform_tree_r(command.commands[1])

        transform_tree_r(command.commands[4])

        code_program.add_code_command("CODE_DEC")
        transform_tree_r(command.commands[0])

        code_program.add_code_command("CODE_DEC")
        transform_tree_r(command.commands[1])

        code_program.add_code_command("CODE_JUMP")
        code_program.add_arg_to_current_command(label_start)

        code_program.add_label(label_exit)


    elif command.type == "COM_EQ":
        code_program.set_type_of_current_command("CODE_JNEQ")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_NEQ":
        code_program.set_type_of_current_command("CODE_JEQ")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_LT":
        code_program.set_type_of_current_command("CODE_JGEQ")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_GT":
        code_program.set_type_of_current_command("CODE_JLEQ")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_LEQ":
        code_program.set_type_of_current_command("CODE_JGT")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_GEQ":
        code_program.set_type_of_current_command("CODE_JLT")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_READ":
        code_program.add_code_command("CODE_READ")
        transform_tree_r(command.commands[0])

    elif command.type == "COM_WRITE":
        code_program.add_code_command("CODE_WRITE")
        transform_tree_r(command.commands[0])

    elif command.type == "COM_COMMANDS":
        for c in command.commands:
            transform_tree_r(c)

    elif command.type == "COM_PROGRAM":
        for c in command.commands:
            transform_tree_r(c)


def transfer_tree_to_code(program: Command):
    transform_tree_r(program)
    return code_program


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

if_test = """
DECLARE 
    x,y,p(8:12)
BEGIN
    IF x = 5 THEN
        x:= 2;
    ENDIF
END
"""

stupid_test = """
DECLARE 
    x,y,w(1:3)
BEGIN
    w(2):=4;
    w(3):=5;
    y:=2;
    x:=3;
    w(x):=w(x) - w(y);
    x:=w(x);
    x:= x + 1;
    WRITE w(x);
END
"""

stupid_test_2 = """
DECLARE 
    x,y,w(10:30)
BEGIN
    w(15):= 12;
    WRITE w(15);
    READ w(15);
    WRITE w(15);
    x:=16;
    READ w(x);
    WRITE w(x);
END
"""

for_test_1 = """
DECLARE 
    x, w(2:40)
BEGIN
    FOR i FROM w(i) TO 40 DO
        FOR j FROM 10 TO 40 DO
            WRITE w(j);
        ENDFOR
        WRITE w(i);
    ENDFOR

END
"""
while_test = """
DECLARE 
    x,y,w(10:30)
BEGIN
    WHILE x < 10 DO
        WHILE y > 10 DO
            y:= 10;
        ENDWHILE
        x:=2;
    ENDWHILE
END
"""
mul_test = """
DECLARE 
    x, w(0:13)
BEGIN
    w(0):=10;
    w(4):=11;
    x:=0;
    y:=4;
    x:=w(x)*w(y);
    WRITE x;
END
"""

inc_test = """
DECLARE 
    x, w(0:13)
BEGIN
    x:=123;
    x:=x-124;
    WRITE x;
END
"""
div_test = """
DECLARE 
    x
BEGIN
    y:= 14;
    x:=y/4;
    WRITE x;
    x:=y/x;
    WRITE x;
    x:=y/14;
    WRITE x;
    x:=y/0;
    WRITE x;
    x:=y/15;
    WRITE x;
    x:=0/0;
    WRITE x;
END
"""

mod_test = """
DECLARE 
    x
BEGIN
    y:= 14;
    x:=y%4;
    WRITE x;
    x:=y%x;
    WRITE x;
    x:=y%14;
    WRITE x;
    x:=y%0;
    WRITE x;
    x:=y%15;
    WRITE x;
    x:=0%0;
    WRITE x;
END
"""

result = parser.parse(div_test)
# print(result)

# symbol_table.show()

intermediate = transfer_tree_to_code(result)
intermediate.code_commands.append(codeCommand("EOFCOMMANDS"))
print(intermediate)


