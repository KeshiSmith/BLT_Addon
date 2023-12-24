import os
import shutil
import ssl
import sys
import time
import zipfile
from urllib import request

import bpy

# 不验证 SSL 证书
ssl._create_default_https_context = ssl._create_unverified_context


# BLT 信息类
class BLT_Info:

  # 插件名称
  addon_name = __package__
  # 插件根目录
  addon_root_path = os.path.dirname(os.path.realpath(__file__))
  # 插件 locale 目录
  addon_locale_path = os.path.join(addon_root_path, "locale")
  # 插件 icons 目录
  addon_icons_path = os.path.join(addon_root_path, "icons")

  # Bleder 全局目录
  blender_global_path = ""
  # Bleder 全局目录赋值
  if sys.platform == 'win32':
    blender_global_path = os.path.join(
        os.getenv("APPDATA"), "Blender Foundation", "Blender")
  elif sys.platform == 'darwin':
    blender_global_path = os.path.join(
        os.getenv("HOME"), "Library", "Application Support", "Blender")
  elif sys.platform == 'linux':
    blender_global_path = os.path.join(
        os.getenv("HOME"), ".config", "blender")
  else:
    raise Exception("不支持的系统平台: " + sys.platform)
  # Blender 版本号
  blender_base_version = "%d.%d" % (bpy.app.version[0], bpy.app.version[1])
  # Blender 全局版本路径
  blender_global_version_path = "%s/%s" % (blender_global_path,
                                           blender_base_version)
  # Blender 全局 datafiles 路径
  blender_global_datafile_path = os.path.join(
      blender_global_version_path, "datafiles")
  # Blender 全局 locale 路径
  blender_global_locale_path = os.path.join(
      blender_global_datafile_path, "locale")

  # BLT 路径
  blt_path = os.path.join(blender_global_path, "BLT_translation_Dicts")
  # BLT info 路径
  blt_info_path = os.path.join(blt_path, "info")
  # BLT datafiles 路径
  blt_datafiles_path = os.path.join(blt_path, "datafiles")
  # BLT locale 路径
  blt_locale_path = os.path.join(blt_datafiles_path, "locale")

  # 文档链接
  url_document = "https://pjcgart.com/2019/04/10/blt/"
  # 问答链接
  url_question_and_answer = "https://blt.qa.pjcgart.com/"

  # 服务器 IP
  server_ip = "localhost"
  # 服务器端口
  server_port = 33333


# BLT 工具类
class BLT_Utils:

  # 获取插件偏好设置
  @staticmethod
  def get_preferences():
    return bpy.context.preferences.addons[BLT_Info.addon_name].preferences

  @staticmethod
  # 文件夹不存在递归创建文件夹
  def makedirs_if_not_exists(path):
    if not os.path.exists(path):
      os.makedirs(path)

  @staticmethod
  # 获取 info 中 BLT 可执行文件位置
  def get_exe_path_from_info():
    info_path = os.path.join(BLT_Info.blt_info_path, "BLT_Version.info")
    blt_exe_path = ""
    if os.path.exists(info_path):
      with open(info_path, "r", encoding="utf-8", errors="ignore") as info:
        # 根据 BLT_Version 文件格式设置字符串切片 [8:-1]
        blt_exe_path = info.readline()[8:-1]
    return blt_exe_path

    # BLT 是否运行中
  @staticmethod
  def blt_is_running():
    tasklist_result = os.popen("tasklist")
    tasklist_stream = tasklist_result._stream
    tasklist = tasklist_stream.buffer.read().decode(
        encoding="utf-8", errors="ignore")
    return tasklist.find("BLT_") != -1

  @staticmethod
  # 是否已启用全局翻译
  def is_enabled_global_translation():
    return os.path.exists(BLT_Info.blender_global_locale_path)

  @staticmethod
  # 移除全局翻译
  def remove_global_translation():
    shutil.rmtree(BLT_Info.blender_global_locale_path)

  @staticmethod
  # 获取全局翻译
  def enable_global_translation():
    # 移除旧版翻译
    if os.path.exists(BLT_Info.blt_datafiles_path):
      shutil.rmtree(BLT_Info.blt_datafiles_path)
    # 检查并创建 blt_path
    BLT_Utils.makedirs_if_not_exists(BLT_Info.blt_path)
    datafiles_zip_path = os.path.join(BLT_Info.blt_path, "datafiles.zip")
    # 判断翻译文件是否存在且过期 (300秒过期)
    if not os.path.exists(datafiles_zip_path) or os.path.isfile(
            datafiles_zip_path) and time.time() - os.path.getmtime(
            datafiles_zip_path) > 300:
      # 存在过期文件时删除
      if os.path.exists(datafiles_zip_path):
        os.remove(datafiles_zip_path)
      # 下载翻译文件
      webpath = "http://raw.pjcgart.com/blt_Translation/mo/datafiles.zip"
      request.urlretrieve(webpath, datafiles_zip_path)
    # 解压翻译文件
    zip_file = zipfile.ZipFile(datafiles_zip_path)
    zip_list = zip_file.namelist()
    for f in zip_list:
      zip_file.extract(f, BLT_Info.blt_path)
    zip_file.close()
    # 复制翻译文件
    BLT_Utils.makedirs_if_not_exists(BLT_Info.blender_global_datafile_path)
    shutil.copytree(
        BLT_Info.blt_locale_path,
        BLT_Info.blender_global_locale_path)
