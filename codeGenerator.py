from parser import Command


class codeCommand:
    def __init__(self, cc_type: str, args=None, block=None):
        self.type = cc_type
        self.args = args
        self.block = block


class codeProgram:
    def __init__(self):
        self.code_commands = []

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

    def switch_condition_ad_current_command(self):
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


code_program = codeProgram()
label = 1


def transform_tree_r(command: Command):
    if not command:  # to check
        return

    label_exit, label_else, label_start, label_tmp = 0, 0, 0, 0

    if command.type == "COM_ASSGNOP":
        code_program.add_code_command("CODE_COPY")
        transform_tree_r(command.commands[0])
        transform_tree_r(command.commands[1])

    elif command.type == "COM_NUM":
        code_program.add_arg_to_current_command(command.index)

    elif command.type == "COM_PID":
        code_program.add_arg_to_current_command(command.index)

    elif command.type == "COM_ARR":
        code_program.add_arg_to_current_command(command.commands[0])
        code_program.add_arg_to_current_command(command.commands[1])

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
        global label
        label =+ 1
        label_exit = label
        label_tmp = label_exit

        code_program.add_code_command("CODE_UNKNOWN")
        code_program.add_arg_to_current_command(label_tmp)
        code_program.add_arg_to_current_command(-1)
        transform_tree_r(command.commands[0])

        if code_program.bad_inequality():
            code_program.switch_condition_ad_current_command()
            label += 1
            label_exit


def transfer_tree_to_code(program: Command):
    transform_tree_r(program)
