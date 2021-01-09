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
        code_program.add_arg_to_current_command(label_else)
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

        code_program.add_code_command("CODE_ITER_SUB")
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

        code_program.add_code_command("CODE_ITER_SUB")
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

error = """
[ Błąd w linii 6: niewłaściwe użycie zmiennej a ]
DECLARE
  a, b(1:20)
BEGIN
  a := 1;
  a:= b(a);
END
"""

ok = """
DECLARE
	fact, n 
BEGIN
	READ n;
	fact := 1;
	FOR k FROM 1 TO n DO
		fact := fact * k;
	ENDFOR    
    
	WRITE fact;

	[ Liczy n! ]
END
"""

my = """
DECLARE
	fact, r, n, k 
BEGIN
	READ n;
	fact := 1;
    k := 1;
    REPEAT
        r := k % 2;  
        IF r != 0 THEN
		    fact := fact * k;
        ELSE
            fact := k * fact;
        ENDIF
        k := k + 1;
	UNTIL k > n;    
    
	WRITE fact;

	[ Liczy n! ]
END
"""
result = parser.parse(ok)
# print(result)

# symbol_table.show()

intermediate = transfer_tree_to_code(result)
intermediate.code_commands.append(codeCommand("EOFCOMMANDS"))
print(intermediate)


