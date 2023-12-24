import shutil

import bpy

from ..utils import BLT_Info, BLT_Utils


class BLT_TranslationGlobal(bpy.types.Operator):
  bl_idname = "blt.translation_global"
  bl_label = "全局翻译本地插件"
  bl_description = "全局翻译本地插件(五分钟内重复点击仅下载翻译文件一次)"
  bl_options = {'INTERNAL'}

  def execute(self, context):
    # 根据当前状态切换语言环境
    if BLT_Utils.is_enabled_global_translation():
      BLT_Utils.remove_global_translation()
    else:
      view = context.preferences.view
      # -------------------------------------------------------------------------
      # 修复 Blender 4.0 更新语言配置文件导致错误
      view.language = "zh_CN" if "zh_CN" in bpy.app.translations.locales else "zh_HANS"
      # ------------------------------------------------------------------------
      view.use_translate_interface = True
      view.use_translate_tooltips = True
      try:
        BLT_Utils.enable_global_translation()
      except Exception as e:
        # 打印错误并报错
        print(str(e))
        self.report({'ERROR'}, "网络有问题...可以请尝试换个网络, 如手机USB连接或手机WIFI分享!")
        return {'FINISHED'}
      source = BLT_Info.addon_locale_path + '/languages'
      target = BLT_Info.blender_global_locale_path + "/languages"
      shutil.copyfile(source, target)
    bpy.ops.blt.dialog('INVOKE_DEFAULT')
    return {'FINISHED'}


class BLT_TranslationWorkspace(bpy.types.Operator):
  bl_idname = "blt.translation_workspace"
  bl_label = "工作空间翻译"
  bl_description = "工作空间翻译"

  workspace_dict_chinese = {
      "Animation": '动画',
      "Compositing": '合成',
      "Geometry Nodes": '几何节点',
      "Layout": '布局',
      "Modeling": '建模',
      "Rendering": '渲染',
      "Scripting": '脚本',
      "Sculpting": '雕刻',
      "Shading": '着色',
      "Texture Paint": '纹理绘制',
      "UV Editing": 'UV 编辑',
      "2D Animation": '2D 动画',
      "2D Full Canvas": '2D 全画布',
      "Motion Tracking": '动作跟踪',
      "Masking": '遮罩',
      "Video Editing": '视频编辑'
  }
  workspace_dict_english = {}

  @classmethod
  def register(cls):
    cls.__generate_dict_english()
    cls.__update_workspace_name_timer()
    bpy.app.handlers.load_post.append(cls.__update_workspace_name_timer)

  @classmethod
  def unregister(cls):
    bpy.app.handlers.load_post.remove(cls.__update_workspace_name_timer)

  @classmethod
  def __generate_dict_english(cls):
    for key in cls.workspace_dict_chinese:
      value = cls.workspace_dict_chinese[key]
      cls.workspace_dict_english[value] = key

  @classmethod
  @bpy.app.handlers.persistent
  def __update_workspace_name_timer(cls, arg1=None, arg2=None):
    bpy.app.timers.register(cls.update_workspace_name)

  @classmethod
  def update_workspace_name(cls):
    dict = cls.workspace_dict_chinese \
        if bpy.context.preferences.view.use_translate_interface \
        else cls.workspace_dict_english
    for workspace in bpy.data.workspaces:
      if workspace.name in dict:
        workspace.name = dict[workspace.name]


class BLT_Translation(bpy.types.Operator):
  bl_idname = "blt.translation"
  bl_label = "切换中英文"
  bl_description = "一键切换中英文"

  def execute(self, context):
    view = context.preferences.view
    # ---------------------------------------------------------------------------
    # 修复 Blender 4.0 更新语言配置文件导致错误
    if bpy.app.translations.locale not in ['zh_CN', "zh_HANS"]:
      view.language = "zh_CN" if "zh_CN" in bpy.app.translations.locales else "zh_HANS"
    # ---------------------------------------------------------------------------
      view.use_translate_tooltips = False
      view.use_translate_interface = False
      view.use_translate_new_dataname = False
    preferences = BLT_Utils.get_preferences()
    if preferences.tooltips_included:
      view.use_translate_tooltips = not view.use_translate_interface
    if preferences.new_dataname_included:
      view.use_translate_new_dataname = not view.use_translate_interface
    view.use_translate_interface = not view.use_translate_interface
    # 更新工作空间界面
    BLT_TranslationWorkspace.update_workspace_name()
    return {"FINISHED"}
