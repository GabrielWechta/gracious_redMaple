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
    assembler_generator.add_comment(f"# starting generating const {const}")
    assembler_generator.add_asm_one_reg("RESET", reg)
    if const == 0:
        assembler_generator.add_comment(f"# ended generating const {const}")
        return
    assembler_generator.add_asm_one_reg("INC", reg)
    const_bin = "{0:b}".format(const)
    for i in range(1, len(const_bin)):
        if int(const_bin[i]) == 1:
            assembler_generator.add_asm_one_reg("SHL", reg)
            assembler_generator.add_asm_one_reg("INC", reg)
        else:  # is 0
            assembler_generator.add_asm_one_reg("SHL", reg)

    assembler_generator.add_comment(f"# ended generating const {const}")


def save_to_memory(reg_what, reg_where, const):
    offset = symbol_table.get_offset(str(const))

    generate_const_in_reg(reg_what, const)
    generate_const_in_reg(reg_where, offset)

    assembler_generator.add_asm_two_reg("STORE", reg_what, reg_where)


def translate_to_asm():
    for code_command in intermediate.code_commands:
        if code_command.type == "CODE_COPY" and len(code_command.args) == 2:
            left_offset = symbol_table.get_offset_by_index(code_command.args[0])
            symbol = symbol_table.dict[code_command.args[1]]
            if symbol[2] is not None:
                right_value = symbol[2]
                right_reg = "b"
                generate_const_in_reg(right_reg, right_value)

            else:
                right_value = symbol[5]
                right_reg = "b"
                generate_const_in_reg(right_reg, right_value)
                assembler_generator.add_asm_two_reg("LOAD", right_reg, right_reg)

            left_reg = "a"

            generate_const_in_reg(left_reg, left_offset)
            assembler_generator.add_asm_two_reg("STORE", right_reg, left_reg)

        elif code_command.type == "CODE_WRITE":
            index = code_command.args[0]
            offset = symbol_table.get_offset_by_index(index)

            reg = "a"
            generate_const_in_reg(reg, offset)

            assembler_generator.add_asm_one_reg("PUT", reg)



symbol_table.show()
translate_to_asm()
print(assembler_generator)
