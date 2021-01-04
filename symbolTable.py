class SymbolTable:
    def __init__(self):
        self.dict = {}
        self.local_index = 0

    def add(self, name, symbol_type, value=None, begin=None, end=None, offset=None):
        self.dict[self.local_index] = [name, symbol_type, value, begin, end, offset]
        self.local_index += 1

    def get(self, name):
        for key, value in self.dict.items():
            if value[0] == name:
                return key
        else:
            return None

    def show(self):
        for key, value in self.dict.items():
            print(key, value)
