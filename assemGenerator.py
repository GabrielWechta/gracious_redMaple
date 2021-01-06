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
        ac = assemblerCommand(ac_type, reg1, dest)
        self.asm_commands.append(ac)

    def add_asm_jump(self, ac_type, dest):
        ac = assemblerCommand(ac_type, dest)
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


def save_to_memory(reg_what, reg_where, const):
    offset = symbol_table.get_offset(str(const))

    generate_const_in_reg(reg_what, const)
    generate_const_in_reg(reg_where, offset)

    assembler_generator.add_asm_two_reg("STORE", reg_what, reg_where)


def smart_copy(left_offset, right_offset):
    right_reg = "b"
    generate_const_in_reg(right_reg, right_offset)
    assembler_generator.add_asm_two_reg("LOAD", right_reg,
                                        right_reg)  # wczytanie do right_reg wartosci spod adresu right_reg

    left_reg = "a"

    generate_const_in_reg(left_reg, left_offset)  # wygenerowanie w left_reg adresu poadanego jako left_offest
    assembler_generator.add_asm_two_reg("STORE", right_reg,
                                        left_reg)  # zapisanie pod adres left_offset wartosci z right_offset


def load_var_from_id_to_reg(register, variable_id):
    variable_offset = symbol_table.get_offset_by_index(variable_id)
    generate_const_in_reg(register, variable_offset)
    assembler_generator.add_asm_two_reg("LOAD", register,
                                        register)  # wczytanie do register wartosci spod adresu register


def get_offset_from_array(array_id, parameter_id):
    array = symbol_table.dict[array_id]
    parameter = symbol_table.dict[parameter_id]
    if parameter[2] is not None:
        return array[5] + (parameter[2] - array[3])  # returns relative memory position from array
    else:
        pass  # TODO


# TODO iterator...
def translate_to_asm():
    for code_command, next_command in zip(intermediate.code_commands, intermediate.code_commands[1:]):
        if code_command.type == "CODE_COPY":
            copy_arguments = code_command.args
            if len(copy_arguments) == 1:  # x:= [operacja]
                pass
            if len(copy_arguments) == 2 and symbol_table.get_type_by_index(
                    copy_arguments[0]) == "ARRAY":  # tab(x lub 2) := [operacja]
                pass

            if symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
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

            if symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE":
                # x := y
                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                right_offset = symbol_table.dict[code_command.args[1]][5]

                smart_copy(left_offset, right_offset)

            if symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[2]) == "CONST":
                # x := p(3)
                left_offset = symbol_table.get_offset_by_index(code_command.args[0])
                right_offset = get_offset_from_array(copy_arguments[1], copy_arguments[2])

                smart_copy(left_offset, right_offset)

            if symbol_table.get_type_by_index(copy_arguments[0]) == "VARIABLE" and symbol_table.get_type_by_index(
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
            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST" and symbol_table.get_type_by_index(copy_arguments[2]) == "CONST":
                # p(3) := 4
                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                right_value = symbol_table.dict[copy_arguments[2]][2]
                right_reg = "b"
                generate_const_in_reg(right_reg, right_value)
                left_reg = "a"
                generate_const_in_reg(left_reg, left_offset)
                assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
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

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "CONST" and symbol_table.get_type_by_index(
                    copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(copy_arguments[3]) == "CONST":
                # p(3) := tab(4)
                left_offset = get_offset_from_array(copy_arguments[0], copy_arguments[1])
                right_offset = get_offset_from_array(copy_arguments[2], copy_arguments[3])

                smart_copy(left_offset, right_offset)

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
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

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
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

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
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

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[3]) == "CONST" :
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

            if symbol_table.get_type_by_index(copy_arguments[0]) == "ARRAY" and symbol_table.get_type_by_index(
                    copy_arguments[1]) == "VARIABLE" and symbol_table.get_type_by_index(
                copy_arguments[2]) == "ARRAY" and symbol_table.get_type_by_index(
                copy_arguments[3]) == "VARIABLE" :
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

        # if len(code_command.args) == 2:
        #     """ assigment type x:=2 or x:=y """
        #     left_offset = symbol_table.get_offset_by_index(code_command.args[0])
        #     symbol = symbol_table.dict[code_command.args[1]]
        #     if symbol[2] is not None:
        #         right_value = symbol[2]
        #         right_reg = "b"
        #         generate_const_in_reg(right_reg, right_value)
        #
        #     else:
        #         right_value = symbol[5]
        #         right_reg = "b"
        #         generate_const_in_reg(right_reg, right_value)
        #         assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg)
        #
        #     left_reg = "a"
        #
        #     generate_const_in_reg(left_reg, left_offset)
        #     assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)
        #
        # elif len(code_command.args) == 3:
        #     """ assigment type x:=tab(2) or x:=tab(y) """
        #     left_offset = symbol_table.get_offset_by_index(code_command.args[0])
        #     array_line = symbol_table.dict[code_command.args[1]] # this is array
        #     element = symbol_table.dict[code_command.args[2]] # this is her element
        #     if element[1] == "CONST": # case when it's const value.
        #         if array_line[3] <= element[2] <= array_line[4]:
        #             right_value = array_line[5] + (element[2] - array_line[3])
        #             right_reg = "b"
        #             generate_const_in_reg(right_reg, right_value)
        #             assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg)
        #         else:
        #             raise IndexError
        #
        #         left_reg = "a"
        #
        #         generate_const_in_reg(left_reg, left_offset)
        #         assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)
        #
        #     elif element[1] == "VARIABLE":
        #         right_value = element[5]
        #         right_reg = "b"
        #         generate_const_in_reg(right_reg, right_value)
        #         assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg) # now in right_reg i have value of y
        #         # TODO check if value of variable is inside tab
        #         # element
        # elif len(code_command.args) == 1:
        #     check = next_command
        #     print(check)

        elif code_command.type == "CODE_WRITE":
            if symbol_table.get_type_by_index(code_command.args[0]) == "VARIABLE":
                index = code_command.args[0]
                offset = symbol_table.get_offset_by_index(index)
            elif symbol_table.get_type_by_index(code_command.args[0]) == "CONST":
                offset = code_command.args[0]
            elif symbol_table.get_type_by_index(code_command.args[0]) == "ARRAY":
                offset = get_offset_from_array(code_command.args[0], code_command.args[1])

            reg = "a"
            generate_const_in_reg(reg, offset)
            assembler_generator.add_asm_one_reg("PUT", reg)

        elif code_command.type == "CODE_READ":
            if symbol_table.get_type_by_index(code_command.args[0]) == "VARIABLE":
                index = code_command.args[0]
                offset = symbol_table.get_offset_by_index(index)
            elif symbol_table.get_type_by_index(code_command.args[0]) == "CONST":
                offset = code_command.args[0]
            elif symbol_table.get_type_by_index(code_command.args[0]) == "ARRAY":
                offset = get_offset_from_array(code_command.args[0], code_command.args[1])

            reg = "a"
            generate_const_in_reg(reg, offset)
            assembler_generator.add_asm_one_reg("GET", reg)

        if next_command.type == "EOFCOMMANDS":  # always must be at the end
            assembler_generator.asm_commands.append(assemblerCommand("HALT"))


symbol_table.show()
translate_to_asm()
print(assembler_generator)
