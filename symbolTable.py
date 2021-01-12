import sys

class SymbolTable:
    def __init__(self):
        self.dict = {}
        self.local_index = 0
        self.offset_pointer = 1

    def add(self, name, symbol_type, value=None, begin=None, end=None, initialized=False):
        self.dict[self.local_index] = [name, symbol_type, value, begin, end, self.offset_pointer, initialized]

        if symbol_type == "ARRAY":
            # TODO czy to +1 jest ok?!
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
            print("no such a symbol in symbol table", file=sys.stderr)
            raise Exception

    def get_type_by_index(self, index):
        try:
            return self.dict[index][1]
        except:
            print("no such a symbol in symbol table", file=sys.stderr)
            raise Exception

    def initialize_by_index(self, index):
        self.dict[index][6] = True

    def uninitialize_by_index(self, index):
        self.dict[index][6] = False

    def raise_if_not_initialized_by_index(self, index):
        if self.dict[index][6] == False:
            print(f"{self.dict[index][0]} is not initialized", file=sys.stderr)
            raise Exception


    def show(self):
        print("i: name: type: value: begin: end: offset: initialize:")
        for key, value in self.dict.items():
            print(key, value)
