from . import auto_load

bl_info = {
    "name": "BLT 插件",
    "author": "keshi, pjwaixingren",
    "description": "这是 BLT 软件的插件版本",
    "blender": (2, 80, 0),
    "version": (0, 2, 20231224),
    "location": "偏好设置",
    "category": "Generic",
    "wiki_url": "https://www.pjcgart.com",
    "tracker_url": "https://blt.qa.pjcgart.com"
}

auto_load.init()


def register():
  auto_load.register()


def unregister():
  auto_load.unregister()
