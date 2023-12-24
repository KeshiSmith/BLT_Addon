import bpy
from bpy.props import StringProperty

from ..utils import BLT_Info, BLT_Utils


class BLT_Settings(bpy.types.Operator):
  bl_idname = "blt.settings"
  bl_label = "BLT 设置"

  @classmethod
  def register(cls) -> None:
    # 初始化相关目录
    BLT_Utils.makedirs_if_not_exists(BLT_Info.blt_path)
    BLT_Utils.makedirs_if_not_exists(BLT_Info.blt_info_path)
    # 增加插件变量
    bpy.types.Scene.blt_message = StringProperty(name="")
    bpy.types.Scene.blt_message_objectname = StringProperty(name="")
    bpy.types.Scene.blt_message_directoryname = StringProperty(name="")

  @classmethod
  def unregister(self) -> None:
    # 删除插件变量
    del bpy.types.Scene.blt_message
    del bpy.types.Scene.blt_message_objectname
    del bpy.types.Scene.blt_message_directoryname
