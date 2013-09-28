# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2011 Matt Ebb
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
#
# ##### END MIT LICENSE BLOCK #####

bl_info = {
    "name": "3Delight",
    "author": "Matt Ebb",
    "version": (0, 7, 6),
    "blender": (2, 6, 3),
    "location": "Info Header (engine dropdown)",
    "description": "3Delight (renderman) integration",
    "warning": "",
    "wiki_url": "http://mattebb.com/3delightblender/",
    "tracker_url": "http://mattebb.com/3delightblender/",
    "category": "Render"}

if "bpy" in locals():
    import imp
    imp.reload(properties)
    imp.reload(ui)
    imp.reload(operators)
    imp.reload(export)
else:
    import bpy
    from . import properties
    from . import ui
    from . import operators
    from . import export

class Render3Delight(bpy.types.RenderEngine):
    bl_idname = '3DELIGHT_RENDER'
    bl_label = "3Delight"
    bl_use_preview = True
    
    def __init__(self):
        export.init(self)
        
    def __del__(self):
        export.free(self)

    # main scene render
    def update(self, data, scene):
        export.update(self, data, scene)

    def render(self, scene):
        export.render(self)

    # preview render - nonexistent yet
    #def preview_update(self, context, id):
    #    export.update_preview(self, data, scene)
    #
    #def preview_render(self):
    #    export.render_preview(self)

    # viewport render
    # def view_update(self, context):
    #    pass   
    # def view_draw(self, context):
    #    pass


def register():
    properties.register()
    operators.register()
    export.register()
    bpy.utils.register_module(__name__)


def unregister():
    properties.unregister()
    ui.unregister()
    operators.unregister()
    export.unregister()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
