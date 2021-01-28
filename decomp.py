import ast
from inspect import getsource, getfile
from textwrap import dedent, indent

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
# todo redundant brackets
# todo custom line funtion to input raw glsl
# todo uniforms, atrabutes, varing, constants
# todo alasis for names. so something like "gl_FragColor" can be renamed to "output colour
# done
# todo structs
# todo type testing so type hints can be minimsed
# todo unpacking
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
        return str(node.value)

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

    def Assign(self, node):
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
        # return node.__class__.__name__

    def Starred(self, node): # todo opengl will do it its self in some place but i will need to add custom logic where it cant
        return self.call(node.value)

    def Store(self, node):
        return ""

    def BinOp(self, node):
        if node.op.__class__.__name__ == "Mod":
            return "mod(%s, %s)" % (self.call(node.left), self.call(node.right))
        elif node.op.__class__.__name__ == "Pow":
            return "pow(%s, %s)" % (self.call(node.left), self.call(node.right))
        return "(" + self.call(node.left) + self.call(node.op) + self.call(node.right) + ")"

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
        return "if (%s)\n{\n %s}%s\n" % (name, body, body_else)  # todo test else

    def Expr(self, node):
        return self.re_expression(node)

    def For(self, node):  # todo for each, neg step
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
        elif len(args) == 3:
            start = self.call(args[0])
            end = self.call(args[1])
            step = self.call(args[2])
        else:
            raise Exception("to many arguments to range")

        if not all((float(start).is_integer(), float(end).is_integer(), float(step).is_integer())):
            t = "float"
        body = self.re_body(node.body)
        f = f"for ({t} {name}={start};{name}<{end};{name}+={step}){{\n{body}\n}}"
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

    def BoolOp(self, node):
        op = self.call(node.op)
        # return "this one"
        return "(" + self.call(node.values[0]) + op + self.call(node.values[1]) + ")"
        # return op.join([self.call(i) for i in node.values])

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
        return " != "

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
        # assert 1==2
        return ""

    def Global(self, node):
        self.errors.append("globals are not supported yet")  # todo look in to global geter
        return ""

    def Not(self, node):  # todo test if works
        return "!"

    def AST(self, node):
        self.errors.append("howd you get the bace class :/")
        print("howd you get the bace class :/")
        return ""

    def AsyncFor(self, node):
        self.errors.append("async is not supported in shader")
        return ""

    def AsyncFunctionDef(self, node):
        self.errors.append("async is not supported in shader")
        return ""

    def AsyncWith(self, node):
        self.errors.append("async is not supported in shader")
        return ""

    def AugLoad(self, node):
        self.errors.append("augload is not supported in shader")
        return ""

    def Await(self, node):
        self.errors.append("augload is not supported in shader")
        return ""

    def Bytes(self, node):
        self.errors.append("Bytes is not supported in shader")
        return ""

    def ClassDef(self, node):
        self.errors.append("ClassDef is not supported in shader")
        return ""

    def Del(self, node):
        self.errors.append("Del is not supported in shader")
        return ""

    def Delete(self, node):
        self.errors.append("Delete is not supported in shader")
        return ""

    def AugStore(self, node):
        self.errors.append("AugStore is not supported in shader")
        return ""

    def withitem(self, node):
        self.errors.append("with is not supported in shader")
        return ""

    def unaryop(self, node):  # todo add unaryop
        self.errors.append("unaryop is not supported in shader")
        return ""

    def type_ignore(self, node):
        self.errors.append("type_ignore is not supported in shader")
        return ""

    def stmt(self, node):  # this is a bace type but ima add it for compleatness
        self.errors.append("stmt is not supported in shader")
        return ""

    def slice(self, node):
        self.errors.append("sliceing is not supported in shader, but indexing is")
        return ""

    def operator(self, node):  # bace class
        self.errors.append("operator is not supported in shader")
        return ""

    def Yield(self, node):
        self.errors.append("generators are not supported in shader")
        return ""

    def With(self, node):
        self.errors.append("with is not supported in shader")
        return ""

    def UAdd(self, node):
        return "+"

    def DictComp(self, node):
        self.errors.append("dictionary comprehension is not supported in shader")
        return ""

    def ExceptHandler(self, node):
        self.errors.append("exeptions are not supported in shader")
        return ""

    def FormattedValue(self, node):
        self.errors.append("strings are not supported in shader")
        return ""

    calls = {

        "Not": Not,
        "Global": Global,
        "FunctionDef": FunctionDef,
        "Continue": Continue,
        "Dict": Dict,
        "Compare": Compare,
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
        # not supported
        "AST": AST,
        "AsyncFor": AsyncFor,
        "AsyncFunctionDef": AsyncFunctionDef,
        "AsyncWith": AsyncWith,
        "AugLoad": AugLoad,
        "Await": Await,
        "Bytes": Bytes,
        "ClassDef": ClassDef,
        "Del": Del,
        "Delete": Delete,
        "AugStore": AugStore,
        "withitem": withitem,
        "unaryop": unaryop,
        "type_ignore": type_ignore,
        "stmt": stmt,
        "operator": operator,
        "Yield": Yield,
        "With": With,
        "DictComp": DictComp,
        "ExceptHandler": ExceptHandler,
        "FormattedValue": FormattedValue,
        "Starred": Starred
        # todo add all
        # [<class 'ast.Ellipsis'>, <class '_ast.Expression'>,
        # <class '_ast.ExtSlice'>, <class '_ast.FloorDiv'>,
        # <class '_ast.FunctionType'>, <class '_ast.GeneratorExp'>,
        # <class '_ast.IfExp'>, <class '_ast.Import'>,
        # <class '_ast.ImportFrom'>, <class '_ast.Interactive'>,
        # <class '_ast.Invert'>, <class '_ast.JoinedStr'>,
        # <class '_ast.LShift'>, <class '_ast.Lambda'>,
        # <class '_ast.List'>, <class '_ast.ListComp'>,
        # <class '_ast.MatMult'>, <class '_ast.Mod'>,
        # <class 'ast.NameConstant'>, <class '_ast.NamedExpr'>,
        # <class '_ast.Nonlocal'>, <class 'ast.Num'>,
        # <class '_ast.Param'>, <class '_ast.Pass'>,
        # <class '_ast.Pow'>, <class '_ast.RShift'>,
        # <class '_ast.Raise'>, <class '_ast.Set'>,
        # <class '_ast.SetComp'>, <class '_ast.Slice'>,
        # <class '_ast.Starred'>, <class 'ast.Str'>, done
        # <class '_ast.Suite'>, <class '_ast.Try'>,
        # <class '_ast.Tuple'>, <class '_ast.TypeIgnore'>,
        # <class '_ast.UAdd'>, <class '_ast.YieldFrom'>,
        # <class '_ast.alias'>, <class '_ast.arg'>,
        # <class '_ast.arguments'>, <class '_ast.boolop'>,
        # <class '_ast.cmpop'>, <class '_ast.comprehension'>,
        # <class '_ast.excepthandler'>, <class '_ast.expr'>,
        # <class '_ast.expr_context'>, <class '_ast.keyword'>,
        # <class '_ast.mod'>, <class '_ast.slice'>]
    }


class Recompiler:
    def __init__(self, functions):
        #self.functions = functions
        # formate (const, uniforms, piping vars, functions, attributes)
        self.fragment = None
        self.geometry = None
        self.vertex = None
        self.tess_evaluation = None
        self.tess_control = None

        #self.vertex = ""
        #self.fragment = ""
        self.debug = False
        self.globals = {}
        self.uniforms = []
        self.attributes = []
        self.import_as = []
        self.version = 120

    def comp_func(self, f):
        func = "{_type} {name} ({args}){{\n{body}}}"
        formate = getsource(f)
        formate = dedent(formate)
        formate = dedent("\n".join([i for i in formate.splitlines() if i and i[0] in (" ", "   ")]))
        # print(formate)
        node = ast.parse(formate, type_comments=True)
        op = Ops(self.globals)
        op.atterl_remove.extend(self.import_as)
        out = op.call(node)
        if op.errors:
            print(self._debug_tree(node))
            raise Exception("\n".join(op.errors))
        t = f.__annotations__
        _type = t.get("return", None)
        if _type is None or _type == "None":
            _type = "void"
        else:
            _type = _type.__name__
        out = func.format(_type=_type, name=f.__name__, args=self.args(t), body=out)

        #if self.debug:
            #self._debug_tree(node)
            #print(out)
        return out

    def args(self, a):

        return "".join([a[i].__name__ + " " + i + ", " for i in a if i != "return"])[:-2]

    def _make_fragment(self):
        out = "#version " + str(self.version) + "\n"
        for i in self.fragment[2]:
            print(i, i.inout)
            if i.inout in ("auto", "in", "inout"):  # todo add check for later in out syintax
                out += "varying " + str(i.type.__name__) + " " + i.name + ";\n"  # todo add interpolatin
            elif i.inout in ("out",):
                if self.version < 130: # todo is right?
                    out += "#define " + i.name + " gl_FragColor\n"
        out += "\n".join(["uniform %s %s;" % (i[1].__name__, i[2]) for i in self.fragment[1]])
        out += "\n"
        out += "".join([(self.comp_func(i) + "\n") for i in self.fragment[3]])
        return out

    def _make_vertex(self):
        out = "#version " + str(self.version) + "\n"
        for t, n in self.vertex[4]:  # (type, name)
            out += "attribute " + str(t.__name__) + " " + str(n) + ";\n"
        for i in self.vertex[2]:
            if i.inout in ("auto", "out", "inout"):  # todo add check for later in out syintax
                out += "varying " + str(i.type.__name__) + " " + i.name + ";\n"  # todo add interpolatin
        out += "\n".join(["uniform %s %s;" % (i[1].__name__, i[2]) for i in self.vertex[1]])
        out += "\n"
        out += "".join([(self.comp_func(i) + "\n") for i in self.vertex[3]])
        return out






        out = "#version " + str(self.version) + "\n"
        #out += "precision highp float;\n"
        out += "varying vec2 fragCoord;\n"
        # out += "\n".join(["uniform %s %s;" % (i[1].__name__, i[2]) for i in self.uniforms])
        # print(self.uniforms)
        func = "".join([i.glsl + "\n" for i in self.functions])
        out += func
        #self.vertex = out
        return out

    def _make_geometry(self):
        out = "#version " + str(self.version) + "\n"
        return out

    def _make_tess_control(self):
        out = "#version " + str(self.version) + "\n"
        return out

    def _make_tess_evaluation(self):
        out = "#version " + str(self.version) + "\n"
        return out

    def run(self):

        # do typing
        # piping auto

        out = {}
        if self.fragment:
            out["fragment"] = self._make_fragment()
            if self.debug:
                print(out["fragment"])
        if self.geometry:
            out["geometry"] = self._make_geometry()
            if self.debug:
                print(out["geometry"])
        if self.vertex:
            out["vertex"] = self._make_vertex()
            if self.debug:
                print(out["vertex"])
        if self.tess_evaluation:
            out["tess_evaluation"] = self._make_tess_evaluation()
            if self.debug:
                print(out["tess_evaluation"])
        if self.tess_control:
            out["tess_control"] = self._make_tess_control()
            if self.debug:
                print(out["tess_control"])

        return out

    def _debug_tree(self, node, level=0):

        print('  ' * level + str_node(node))

        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self._debug_tree(item, level=level + 1)
            elif isinstance(value, ast.AST):
                self._debug_tree(value, level=level + 1)
