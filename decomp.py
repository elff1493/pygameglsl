import dis
import ast
from inspect import getsource, getfile
from textwrap import dedent, indent
import GLSL_helpers as _gl


# print(_gl, "ob")
class vec2: ...


v = """
#version 120

attribute vec2 vPosition;
attribute vec2 vTexcoords;
varying vec2 fragCoord;

void main()
{
    gl_Position = vec4(vPosition.x, vPosition.y, 0.0, 1.0);
    fragCoord = vTexcoords;
}
"""
f = """
#version 120

varying vec2 fTexcoords;
uniform sampler2D textureObj;
uniform vec3 iResolution;
uniform float iTime;


#define param 0.63


%s

"""


class TypeType:
    def __init__(self):
        self.name = ""
        self.scope = "main"
        self.same_as = []
        self.values_set = []
        self.posible_type = [bool, int, float]


class TypeFinder:
    def __init__(self):
        self.a = []


def get_code(code):
    c = code.__code__
    with open(getfile(code)) as file:
        t = sum(c.co_lnotab[1::2])
        line = file.readlines()[c.co_firstlineno:t + c.co_firstlineno]
    return "".join([i[4:] for i in line])


def str_node(node):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
    else:
        return repr(node)


# todo add all ops
# todo fix brackets (1+2)*3 is the same as 1+(2*3)
# todo custom line funtion to input raw glsl
# todo uniforms, atrabutes, varing, constants
# todo alasis for names. so something like "gl_FragColor" can be renamed to "output colour
# todo funtions
# todo structs
# todo type testing so type hints can be minimsed

class Ops:
    def __init__(self, _globals):
        self.globals = _globals
        self.atterl_remove = ["self"]
        self.errors = []

    def Attribute(self, node):
        name = self.call(node.value)
        if name in self.atterl_remove:
            return node.attr
        return name + "." + node.attr

    def AnnAssign(self, node):
        v = ""
        if node.value:
            v = " = %s" % self.call(node.value)
        return "%s %s %s" % (self.call(node.annotation), self.call(node.target), v)

    def AugAssign(self, node):
        return "%s %s= %s" % (self.call(node.target), self.call(node.op), self.re_expression(node.value))

    def Constant(self, node):
        return str(node.value)  # todo test if sting or invaild

    def Div(self, node):
        return "/"

    def Add(self, node):
        return "+"

    def Mult(self, node):
        return "*"

    def unpack(self, node):
        out = ""
        for i in node.args:
            out += self.call(i) + ", "
        return out[:-2]

    def Call(self, node):
        return "%s(%s)" % (self.call(node.func), self.unpack(node))

    def Assign(self, node):  # todo unpacking
        if len(node.targets) > 1:
            raise Exception("unpacking not supported yet")
        return "%s = %s" % (self.call(node.targets[0]), self.call(node.value))

    def Name(self, node):
        return node.id

    def re_expression(self, node):
        out = ""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        out += self.call(item)
            elif isinstance(value, ast.AST):
                out += self.call(value)
        if not out:
            return self.call(node)

        return out

    def re_body(self, node):
        if isinstance(node, ast.AST):
            body = node.body
        else:
            body = node
        out = ""
        for n in body:
            out += self.call(n) + ";\n"
        return indent(out, "  ")

    def call(self, node):
        if node.__class__.__name__ in Ops.calls:
            return Ops.calls[node.__class__.__name__](self, node)
        raise TypeError(str(node.__class__.__name__))
        #return node.__class__.__name__

    def Store(self, node):
        return ""

    def BinOp(self, node):
        if node.op.__class__.__name__ == "Mod":
            return "mod(%s, %s)" % (self.call(node.left), self.call(node.right))
        elif node.op.__class__.__name__ == "Pow":
            return "pow(%s, %s)" % (self.call(node.left), self.call(node.right))
        return self.call(node.left) \
               + self.call(node.op) \
               + self.call(node.right)

    def Load(self, node):
        return ""

    def Module(self, node):
        return self.re_body(node)

    def Sub(self, node):
        return "-"

    def Return(self, node):
        return "return " + self.call(node.value)

    def While(self, node):
        return "while (%s)\n {\n%s}" % (self.re_expression(node.test), self.re_body(node))

    def If(self, node):
        out = ""
        name = self.call(node.test)
        body = self.re_body(node).replace("\n", "\n ")
        body_else = ""
        if node.orelse:
            body_else = " else {\n%s} " % self.re_body(node.orelse)
        return "if (%s)\n{\n %s}%s" % (name, body, body_else)  # todo add else

    def Expr(self, node):
        return self.re_expression(node)

    def For(self, node):  # todo float step, for each, neg step
        t = "int"
        name = self.call(node.target)
        args = node.iter.args
        start = 0
        step = 1
        end = self.call(args[0])
        if len(args) == 1:
            end = self.call(args[0])
        elif len(args) == 2:
            start = self.call(args[0])
            end = self.call(args[1])
        else:
            pass

        body = self.re_body(node.body)
        f = f"for ({t} {name}={start};i<{end};{name}+={step}){{\n{body}\n}}"
        return f

    def UnaryOp(self, node):
        return self.call(node.op) + self.call(node.operand)

    def USub(self, node):
        return "-"

    def Lt(self, node):
        return "<"

    def Gt(self, node):
        return ">"

    def Break(self, node):
        return "break"

    def Or(self, node):
        return " || "  # logical or

    def And(self, node):
        return " && "

    def BoolOp(self, node): # todo test
        op = self.call(node.op)
        #return "this one"
        return self.call(node.values[0]) + op + self.call(node.values[1])
        return op.join([self.call(i) for i in node.values])

    def Subscript(self, node):
        return self.call(node.value) + "[" + self.call(node.slice) + "]"

    def Index(self, node):
        return self.call(node.value)

    def Assert(self, node):
        self.errors.append("assert not supported")
        return ""

    def BitAnd(self, node):
        return " & "

    def BitOr(self, node):
        return " | "

    def BitXor(self, node):
        return " ^ "

    def Compare(self, node):
        return self.call(node.left) \
               + ("".join([self.call(op) + " " + self.call(comp) for op, comp in zip(node.ops, node.comparators)]))

    def Eq(self, node):
        return " == "

    def NotEq(self, node):
        return " != "

    def LtE(self, node):
        return " <= "

    def GtE(self, node):
        return " >= "

    def Is(self, node):
        self.errors.append("is is not supported, defulted to ==")
        return " == "

    def IsNot(self, node):
        self.errors.append("is not is not supported, defulted to !=")
        return " == "

    def In(self, node):
        self.errors.append("In is not supported")
        return ""

    def In(self, node):
        self.errors.append("In is not supported")
        return ""

    def NotIn(self, node):
        self.errors.append("not in is not supported")
        return ""

    def Dict(self, node):
        self.errors.append("dictionaries are not supported")
        return ""

    def Continue(self, node):
        return "continue"

    def FunctionDef(self, node):
        self.errors.append("nested functions are not supported")
        return ""

    def Global(self, node):
        self.errors.append("globals are not supported yet")  # todo look in to global geter
        return ""

    def Not(self, node):  # todo test if works
        return "!"

    calls = {

        "Not": Not,
        "Global": Global,
        "FunctionDef": FunctionDef,
        "Continue":Continue,
        "Dict": Dict,
        "Compare":Compare,
        "BitXor": BitXor,
        "BitOr": BitOr,
        "BitAnd": BitAnd,
        "Assert": Assert,
        "Index": Index,
        "Subscript": Subscript,
        "And": And,
        "BoolOp": BoolOp,
        "Or": Or,
        "Break": Break,

        "UnaryOp": UnaryOp,
        "USub": USub,
        "Constant": Constant,
        "Add": Add,
        "Assign": Assign,
        "Load": Load,
        "Store": Store,
        "BinOp": BinOp,
        "Name": Name,
        "Module": Module,
        "If": If,
        "Call": Call,
        "Mult": Mult,
        "While": While,
        "Expr": Expr,
        "AugAssign": AugAssign,
        "AnnAssign": AnnAssign,
        "Div": Div,
        "For": For,
        "Sub": Sub,
        "Attribute": Attribute,
        "Return": Return,


        "Eq": Eq,
        "NotEq": NotEq,
        "Lt": Lt,
        "LtE": LtE,
        "Gt": Gt,
        "GtE": GtE,
        "Is": Is,
        "IsNot": IsNot,
        "In": In,
        "NotIn": NotIn,
    }

owo2 = "owo\n\n\n\n\nowo"
def unindent(s):
    return s


class Recompiler:
    def __init__(self, functions):
        self.functions = functions
        self.vertex = ""
        self.fragment = ""
        self.debug = False
        self.globals = {}
        self.uniforms = []
        self.import_as = ""
        # self.code = get_code(data.__code__) # todo replace with inspects get sorce
        # self.ast = ast.parse(self.code, type_comments=True)

    def comp_func(self, f):
        func = "{_type} {name} ({args}){{\n{body}}}"
        formate = getsource(f)
        formate = dedent(formate)
        formate = dedent("\n".join([i for i in formate.splitlines() if i and i[0] in (" ", "   ")]))
        # print(formate)
        node = ast.parse(formate, type_comments=True)
        op = Ops(self.globals)
        op.atterl_remove.append(self.import_as)
        out = op.call(node)
        if op.errors:
            raise Exception("\n".join(op.errors))
        t = f.__annotations__
        _type = t.get("return", None)
        if _type == None:
            _type = "void"
        else:
            _type = _type.__name__
        out = func.format(_type=_type, name=f.__name__, args=self.args(t), body=out)
        #print(globals(), "g", globals()["owo2"])
        if self.debug:
            self._debug_tree(node)
            print(out)
        return out

    def args(self, a):

        return "".join([a[i].__name__ + " " + i + ", " for i in a if i != "return"])[:-2]

    def run(self):

        # do uniforms, atrabutes, varing
        # do typing
        # compile all functions
        # make vertex and fragment
        for i in self.functions:
            i.glsl = self.comp_func(i.callback)
        self.vertex = v
        out = "#version 120\n"
        out += "precision highp float;\n"
        out += "varying vec2 fragCoord;\n"
        out += "\n".join(["uniform %s %s;" % (i[1].__name__, i[2]) for i in self.uniforms])
        #print(self.uniforms)
        func = "".join([i.glsl + "\n" for i in self.functions])
        out += func
        self.fragment = out
        #print(out)

    def _debug_tree(self, node, level=0):

        print('  ' * level + str_node(node))

        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self._debug_tree(item, level=level + 1)
            elif isinstance(value, ast.AST):
                self._debug_tree(value, level=level + 1)
