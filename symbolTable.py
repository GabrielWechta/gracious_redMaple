import sys

class SymbolTable:
    def __init__(self):
        self.dict = {}
        self.local_index = 0
        self.offset_pointer = 1

    def add(self, name, symbol_type, value=None, begin=None, end=None, offset=None):
        self.dict[self.local_index] = [name, symbol_type, value, begin, end, self.offset_pointer]

        if symbol_type == "ARRAY":
            self.offset_pointer += end - begin
        else:
            self.offset_pointer += 1

        self.local_index += 1

    def get(self, name):
        for key, value in self.dict.items():
            if value[0] == name:
                return key
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


    def show(self):
        print("i: name: type: value: begin: end: offset")
        for key, value in self.dict.items():
            print(key, value)
