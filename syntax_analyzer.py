from lark import Lark, Transformer, v_args, Token

grammar = r"""
start: statement+

statement: assignment
         | if_statement
         | while_statement
         | loop_statement
         | loop_while_statement
         | print_statement

assignment: NAME "=" expr

if_statement: "if" condition block "end"

while_statement: "while" condition block "end"

loop_statement: "loop" NAME "in" expr block "end"           -> for_loop

loop_while_statement: LOOP_WHILE condition block "end"      -> loop_while


print_statement: "print" "(" expr ")"


block: statement+

condition: expr comparator expr

comparator: ">" | "<" | "==" | "!="

?expr: expr "+" term      -> add
     | expr "-" term      -> sub
     | term

?term: term "*" factor    -> mul
     | term "/" factor    -> div
     | factor

?factor: NAME
       | STRING
       | NUMBER
       | boolean
       | list
       | "(" expr ")"

list: "[" [expr ("," expr)*] "]"    -> list_expr

boolean: "true"      -> true
       | "false"     -> false

LOOP_WHILE: "loop_while"

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /\d+/
STRING: /"[^"]*"/

%import common.WS
%ignore WS
"""

parser = Lark(grammar, parser='lalr', start='start')

@v_args(inline=True)
class ExecuteTree(Transformer):
    def __init__(self):
        self.vars = {}

    # statements
    def assignment(self, name, value):
        self.vars[name] = value
        return None

    def print_statement(self, string):
        print(string[1:-1])  # remove quotes
        
    def print_statement(self, value):
        print(value)

    def if_statement(self, condition_result, block):
        if condition_result:
            for stmt in block:
                self._exec(stmt)

    def while_statement(self, condition_result, block):
        while condition_result():
            for stmt in block:
                self._exec(stmt)
            condition_result = self._make_condition_func(block[0].children[0])

    def for_loop(self, varname, iterable, block):
        if not isinstance(iterable, list):
            iterable = [iterable]
        for val in iterable:
            self.vars[varname] = val
            for stmt in block:
                self._exec(stmt)

    def loop_while(self, condition_result, block):
        while condition_result():
            for stmt in block:
                self._exec(stmt)
        
            condition_result = self._make_condition_func(block[0].children[0])

    def block(self, *statements):
        return list(statements)

    # Conditions
    def condition(self, left, comp, right):
        left_val = left if not callable(left) else left()
        right_val = right if not callable(right) else right()

        if comp == '>':
            return left_val > right_val
        elif comp == '<':
            return left_val < right_val
        elif comp == '==':
            return left_val == right_val
        elif comp == '!=':
            return left_val != right_val
        else:
            raise Exception(f"Unknown comparator: {comp}")

    def comparator(self, token):
        return str(token)

    # Expressions
    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a // b  # integer division

    def list_expr(self, *elements):
        return list(elements)

    def true(self): return True
    def false(self): return False

    def NUMBER(self, tok): return int(tok)
    def NAME(self, tok):
        name = str(tok)
        if name in self.vars:
            return self.vars[name]
        else:
            raise Exception(f"Undefined variable: {name}")

    # helper method 
    def _exec(self, tree):
        self.transform(tree)

    # override transform to process statements
    def transform(self, tree):
        # Dispatch to methods for rules or tokens
        if tree.data == "start" or tree.data == "block":
            for child in tree.children:
                self._exec(child)
            return None
        else:
            method = getattr(self, tree.data, None)
            if method:
                return method(*tree.children)
            else:
                # Terminal or token
                if hasattr(tree, 'value'):
                    return tree.value
                else:
                    return tree

def analyze(code):
    try:
        tree = parser.parse(code)
        print(tree.pretty())
        executor = ExecuteTree()
        executor.transform(tree)
    except Exception as e:
        print("Syntax error or runtime error:", e)

if __name__ == "__main__":
    sample_code = """
    x = 0
    loop_while x < 5
        print("Value of x:")
        print(x)
        x = x + 1
    end
    """

    analyze(sample_code)

def lexical_analyze(code):
    try:
        tokens = list(parser.lex(code))
        output = "\n".join(f"{token.type}: {token.value}" for token in tokens)
        return output
    except Exception as e:
        return f"Lexical Error: {e}"