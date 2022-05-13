


def is_leaf(data):
    if len(data) == 3:
        for i in data:
            if is_leaf(i):
                leaf = False
                break
        else:
            leaf = True
    else:
        leaf = False

    print(f"{leaf} {data=}")
    return leaf

class Token():
    def __init__(self, data):
        print(f"> {data}")
        self.leaf = None
        self.lval = None
        self.rval = None
        self.comp = None

        if is_leaf(data):
            self.leaf = data
        elif len(data)>=3:
            self.lval = Token(data[0])
            self.comp = data[1]
            self.rval = Token(data[2:])
        elif len(data) == 1:
            self.leaf = data
        else:
            sys.exit(1)

    def __str__(self):
        if self.leaf:
            return self.leaf
        else:
            return f"({self.comp}, {self.lval}, {self.rval})"

print(Token([("a", "=", "b")]))
