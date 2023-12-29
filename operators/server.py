import os
import subprocess
import sys
from threading import Thread

import bpy

from ..modules.websocket import create_connection
from ..modules.websocket_server import WebsocketServer
from ..utils import BLT_Info


# BLT 导入工具类
class BLT_Import_Utils:

  # 导入对象
  @staticmethod
  def import_object(blender_file_path, object_name):
    # 加载对象
    with bpy.data.libraries.load(blender_file_path) as (data_from, data_to):
      data_to.objects = data_from.objects
      data_to.collections = data_from.collections
    # 判断对象是否存在
    has_object = any(obj.name == object_name for obj in data_to.objects)
    has_collection = any(
        collection.name == object_name for collection in data_to.collections)
    collection_name = object_name
    # 如果对象存在则导入指定对象
    if has_object and not has_collection:
      for object in data_to.objects:
        if object.name == collection_name:
          bpy.context.scene.collection.objects.link(object)
    # 如果对象和对象不同时存在则导入指定集合
    elif has_object != has_collection:
      for collection in data_to.collections:
        if collection.name == collection_name:
          bpy.context.scene.collection.children.link(collection)
    # 如果对象和集合都不存在则导入所有集合
    else:
      for collection in data_to.collections:
        bpy.context.scene.collection.children.link(collection)

  # 导入集合
  @staticmethod
  def import_collection(blender_file_path, object_name):
    collection_name = object_name
    # 加载集合
    with bpy.data.libraries.load(blender_file_path) as (data_from, data_to):
      data_to.objects = data_from.objects
      data_to.collections = data_from.collections
    # 判断集合是否存在
    for collection in data_to.collections:
      # 如果集合存在则导入指定集合
      if collection.name == collection_name:
        bpy.context.scene.collection.children.link(collection)

  # 导入材质
  @staticmethod
  def import_material(blender_file_path, object_name):
    # 加载材质
    with bpy.data.libraries.load(blender_file_path) as (data_from, data_to):
      data_to.materials = data_from.materials
    # 判断材质是否存在
    for material in data_to.materials:
      # 如果材质存在则导入指定材质
      if material.name == object_name:
        print("import now!!!")

  # 导入 HDRI
  @staticmethod
  def import_hdri(blender_file_path):
    # 设置变量
    word = bpy.data.worlds['World']
    word.use_nodes = True
    nodes = word.node_tree.nodes
    links = word.node_tree.links
    # 移除 HDR 节点
    for node in nodes:
      nodes.remove(node)
    # 添加 HDR 环境贴图坐标节点
    coordinate = nodes.new(type="ShaderNodeTexCoord")
    coordinate.location = (0, 0)
    # 添加 HDR 环境贴图映射节点
    mapping = nodes.new(type="ShaderNodeMapping")
    mapping.vector_type = "TEXTURE"
    mapping.inputs['Rotation'].default_value = (0, 0, 3.141593)
    mapping.location = (300, 0)
    # 添加 HDR 环境贴图节点
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.image = bpy.data.images.load(blender_file_path)
    environment.location = (600, 0)
    # 添加 HDR 背景节点
    background = nodes.new("ShaderNodeBackground")
    background.location = (900, 0)
    # 添加 HDR 输出节点
    output = nodes.new("ShaderNodeOutputWorld")
    output.location = (1200, 0)
    # 链接节点
    links.new(coordinate.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], environment.inputs['Vector'])
    links.new(environment.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])

  # 导入 BVH
  @staticmethod
  def import_bvh(blender_file_path):
    # 获取文件路径
    exe_path = sys.argv[0]
    blend_file_path = blender_file_path[:-4] + ".blend"
    armature_name = blender_file_path[:-4].split("/")[-1]
    main_path = os.path.abspath(os.path.dirname(
        os.path.split(os.path.realpath(__file__))[0]))
    # 获取资源高度
    resource_hight = 2
    try:
      resource_hight = bpy.context.scene.anim_resource_armature.dimensions[2]
    except Exception as error:
      print("infoerr", error)
    # 文件路径
    import_script_path = main_path + "\\Anim\\operators\\bvh\\blt_import_bvh.py"
    render_file_path = main_path + "\\Anim\\operators\\bvh\\BLT_BVH.blend"
    # 文件内容
    data = r"""import bpy
bpy.data.scenes['Scene'].frame_start=0
bpy.data.scenes['Scene'].frame_end=0
bpy.ops.import_anim.bvh(filepath="%s",global_scale=0.1)
obj=bpy.context.selected_objects[0]
dim_y=%s/obj.dimensions[2]
bpy.ops.transform.resize(value=(dim_y,dim_y, dim_y), orient_type="GLOBAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", mirror=False, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
bpy.ops.wm.save_as_mainfile(filepath="%s")
bpy.ops.wm.quit_blender()
""" % (blender_file_path.replace("\\", "/"), resource_hight, blend_file_path)
    # 写入文件
    with open(import_script_path, 'w') as script:
      script.write(data)
    # 执行文件
    subprocess.run([exe_path, render_file_path, "--background",
                   "--python", import_script_path.replace("\\", "/")])
    # 加载对象
    with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
      data_to.objects = [
          name for name in data_from.objects if name == armature_name]
    # 获取对象
    armature = bpy.data.objects[armature_name]
    # 链接对象
    bpy.context.collection.objects.link(armature)
    # 设置对象
    bpy.context.scene.anim_target_armature = armature


# BLT 服务器
class BLT_Server(bpy.types.Operator):
  bl_idname = "blt.server"
  bl_label = "启动 BLT 服务器"

  # 新建客户端
  @classmethod
  def new_client(cls, _, server):
    server.send_message_to_all("Geterver")

  # 发送消息
  @classmethod
  def sendmsg(cls, msg):
    websocket = create_connection("ws://127.0.0.1:33333")
    info = '"%s": %s' % (bpy.context.scene.blt_message_objectname, msg)
    websocket.send(info)
    websocket.close()
    print(info)

  # 接收消息
  @classmethod
  def message_received(cls, _, server, message):
    message = message.encode('raw_unicode_escape').decode("utf-8")
    print(message)
    if message.find("FilePath:") != -1:
      bpy.context.scene.blt_message = message
      message = bpy.context.scene.blt_message
      file_type = message.split(":Filetype:")[1]
      blender_file_path = message.split(":Filetype:")[0].split("FilePath:")[1]
      object_name = blender_file_path.split("/")[-1].split(".")[0]
      bpy.context.scene.blt_message_objectname = object_name
      for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
          if area.type == 'VIEW_3D':
            # 导入对象
            if (file_type == "Object"):
              BLT_Import_Utils.import_object(blender_file_path, object_name)
            # 导入集合
            elif (file_type == "Collection"):
              BLT_Import_Utils.import_collection(
                  blender_file_path, object_name)
            # 导入材质
            elif (file_type == "Material"):
              BLT_Import_Utils.import_material(blender_file_path, object_name)
            # 导入 HDRI
            elif (file_type == "HDRI"):
              BLT_Import_Utils.import_hdri(blender_file_path)
            # 导入 BVH
            elif (file_type == "BVH"):
              BLT_Import_Utils.import_bvh(blender_file_path)
            # 渲染模式
            for space in area.spaces:
              if space.type == 'VIEW_3D' and file_type != "BVH":
                space.shading.type = 'RENDERED'

      # 发送消息
      thread = Thread(
          None, cls.sendmsg,
          args=["已经导入Blender(Blender Import Finished)!!!"])
      thread.setDaemon(True)
      thread.start()

    # 服务器返回信息
    if message.find("Blender(Blender Import Finished)") != -1:
      try:
        server.send_message_to_all(message)
      except Exception as e:
        print(e)

  # 启动服务器
  @classmethod
  def startServer(cls):
    try:
      server = WebsocketServer(BLT_Info.server_port, BLT_Info.server_ip)
      server.set_fn_new_client(cls.new_client)
      server.set_fn_message_received(cls.message_received)
      server.run_forever()
    except Exception as e:
      print(e)

  # 注册初始化
  @classmethod
  def register(cls) -> None:
    if sys.platform == 'win32':
      cls.thread = Thread(None, cls.startServer)
      cls.thread.setDaemon(True)
      cls.thread.start()
