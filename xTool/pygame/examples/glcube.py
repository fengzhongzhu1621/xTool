#!/usr/bin/env python
"""pygame.examples.glcube

Draw a cube on the screen.

绘制一个旋转的彩色立方体示例

Amazing.

Every frame we orbit the camera around a small amount
creating the illusion of a spinning object.

每一帧我们围绕相机旋转一小段距离，创造出旋转物体的错觉。

First we setup some points of a multicolored cube. Then we then go through
a semi-unoptimized loop to draw the cube points onto the screen.

首先我们设置一个彩色立方体的顶点，然后通过一个半优化的循环将立方体顶点绘制到屏幕上。

OpenGL does all the hard work for us. :]

OpenGL为我们完成了所有困难的工作。:]


Keyboard Controls
-----------------
键盘控制
-----------------

* ESCAPE key to quit - ESC键退出
* f key to toggle fullscreen - f键切换全屏模式

"""
import ctypes
import math

import pygame as pg

# 尝试导入OpenGL库
try:
    import OpenGL.GL as GL  # OpenGL核心功能
    import OpenGL.GLU as GLU  # OpenGL实用工具库
except ImportError:
    print("pyopengl missing. The GLCUBE example requires: pyopengl numpy")
    print("缺少pyopengl库。GLCUBE示例需要：pyopengl numpy")
    raise SystemExit

# 尝试导入numpy库
try:
    from numpy import array, dot, eye, float32, uint32, zeros
except ImportError:
    print("numpy missing. The GLCUBE example requires: pyopengl numpy")
    print("缺少numpy库。GLCUBE示例需要：pyopengl numpy")
    raise SystemExit


# 是否使用"现代"OpenGL API还是旧版API？
# 这个示例展示了如何同时使用两种方法。
USE_MODERN_GL = True

# 彩色立方体的简单数据
# 这里我们有每个角的3D点位置和颜色
# 一个索引列表描述每个面，另一个索引列表描述每条边

# 立方体的8个顶点坐标 (x, y, z)
CUBE_POINTS = (
    (0.5, -0.5, -0.5),  # 顶点0: 右前下
    (0.5, 0.5, -0.5),  # 顶点1: 右前上
    (-0.5, 0.5, -0.5),  # 顶点2: 左前上
    (-0.5, -0.5, -0.5),  # 顶点3: 左前下
    (0.5, -0.5, 0.5),  # 顶点4: 右后下
    (0.5, 0.5, 0.5),  # 顶点5: 右后上
    (-0.5, -0.5, 0.5),  # 顶点6: 左后下
    (-0.5, 0.5, 0.5),  # 顶点7: 左后上
)

# 每个顶点的颜色 (RGB值，范围0-1)
CUBE_COLORS = (
    (1, 0, 0),  # 红色
    (1, 1, 0),  # 黄色
    (0, 1, 0),  # 绿色
    (0, 0, 0),  # 黑色
    (1, 0, 1),  # 紫色
    (1, 1, 1),  # 白色
    (0, 0, 1),  # 蓝色
    (0, 1, 1),  # 青色
)

# 立方体的6个四边形面，每个面由4个顶点索引组成
CUBE_QUAD_VERTS = (
    (0, 1, 2, 3),  # 前面
    (3, 2, 7, 6),  # 左面
    (6, 7, 5, 4),  # 后面
    (4, 5, 1, 0),  # 右面
    (1, 5, 7, 2),  # 上面
    (4, 0, 3, 6),  # 下面
)

# 立方体的12条边，每条边由2个顶点索引组成
CUBE_EDGES = (
    (0, 1),  # 前右竖边
    (0, 3),  # 前下横边
    (0, 4),  # 右下斜边
    (2, 1),  # 前上横边
    (2, 3),  # 前左竖边
    (2, 7),  # 左上斜边
    (6, 3),  # 左下竖边
    (6, 4),  # 后下横边
    (6, 7),  # 后左竖边
    (5, 1),  # 右上斜边
    (5, 4),  # 后右竖边
    (5, 7),  # 后上横边
)


def translate(matrix, x=0.0, y=0.0, z=0.0):
    """
    在x、y和z轴上平移（移动）矩阵。

    :param matrix: 要平移的矩阵
    :param x: 在x轴上平移的方向和大小，默认为0
    :param y: 在y轴上平移的方向和大小，默认为0
    :param z: 在z轴上平移的方向和大小，默认为0
    :return: 平移后的矩阵
    """
    translation_matrix = array(
        [
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=matrix.dtype,
    ).T
    matrix[...] = dot(matrix, translation_matrix)
    return matrix


def frustum(left, right, bottom, top, znear, zfar):
    """
    从裁剪平面或相机'视锥体'构建透视矩阵。

    :param left: 近裁剪平面的左侧位置
    :param right: 近裁剪平面的右侧位置
    :param bottom: 近裁剪平面的底部位置
    :param top: 近裁剪平面的顶部位置
    :param znear: 近裁剪平面的z深度
    :param zfar: 远裁剪平面的z深度

    :return: 透视矩阵
    """
    perspective_matrix = zeros((4, 4), dtype=float32)
    perspective_matrix[0, 0] = +2.0 * znear / (right - left)
    perspective_matrix[2, 0] = (right + left) / (right - left)
    perspective_matrix[1, 1] = +2.0 * znear / (top - bottom)
    perspective_matrix[3, 1] = (top + bottom) / (top - bottom)
    perspective_matrix[2, 2] = -(zfar + znear) / (zfar - znear)
    perspective_matrix[3, 2] = -2.0 * znear * zfar / (zfar - znear)
    perspective_matrix[2, 3] = -1.0
    return perspective_matrix


def perspective(fovy, aspect, znear, zfar):
    """
    从视野角度、宽高比和深度平面构建透视矩阵。

    :param fovy: y轴上的视野角度
    :param aspect: 视口的宽高比
    :param znear: 近裁剪平面的z深度
    :param zfar: 远裁剪平面的z深度

    :return: 透视矩阵
    """
    h = math.tan(fovy / 360.0 * math.pi) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar)


def rotate(matrix, angle, x, y, z):
    """
    围绕一个轴旋转矩阵。

    :param matrix: 要旋转的矩阵
    :param angle: 旋转的角度
    :param x: 旋转轴的x分量
    :param y: 旋转轴的y分量
    :param z: 旋转轴的z分量

    :return: 旋转后的矩阵
    """
    angle = math.pi * angle / 180
    c, s = math.cos(angle), math.sin(angle)
    n = math.sqrt(x * x + y * y + z * z)
    x, y, z = x / n, y / n, z / n
    cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
    rotation_matrix = array(
        [
            [cx * x + c, cy * x - z * s, cz * x + y * s, 0],
            [cx * y + z * s, cy * y + c, cz * y - x * s, 0],
            [cx * z - y * s, cy * z + x * s, cz * z + c, 0],
            [0, 0, 0, 1],
        ],
        dtype=matrix.dtype,
    ).T
    matrix[...] = dot(matrix, rotation_matrix)
    return matrix


class Rotation:
    """
    存储三个轴旋转角度的数据类。
    """

    def __init__(self):
        self.theta = 20  # z轴旋转角度
        self.phi = 40  # y轴旋转角度
        self.psi = 25  # x轴旋转角度


def drawcube_old():
    """
    使用OpenGL 3.2核心上下文之前的旧版OpenGL方法绘制立方体。
    """
    allpoints = list(zip(CUBE_POINTS, CUBE_COLORS))

    GL.glBegin(GL.GL_QUADS)
    for face in CUBE_QUAD_VERTS:
        for vert in face:
            pos, color = allpoints[vert]
            GL.glColor3fv(color)
            GL.glVertex3fv(pos)
    GL.glEnd()

    GL.glColor3f(1.0, 1.0, 1.0)
    GL.glBegin(GL.GL_LINES)
    for line in CUBE_EDGES:
        for vert in line:
            pos, color = allpoints[vert]
            GL.glVertex3fv(pos)

    GL.glEnd()


def init_gl_stuff_old():
    """
    初始化OpenGL，适用于3.2核心上下文之前的版本
    """
    GL.glEnable(GL.GL_DEPTH_TEST)  # use our zbuffer

    # setup the camera
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GLU.gluPerspective(45.0, 640 / 480.0, 0.1, 100.0)  # setup lens
    GL.glTranslatef(0.0, 0.0, -3.0)  # move back
    GL.glRotatef(25, 1, 0, 0)  # orbit higher


def init_gl_modern(display_size):
    """
    Initialise open GL in the 'modern' open GL style for open GL versions
    greater than 3.1.

    :param display_size: Size of the window/viewport.
    """

    # Create shaders
    # --------------------------------------
    vertex_code = """

    #version 150
    uniform mat4   model;
    uniform mat4   view;
    uniform mat4   projection;

    uniform vec4   colour_mul;
    uniform vec4   colour_add;

    in vec4 vertex_colour;         // vertex colour in
    in vec3 vertex_position;

    out vec4   vertex_color_out;            // vertex colour out
    void main()
    {
        vertex_color_out = (colour_mul * vertex_colour) + colour_add;
        gl_Position = projection * view * model * vec4(vertex_position, 1.0);
    }

    """

    fragment_code = """
    #version 150
    in vec4 vertex_color_out;  // vertex colour from vertex shader
    out vec4 fragColor;
    void main()
    {
        fragColor = vertex_color_out;
    }
    """

    program = GL.glCreateProgram()
    vertex = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    fragment = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(vertex, vertex_code)
    GL.glCompileShader(vertex)

    # this logs issues the shader compiler finds.
    log = GL.glGetShaderInfoLog(vertex)
    if isinstance(log, bytes):
        log = log.decode()
    for line in log.split("\n"):
        print(line)

    GL.glAttachShader(program, vertex)
    GL.glShaderSource(fragment, fragment_code)
    GL.glCompileShader(fragment)

    # this logs issues the shader compiler finds.
    log = GL.glGetShaderInfoLog(fragment)
    if isinstance(log, bytes):
        log = log.decode()
    for line in log.split("\n"):
        print(line)

    GL.glAttachShader(program, fragment)
    GL.glValidateProgram(program)
    GL.glLinkProgram(program)

    GL.glDetachShader(program, vertex)
    GL.glDetachShader(program, fragment)
    GL.glUseProgram(program)

    # Create vertex buffers and shader constants
    # ------------------------------------------

    # Cube Data
    vertices = zeros(8, [("vertex_position", float32, 3), ("vertex_colour", float32, 4)])

    vertices["vertex_position"] = [
        [1, 1, 1],
        [-1, 1, 1],
        [-1, -1, 1],
        [1, -1, 1],
        [1, -1, -1],
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, -1],
    ]

    vertices["vertex_colour"] = [
        [0, 1, 1, 1],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [0, 1, 0, 1],
        [1, 1, 0, 1],
        [1, 1, 1, 1],
        [1, 0, 1, 1],
        [1, 0, 0, 1],
    ]

    filled_cube_indices = array(
        [
            0,
            1,
            2,
            0,
            2,
            3,
            0,
            3,
            4,
            0,
            4,
            5,
            0,
            5,
            6,
            0,
            6,
            1,
            1,
            6,
            7,
            1,
            7,
            2,
            7,
            4,
            3,
            7,
            3,
            2,
            4,
            7,
            6,
            4,
            6,
            5,
        ],
        dtype=uint32,
    )

    outline_cube_indices = array(
        [0, 1, 1, 2, 2, 3, 3, 0, 4, 7, 7, 6, 6, 5, 5, 4, 0, 5, 1, 6, 2, 7, 3, 4],
        dtype=uint32,
    )

    shader_data = {"buffer": {}, "constants": {}}

    GL.glBindVertexArray(GL.glGenVertexArrays(1))  # Have to do this first

    shader_data["buffer"]["vertices"] = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, shader_data["buffer"]["vertices"])
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_DYNAMIC_DRAW)

    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)

    loc = GL.glGetAttribLocation(program, "vertex_position")
    GL.glEnableVertexAttribArray(loc)
    GL.glVertexAttribPointer(loc, 3, GL.GL_FLOAT, False, stride, offset)

    offset = ctypes.c_void_p(vertices.dtype["vertex_position"].itemsize)

    loc = GL.glGetAttribLocation(program, "vertex_colour")
    GL.glEnableVertexAttribArray(loc)
    GL.glVertexAttribPointer(loc, 4, GL.GL_FLOAT, False, stride, offset)

    shader_data["buffer"]["filled"] = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["filled"])
    GL.glBufferData(
        GL.GL_ELEMENT_ARRAY_BUFFER,
        filled_cube_indices.nbytes,
        filled_cube_indices,
        GL.GL_STATIC_DRAW,
    )

    shader_data["buffer"]["outline"] = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["outline"])
    GL.glBufferData(
        GL.GL_ELEMENT_ARRAY_BUFFER,
        outline_cube_indices.nbytes,
        outline_cube_indices,
        GL.GL_STATIC_DRAW,
    )

    shader_data["constants"]["model"] = GL.glGetUniformLocation(program, "model")
    GL.glUniformMatrix4fv(shader_data["constants"]["model"], 1, False, eye(4))

    shader_data["constants"]["view"] = GL.glGetUniformLocation(program, "view")
    view = translate(eye(4), z=-6)
    GL.glUniformMatrix4fv(shader_data["constants"]["view"], 1, False, view)

    shader_data["constants"]["projection"] = GL.glGetUniformLocation(program, "projection")
    GL.glUniformMatrix4fv(shader_data["constants"]["projection"], 1, False, eye(4))

    # This colour is multiplied with the base vertex colour in producing
    # the final output
    shader_data["constants"]["colour_mul"] = GL.glGetUniformLocation(program, "colour_mul")
    GL.glUniform4f(shader_data["constants"]["colour_mul"], 1, 1, 1, 1)

    # This colour is added on to the base vertex colour in producing
    # the final output
    shader_data["constants"]["colour_add"] = GL.glGetUniformLocation(program, "colour_add")
    GL.glUniform4f(shader_data["constants"]["colour_add"], 0, 0, 0, 0)

    # Set GL drawing data
    # -------------------
    GL.glClearColor(0, 0, 0, 0)
    GL.glPolygonOffset(1, 1)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glLineWidth(1.0)

    projection = perspective(45.0, display_size[0] / float(display_size[1]), 2.0, 100.0)
    GL.glUniformMatrix4fv(shader_data["constants"]["projection"], 1, False, projection)

    return shader_data, filled_cube_indices, outline_cube_indices


def draw_cube_modern(shader_data, filled_cube_indices, outline_cube_indices, rotation):
    """
    Draw a cube in the 'modern' Open GL style, for post 3.1 versions of
    open GL.

    :param shader_data: compile vertex & pixel shader data for drawing a cube.
    :param filled_cube_indices: the indices to draw the 'filled' cube.
    :param outline_cube_indices: the indices to draw the 'outline' cube.
    :param rotation: the current rotations to apply.
    """

    GL.glClear(
        GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT
    )  # pyright: ignore[reportUnknownMemberType, reportOperatorIssue]

    # Filled cube
    GL.glDisable(GL.GL_BLEND)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
    GL.glUniform4f(shader_data["constants"]["colour_mul"], 1, 1, 1, 1)
    GL.glUniform4f(shader_data["constants"]["colour_add"], 0, 0, 0, 0.0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["filled"])
    GL.glDrawElements(GL.GL_TRIANGLES, len(filled_cube_indices), GL.GL_UNSIGNED_INT, None)

    # Outlined cube
    GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)
    GL.glEnable(GL.GL_BLEND)
    GL.glUniform4f(shader_data["constants"]["colour_mul"], 0, 0, 0, 0.0)
    GL.glUniform4f(shader_data["constants"]["colour_add"], 1, 1, 1, 1.0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["outline"])
    GL.glDrawElements(GL.GL_LINES, len(outline_cube_indices), GL.GL_UNSIGNED_INT, None)

    # Rotate cube
    # rotation.theta += 1.0  # degrees
    rotation.phi += 1.0  # degrees
    # rotation.psi += 1.0  # degrees
    model = eye(4, dtype=float32)
    # rotate(model, rotation.theta, 0, 0, 1)
    rotate(model, rotation.phi, 0, 1, 0)
    rotate(model, rotation.psi, 1, 0, 0)
    GL.glUniformMatrix4fv(shader_data["constants"]["model"], 1, False, model)


def main():
    """run the demo"""

    # initialize pygame and setup an opengl display
    pg.init()

    gl_version = (3, 0)  # GL Version number (Major, Minor)
    if USE_MODERN_GL:
        gl_version = (3, 2)  # GL Version number (Major, Minor)

        # By setting these attributes we can choose which Open GL Profile
        # to use, profiles greater than 3.2 use a different rendering path
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, gl_version[0])
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, gl_version[1])
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

    fullscreen = False  # start in windowed mode

    display_size = (640, 480)
    pg.display.set_mode(display_size, pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

    if USE_MODERN_GL:
        gpu, f_indices, o_indices = init_gl_modern(display_size)
        rotation = Rotation()
    else:
        init_gl_stuff_old()

    going = True
    while going:
        # check for quit'n events
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                going = False

            elif event.type == pg.KEYDOWN and event.key == pg.K_f:
                if not fullscreen:
                    print("Changing to FULLSCREEN")
                    pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN)
                else:
                    print("Changing to windowed mode")
                    pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
                fullscreen = not fullscreen
                if gl_version[0] >= 4 or (gl_version[0] == 3 and gl_version[1] >= 2):
                    gpu, f_indices, o_indices = init_gl_modern(display_size)
                    rotation = Rotation()
                else:
                    init_gl_stuff_old()

        if USE_MODERN_GL:
            draw_cube_modern(gpu, f_indices, o_indices, rotation)  # pyright: ignore[reportPossiblyUnboundVariable]
        else:
            # clear screen and move camera
            GL.glClear(
                GL.GL_COLOR_BUFFER_BIT
                | GL.GL_DEPTH_BUFFER_BIT  # pyright: ignore[reportUnknownMemberType, reportOperatorIssue]
            )
            # orbit camera around by 1 degree
            GL.glRotatef(1, 0, 1, 0)
            drawcube_old()

        pg.display.flip()
        pg.time.wait(10)

    pg.quit()


if __name__ == "__main__":
    main()
