import bpy

from ..utils import BLT_Utils


class BLT_QuitDialog(bpy.types.Operator):
  bl_idname = "blt.dialog"
  bl_label = "退出 Blender"

  def draw(self, context):
    layout = self.layout
    enabled = BLT_Utils.is_enabled_global_translation()
    message = "全局翻译已启用" if enabled else "全局翻译已禁用"
    layout.label(text=message + ", 重启 Blender 将使之生效.", icon='QUESTION')
    layout.label(text="是否确定立刻关闭 Blender?")

  def execute(self, context):
    bpy.ops.wm.quit_blender()
    return {'FINISHED'}

  def cancel(self, context):
    return {'CANCEL'}

  def invoke(self, context, event):
    wm = context.window_manager
    return wm.invoke_props_dialog(self)
