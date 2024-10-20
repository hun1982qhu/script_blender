import bpy
import bmesh
import math

# {{{ 定义属性类


class CustomCubeProperties(bpy.types.PropertyGroup):
    """"""

    # 尺寸属性
    length: bpy.props.FloatProperty(
        name="长度",
        default=0.36,
        min=0.01,
        max=1.0,
        update=lambda self, context: update_cube(context),
    )
    width: bpy.props.FloatProperty(
        name="宽度",
        default=0.24,
        min=0.01,
        max=1.0,
        update=lambda self, context: update_cube(context),
    )
    height: bpy.props.FloatProperty(
        name="高度",
        default=0.015,
        min=0.001,
        max=1.0,
        update=lambda self, context: update_cube(context),
    )

    # 位置属性
    pos_x: bpy.props.FloatProperty(
        name="位置 X",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )
    pos_y: bpy.props.FloatProperty(
        name="位置 Y",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )
    pos_z: bpy.props.FloatProperty(
        name="位置 Z",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )

    # 旋转属性（以度为单位）
    rot_x: bpy.props.FloatProperty(
        name="旋转 X",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )
    rot_y: bpy.props.FloatProperty(
        name="旋转 Y",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )
    rot_z: bpy.props.FloatProperty(
        name="旋转 Z",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )

    # 折叠/展开属性
    show_size_settings: bpy.props.BoolProperty(
        name="尺寸设置",
        default=True,
    )
    show_position_settings: bpy.props.BoolProperty(
        name="位置设置",
        default=True,
    )
    show_rotation_settings: bpy.props.BoolProperty(
        name="旋转设置",
        default=True,
    )


# }}} 定义属性类

# {{{ 创建自定义面板类


class OBJECT_PT_CustomCubePanel(bpy.types.Panel):
    """"""

    bl_label = "自定义瓦片设置"
    bl_idname = "OBJECT_PT_custom_cube_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "工具"

    def draw(self, context):
        layout = self.layout
        props = context.scene.custom_cube_props

        # 尺寸设置
        box = layout.box()
        row = box.row()
        row.prop(
            props,
            "show_size_settings",
            icon="TRIA_DOWN" if props.show_size_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        row.label(text="尺寸设置")
        if props.show_size_settings:
            sub_box = box.box()
            sub_box.prop(props, "length")
            sub_box.prop(props, "width")
            sub_box.prop(props, "height")

        # 位置设置
        box = layout.box()
        row = box.row()
        row.prop(
            props,
            "show_position_settings",
            icon="TRIA_DOWN" if props.show_position_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        row.label(text="位置设置")
        if props.show_position_settings:
            sub_box = box.box()
            sub_box.prop(props, "pos_x")
            sub_box.prop(props, "pos_y")
            sub_box.prop(props, "pos_z")

        # 旋转设置
        box = layout.box()
        row = box.row()
        row.prop(
            props,
            "show_rotation_settings",
            icon="TRIA_DOWN" if props.show_rotation_settings else "TRIA_RIGHT",
            icon_only=True,
            emboss=False,
        )
        row.label(text="旋转设置（度）")
        if props.show_rotation_settings:
            sub_box = box.box()
            sub_box.prop(props, "rot_x")
            sub_box.prop(props, "rot_y")
            sub_box.prop(props, "rot_z")

        # 创建按钮来生成立方体
        layout.operator("mesh.create_custom_cube", text="创建瓦片")
        # 创建按钮来删除立方体
        layout.operator("mesh.delete_custom_cube", text="删除瓦片")

        # 添加删除面板的按钮
        layout.operator("object.delete_custom_panel", text="删除面板")


# }}} 创建自定义面板类

# {{{ 操作：创建自定义立方体


class MESH_OT_CreateCustomCube(bpy.types.Operator):
    """"""

    bl_idname = "mesh.create_custom_cube"
    bl_label = "创建自定义瓦片"

    def execute(self, context):
        props = context.scene.custom_cube_props
        create_cube(
            props.length,
            props.width,
            props.height,
            (props.pos_x, props.pos_y, props.pos_z),
            (props.rot_x, props.rot_y, props.rot_z),
        )
        return {"FINISHED"}


# }}} 操作：创建自定义立方体

# {{{ 操作：删除自定义立方体


class MESH_OT_DeleteCustomCube(bpy.types.Operator):
    """"""

    bl_idname = "mesh.delete_custom_cube"
    bl_label = "删除自定义瓦片"

    def execute(self, context):
        delete_cube()
        return {"FINISHED"}


# }}} 操作：删除自定义立方体

# {{{ 删除名为 "Custom_Cube" 的对象


def delete_cube():
    """"""
    # 获取名为 "Custom_Cube" 的对象
    obj = bpy.data.objects.get("Custom_Cube")

    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)


# }}} 删除名为 "Custom_Cube" 的对象

# {{{ 创建一个带有60×30环切的立方体


def create_cube(length, width, height, position, rotation):
    """"""
    # 删除现有的立方体
    delete_cube()

    # 创建一个新的网格对象
    mesh = bpy.data.meshes.new("Custom_Cube_Mesh")
    cube = bpy.data.objects.new("Custom_Cube", mesh)
    bpy.context.collection.objects.link(cube)

    # 使用 bmesh 创建立方体
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    # 缩放立方体到指定尺寸
    for v in bm.verts:
        v.co.x *= width / 2
        v.co.y *= length / 2
        v.co.z *= height / 2

    # 定义一个函数来在指定轴上进行细分
    def subdivide_edges(bm, axis, cuts):
        edges_to_subdivide = [
            e for e in bm.edges if abs(e.verts[0].co[axis] - e.verts[1].co[axis]) != 0
        ]
        bmesh.ops.subdivide_edges(bm, edges=edges_to_subdivide, cuts=cuts)

    # 在 X 轴上添加60个环切
    subdivide_edges(bm, axis=0, cuts=30)
    # 在 Y 轴上添加30个环切
    subdivide_edges(bm, axis=1, cuts=60)

    # 更新网格并释放 bmesh
    bm.to_mesh(mesh)
    bm.free()

    # 设置立方体的位置和旋转
    cube.location = position
    cube.rotation_euler = (
        math.radians(rotation[0]),
        math.radians(rotation[1]),
        math.radians(rotation[2]),
    )

    # 保存立方体的引用到自定义属性
    bpy.context.scene.custom_cube_ref = cube


# }}} 创建一个带有60×30环切的立方体

# {{{ 更新立方体尺寸的函数


def update_cube(context):
    """"""
    cube = getattr(bpy.context.scene, "custom_cube_ref", None)
    if cube and cube.name == "Custom_Cube":
        props = context.scene.custom_cube_props
        # 重新创建立方体以更新尺寸和环切
        create_cube(
            props.length,
            props.width,
            props.height,
            (props.pos_x, props.pos_y, props.pos_z),
            (props.rot_x, props.rot_y, props.rot_z),
        )


# }}} 更新立方体尺寸的函数

# {{{ 更新立方体位置和旋转的函数


def update_cube_transform(context):
    """"""
    cube = getattr(bpy.context.scene, "custom_cube_ref", None)
    if cube and cube.name == "Custom_Cube":
        props = context.scene.custom_cube_props
        # 更新立方体的位置
        cube.location = (props.pos_x, props.pos_y, props.pos_z)
        # 更新立方体的旋转（将度数转换为弧度）
        cube.rotation_euler = (
            math.radians(props.rot_x),
            math.radians(props.rot_y),
            math.radians(props.rot_z),
        )


# }}} 更新立方体位置和旋转的函数

# {{{ 操作：删除自定义面板


class MESH_OT_DeletePanel(bpy.types.Operator):
    """删除自定义面板"""

    bl_idname = "object.delete_custom_panel"
    bl_label = "删除面板"

    def execute(self, context):
        # 注销自定义面板类，删除面板
        try:
            bpy.utils.unregister_class(OBJECT_PT_CustomCubePanel)
            self.report({"INFO"}, "自定义面板已删除")
        except Exception as e:
            self.report({"WARNING"}, f"面板未找到或已删除: {e}")
        return {"FINISHED"}


# }}} 操作：删除自定义面板

# {{{ 注册类

classes = [
    CustomCubeProperties,
    OBJECT_PT_CustomCubePanel,
    MESH_OT_CreateCustomCube,
    MESH_OT_DeleteCustomCube,
    MESH_OT_DeletePanel,
]


def register():
    # 先注销已注册的类（如果存在）
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

    # 注册类
    for cls in classes:
        bpy.utils.register_class(cls)

    # 注册属性组
    bpy.types.Scene.custom_cube_props = bpy.props.PointerProperty(
        type=CustomCubeProperties
    )
    bpy.types.Scene.custom_cube_ref = bpy.props.PointerProperty(type=bpy.types.Object)


# }}} 注册类

# {{{ 注销类


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    del bpy.types.Scene.custom_cube_props
    del bpy.types.Scene.custom_cube_ref


# }}} 注销类

if __name__ == "__main__":
    register()
