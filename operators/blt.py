import subprocess

import bpy

from ..utils import BLT_Utils


class BLT_Start(bpy.types.Operator):
  bl_idname = "blt.start"
  bl_label = "启动 BLT 客户端"
  bl_description = "一键启动 BLT 客户端"

  def execute(self, context):
    # 检查是否正在运行中
    if BLT_Utils.blt_is_running():
      self.report({'INFO'}, "BLT已经被启动.")
      return {'FINISHED'}
    # 获取客户端位置并运行
    blt_exe_path = BLT_Utils.get_exe_path_from_info()
    if not blt_exe_path:
      self.report({'ERROR'}, "你还没有安装或使用过BLT, 请先下载并运行BLT.")
    else:
      subprocess.Popen(blt_exe_path)
      self.report({'INFO'}, "BLT已经被启动, 请耐心等待.")
    return {'FINISHED'}
