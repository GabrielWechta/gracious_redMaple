""" This is compiler. Behold. It de facto produces assembly like code for maszyna_wirtualna by PhD Gebala.
    All about this assembly code can be checked out on my repo.
    It uses intermediate code from codGenerator.
    """
import sys

from codeGenerator import symbol_table, intermediate


class assemblerCommand:
    """ Structure for simpler arguments handling. """

    def __init__(self, ac_type, *args):
        self.type = ac_type
        self.args = ""
        for arg in args:
            self.args += arg + " "


class assemblerGenerator:
    def __init__(self):
        self.asm_commands = []

    def __str__(self):
        table = ""
        for command in self.asm_commands:
            try:
                table += command.type + " " + str(command.args) + "\n"
            except AttributeError:  # for comments for debugging
                table += command + "\n"

        return table

    """ FUNCTIONS FOR ADDING DIRECT ASSEM INSTRUCTIONS """

    def add_asm_two_reg(self, ac_type, reg1, reg2):
        ac = assemblerCommand(ac_type, reg1, reg2)
        self.asm_commands.append(ac)

    def add_asm_one_reg(self, ac_type, reg1):
        ac = assemblerCommand(ac_type, reg1)
        self.asm_commands.append(ac)

    def add_asm_reg_jump(self, ac_type, reg1, dest):
        ac = assemblerCommand(ac_type, reg1, str(dest))
        self.asm_commands.append(ac)

    def add_asm_jump(self, ac_type, dest):
        ac = assemblerCommand(ac_type, str(dest))
        self.asm_commands.append(ac)

    """ FUNCTIONS FOR HANDLING JUMPS """

    def add_leap_of_faith_jump(self, ac_type, label_id):
        ac = assemblerCommand(ac_type, "find:" + str(label_id))
        self.asm_commands.append(ac)

    def add_leap_of_faith_jump_reg(self, ac_type, reg1, label_id):
        ac = assemblerCommand(ac_type, reg1, "find:" + str(label_id))
        self.asm_commands.append(ac)

    def add_leap_of_faith_label(self, label_id):
        self.asm_commands.append("here:" + str(label_id))

    def add_comment(self, comment):
        self.asm_commands.append(comment)

    def leap_of_faith_fixer(self):
        """ Both this function's idea and this function's code is a big leap of faith.
            It replaces here:n and find:n - where n is number, to get relative jump distance."""
        labels_addresses = {}
        address = 1
        i = 0
        while i < len(self.asm_commands):
            if not isinstance(self.asm_commands[i], assemblerCommand):
                labels_addresses[self.asm_commands[i].split(":")[1]] = address

                i -= 1
                self.asm_commands.pop(i + 1)
            else:
                address += 1
            i += 1

        for i, command in enumerate(self.asm_commands):
            words = command.args.split(" ")
            if len(words) >= 2 and "find:" in words[-2]:
                words[-2] = str(labels_addresses[words[-2].split(":")[1]] - (i + 1))  # Ladies, gentlemen - python
                self.asm_commands[i].args = " ".join(words)

        # print(labels_addresses)  # for debugging


assembler_generator = assemblerGenerator()


def generate_const_in_reg(reg, const):
    """ In my implementation basic way to get known value in register, it uses smart ways (adding and shifts) to do that. """
    # assembler_generator.add_comment(f"# starting generating const {const}")
    assembler_generator.add_asm_one_reg("RESET", reg)
    if const == 0:
        # assembler_generator.add_comment(f"# ended generating const {const}")
        return
    assembler_generator.add_asm_one_reg("INC", reg)
    const_bin = "{0:b}".format(const)
    for i in range(1, len(const_bin)):
        if int(const_bin[i]) == 1:
            assembler_generator.add_asm_one_reg("SHL", reg)
            assembler_generator.add_asm_one_reg("INC", reg)
        else:  # is 0
            assembler_generator.add_asm_one_reg("SHL", reg)

    # assembler_generator.add_comment(f"# ended generating const {const}")


def save_to_memory(reg_what, reg_where, offset, const):
    generate_const_in_reg(reg_what, const)
    generate_const_in_reg(reg_where, offset)

    assembler_generator.add_asm_two_reg("STORE", reg_what, reg_where)


def smart_copy(left_offset, right_offset):
    # assembler_generator.add_comment("# in smart copy")
    right_reg = "b"
    generate_const_in_reg(right_reg, right_offset)
    assembler_generator.add_asm_two_reg("LOAD", right_reg,
                                        right_reg)  # load to right_reg value from address(right_reg)

    left_reg = "a"

    generate_const_in_reg(left_reg, left_offset)  # generate in left_reg value equal to left_offset
    assembler_generator.add_asm_two_reg("STORE", right_reg,
                                        left_reg)  # saving to left_offset value from right_offset
    # assembler_generator.add_comment("# after smart copsy")


def save_all_consts_to_memory():
    """ This is big and bad idea but makes code simpler. Especially in load_all_kinds_to_regs. """
    for key, value in symbol_table.dict.items():
        if value[2] is not None:
            save_to_memory("a", "b", value[5], value[2])
    # assembler_generator.add_comment("# consts saved to memory")


def load_var_from_id_to_reg(register, symbol_id):
    variable_offset = symbol_table.get_offset_by_index(symbol_id)
    generate_const_in_reg(register, variable_offset)
    assembler_generator.add_asm_two_reg("LOAD", register,
                                        register)  # load to register value from address register


def load_var_from_offset_to_reg(register, offset):
    generate_const_in_reg(register, offset)
    assembler_generator.add_asm_two_reg("LOAD", register, register)


def load_var_from_array_with_variable_to_reg(register, array_id, variable_id):
    """ Registers c and f are used here!!!
        This is used for loading to memory array element that is being get by variable ( tab(x) )"""
    array = symbol_table.dict[array_id]

    load_var_from_id_to_reg(register, variable_id)
    generate_const_in_reg("c", array[3])
    generate_const_in_reg("f", array[5])
    assembler_generator.add_asm_two_reg("SUB", register, "c")
    assembler_generator.add_asm_two_reg("ADD", register, "f")
    assembler_generator.add_asm_two_reg("LOAD", register, register)  # now in register should be wanted array field


def get_offset_from_array(array_id, parameter_id):
    array = symbol_table.dict[array_id]
    parameter = symbol_table.dict[parameter_id]
    if parameter[2] is not None:
        return array[5] + (parameter[2] - array[3])  # returns relative memory position from array


def copy_reg_value_to_reg(reg_to, reg_from):
    """ Register a is used here!!!"""
    assembler_generator.add_asm_one_reg("RESET", "a")  # offset = 0 is save place (I hope)
    assembler_generator.add_asm_two_reg("STORE", reg_from, "a")
    assembler_generator.add_asm_two_reg("LOAD", reg_to, "a")


def load_all_kinds_to_regs(left_reg, right_reg, *arguments):
    """ Loads value to left reg and value to right reg despite type of expression. """
    arguments = arguments[0]  # getting list from tuple
    if len(arguments) == 2:
        if symbol_table.get_type_by_index(arguments[0]) == "CONST" or symbol_table.get_type_by_index(
                arguments[0]) == "VARIABLE":
            symbol_table.raise_if_not_initialized_by_index(arguments[0])
            load_var_from_id_to_reg(left_reg, arguments[0])  # now in left_reg should be value of arguments[0]

        if symbol_table.get_type_by_index(arguments[1]) == "CONST" or symbol_table.get_type_by_index(
                arguments[1]) == "VARIABLE":
            symbol_table.raise_if_not_initialized_by_index(arguments[1])
            load_var_from_id_to_reg(right_reg, arguments[1])

    if len(arguments) == 3:
        if symbol_table.get_type_by_index(arguments[0]) == "CONST" or symbol_table.get_type_by_index(
                arguments[0]) == "VARIABLE":
            symbol_table.raise_if_not_initialized_by_index(arguments[0])
            load_var_from_id_to_reg(left_reg, arguments[0])  # now in left_reg should be value of arguments[0]

        if symbol_table.get_type_by_index(arguments[0]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[1]) == "CONST":
                offset = get_offset_from_array(arguments[0], arguments[1])
                load_var_from_offset_to_reg(left_reg, offset)

            if symbol_table.get_type_by_index(arguments[1]) == "VARIABLE":
                symbol_table.raise_if_not_initialized_by_index(arguments[1])
                load_var_from_array_with_variable_to_reg(left_reg, arguments[0], arguments[1])

        if symbol_table.get_type_by_index(arguments[1]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[2]) == "CONST":
                offset = get_offset_from_array(arguments[1], arguments[2])
                load_var_from_offset_to_reg(right_reg, offset)
                return  # it must be here cause otherwise this case falls inside another big if

            if symbol_table.get_type_by_index(arguments[2]) == "VARIABLE":
                symbol_table.raise_if_not_initialized_by_index(arguments[2])
                load_var_from_array_with_variable_to_reg(right_reg, arguments[1], arguments[2])
                return  # it must be here cause otherwise this case falls inside another big if

        if symbol_table.get_type_by_index(arguments[2]) == "CONST" or symbol_table.get_type_by_index(
                arguments[2]) == "VARIABLE":
            symbol_table.raise_if_not_initialized_by_index(arguments[2])
            load_var_from_id_to_reg(right_reg, arguments[2])  # now in right_reg should be value of arguments[2]

    if len(arguments) == 4:
        if symbol_table.get_type_by_index(arguments[0]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[1]) == "CONST":
                offset = get_offset_from_array(arguments[0], arguments[1])
                load_var_from_offset_to_reg(left_reg, offset)

            if symbol_table.get_type_by_index(arguments[1]) == "VARIABLE":
                symbol_table.raise_if_not_initialized_by_index(arguments[1])
                load_var_from_array_with_variable_to_reg(left_reg, arguments[0], arguments[1])

        if symbol_table.get_type_by_index(arguments[2]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[3]) == "CONST":
                offset = get_offset_from_array(arguments[2], arguments[3])
                load_var_from_offset_to_reg(right_reg, offset)

            if symbol_table.get_type_by_index(arguments[3]) == "VARIABLE":
                symbol_table.raise_if_not_initialized_by_index(arguments[3])
                load_var_from_array_with_variable_to_reg(right_reg, arguments[2], arguments[3])


def load_all_kind_to_one_reg(register, *arguments):
    arguments = arguments[0]  # getting list from tuple
    if len(arguments) == 1:
        if symbol_table.get_type_by_index(arguments[0]) == "CONST" or symbol_table.get_type_by_index(
                arguments[0]) == "VARIABLE" or symbol_table.get_type_by_index(arguments[0]) == "ITERATOR":
            load_var_from_id_to_reg(register, arguments[0])  # now in register should be value of arguments[0]
    if len(arguments) == 2:
        if symbol_table.get_type_by_index(arguments[0]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[1]) == "CONST":
                offset = get_offset_from_array(arguments[0], arguments[1])
                load_var_from_offset_to_reg(register, offset)

            if symbol_table.get_type_by_index(arguments[1]) == "VARIABLE":
                load_var_from_array_with_variable_to_reg(register, arguments[0], arguments[1])


def translate_to_asm():
    for code_command, next_command in zip(intermediate.code_commands, intermediate.code_commands[1:]):
        if next_command.type == "CODE_ADD":
            load_all_kinds_to_regs("a", "b", next_command.args)

            assembler_generator.add_asm_two_reg("ADD", "a", "b")

            assembler_generator.add_asm_one_reg("RESET", "b")
            assembler_generator.add_asm_two_reg("STORE", "a", "b")  # safely saved in 0-offset for copy to pick it up.

        if next_command.type == "CODE_SUB":
            load_all_kinds_to_regs("a", "b", next_command.args)

            assembler_generator.add_asm_two_reg("SUB", "a", "b")

            assembler_generator.add_asm_one_reg("RESET", "b")
            assembler_generator.add_asm_two_reg("STORE", "a", "b")  # safely saved in 0-offset for copy to pick it up.

        if next_command.type == "CODE_MUL":
            load_all_kinds_to_regs("a", "b", next_command.args)

            #### MULTIPLYING ALGORITHM #####
            assembler_generator.add_asm_one_reg("RESET", "c")
            assembler_generator.add_asm_reg_jump("JODD", "b", 2)
            assembler_generator.add_asm_jump("JUMP", 2)
            assembler_generator.add_asm_two_reg("ADD", "c", "a")
            assembler_generator.add_asm_one_reg("SHL", "a")
            assembler_generator.add_asm_one_reg("SHR", "b")
            assembler_generator.add_asm_reg_jump("JZERO", "b", 2)
            assembler_generator.add_asm_jump("JUMP", -6)

            assembler_generator.add_asm_one_reg("RESET", "b")
            assembler_generator.add_asm_two_reg("STORE", "c", "b")  # safely saved in 0-offset for copy to pick it up.

        if next_command.type == "CODE_DIV":
            load_all_kinds_to_regs("d", "c", next_command.args)

            ### DIVISION ALGORITHM ###
            # assembler_generator.add_comment("# div begins ")
            assembler_generator.add_asm_one_reg("RESET", "b")
            assembler_generator.add_asm_reg_jump("JZERO", "c", 30)

            copy_reg_value_to_reg("e", "c")
            copy_reg_value_to_reg("b", "e")

            assembler_generator.add_asm_two_reg("SUB", "b", "d")
            assembler_generator.add_asm_reg_jump("JZERO", "b", 2)
            assembler_generator.add_asm_jump("JUMP", 3)
            assembler_generator.add_asm_two_reg("ADD", "e", "e")
            assembler_generator.add_asm_jump("JUMP", -7)

            assembler_generator.add_asm_one_reg("RESET", "b")

            copy_reg_value_to_reg("f", "e")

            assembler_generator.add_asm_two_reg("SUB", "f", "d")
            assembler_generator.add_asm_reg_jump("JZERO", "f", 4)
            assembler_generator.add_asm_two_reg("ADD", "b", "b")
            assembler_generator.add_asm_one_reg("SHR", "e")
            assembler_generator.add_asm_jump("JUMP", 5)
            assembler_generator.add_asm_two_reg("ADD", "b", "b")
            assembler_generator.add_asm_one_reg("INC", "b")
            assembler_generator.add_asm_two_reg("SUB", "d", "e")
            assembler_generator.add_asm_one_reg("SHR", "e")

            copy_reg_value_to_reg("f", "c")

            assembler_generator.add_asm_two_reg("SUB", "f", "e")
            assembler_generator.add_asm_reg_jump("JZERO", "f", -16)

            # assembler_generator.add_comment("# div ends")

            assembler_generator.add_asm_one_reg("RESET", "a")
            assembler_generator.add_asm_two_reg("STORE", "b", "a")  # safely saved in 0-offset for copy to pick it up.

        if next_command.type == "CODE_MOD":
            load_all_kinds_to_regs("d", "c", next_command.args)

            ### DIVISION ALGORITHM ###
            # assembler_generator.add_comment("# modulo begins ")
            assembler_generator.add_asm_reg_jump("JZERO", "c", 32)
            assembler_generator.add_asm_reg_jump("JZERO", "c", 30)

            copy_reg_value_to_reg("e", "c")
            copy_reg_value_to_reg("b", "e")

            assembler_generator.add_asm_two_reg("SUB", "b", "d")
            assembler_generator.add_asm_reg_jump("JZERO", "b", 2)
            assembler_generator.add_asm_jump("JUMP", 3)
            assembler_generator.add_asm_two_reg("ADD", "e", "e")
            assembler_generator.add_asm_jump("JUMP", -7)

            assembler_generator.add_asm_one_reg("RESET", "b")

            copy_reg_value_to_reg("f", "e")

            assembler_generator.add_asm_two_reg("SUB", "f", "d")
            assembler_generator.add_asm_reg_jump("JZERO", "f", 4)
            assembler_generator.add_asm_two_reg("ADD", "b", "b")
            assembler_generator.add_asm_one_reg("SHR", "e")
            assembler_generator.add_asm_jump("JUMP", 5)
            assembler_generator.add_asm_two_reg("ADD", "b", "b")
            assembler_generator.add_asm_one_reg("INC", "b")
            assembler_generator.add_asm_two_reg("SUB", "d", "e")
            assembler_generator.add_asm_one_reg("SHR", "e")

            copy_reg_value_to_reg("f", "c")

            assembler_generator.add_asm_two_reg("SUB", "f", "e")
            assembler_generator.add_asm_reg_jump("JZERO", "f", -16)
            assembler_generator.add_asm_jump("JUMP", 2)
            assembler_generator.add_asm_one_reg("RESET", "d")
            copy_reg_value_to_reg("b", "d")

            # assembler_generator.add_comment("# modulo ends")

            assembler_generator.add_asm_one_reg("RESET", "a")
            assembler_generator.add_asm_two_reg("STORE", "d", "a")  # safely saved in 0-offset for copy to pick it up.

        if code_command.type == "CODE_JEQ":
            load_all_kinds_to_regs("b", "c", code_command.args[2:])
            copy_reg_value_to_reg("d", "b")
            # assembler_generator.add_comment("# EQ start her")

            assembler_generator.add_asm_two_reg("SUB", "b", "c")
            assembler_generator.add_asm_reg_jump("JZERO", "b", 2)
            assembler_generator.add_asm_jump("JUMP", 3)
            assembler_generator.add_asm_two_reg("SUB", "c", "d")
            assembler_generator.add_leap_of_faith_jump_reg("JZERO", "c", code_command.args[0])
            # assembler_generator.add_comment("# EQ ends here")

        if code_command.type == "CODE_JNEQ":
            load_all_kinds_to_regs("b", "c", code_command.args[2:])
            copy_reg_value_to_reg("d", "b")
            # assembler_generator.add_comment("# EQ start her")

            assembler_generator.add_asm_two_reg("SUB", "b", "c")
            assembler_generator.add_asm_reg_jump("JZERO", "b", 2)
            assembler_generator.add_asm_jump("JUMP", 3)
            assembler_generator.add_asm_two_reg("SUB", "c", "d")
            assembler_generator.add_asm_reg_jump("JZERO", "c", 2)
            assembler_generator.add_leap_of_faith_jump("JUMP", code_command.args[0])
            # assembler_generator.add_comment("# EQ ends here")

        if code_command.type == "CODE_JLT":
            load_all_kinds_to_regs("b", "c", code_command.args[2:])
            copy_reg_value_to_reg("d", "b")

            assembler_generator.add_asm_two_reg("SUB", "b", "c")
            assembler_generator.add_asm_reg_jump("JZERO", "b", 2)
            assembler_generator.add_asm_jump("JUMP", 4)
            assembler_generator.add_asm_one_reg("INC", "d")
            assembler_generator.add_asm_two_reg("SUB", "d", "c")
            assembler_generator.add_leap_of_faith_jump_reg("JZERO", "d", code_command.args[0])

        if code_command.type == "CODE_JGT":
            load_all_kinds_to_regs("b", "c", code_command.args[2:])
            copy_reg_value_to_reg("d", "c")

            assembler_generator.add_asm_two_reg("SUB", "c", "b")
            assembler_generator.add_asm_reg_jump("JZERO", "c", 2)
            assembler_generator.add_asm_jump("JUMP", 4)
            assembler_generator.add_asm_one_reg("INC", "d")
            assembler_generator.add_asm_two_reg("SUB", "d", "b")
            assembler_generator.add_leap_of_faith_jump_reg("JZERO", "d", code_command.args[0])

        if code_command.type == "CODE_JLEQ":
            load_all_kinds_to_regs("a", "b", code_command.args[2:])

            assembler_generator.add_asm_two_reg("SUB", "a", "b")
            assembler_generator.add_leap_of_faith_jump_reg("JZERO", "a", code_command.args[0])

        if code_command.type == "CODE_JGEQ":
            load_all_kinds_to_regs("a", "b", code_command.args[2:])

            assembler_generator.add_asm_two_reg("SUB", "b", "a")
            assembler_generator.add_leap_of_faith_jump_reg("JZERO", "b", code_command.args[0])

        if code_command.type == "CODE_JZERO":
            load_all_kind_to_one_reg("a", code_command.args[2:])

            assembler_generator.add_leap_of_faith_jump_reg("JZERO", "a", code_command.args[0])

        if code_command.type == "CODE_LABEL":
            assembler_generator.add_leap_of_faith_label(code_command.args[0])

        if code_command.type == "CODE_JUMP":
            assembler_generator.add_leap_of_faith_jump("JUMP", code_command.args[0])

        if code_command.type == "CODE_COPY":
            """ The most pathological moment in the intermediate code. All cases that can happen 
                are separately handled """
            copy_arguments = code_command.args
            if len(copy_arguments) == 1:  # x:= [operation]
                if symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE":
                    left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                    smart_copy(left_offset, 0)

                    symbol_table.initialize_by_index(copy_arguments[0])

            elif len(copy_arguments) == 2 and symbol_table.get_type_by_index(
                    copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[1]) == "CONST":  # tab(2) := [operation]:
                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                smart_copy(left_offset, 0)

            elif len(copy_arguments) == 2 and symbol_table.get_type_by_index(
                    copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[1]) == "VARIABLE":  # tab(x) := [operation]
                array = symbol_table.dict[copy_arguments[0]]
                load_var_from_id_to_reg("c", copy_arguments[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                right_reg = "b"

                generate_const_in_reg(right_reg, 0)
                assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg)
                assembler_generator.add_asm_two_reg("STORE", right_reg, "c")


            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST":
                # x := 2
                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                symbol = symbol_table.dict[code_command.args[1]]
                right_value = symbol[2]
                right_reg = "b"
                generate_const_in_reg(right_reg, right_value)
                left_reg = "a"
                generate_const_in_reg(left_reg, left_offset)
                assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)

                symbol_table.initialize_by_index(copy_arguments[0])

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE":
                # x := y

                symbol_table.raise_if_not_initialized_by_index(copy_arguments[1])

                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                right_offset = symbol_table.dict[code_command.args[1]][5]

                smart_copy(left_offset, right_offset)

                symbol_table.initialize_by_index(copy_arguments[0])

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[2]) == "CONST":
                # x := p(3)
                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                right_offset = get_offset_from_array(copy_arguments[1], copy_arguments[2])

                smart_copy(left_offset, right_offset)

                symbol_table.initialize_by_index(copy_arguments[0])


            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[2]) == "VARIABLE":
                # x := p(y)

                symbol_table.raise_if_not_initialized_by_index(copy_arguments[2])

                left_offset = symbol_table.get_offset_by_index(code_command.args[0])

                # variable = symbol_table.dict[copy_arguments[2]]
                array = symbol_table.dict[copy_arguments[1]]

                load_var_from_id_to_reg("c", copy_arguments[2])  # value of variable

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address
                assembler_generator.add_asm_two_reg("LOAD", "c", "c")

                left_reg = "a"
                generate_const_in_reg(left_reg, left_offset)

                assembler_generator.add_asm_two_reg("STORE", "c", left_reg)

                symbol_table.initialize_by_index(copy_arguments[0])

            #### arrays ####
            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST" and symbol_table.get_type_by_index(copy_arguments[2]) == "CONST":
                # p(3) := 4
                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                right_value = symbol_table.dict[copy_arguments[2]][2]
                right_reg = "b"
                generate_const_in_reg(right_reg, right_value)
                left_reg = "a"
                generate_const_in_reg(left_reg, left_offset)
                assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST" and symbol_table.get_type_by_index(copy_arguments[2]) == "VARIABLE":
                # p(3) := x
                symbol_table.raise_if_not_initialized_by_index(copy_arguments[2])

                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                left_reg = "b"
                generate_const_in_reg(left_reg, left_offset)

                right_var_offset = symbol_table.get_offset_by_index(copy_arguments[2])
                right_reg = "a"
                generate_const_in_reg(right_reg, right_var_offset)
                assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg)

                assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[3]) == "CONST":
                # p(3) := tab(4)
                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                right_offset = get_offset_from_array(copy_arguments[2], copy_arguments[3])

                smart_copy(left_offset, right_offset)

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[3]) == "VARIABLE":
                # p(3) := tab(x)

                symbol_table.raise_if_not_initialized_by_index(copy_arguments[3])

                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])

                array = symbol_table.dict[copy_arguments[2]]

                load_var_from_id_to_reg("c", copy_arguments[3])  # value of variable

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address
                assembler_generator.add_asm_two_reg("LOAD", "c", "c")

                left_reg = "a"
                generate_const_in_reg(left_reg, left_offset)

                assembler_generator.add_asm_two_reg("STORE", "c", left_reg)

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE" and symbol_table.get_type_by_index(copy_arguments[2]) == "CONST":
                # p(x) := 3

                symbol_table.raise_if_not_initialized_by_index(copy_arguments[1])

                array = symbol_table.dict[copy_arguments[0]]
                load_var_from_id_to_reg("c", copy_arguments[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                right_value = symbol_table.dict[copy_arguments[2]][2]
                right_reg = "b"
                generate_const_in_reg(right_reg, right_value)

                assembler_generator.add_asm_two_reg("STORE", right_reg, "c")

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "VARIABLE":
                # p(x) := y
                symbol_table.raise_if_not_initialized_by_index(copy_arguments[1])
                symbol_table.raise_if_not_initialized_by_index(copy_arguments[2])

                array = symbol_table.dict[copy_arguments[0]]
                load_var_from_id_to_reg("c", copy_arguments[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                right_reg = "b"
                load_var_from_id_to_reg(right_reg, copy_arguments[2])

                assembler_generator.add_asm_two_reg("STORE", right_reg, "c")

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[3]) == "CONST":
                # p(x) = p(2)
                symbol_table.raise_if_not_initialized_by_index(copy_arguments[1])

                array = symbol_table.dict[copy_arguments[0]]
                load_var_from_id_to_reg("c", copy_arguments[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                right_offset = get_offset_from_array(copy_arguments[2], copy_arguments[3])
                right_reg = "b"
                generate_const_in_reg(right_reg, right_offset)

                assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg)
                assembler_generator.add_asm_two_reg("STORE", right_reg, "c")

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[3]) == "VARIABLE":
                # p(x) = p(y)
                symbol_table.raise_if_not_initialized_by_index(copy_arguments[1])

                symbol_table.raise_if_not_initialized_by_index(copy_arguments[3])

                array = symbol_table.dict[copy_arguments[0]]
                load_var_from_id_to_reg("c", copy_arguments[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                array2 = symbol_table.dict[copy_arguments[2]]
                load_var_from_id_to_reg("d", copy_arguments[3])

                generate_const_in_reg("a", array2[3])  # array begin
                generate_const_in_reg("b", array2[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "d", "a")  # now in d is value of variable - array2 begin
                assembler_generator.add_asm_two_reg("ADD", "d", "b")  # now in d is relative address

                assembler_generator.add_asm_two_reg("LOAD", "d", "d")
                assembler_generator.add_asm_two_reg("STORE", "d", "c")

        if code_command.type == "CODE_INC":
            # assembler_generator.add_comment("#BEGINIG")
            load_all_kind_to_one_reg("a", code_command.args)  # loading value to register
            assembler_generator.add_asm_one_reg("INC", "a")  # incrementing

            """ Assuming that only variables (not arrays) can be incremented. """
            offset = symbol_table.get_offset_by_index(code_command.args[0])
            generate_const_in_reg("b", offset)  # generating address in register
            assembler_generator.add_asm_two_reg("STORE", "a", "b")  # storing
            # assembler_generator.add_comment("#ENDING")

        if code_command.type == "CODE_DEC":
            load_all_kind_to_one_reg("a", code_command.args)  # loading value to register
            assembler_generator.add_asm_one_reg("DEC", "a")  # incrementing

            """ Assuming that only variables (not arrays) can be incremented. """
            offset = symbol_table.get_offset_by_index(code_command.args[0])
            generate_const_in_reg("b", offset)  # generating address in register
            assembler_generator.add_asm_two_reg("STORE", "a", "b")  # storing

        if code_command.type == "CODE_ITER_SUB":
            load_all_kinds_to_regs("e", "f", code_command.args)

            assembler_generator.add_asm_two_reg("SUB", "e", "f")
            offset = symbol_table.get_offset_by_index(code_command.args[0])
            generate_const_in_reg("d", offset)
            assembler_generator.add_asm_two_reg("STORE", "e", "d")

            """To forget iterator after loop"""
        if (code_command.type == "CODE_INC" or code_command.type == "CODE_DEC") and next_command.type == "CODE_DEC":
            symbol_table.uninitialize_by_index(code_command.args[0])
            symbol_table.uninitialize_by_index(next_command.args[0])

        elif code_command.type == "CODE_WRITE":
            if symbol_table.get_type_by_index(code_command.args[0]) == "VARIABLE":
                symbol_table.raise_if_not_initialized_by_index(code_command.args[0])

                index = code_command.args[0]
                offset = symbol_table.get_offset_by_index(index)

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("PUT", reg)

            elif symbol_table.get_type_by_index(code_command.args[0]) == "CONST":
                offset = symbol_table.get_offset_by_index(code_command.args[0])

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("PUT", reg)

                # """ FOR DEBUGGING """
                # reg = "a"
                # generate_const_in_reg(reg, symbol_table.dict[code_command.args[0]][2])
                # assembler_generator.add_asm_one_reg("PUT", reg)

            elif symbol_table.get_type_by_index(code_command.args[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    code_command.args[1]) == "CONST":
                offset = get_offset_from_array(code_command.args[0], code_command.args[1])

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("PUT", reg)

            if symbol_table.get_type_by_index(code_command.args[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    code_command.args[1]) == "VARIABLE":
                array = symbol_table.dict[code_command.args[0]]
                load_var_from_id_to_reg("c", code_command.args[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                assembler_generator.add_asm_one_reg("PUT", "c")

        elif code_command.type == "CODE_READ":
            if symbol_table.get_type_by_index(code_command.args[0]) == "VARIABLE":
                symbol_table.initialize_by_index(code_command.args[0])

                index = code_command.args[0]
                offset = symbol_table.get_offset_by_index(index)

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("GET", reg)

            elif symbol_table.get_type_by_index(code_command.args[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    code_command.args[1]) == "CONST":
                offset = get_offset_from_array(code_command.args[0], code_command.args[1])

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("GET", reg)

            if symbol_table.get_type_by_index(code_command.args[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    code_command.args[1]) == "VARIABLE":
                symbol_table.raise_if_not_initialized_by_index(code_command.args[1])

                array = symbol_table.dict[code_command.args[0]]
                load_var_from_id_to_reg("c", code_command.args[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                assembler_generator.add_asm_one_reg("GET", "c")

        if next_command.type == "EOFCOMMANDS":  # always must be at the end
            assembler_generator.asm_commands.append(assemblerCommand("HALT"))


""" TRANSLATING TO ASM """
# commented parts will stay for debugging

# symbol_table.show()
# print(symbol_table.declaration_sack)

symbol_table.check_declaration_sack()  # stops program if some other variables then declared were used in program

save_all_consts_to_memory()  # saving all approached consts to memory, in there dedicated offsets
translate_to_asm()  # this is happening here
assembler_generator.leap_of_faith_fixer()  # fixing heres and finds added by JUMPs

# symbol_table.show()

file = open(sys.argv[2], 'w')  # saving to file
file.write(str(assembler_generator))
