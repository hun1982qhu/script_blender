import bpy
import math
import bmesh
import mathutils


# {{{ 定义属性类


class CustomCubeProperties(bpy.types.PropertyGroup):
    """"""

    # {{{ 尺寸属性

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

    # }}} 尺寸属性

    # {{{ 位置属性

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

    # }}} 位置属性

    # {{{ 旋转属性（以度为单位）

    rot_x: bpy.props.FloatProperty(
        name="旋转 X",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )
    rot_y: bpy.props.FloatProperty(
        name="旋转 Y",
        default=90,
        update=lambda self, context: update_cube_transform(context),
    )
    rot_z: bpy.props.FloatProperty(
        name="旋转 Z",
        default=0.0,
        update=lambda self, context: update_cube_transform(context),
    )

    # }}} 旋转属性（以度为单位）

    # {{{ Empty 距离

    empty_distance: bpy.props.FloatProperty(
        name="Empty 距离",
        default=0.1,
        min=-1.0,  # 设置最小值为负数，支持负数距离
        max=1.0,
        update=lambda self, context: update_empty_transform(context),
    )

    # }}} Empty 距离

    # {{{ 折叠/展开属性

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

    # }}} 折叠/展开属性


# }}} 定义属性类

# {{{ 创建自定义面板类


class OBJECT_PT_CustomCubePanel(bpy.types.Panel):
    """"""

    # {{{ 设置面板的名称、标签、ID、位置、类别等信息

    bl_label = "自定义瓦片设置"
    bl_idname = "OBJECT_PT_custom_cube_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "工具"

    # }}} 设置面板的名称、标签、ID、位置、类别等信息

    # {{{ 定义面板的布局

    def draw(self, context):
        layout = self.layout
        props = context.scene.custom_cube_props

        # {{{ 尺寸设置

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

        # }}} 尺寸设置

        # {{{ 位置设置

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

        # }}} 位置设置

        # {{{ 旋转设置

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

        # }}} 旋转设置

        # {{{ Empty Distance 设置

        box = layout.box()
        row = box.row()
        row.label(text="Empty 距离")
        box.prop(props, "empty_distance")

        # 创建按钮来生成立方体
        layout.operator("mesh.create_custom_cube", text="创建瓦片")
        # 创建按钮来删除立方体
        layout.operator("mesh.delete_custom_cube", text="删除瓦片")

        # 添加删除面板的按钮
        layout.operator("object.delete_custom_panel", text="删除面板")

        # }}} Empty Distance 设置

    # }}} 定义面板的布局


# }}} 创建自定义面板类

# {{{ 操作：创建自定义对象


class MESH_OT_CreateCustomCube(bpy.types.Operator):
    """"""

    # {{{ 设置操作的 ID 和标签

    bl_idname = "mesh.create_custom_cube"
    bl_label = "创建自定义瓦片"

    # }}} 设置操作的 ID 和标签

    # {{{ 执行操作的函数

    def execute(self, context):
        props = context.scene.custom_cube_props
        create_cube(
            props.length,
            props.width,
            props.height,
            (props.pos_x, props.pos_y, props.pos_z),
            (props.rot_x, props.rot_y, props.rot_z),
            props.empty_distance,  # 传入 empty 的距离参数
        )
        return {"FINISHED"}

    # }}} 执行操作的函数


# }}} 操作：创建自定义对象

# {{{ 操作：删除自定义对象


class MESH_OT_DeleteCustomCube(bpy.types.Operator):
    """"""

    # {{{ 设置操作的 ID 和标签

    bl_idname = "mesh.delete_custom_cube"
    bl_label = "删除自定义瓦片"

    # }}} 设置操作的 ID 和标签

    # {{{ 执行操作的函数

    def execute(self, context):
        delete_cube()
        delete_empty()
        return {"FINISHED"}

    # }}} 执行操作的函数


# }}} 操作：删除自定义对象

# {{{ 操作：删除自定义面板


class MESH_OT_DeletePanel(bpy.types.Operator):
    """
    删除自定义面板
    """

    # {{{ 设置操作的 ID 和标签

    bl_idname = "object.delete_custom_panel"
    bl_label = "删除面板"

    # }}} 设置操作的 ID 和标签

    # {{{ 执行操作的函数

    def execute(self, context):
        # 注销自定义面板类，删除面板
        try:
            bpy.utils.unregister_class(OBJECT_PT_CustomCubePanel)
            self.report({"INFO"}, "自定义面板已删除")
        except Exception as e:
            self.report({"WARNING"}, f"面板未找到或已删除: {e}")
        return {"FINISHED"}

    # }}} 执行操作的函数


# }}} 操作：删除自定义面板

# {{{ 创建一个带有60×30环切的立方体，并生成一个Empty


def create_cube(length, width, height, position, rotation, empty_distance):
    """"""
    # {{{ 删除现有的立方体和 Empty

    delete_cube()
    delete_empty()

    # }}} 删除现有的立方体和 Empty

    # {{{ 创建一个新的网格对象

    mesh = bpy.data.meshes.new("Custom_Cube_Mesh")
    cube = bpy.data.objects.new("Custom_Cube", mesh)
    bpy.context.collection.objects.link(cube)

    # }}} 创建一个新的网格对象

    # {{{ 使用 bmesh 创建立方体

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    # }}} 使用 bmesh 创建立方体

    # {{{ 缩放立方体到指定尺寸

    for v in bm.verts:
        v.co.x *= width / 2
        v.co.y *= length / 2
        v.co.z *= height / 2

    # }}} 缩放立方体到指定尺寸

    # {{{ 定义一个函数来在指定轴上进行细分

    def subdivide_edges(bm, axis, cuts):
        edges_to_subdivide = [
            e for e in bm.edges if abs(e.verts[0].co[axis] - e.verts[1].co[axis]) != 0
        ]
        bmesh.ops.subdivide_edges(bm, edges=edges_to_subdivide, cuts=cuts)

    # }}} 定义一个函数来在指定轴上进行细分

    # {{{ 在X轴和Y轴分别添加60和30个环切

    # 在 X 轴上添加60个环切
    subdivide_edges(bm, axis=0, cuts=30)
    # 在 Y 轴上添加30个环切
    subdivide_edges(bm, axis=1, cuts=60)

    # }}} 在X轴和Y轴分别添加60和30个环切

    # {{{ 更新网格并释放 bmesh

    bm.to_mesh(mesh)
    bm.free()

    # }}} 更新网格并释放 bmesh

    # {{{ 设置立方体的位置和旋转

    cube.location = position
    cube.rotation_euler = (
        math.radians(rotation[0]),
        math.radians(rotation[1]),
        math.radians(rotation[2]),
    )

    # }}} 设置立方体的位置和旋转

    # {{{ 创建一个 Empty Plain Axes

    empty = bpy.data.objects.new("Empty_Plain_Axes", None)
    empty.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(empty)

    # }}} 创建一个 Empty Plain Axes

    # {{{ 更新 Empty 的位置和法线方向

    update_empty_position(cube, empty, empty_distance)

    # }}} 更新 Empty 的位置和法线方向

    # {{{ 保存立方体和 Empty 的引用到自定义属性

    bpy.context.scene.custom_cube_ref = cube
    bpy.context.scene.custom_empty_ref = empty

    # }}} 保存立方体和 Empty 的引用到自定义属性


# }}} 创建一个带有60×30环切的立方体，并生成一个Empty

# {{{ 删除名为 "Custom_Cube" 的对象


def delete_cube():
    """"""
    obj = bpy.data.objects.get("Custom_Cube")
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)


# }}} 删除名为 "Custom_Cube" 的对象

# {{{ 删除名为 "Empty_Plain_Axes" 的对象


def delete_empty():
    """"""
    obj = bpy.data.objects.get("Empty_Plain_Axes")
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)


# }}} 删除名为 "Empty_Plain_Axes" 的对象

# {{{ 更新 Empty 位置函数


def update_empty_position(cube, empty, distance):
    """"""
    # 计算法线方向（cube 长和宽所在平面的法线）
    normal_vector = cube.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))
    # 更新 Empty 的位置，确保其在法线方向偏移指定距离
    empty.location = cube.location + normal_vector * distance


# }}} 更新 Empty 位置函数

# {{{ 更新 Empty 位置和旋转的函数


def update_empty_transform(context):
    """"""
    cube = getattr(bpy.context.scene, "custom_cube_ref", None)
    empty = getattr(bpy.context.scene, "custom_empty_ref", None)
    props = context.scene.custom_cube_props

    if cube and empty:
        # 更新 Empty 位置，确保始终保持在法线方向上并与 cube 一起移动和旋转
        update_empty_position(cube, empty, props.empty_distance)


# }}} 更新 Empty 位置和旋转的函数

# {{{ 注册类

classes = [
    CustomCubeProperties,
    OBJECT_PT_CustomCubePanel,
    MESH_OT_CreateCustomCube,
    MESH_OT_DeleteCustomCube,
    MESH_OT_DeletePanel,
]


def register():
    # 这里 classes 是一个包含多个自定义类的列表，
    # 例如 CustomCubeProperties、OBJECT_PT_CustomCubePanel、MESH_OT_CreateCustomCube 等。
    # 这段代码通过 bpy.utils.register_class(cls) 将这些类逐一注册到 Blender 系统中，
    # 使它们在 Blender 中可以作为自定义面板、操作和属性使用。
    for cls in classes:
        bpy.utils.register_class(cls)
    # Blender 使用 PointerProperty 来定义属性，这些属性会被添加到 bpy.types.Scene 中，从而让它们可以在整个场景中被访问。这三行代码具体的作用是：
    # bpy.types.Scene.custom_cube_props:
    # 定义并注册了一个新的属性 custom_cube_props，其类型为 CustomCubeProperties。这是自定义的属性组，包含了瓦片（或立方体）的尺寸、位置、旋转等信息，用户在界面中调整这些值时，Blender 会调用相应的更新函数。
    bpy.types.Scene.custom_cube_props = bpy.props.PointerProperty(
        type=CustomCubeProperties
    )
    # bpy.types.Scene.custom_cube_ref:
    # 定义并注册了一个新的属性 custom_cube_ref，它是一个指向 Blender 对象（bpy.types.Object）的指针。这个属性用来存储生成的自定义立方体对象的引用，以便在场景中可以访问和修改该对象。
    bpy.types.Scene.custom_cube_ref = bpy.props.PointerProperty(type=bpy.types.Object)
    # bpy.types.Scene.custom_empty_ref:
    # 类似地，custom_empty_ref 是一个指向 bpy.types.Object 的指针，用来存储创建的 Empty_Plain_Axes 对象的引用。这样做的目的是在场景中保存 Empty 的引用，以便对其进行位置和旋转的更新。
    bpy.types.Scene.custom_empty_ref = bpy.props.PointerProperty(type=bpy.types.Object)


# }}} 注册类

# {{{ 注销类


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.custom_cube_props
    del bpy.types.Scene.custom_cube_ref
    del bpy.types.Scene.custom_empty_ref


# }}} 注销类


if __name__ == "__main__":
    register()
