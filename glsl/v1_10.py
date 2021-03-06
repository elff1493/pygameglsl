from typing import TypeVar, Union, Generic, SupportsInt, SupportsFloat
from collections import Iterable


class vec2(Iterable):
    y = 0
    def __init__(self, x: float, y: float = "fills"):

        self.x: float = x

        #self.y: float = y

    def __truediv__(self, other): ...

    def __abs__(self): ...

    def __add__(self, other): ...

    def __rmul__(self, other) -> "vec2": ...


#vec2.__annotations__["y"] = float
#vec2.__dict__["y"] = 0.0

class vec3(Iterable):
    def __init__(self, x: float, y: float, z: float): ...


class vec4(Iterable):
    def __init__(self, r: float, g: float = "fills", b: float = "fills", a: float = "fills"): ...

    def __rmul__(self, other) -> "vec4": ...
    def __mul__(self, other) -> "vec4": ...


class bvec2(Iterable):
    def __init__(self, x: bool, y: bool): ...


class bvec3(Iterable):
    def __init__(self, x: bool, y: bool, z: bool): ...


class bvec4(Iterable):
    def __init__(self, r: bool, g: bool, b: bool, a: bool): ...


class ivec2(Iterable):
    def __init__(self, x: int, y: int): ...


class ivec3(Iterable):
    def __init__(self, x: int, y: int, z: int): ...


class ivec4(Iterable):
    def __init__(self, r: int, g: int, b: int, a: int): ...


class mat2: ...


class mat3: ...


class mat4: ...


class sampler1D: ...


class sampler2D: ...


class sampler3D: ...


class sampler1DShadow: ...


class sampler2DShadow: ...


class samplerCube: ...


class void: ...


class struct:
    def __init__(self, **kwargs): # todo
        #setattr(self, 4)
        for i in self.__class__.__annotations__:
            print(i)



mat = Union[mat2, mat3, mat4]
vec = Union[vec2, vec3, vec4]
ivec = Union[ivec2, ivec3, ivec4]
bvec = Union[bvec2, bvec3, bvec4]

GenType = TypeVar("GenType", int, float, vec, ivec)  # mat to? # todo
all_types = Union[GenType, vec, bvec, mat, sampler1D, sampler2D]  # todo add all


# trig
def radians(degrees: GenType) -> GenType: ...


def degrees(radians: GenType) -> GenType: ...


def sin(angle: GenType) -> GenType: ...


def cos(angle: GenType) -> GenType: ...


def tan(angle: GenType) -> GenType: ...


def asin(x: GenType) -> GenType: ...


def acos(x: GenType) -> GenType: ...


def atan(y: GenType, x: GenType) -> GenType: ...


def atan(y_over_x: GenType) -> GenType: ...


# exponets
def pow(x: GenType, y: GenType) -> GenType: ...


def exp(x: GenType) -> GenType: ...


def log(x: GenType) -> GenType: ...


def exp2(x: GenType) -> GenType: ...


def log2(x: GenType) -> GenType: ...


def sqrt(x: GenType) -> GenType: ...


def inversesqrt(x: GenType) -> GenType: ...


#  Common Functions
def abs(x: GenType) -> GenType: ...


def sign(x: GenType) -> GenType: ...


def floor(x: GenType) -> GenType: ...


def ceil(x: GenType) -> GenType: ...


def fract(x: GenType) -> GenType: ...


def mod(x: GenType, y: float) -> GenType: ...


def mod(x: GenType, y: GenType) -> GenType: ...


def min(x: GenType, y: GenType) -> GenType: ...


def min(x: GenType, y: float) -> GenType: ...


def max(x: GenType, y: GenType) -> GenType: ...


def max(x: GenType, y: float) -> GenType: ...


def clamp(x: GenType, minVal: GenType, maxVal: GenType) -> GenType: ...


def clamp(x: GenType, minVal: GenType, maxVal: float) -> GenType: ...


def mix(x: GenType, y: GenType, a: GenType) -> GenType: ...


def mix(x: GenType, y: GenType, a: float) -> GenType: ...


def step(edge: GenType, x: GenType) -> GenType: ...


def step(edge: float, x: GenType) -> GenType: ...


def smoothstep(edge0: GenType, edge1: GenType, x: GenType) -> GenType: ...


def smoothstep(edge0: float, edge1: float, x: GenType) -> GenType: ...


# Geometric Functions

def length(x: GenType) -> float: ...


def distance(p0: GenType, p1: GenType) -> float: ...


def dot(x: GenType, y: GenType) -> float: ...


def cross(x: GenType, y: vec3) -> vec3: ...


def normalize(x: GenType) -> GenType: ...


def ftransform() -> vec4: ...


def faceforward(N: GenType, I: GenType, Nref: GenType) -> GenType: ...


def reflect(I: GenType, N: GenType) -> GenType: ...


def refract(I: GenType, N: GenType, eta: float) -> GenType: ...


#
def matrixCompMult(x: mat, y: mat) -> mat: ...


# Vector Relational Functions
# todo fix overloadin by adding fivec, ibvec, fibvec types
def lessThan(x: vec, y: vec) -> bvec: ...


def lessThan(x: ivec, y: ivec) -> bvec: ...


def lessThanEqual(x: vec, y: vec) -> bvec: ...  # map pairs


def lessThanEqual(x: ivec, y: ivec) -> bvec: ...


def greaterThan(x: vec, y: vec) -> bvec: ...


def greaterThan(x: ivec, y: ivec) -> bvec: ...


def greaterThanEqual(x: vec, y: vec) -> bvec: ...


def greaterThanEqual(x: ivec, y: ivec) -> bvec: ...


def equal(x: vec, y: vec) -> bvec: ...


def equal(x: ivec, y: ivec) -> bvec: ...


def equal(x: bvec, y: bvec) -> bvec: ...


def notEqual(x: vec, y: vec) -> bvec: ...


def notEqual(x: ivec, y: ivec) -> bvec: ...


def notEqual(x: bvec, y: bvec) -> bvec: ...


def any(x: bvec) -> bool: ...


def all(x: bvec) -> bool: ...


def Not(x: bvec) -> bvec: ...  # todo must add case for Not/not


# texture accec
def texture1D(sampler: sampler1D, coord: float, bias: float = float) -> vec4: ...


def texture1DProj(sampler: sampler1D, coord: vec2, bias: float = float) -> vec4: ...


def texture1DProj(sampler: sampler1D, coord: vec4, bias: float = float) -> vec4: ...


def texture1DLod(sampler: sampler1D, coord: float, lod: float) -> vec4: ...


def texture1DProjLod(sampler: sampler1D, coord: vec2, lod: float) -> vec4: ...


def texture1DProjLod(sampler: sampler1D, coord: vec4, lod: float) -> vec4: ...


def texture2D(sampler: sampler2D, coord: vec2, bias: float = float) -> vec4: ...


def texture2DProj(sampler: sampler2D, coord: vec3, bias: float = float) -> vec4: ...


def texture2DProj(sampler: sampler2D, coord: vec4, bias: float = float) -> vec4: ...


def texture2DLod(sampler: sampler2D, coord: vec2, lod: float) -> vec4: ...


def texture2DProjLod(sampler: sampler2D, coord: vec3, lod: float) -> vec4: ...


def texture2DProjLod(sampler: sampler2D, coord: vec4, lod: float) -> vec4: ...


def texture3D(sampler: sampler3D, coord: vec3, bias: float = float) -> vec4: ...


def texture3DProj(sampler: sampler3D, coord: vec4, bias: float = float) -> vec4: ...


def texture3DLod(sampler: sampler3D, coord: vec3, lod: float) -> vec4: ...


def texture3DProjLod(sampler: sampler3D, coord: vec4, lod: float) -> vec4: ...


def textureCube(sampler: samplerCube, coord: vec3, bias: float = float) -> vec4: ...


def textureCubeLod(sampler: samplerCube, coord: float, lod: float) -> vec4: ...


def shadow1D(sampler: sampler1DShadow, coord: vec3, bias: float = float) -> vec4: ...


def shadow2D(sampler: sampler2DShadow, coord: vec3, bias: float = float) -> vec4: ...


def shadow1DProj(sampler: sampler1DShadow, coord: vec4, bias: float = float) -> vec4: ...


def shadow2DProj(sampler: sampler2DShadow, coord: vec4, bias: float = float) -> vec4: ...


def shadow1DLod(sampler: sampler1DShadow, coord: vec3, lod: float) -> vec4: ...


def shadow2DLod(sampler: sampler2DShadow, coord: vec3, lod: float) -> vec4: ...


def shadow1DProjLod(sampler: sampler1DShadow, coord: vec4, lod: float) -> vec4: ...


def shadow2DProjLod(sampler: sampler2DShadow, coord: vec4, lod: float) -> vec4: ...


def dFdx(p: GenType) -> GenType: ...


def dFdy(p: GenType) -> GenType: ...


def fwidth(p: GenType) -> GenType: ...


def noise1(x: GenType) -> float: ...


def noise2(x: GenType) -> vec2: ...


def noise3(x: GenType) -> vec3: ...


def noise4(x: GenType) -> vec4: ...


# frags biltins
gl_FragCoord: vec2
gl_FrontFacing: bool
gl_FragColor: vec4
# vec4 gl_FragData[gl_MaxDrawBuffers]
gl_FragDepth: float

#  Vertex Attributes
gl_Color: vec4
gl_SecondaryColor: vec4
gl_Normal: vec4
gl_Vertex: vec4
gl_MultiTexCoord0: vec4
gl_MultiTexCoord1: vec4
gl_MultiTexCoord2: vec4
gl_MultiTexCoord3: vec4
gl_MultiTexCoord4: vec4
gl_MultiTexCoord5: vec4
gl_MultiTexCoord6: vec4
gl_MultiTexCoord7: vec4
gl_FogCoord: float

# const (may be diffrent)
gl_MaxLights: int = 8
gl_MaxClipPlanes: int = 6
gl_MaxTextureUnits: int = 2
gl_MaxTextureCoords: int = 2
gl_MaxVertexAttribs: int = 16

gl_MaxVertexUniformComponents: int = 512
gl_MaxVaryingFloats: int = 32
gl_MaxVertexTextureImageUnits: int = 0
gl_MaxCombinedTextureImageUnits: int = 2
gl_MaxTextureImageUnits: int = 2
gl_MaxFragmentUniformComponents: int = 64
gl_MaxDrawBuffers: int = 1

#  uniforms biltin

gl_ModelViewMatrix: mat4
gl_ProjectionMatrix: mat4
gl_ModelViewProjectionMatrix: mat4
# gl_TextureMatrix: mat4[gl_MaxTextureCoords]

gl_NormalMatrix: mat3
gl_ModelViewMatrixInverse: mat4
gl_ProjectionMatrixInverse: mat4
gl_ModelViewProjectionMatrixInverse: mat4
# gl_TextureMatrixInverse: mat4[gl_MaxTextureCoords]
gl_ModelViewMatrixTranspose: mat4
gl_ProjectionMatrixTranspose: mat4
gl_ModelViewProjectionMatrixTranspose: mat4
# gl_TextureMatrixTranspose: mat4[gl_MaxTextureCoords]
gl_ModelViewMatrixInverseTranspose: mat4
gl_ProjectionMatrixInverseTranspose: mat4
gl_ModelViewProjectionMatrixInverseTranspose: mat4
# uniform mat4 gl_TextureMatrixInverseTranspose[gl_MaxTextureCoords]

"""
// Depth range in window coordinates, p. 33
//
struct gl_DepthRangeParameters {
float near; // n
float far; // f
float diff; // f - n
};
uniform gl_DepthRangeParameters gl_DepthRange;
//
// Clip planes p. 42.
//
uniform vec4 gl_ClipPlane[gl_MaxClipPlanes];
//
// Point Size, p. 66, 67.
//
struct gl_PointParameters {
float size;
float sizeMin;
float sizeMax;
float fadeThresholdSize;
float distanceConstantAttenuation;
float distanceLinearAttenuation;
float distanceQuadraticAttenuation;
};
uniform gl_PointParameters gl_Point;
//
// Material State p. 50, 55.
//
struct gl_MaterialParameters {
vec4 emission; // Ecm
vec4 ambient; // Acm
vec4 diffuse; // Dcm
vec4 specular; // Scm
float shininess; // Srm
};
uniform gl_MaterialParameters gl_FrontMaterial;
uniform gl_MaterialParameters gl_BackMaterial;
//
// Light State p 50, 53, 55.
//
struct gl_LightSourceParameters {
vec4 ambient; // Acli
vec4 diffuse; // Dcli
vec4 specular; // Scli
vec4 position; // Ppli
vec4 halfVector; // Derived: Hi
vec3 spotDirection; // Sdli
float spotExponent; // Srli
float spotCutoff; // Crli
// (range: [0.0,90.0], 180.0)
float spotCosCutoff; // Derived: cos(Crli)
// (range: [1.0,0.0],-1.0)
float constantAttenuation; // K0
float linearAttenuation; // K1
float quadraticAttenuation;// K2
};
uniform gl_LightSourceParameters gl_LightSource[gl_MaxLights];
struct gl_LightModelParameters {
vec4 ambient; // Acs
};
uniform gl_LightModelParameters gl_LightModel;
//
// Derived state from products of light and material.
//
struct gl_LightModelProducts {
vec4 sceneColor; // Derived. Ecm + Acm * Acs
};
uniform gl_LightModelProducts gl_FrontLightModelProduct;
uniform gl_LightModelProducts gl_BackLightModelProduct;
struct gl_LightProducts {
vec4 ambient; // Acm * Acli
vec4 diffuse; // Dcm * Dcli
vec4 specular; // Scm * Scli
};
uniform gl_LightProducts gl_FrontLightProduct[gl_MaxLights];
uniform gl_LightProducts gl_BackLightProduct[gl_MaxLights];
//
// Texture Environment and Generation, p. 152, p. 40-42.
//
uniform vec4 gl_TextureEnvColor[gl_MaxTextureImageUnits];
uniform vec4 gl_EyePlaneS[gl_MaxTextureCoords];
uniform vec4 gl_EyePlaneT[gl_MaxTextureCoords];
uniform vec4 gl_EyePlaneR[gl_MaxTextureCoords];
uniform vec4 gl_EyePlaneQ[gl_MaxTextureCoords];
uniform vec4 gl_ObjectPlaneS[gl_MaxTextureCoords];
uniform vec4 gl_ObjectPlaneT[gl_MaxTextureCoords];
uniform vec4 gl_ObjectPlaneR[gl_MaxTextureCoords];
uniform vec4 gl_ObjectPlaneQ[gl_MaxTextureCoords];


struct gl_FogParameters {
vec4 color;
float density;
float start;
float end;
float scale; // Derived: 1.0 / (end - start)
};
uniform gl_FogParameters gl_Fog;

"""

# varing

gl_FrontColor: vec4
gl_BackColor: vec4
gl_FrontSecondaryColor: vec4
gl_BackSecondaryColor: vec4
# gl_TexCoord[]: vec4
gl_FogFragCoord: float

gl_Color: vec4
gl_SecondaryColor: vec4
# gl_TexCoord[]
gl_FogFragCoord: float
