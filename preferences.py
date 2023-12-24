from bpy.props import BoolProperty, EnumProperty
from bpy.types import AddonPreferences

from .utils import BLT_Info, BLT_Utils


class BLT_Preferences(AddonPreferences):
  bl_idname = BLT_Info.addon_name

  tabs: EnumProperty(items=[("GTRANSLATION", "全局翻译[GT]", "全局翻译"),
                            ("QTRANSLATION", "一键翻译[QT]", "一键翻译"),
                            ("LINKS", "相关链接[LK]", "相关链接")],
                     name="选项卡",
                     description="设置选项卡")

  button_toggle: BoolProperty(
      name="一键翻译",
      description="启动/禁用一键翻译按钮.\n"
      "PS: 翻译按钮显示在顶栏上",
      default=True
  )

  tooltips_included: BoolProperty(
      name="工具提示",
      description="使用一键翻译进行切换时将影响工具提示的切换.\n"
      "PS: 默认已影响界面的切换",
      default=True
  )

  new_dataname_included: BoolProperty(
      name="新建数据",
      description="使用一键翻译进行切换时将影响新建数据的切换.\n"
      "PS: 默认已影响界面的切换",
      default=True
  )

  def draw_global_translation(self, contxt):
    layout = self.layout
    enabled = BLT_Utils.is_enabled_global_translation()
    layout.operator("blt.translation_global",
                    text="已启用全局翻译" if enabled else "未启用全局翻译",
                    icon='FILE_REFRESH',
                    depress=enabled)
    message = layout.row()
    message.alignment = 'CENTER'
    message.label(text="启用或禁用全局翻译后, 重启 Blender 后生效!!!")

  def draw_workspace_translation(self, context):
    layout = self.layout
    box = layout.box()
    row = box.row()
    row.label(text="一键翻译:")
    row.prop(self, "button_toggle", text="启用")
    split = box.split()
    split.active = self.button_toggle
    split.prop(self, "tooltips_included")
    split.prop(self, "new_dataname_included")

  def draw_links(self, contxt):
    layout = self.layout

    box = layout.box()
    about_title = box.row()
    about_title.alignment = 'CENTER'
    about_title.label(text="关于插件")
    about_msg = box.row()
    about_msg.alignment = 'CENTER'
    about_msg.label(text="☆此插件为免费插件, 禁止用于任何商业用途☆")

    box = layout.box()
    url_title = box.row()
    url_title.alignment = 'CENTER'
    url_title.label(text="文档与反馈")
    urls = box.row()
    urls.operator("wm.url_open", text="帮助文档").url = BLT_Info.url_document
    urls.operator("wm.url_open",
                  text="问答平台").url = BLT_Info.url_question_and_answer

  def draw(self, context):
    layout = self.layout
    tabs = layout.row()
    tabs.prop(self, "tabs", expand=True)
    layout.separator()
    if self.tabs == 'GTRANSLATION':
      self.draw_global_translation(context)
    elif self.tabs == 'QTRANSLATION':
      self.draw_workspace_translation(context)
    elif self.tabs == 'LINKS':
      self.draw_links(context)
    layout.separator()
