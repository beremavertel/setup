DEBUG = False

def is_leaf(data, rec=0):
    if DEBUG:
        print(f"Testing {data}")
    if not isinstance(data, (list, tuple)):
        leaf = True
    elif rec <= 1:
        leaf = True
        for x in data:
            if len(data) > 1 and isinstance(x, (list, tuple)):
                leaf = False
                break
            leaf = leaf and is_leaf(x, rec+1)
    else:
        leaf = False

    if DEBUG:
        print(f"{leaf} {data=}")
    return leaf


class Token():
    def __init__(self, data, external=True):
        if DEBUG:
            print(f"> {data}")
        self.leaf = None
        self.lval = None
        self.rval = None
        self.comp = None
        self.external = external

        if is_leaf(data):
            self.leaf = data
        elif len(data)>=3:
            self.lval = Token(data[0], external=False)
            self.comp = data[1]
            rval = data[2:]
            if len(rval) == 1:
                rval = rval[0]
            self.rval = Token(rval, external=False)
        elif len(data) == 1:
            self.leaf = data
        else:
            sys.exit(1)

    def __str__(self):
        if self.leaf:
            return str(self.leaf)
        else:
            s = f"('{self.comp}', {self.lval}, {self.rval})"
            if self.external:
                s = f"[{s[1:-1]}]"
            return s


dep = 0

def flatten(s):
    return "["  + ", ".join(repr(part) for part in _tflatten(Token(s))) + "]"

def _tflatten(t):
    global dep
    if DEBUG:
        print(" "*dep, t)
    dep += 1
    try:
        if t.leaf:
            return [t.leaf]
        else:
            x = _tflatten(t.lval)
            y = _tflatten(t.rval)
            return [t.comp] + x + y
    except AttributeError:
        return t
    finally:
        dep -= 1


def token(s):
    return str(Token(s))


def test(s, expected=True):
    global DEBUG
    retval = eval(s)
    if not (isinstance(expected, list) and retval in expected or retval == expected):
        DEBUG = True
        print("-"*100)
        print(f"Running '{s}'")
        print(f"Got      {retval}")
        print(f"Expected {expected}")
        eval(s)
        print("-"*100)
        print("\n")
        DEBUG = False


if __name__ == "__main__":
    test("is_leaf(('a', 'b', 'c'))")
    test("is_leaf([('a', 'b', 'c')])")
    test("is_leaf([('a', 'b', 'c'), 'and', ('x',)])", False)
    test("is_leaf([('a', 'b', 'c'), 'and', 'x'])", False)
    test("is_leaf([('a', 'b', 'c'), 'and'])", False)
    test("token(('a','b','c'))", "('a', 'b', 'c')")
    test("token([('a','b','c')])", "[('a', 'b', 'c')]")
    test("token([('a','b','c'), 'and', ('d', 'e', 'f')])", "['and', ('a', 'b', 'c'), ('d', 'e', 'f')]")
    test("token([('a','b','c'), 'and', ('d', 'e', 'f'), 'or', ('g', 'e', 'h')])", "['and', ('a', 'b', 'c'), ('or', ('d', 'e', 'f'), ('g', 'e', 'h'))]")

    test("token([(('a','b','c'), 'or', ('q', 'e', 'w')), 'and', ('d', 'e', 'f'), 'or', ('g', 'e', 'h')])",
         "['and', ('or', ('a', 'b', 'c'), ('q', 'e', 'w')), ('or', ('d', 'e', 'f'), ('g', 'e', 'h'))]")
    test("flatten([(('a','b','c'), 'or', ('q', 'e', 'w')), 'and', ('d', 'e', 'f'), 'or', ('g', 'e', 'h')])",
         "['and', 'or', ('a', 'b', 'c'), ('q', 'e', 'w'), 'or', ('d', 'e', 'f'), ('g', 'e', 'h')]")
    test("flatten([('a','b','c'), 'and', ('d', 'e', 'f'), 'or', ('g', 'e', 'h')])",
         ["['or', 'and', ('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'e', 'h')]",
          "['and', ('a', 'b', 'c'), 'or', ('d', 'e', 'f'), ('g', 'e', 'h')]"])
