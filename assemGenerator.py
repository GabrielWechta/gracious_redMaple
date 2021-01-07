from codeGenerator import symbol_table, intermediate


class assemblerCommand:
    def __init__(self, ac_type, *args):
        self.type = ac_type
        self.args = ""
        for arg in args:
            self.args += arg + " "


class assemblerGenerator:
    def __init__(self):
        self.asm_commands = []

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

    def add_comment(self, comment):
        self.asm_commands.append(comment)

    def __str__(self):
        table = ""
        for command in self.asm_commands:
            try:
                table += command.type + " " + str(command.args) + "\n"
            except AttributeError:  # for comments for debugging
                table += command + "\n"

        return table


assembler_generator = assemblerGenerator()


def generate_const_in_reg(reg, const):
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
                                        right_reg)  # wczytanie do right_reg wartosci spod adresu right_reg

    left_reg = "a"

    generate_const_in_reg(left_reg, left_offset)  # wygenerowanie w left_reg adresu poadanego jako left_offest
    assembler_generator.add_asm_two_reg("STORE", right_reg,
                                        left_reg)  # zapisanie pod adres left_offset wartosci z right_offset
    # assembler_generator.add_comment("# after smart copsy")


def save_all_consts_to_memory():  # to dla lepszego korzystania z load_all_kinds_to_regs
    for key, value in symbol_table.dict.items():
        if value[2] is not None:
            save_to_memory("a", "b", value[5], value[2])
    # assembler_generator.add_comment("# consts saved to memory")


def load_var_from_id_to_reg(register, symbol_id):
    variable_offset = symbol_table.get_offset_by_index(symbol_id)
    generate_const_in_reg(register, variable_offset)
    assembler_generator.add_asm_two_reg("LOAD", register,
                                        register)  # wczytanie do register wartosci spod adresu register


def load_var_from_offset_to_reg(register, offset):
    generate_const_in_reg(register, offset)
    assembler_generator.add_asm_two_reg("LOAD", register, register)


def load_var_from_array_with_variable_to_reg(register, array_id, variable_id):
    """registers c and d are used here!!!"""
    array = symbol_table.dict[array_id]

    load_var_from_id_to_reg(register, variable_id)
    generate_const_in_reg("c", array[3])
    generate_const_in_reg("d", array[5])
    assembler_generator.add_asm_two_reg("SUB", register, "c")
    assembler_generator.add_asm_two_reg("ADD", register, "d")
    assembler_generator.add_asm_two_reg("LOAD", register, register)  # now in register should be wanted array field


def get_offset_from_array(array_id, parameter_id):
    array = symbol_table.dict[array_id]
    parameter = symbol_table.dict[parameter_id]
    if parameter[2] is not None:
        return array[5] + (parameter[2] - array[3])  # returns relative memory position from array
    else:
        pass  # TODO


def load_all_kinds_to_regs(left_reg, right_reg, *arguments):
    """Loads value to left reg and value to right reg despite type of expression"""
    arguments = arguments[0]  # getting list from tuple
    if len(arguments) == 2:
        if symbol_table.get_type_by_index(arguments[0]) == "CONST" or symbol_table.get_type_by_index(
                arguments[0]) == "VARIABLE":
            load_var_from_id_to_reg(left_reg, arguments[0])  # now in left_reg should be value of arguments[0]

        if symbol_table.get_type_by_index(arguments[1]) == "CONST" or symbol_table.get_type_by_index(
                arguments[1]) == "VARIABLE":
            load_var_from_id_to_reg(right_reg, arguments[1])

    if len(arguments) == 3:
        if symbol_table.get_type_by_index(arguments[0]) == "CONST" or symbol_table.get_type_by_index(
                arguments[0]) == "VARIABLE":
            load_var_from_id_to_reg(left_reg, arguments[0])  # now in left_reg should be value of arguments[0]

        if symbol_table.get_type_by_index(arguments[0]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[1]) == "CONST":
                offset = get_offset_from_array(arguments[0], arguments[1])
                load_var_from_offset_to_reg(left_reg, offset)

            if symbol_table.get_type_by_index(arguments[1]) == "VARIABLE":
                load_var_from_array_with_variable_to_reg(left_reg, arguments[0], arguments[1])

        if symbol_table.get_type_by_index(arguments[1]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[2]) == "CONST":
                offset = get_offset_from_array(arguments[1], arguments[2])
                load_var_from_offset_to_reg(right_reg, offset)

            if symbol_table.get_type_by_index(arguments[2]) == "VARIABLE":
                load_var_from_array_with_variable_to_reg(right_reg, arguments[1], arguments[2])

        if symbol_table.get_type_by_index(arguments[2]) == "CONST" or symbol_table.get_type_by_index(
                arguments[2]) == "VARIABLE":
            load_var_from_id_to_reg(right_reg, arguments[2])  # now in right_reg should be value of arguments[2]

    if len(arguments) == 4:
        if symbol_table.get_type_by_index(arguments[0]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[1]) == "CONST":
                offset = get_offset_from_array(arguments[0], arguments[1])
                load_var_from_offset_to_reg(left_reg, offset)

            if symbol_table.get_type_by_index(arguments[1]) == "VARIABLE":
                load_var_from_array_with_variable_to_reg(left_reg, arguments[0], arguments[1])

        if symbol_table.get_type_by_index(arguments[2]) == "ARRAY":
            if symbol_table.get_type_by_index(arguments[3]) == "CONST":
                offset = get_offset_from_array(arguments[2], arguments[3])
                load_var_from_offset_to_reg(right_reg, offset)

            if symbol_table.get_type_by_index(arguments[3]) == "VARIABLE":
                load_var_from_array_with_variable_to_reg(right_reg, arguments[2], arguments[3])


def load_all_kind_to_one_reg(register, *arguments):
    arguments = arguments[0]  # getting list from tuple
    if len(arguments) == 1:
        if symbol_table.get_type_by_index(arguments[0]) == "CONST" or symbol_table.get_type_by_index(
                arguments[0]) == "VARIABLE":
            load_var_from_id_to_reg(register, arguments[0])  # now in left_reg should be value of arguments[0]
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

            #### for testing #####
            assembler_generator.add_asm_two_reg("ADD", "a", "b")

            assembler_generator.add_asm_one_reg("RESET", "b")
            assembler_generator.add_asm_two_reg("STORE", "a", "b")  # safely saved in 0-offset for copy to pick it up.
            """ for printing offset 0 do:"""
            # assembler_generator.add_asm_one_reg("PUT", "b")

        if next_command.type == "CODE_SUB":
            load_all_kinds_to_regs("a", "b", next_command.args)

            #### for testing #####
            assembler_generator.add_asm_two_reg("SUB", "a", "b")

            assembler_generator.add_asm_one_reg("RESET", "b")
            assembler_generator.add_asm_two_reg("STORE", "a", "b")  # safely saved in 0-offset for copy to pick it up.
            """ for printing offset 0 do:"""
            # assembler_generator.add_asm_one_reg("PUT", "b")

        if next_command.type == "CODE_MUL":
            load_all_kinds_to_regs("a", "b", next_command.args)
            # TODO optimize chyba będzie lepiej jak a>b albo na odwrót
            # TODO lewy i prawa to trudne rzeczy
            #### MULTIPLYING #####
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
            """ for printing offset 0 do:"""
            # assembler_generator.add_asm_one_reg("PUT", "b")

        if code_command.type == "CODE_COPY":
            copy_arguments = code_command.args
            if len(copy_arguments) == 1:  # x:= [operacja]
                if symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE":
                    left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                    smart_copy(left_offset, 0)

            elif len(copy_arguments) == 2 and symbol_table.get_type_by_index(
                    copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[1]) == "CONST":  # tab(2) := [operacja]:
                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                smart_copy(left_offset, 0)
            elif len(copy_arguments) == 2 and symbol_table.get_type_by_index(
                    copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[1]) == "VARIABLE":  # tab(x) := [operacja]
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

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE":
                # x := y
                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                right_offset = symbol_table.dict[code_command.args[1]][5]

                smart_copy(left_offset, right_offset)

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[2]) == "CONST":
                # x := p(3)
                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                right_offset = get_offset_from_array(copy_arguments[1], copy_arguments[2])

                smart_copy(left_offset, right_offset)

            elif symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[2]) == "VARIABLE":
                # x := p(y)
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
                # p(x) := x
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

        # TODO READ and WRITE should be change to print const and not place in memory, but do it after everything works
        elif code_command.type == "CODE_WRITE":
            if symbol_table.get_type_by_index(code_command.args[0]) == "VARIABLE":
                index = code_command.args[0]
                offset = symbol_table.get_offset_by_index(index)

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("PUT", reg)

            elif symbol_table.get_type_by_index(code_command.args[0]) == "CONST":
                offset = code_command.args[0]

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("PUT", reg)

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
                index = code_command.args[0]
                offset = symbol_table.get_offset_by_index(index)

                reg = "a"
                generate_const_in_reg(reg, offset)
                assembler_generator.add_asm_one_reg("GET", reg)

            elif symbol_table.get_type_by_index(code_command.args[0]) == "CONST":
                offset = code_command.args[0]

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
                array = symbol_table.dict[code_command.args[0]]
                load_var_from_id_to_reg("c", code_command.args[1])

                generate_const_in_reg("a", array[3])  # array begin
                generate_const_in_reg("b", array[5])  # array offset
                assembler_generator.add_asm_two_reg("SUB", "c", "a")  # now in c is value of variable - array begin
                assembler_generator.add_asm_two_reg("ADD", "c", "b")  # now in c is relative address

                assembler_generator.add_asm_one_reg("GET", "c")

        if next_command.type == "EOFCOMMANDS":  # always must be at the end
            assembler_generator.asm_commands.append(assemblerCommand("HALT"))


symbol_table.show()
save_all_consts_to_memory()
translate_to_asm()
print(assembler_generator)

with open('/home/gabriel/Desktop/first.txt', 'w') as f:
    print(assembler_generator, file=f)
