import bpy

# {{{ 定义属性类


class CustomCubeProperties(bpy.types.PropertyGroup):
    """"""

    length: bpy.props.FloatProperty(
        name="Length",
        default=0.25,
        min=0.01,
        max=0.3,
        update=lambda self, context: update_cube(context),
    )
    width: bpy.props.FloatProperty(
        name="Width",
        default=0.2,
        min=0.01,
        max=0.3,
        update=lambda self, context: update_cube(context),
    )
    height: bpy.props.FloatProperty(
        name="Height",
        default=0.02,
        min=0.01,
        max=0.1,
        update=lambda self, context: update_cube(context),
    )


# }}} 定义属性类

# {{{ 创建自定义面板类


class OBJECT_PT_CustomCubePanel(bpy.types.Panel):
    """"""

    bl_label = "Custom Cube Settings"
    bl_idname = "OBJECT_PT_custom_cube_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        props = context.scene.custom_cube_props

        # 创建 UI 控件
        layout.prop(props, "length")
        layout.prop(props, "width")
        layout.prop(props, "height")

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
    bl_label = "Create Custom Cube"

    def execute(self, context):
        props = context.scene.custom_cube_props
        create_cube(props.length, props.width, props.height)
        return {"FINISHED"}


# }}} 操作：创建自定义立方体

# {{{ 操作：删除自定义立方体


class MESH_OT_DeleteCustomCube(bpy.types.Operator):
    """"""

    bl_idname = "mesh.delete_custom_cube"
    bl_label = "Delete Custom Cube"

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
        # 确保对象在视图层并且可以被选中
        for collection in bpy.context.view_layer.layer_collection.children:
            if obj.name in collection.collection.objects:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                break

        # 删除选中的对象
        bpy.ops.object.delete()


# }}} 删除名为 "Custom_Cube" 的对象

# {{{ 创建一个立方体


def create_cube(length=0.25, width=0.2, height=0.02):
    """"""

    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False)
    cube = bpy.context.object
    cube.scale = (width / 2, length / 2, height / 2)
    cube.name = "orgin_tile"
    bpy.context.scene.custom_cube_ref = cube  # 保存立方体的引用到自定义属性


# }}} 创建一个立方体

# {{{ 更新立方体尺寸的函数


def update_cube(context):
    """"""

    cube = getattr(bpy.context.scene, "custom_cube_ref", None)
    if cube and cube.name == "Custom_Cube":
        props = context.scene.custom_cube_props
        cube.scale = (props.length / 2, props.width / 2, props.height / 2)


# }}} 更新立方体尺寸的函数

# {{{ 操作：删除自定义面板


class MESH_OT_DeletePanel(bpy.types.Operator):
    """删除自定义面板"""

    bl_idname = "object.delete_custom_panel"
    bl_label = "删除面板"

    def execute(self, context):
        # 注销自定义面板类，删除面板
        bpy.utils.unregister_class(OBJECT_PT_CustomCubePanel)
        self.report({"INFO"}, "自定义面板已删除")
        return {"FINISHED"}


# }}} 操作：删除自定义面板

# {{{ 注册类


def register():
    """"""
    bpy.utils.register_class(CustomCubeProperties)
    bpy.utils.register_class(OBJECT_PT_CustomCubePanel)
    bpy.utils.register_class(MESH_OT_CreateCustomCube)
    bpy.utils.register_class(MESH_OT_DeleteCustomCube)
    bpy.utils.register_class(MESH_OT_DeletePanel)  # 注册删除面板的操作

    # 注册属性组
    bpy.types.Scene.custom_cube_props = bpy.props.PointerProperty(
        type=CustomCubeProperties
    )
    bpy.types.Scene.custom_cube_ref = bpy.props.PointerProperty(type=bpy.types.Object)


# }}} 注册类

# {{{ 注销类


def unregister():
    """"""
    bpy.utils.unregister_class(CustomCubeProperties)
    bpy.utils.unregister_class(OBJECT_PT_CustomCubePanel)
    bpy.utils.unregister_class(MESH_OT_CreateCustomCube)
    bpy.utils.unregister_class(MESH_OT_DeleteCustomCube)
    bpy.utils.unregister_class(MESH_OT_DeletePanel)  # 注销删除面板的操作
    del bpy.types.Scene.custom_cube_props
    del bpy.types.Scene.custom_cube_ref


# }}} 注销类

if __name__ == "__main__":
    register()
