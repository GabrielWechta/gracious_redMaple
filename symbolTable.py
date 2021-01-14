""" Symbol table for jftt compiler.
    It's not the best piece of code ever written, mainly because many incorrect
    things were assumed. And on not very good fundaments next functions were build.
"""
import sys


class SymbolTable:
    def __init__(self):
        self.dict = {}  # hash map with symbols
        self.local_index = 0  # for indexing dictionary
        self.offset_pointer = 1  # points to index in memory. Starting from 1, because 0 - offset is reserved for saving operation's result
        self.declaration_sack = []  # list for checking if some not legal vars were used in program

    def add(self, name, symbol_type, value=None, begin=None, end=None, initialized=False):
        self.dict[self.local_index] = [name, symbol_type, value, begin, end, self.offset_pointer, initialized]

        if symbol_type == "ARRAY":
            self.offset_pointer += end - begin + 1
        else:
            self.offset_pointer += 1

        self.local_index += 1

    def get(self, name):
        for key, value in self.dict.items():
            if value[0] == name:
                return key
        else:
            return None

    def get_symbol_by_name(self, name):
        for key, value in self.dict.items():
            if value[0] == name:
                return value
        else:
            return None

    def get_offset_by_index(self, index):
        try:
            return self.dict[index][5]
        except:
            print("No such a symbol in symbol table", file=sys.stderr)
            raise Exception

    def get_type_by_index(self, index):
        try:
            return self.dict[index][1]
        except:
            print("No such a symbol in symbol table", file=sys.stderr)
            raise Exception

    def initialize_by_index(self, index):
        self.dict[index][6] = True

    def uninitialize_by_index(self, index):
        self.dict[index][6] = False

    def raise_if_not_initialized_by_index(self, index):
        """ Main function for checking if variable was initialized before being used on right side of expression. """
        if not self.dict[index][6]:
            print(f"{self.dict[index][0]} is not initialized", file=sys.stderr)
            sys.exit()

    def add_to_declaration_sack(self, name):
        self.declaration_sack.append(name)

    def check_declaration_sack(self):
        """ Main function for checking if all variables used were declared before. """
        for key, value in self.dict.items():
            if value[1] == "VARIABLE" and not value[0].endswith("_FAKE_iter"):
                if value[0] not in self.declaration_sack:
                    print(f"{value[0]} was not declared.", file=sys.stderr)
                    sys.exit()

    def show(self):
        print("i: name: type: value: begin: end: offset: initialize:")
        for key, value in self.dict.items():
            print(key, value)
