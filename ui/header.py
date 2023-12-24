import os
import sys

import bpy
import bpy.utils.previews

from ..operators.blt import BLT_Start
from ..operators.translation import BLT_Translation
from ..utils import BLT_Info, BLT_Utils


# BLT 对接按钮
class BLT_Header(bpy.types.Header):
  bl_idname = "BLT_HT_HEADER"
  bl_space_type = "TOPBAR"

  @classmethod
  def register(cls):
    # 创建图标资源
    icons_dir = BLT_Info.addon_icons_path
    cls.icons = bpy.utils.previews.new()
    # 添加对接按钮
    cls.icons.load("BLT", os.path.join(icons_dir, "BLT.png"), 'IMAGE')
    bpy.types.TOPBAR_HT_upper_bar.append(cls.link_button)
    # 添加翻译按钮
    cls.icons.load("CN", os.path.join(icons_dir, "CN.png"), 'IMAGE')
    cls.icons.load("EN", os.path.join(icons_dir, "EN.png"), 'IMAGE')
    bpy.types.TOPBAR_HT_upper_bar.append(cls.translation_button)

  @classmethod
  def unregister(cls):
    bpy.types.TOPBAR_HT_upper_bar.remove(cls.translation_button)
    bpy.types.TOPBAR_HT_upper_bar.remove(cls.link_button)
    bpy.utils.previews.remove(cls.icons)
    cls.icons.clear()

  # 绘制接口
  def draw(self, context):
    return super().draw(context)

  # 绘制对接按钮
  def link_button(self, context):
    # 仅在 WINDOWS 系统绘制此按钮
    if sys.platform == 'win32' and context.region.alignment != 'RIGHT':
      self.layout.operator(
          BLT_Start.bl_idname,
          text="",
          icon_value=BLT_Header.icons["BLT"].icon_id)

  # 绘制翻译按钮
  def translation_button(self, context):
    if BLT_Utils.get_preferences(
    ).button_toggle and context.region.alignment != 'RIGHT':
      view = context.preferences.view
      self.layout.operator(
          BLT_Translation.bl_idname,
          text="",
          icon_value=BLT_Header.icons["CN" if view.use_translate_interface else "EN"].icon_id)
