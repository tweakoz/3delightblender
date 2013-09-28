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

import bpy
import math
import blf


# global dictionaries
from .shader_parameters import exclude_lamp_params

# helper functions for parameters
from .shader_parameters import get_shader_pointerproperty
from .shader_parameters import rna_to_shaderparameters
from .shader_parameters import shader_type_initialised
from .shader_parameters import tex_optimised_path
from .shader_parameters import tex_source_path


# Use some of the existing buttons.
import bl_ui.properties_render as properties_render
properties_render.RENDER_PT_render.COMPAT_ENGINES.add('3DELIGHT_RENDER')
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('3DELIGHT_RENDER')
properties_render.RENDER_PT_output.COMPAT_ENGINES.add('3DELIGHT_RENDER')
properties_render.RENDER_PT_post_processing.COMPAT_ENGINES.add('3DELIGHT_RENDER')
del properties_render

import bl_ui.properties_material as properties_material
properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add('3DELIGHT_RENDER')
# properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add('3DELIGHT_RENDER')
properties_material.MATERIAL_PT_custom_props.COMPAT_ENGINES.add('3DELIGHT_RENDER')
del properties_material

import bl_ui.properties_data_lamp as properties_data_lamp
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add('3DELIGHT_RENDER')
properties_data_lamp.DATA_PT_spot.COMPAT_ENGINES.add('3DELIGHT_RENDER')
del properties_data_lamp

# enable all existing panels for these contexts
import bl_ui.properties_data_mesh as properties_data_mesh
for member in dir(properties_data_mesh):
    subclass = getattr(properties_data_mesh, member)
    try: subclass.COMPAT_ENGINES.add('3DELIGHT_RENDER')
    except: pass
del properties_data_mesh

import bl_ui.properties_object as properties_object
for member in dir(properties_object):
    subclass = getattr(properties_object, member)
    try: subclass.COMPAT_ENGINES.add('3DELIGHT_RENDER')
    except: pass
del properties_object

import bl_ui.properties_data_mesh as properties_data_mesh
for member in dir(properties_data_mesh):
    subclass = getattr(properties_data_mesh, member)
    try: subclass.COMPAT_ENGINES.add('3DELIGHT_RENDER')
    except: pass
del properties_data_mesh

import bl_ui.properties_data_camera as properties_data_camera
for member in dir(properties_data_camera):
    subclass = getattr(properties_data_camera, member)
    try: subclass.COMPAT_ENGINES.add('3DELIGHT_RENDER')
    except: pass
del properties_data_camera

import bl_ui.properties_particle as properties_particle
for member in dir(properties_particle):
    if member == 'PARTICLE_PT_render': continue

    subclass = getattr(properties_particle, member)
    try: subclass.COMPAT_ENGINES.add('3DELIGHT_RENDER')
    except:  pass
del properties_particle


# ------- UI panel definitions -------


narrowui = 180


class RENDER_PT_3Delight_sampling(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Sampling"
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        
        #layout.prop(rm, "display_driver")
        
        split = layout.split()
        col = split.column()
        col.label("Pixel Samples:")
        row = col.row(align=True)
        row.prop(rm, "pixelsamples_x", text="X")
        row.prop(rm, "pixelsamples_y", text="Y")
        
        col.separator()
        
        col.label("Pixel Filter:")
        col.prop(rm, "pixelfilter", text="")
        row = col.row(align=True)
        row.prop(rm, "pixelfilter_x", text="Size X")
        row.prop(rm, "pixelfilter_y", text="Size Y")
        
        col.separator()
        
        col.prop(rm, "shadingrate")
        
        col = split.column()
        col.prop(rm, "depth_of_field")
        sub = col.column(align=True)
        sub.enabled = rm.depth_of_field
        sub.prop(rm, "fstop")
        
        col.separator()
        
        col.prop(rm, "motion_blur")
        sub = col.column(align=False)
        sub.enabled = rm.motion_blur
        sub.prop(rm, "motion_segments")
        
        scol = sub.column(align=True)
        scol.prop(rm, "shutter_open")
        scol.prop(rm, "shutter_close")
        
        scol = sub.column(align=True)
        scol.prop(rm, "shutter_efficiency_open")
        scol.prop(rm, "shutter_efficiency_close")

class CollectionPanel3dl():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (rd.engine in {'3DELIGHT_RENDER'})

    def _draw_collection(self, context, layout, ptr, name, operator, opcontext, prop_coll, prop_index):
        layout.label(name)
        row = layout.row()
        row.template_list(ptr, prop_coll, ptr, prop_index, rows=1)
        col = row.column(align=True)
        
        op = col.operator(operator, icon="ZOOMIN", text="")
        op.context = opcontext
        op.collection = prop_coll
        op.prop_index = prop_index
        op.defaultname = ''
        op.action = 'ADD'
        
        op = col.operator(operator, icon="ZOOMOUT", text="")
        op.context = opcontext
        op.collection = prop_coll
        op.prop_index = prop_index
        op.action = 'REMOVE'
        
        if hasattr(ptr, prop_coll) and len(getattr(ptr, prop_coll)) > 0 and getattr(ptr, prop_index) >= 0:
            item = getattr(ptr, prop_coll)[getattr(ptr, prop_index)]
            self.draw_item(layout, context, item)


class MESH_PT_3Delight_prim_vars(CollectionPanel3dl, bpy.types.Panel):
    bl_context = "data"
    bl_label = "Primitive Variables"

    def draw_item(self, layout, context, item):
        ob = context.object
        if context.mesh:
            geo = context.mesh
        layout.prop(item, "name")
        
        row = layout.row()
        row.prop(item, "data_source", text="Source")
        if item.data_source == 'VERTEX_COLOR':
            row.prop_search(item, "data_name", geo, "vertex_colors", text="")
        elif item.data_source == 'UV_TEXTURE':
            row.prop_search(item, "data_name", geo, "uv_textures", text="")
        elif item.data_source == 'VERTEX_GROUP':
            row.prop_search(item, "data_name", ob, "vertex_groups", text="")

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        if not context.mesh: return False
        return (rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        mesh = context.mesh
        rm = mesh.renderman
        
        self._draw_collection(context, layout, rm, "Primitive Variables:", "collection.add_remove",
                                        "mesh", "prim_vars", "prim_vars_index")

        layout.prop(rm, "export_default_uv")
        layout.prop(rm, "export_default_vcol")
        layout.prop(rm, "export_smooth_normals")
        

class RENDER_PT_renderman_output(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Renderman Output"
    bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        
        layout.prop(rm, "path_rib_output")
        layout.prop(rm, "output_action")
        layout.prop(rm, "display_driver")
        if rm.display_driver not in ('idisplay', 'AUTO'):
            layout.prop(rm, "path_display_driver_image")


class RENDER_PT_renderman_hider(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Hider"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        
        layout.prop(rm, "hider")
        
        if rm.hider == 'hidden':
            layout.prop(rm, "hidden_depthfilter")
            if rm.hidden_depthfilter == 'midpoint':
                layout.prop(rm, "hidden_midpointratio")

            layout.prop(rm, "hidden_jitter")
            layout.prop(rm, "hidden_samplemotion")
            layout.prop(rm, "hidden_extrememotiondof")
            layout.prop(rm, "hidden_maxvpdepth")
        elif rm.hider == 'raytrace':
            col = layout.column()
            col.active = rm.display_driver == 'idisplay'
            col.prop(rm, "raytrace_progressive")


class RENDER_PT_3Delight_environment(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Environment Variables"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        env = rm.env_vars
        
        layout.prop(env, "out")
        layout.prop(env, "shd")
        layout.prop(env, "ptc")
        layout.prop(env, "arc")

class RENDER_PT_3Delight_paths(CollectionPanel3dl, bpy.types.Panel):
    bl_context = "render"
    bl_label = "Search Paths"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_item(self, layout, context, item):
        layout.prop(item, "name")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        
        layout.prop(rm, "use_default_paths")
        layout.prop(rm, "use_builtin_paths")
        
        self._draw_collection(context, layout, rm, "Shader Paths:", "collection.add_remove",
                                        "scene", "shader_paths", "shader_paths_index")
        
        self._draw_collection(context, layout, rm, "Texture Paths:", "collection.add_remove",
                                        "scene", "texture_paths", "texture_paths_index")
        
        self._draw_collection(context, layout, rm, "Procedural Paths:", "collection.add_remove",
                                        "scene", "procedural_paths", "procedural_paths_index")
        
        self._draw_collection(context, layout, rm, "Archive Paths:", "collection.add_remove",
                                        "scene", "archive_paths", "archive_paths_index")

        layout.prop(rm, "path_3delight")
        layout.prop(rm, "path_renderer")
        layout.prop(rm, "path_shader_compiler")
        layout.prop(rm, "path_shader_info")
        layout.prop(rm, "path_texture_optimiser")
'''
class RENDER_PT_3Delight_render_passes(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Render Passes"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (rd.engine in {'3DELIGHT_RENDER'})

    def _draw_collection(self, layout, ptr, name, operator, prop_coll, prop_index):
        layout.label(name)
        row = layout.row()
        row.template_list(ptr, prop_coll, ptr, prop_index, rows=2)
        col = row.column(align=True)
        
        op = col.operator(operator, icon="ZOOMIN", text="")
        op.collection = prop_coll
        op.prop_index = prop_index
        op.defaultname = 'Pass'
        op.action = 'ADD'
        
        op = col.operator(operator, icon="ZOOMOUT", text="")
        op.collection = prop_coll
        op.prop_index = prop_index
        op.action = 'REMOVE'
        
        if hasattr(ptr, prop_coll) and getattr(ptr, prop_index) >= 0:
            entry = getattr(ptr, prop_coll)[getattr(ptr, prop_index)]
            layout.prop(entry, "name")
            layout.prop(entry, "type")
            layout.separator()
            layout.prop(entry, "motion_blur")
            layout.prop(entry, "surface_shaders")
            layout.prop(entry, "displacement_shaders")
            layout.prop(entry, "atmosphere_shaders")
            
 
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        
        self._draw_collection(layout, rm, "...", "collection.add_remove",
                                        "render_passes", "render_passes_index")
        
        layout.separator()
'''
class RENDER_PT_3Delight_performance(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Performance"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (context.scene.render.engine in cls.COMPAT_ENGINES)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rm = scene.renderman
        
        split = layout.split()
        col = split.column()
        col.prop(rm, "threads")
        col.prop(rm, "max_trace_depth")
        col.prop(rm, "max_eye_splits")
        #col.prop(rm, "recompile_shaders")
        

class ShaderPanel3dl():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}
    
    shader_type = 'surface'
    param_exclude = {}
    
    def found_shaders(self, context, rm):
        # pretty much guaranteed to have at least one surface shader...? weak
        return len(rm.surface_shaders.surface_shader_list_items(context)) > 3
        
        '''
        if self.shader_type == 'surface':
            return len(rm.surface_shaders.surface_shader_list_items(context)) > 3
        elif self.shader_type == 'displacement':
            return len(rm.displacement_shaders.displacement_shader_list_items(context)) > 3
        elif self.shader_type == 'interior':
            return len(rm.interior_shaders.interior_shader_list_items(context)) > 3
        else:
            return False
        '''
    
    def _draw_params(self, scene, rmptr, layout):

        # First update the stored parameters if they don't exist or are new

        if not shader_type_initialised(rmptr, self.shader_type):
            op = layout.operator("shading.refresh_shader_parameters", text="Init Shader Parameters", icon='ZOOMIN')
            op.shader_type = self.shader_type
            op.initialise_all = True
            return

        # Find the pointer to the shader parameters
        stored_shaders = getattr(rmptr, "%s_shaders" % self.shader_type)
        sptr = get_shader_pointerproperty(rmptr, self.shader_type)
        
        # Iterate and display all parameters stored for this shader
        for sp in rna_to_shaderparameters(scene, rmptr, self.shader_type):
            if sp.name not in self.param_exclude.keys():
                row = layout.row()
                row.prop(sptr, sp.pyname)
                
                if sp.data_type == 'string' and sp.gadgettype != 'optionmenu':
                    # check to see if it's a texture already
                    if getattr(sptr, sp.pyname) in [tex.name for tex in bpy.data.textures]:
                        op = row.operator("texture.convert_to_texture", text="", icon='TEXTURE')
                    else:
                        op = row.operator("texture.convert_to_texture", text="", icon='ZOOMIN')
                    op.propname = sp.pyname
                    op.shader_type = self.shader_type
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
      
        if cls.bl_context == 'data' and cls.shader_type == 'light':
            return (hasattr(context, "lamp") and context.lamp != None and rd.engine in {'3DELIGHT_RENDER'})
        elif cls.bl_context == 'world':
            return (hasattr(context, "world") and context.world != None and rd.engine in {'3DELIGHT_RENDER'})
        elif cls.bl_context == 'material':
            return (hasattr(context, "material") and context.material != None and rd.engine in {'3DELIGHT_RENDER'})



class WORLD_PT_3Delight_gi(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    bl_label = "Global Illumination"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}
    
    @classmethod
    def poll(cls, context):
        return (context.scene.render.engine in cls.COMPAT_ENGINES)
        
    def draw_header(self, context):
        rm = context.world.renderman
        self.layout.prop(rm, "global_illumination", text="")
    
    def draw(self, context):
        layout = self.layout
        rm = context.world.renderman
        
        col = layout.column()
        col.active = rm.global_illumination
        
        col.prop(rm.gi_primary.light_shaders, "active")
        
        if rm.gi_primary.light_shaders.active != 'gi_pointcloud':
            col.prop(rm.gi_secondary.light_shaders, "active")


class WORLD_PT_3Delight_gi_primary(ShaderPanel3dl, bpy.types.Panel):
    bl_context = "world"
    bl_label = "Primary GI"
    shader_type = 'light'
    

    def draw(self, context):
        layout = self.layout
        world = context.world
        rm = world.renderman
        scene = context.scene
        
        col = layout.column()
        col.active = rm.global_illumination
        
        self._draw_params(scene, rm.gi_primary, col)

class WORLD_PT_3Delight_gi_photons(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    
    bl_context = "world"
    bl_label = "Photons"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}
    
    @classmethod
    def poll(cls, context):
        rm = context.world.renderman
        return ((context.scene.render.engine in cls.COMPAT_ENGINES) and
            (rm.gi_secondary.light_shaders.active == 'gi_photon' or rm.gi_primary.light_shaders.active == 'gi_photon') and rm.gi_primary.light_shaders.active != 'gi_pointcloud')

    def draw(self, context):
        layout = self.layout
        world = context.world
        rm = world.renderman
        scene = context.scene
        
        col = layout.column()
        col.active = rm.global_illumination
    
        col.prop(rm.gi_secondary, "photon_count")
        col.prop(rm.gi_secondary, "photon_map_global")
        col.prop(rm.gi_secondary, "photon_map_caustic")

class WORLD_PT_3Delight_gi_pointcloud(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    
    bl_context = "world"
    bl_label = "Point Cloud"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}
    
    @classmethod
    def poll(cls, context):
        rm = context.world.renderman
        return ((context.scene.render.engine in cls.COMPAT_ENGINES) and
            (rm.gi_secondary.light_shaders.active == 'gi_pointcloud' or rm.gi_primary.light_shaders.active == 'gi_pointcloud'))

    def draw(self, context):
        layout = self.layout
        world = context.world
        rm = world.renderman
        scene = context.scene
        
        col = layout.column()
        col.active = rm.global_illumination
    
        # unused as yet 
        #col.prop(rm.gi_secondary, "ptc_coordsys")
        
        col.prop(rm.gi_secondary, "ptc_path")
        col.prop(rm.gi_secondary, "ptc_generate_auto")
        subcol = col.column()
        subcol.active = rm.gi_secondary.ptc_generate_auto
        subcol.prop(rm.gi_secondary, "ptc_shadingrate")

# unused atm
''' 
class MATERIAL_MT_3Delight_preview_specials(bpy.types.Menu):
    bl_label = "3Delight Preview Specials"

    def draw(self, context):
        layout = self.layout
        rm = context.material.renderman
        #col = layout.column()
        #col.prop(rm, "preview_render_type", expand=True)
        #col.separator()
        col.prop(rm, "preview_render_shadow")
'''        

class MATERIAL_PT_3Delight_preview(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    
    bl_context = "material"
    bl_label = "Preview"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}

    @classmethod
    def poll(cls, context):
        return (context.scene.render.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        mat = context.material

        row = layout.row()
        row.template_preview(context.material, show_buttons=1)
        
        #col = row.column()
        #col.scale_x = 1.5
        #col.prop(rm, "preview_render_type", text="", expand=True)
        #col.menu("MATERIAL_MT_3Delight_preview_specials", icon='DOWNARROW_HLT', text="")
        


class MATERIAL_PT_3Delight_shader_surface(ShaderPanel3dl, bpy.types.Panel):
    bl_context = "material"
    bl_label = "Surface Shader"
    shader_type = 'surface'

    def draw(self, context):
        layout = self.layout
        mat = context.material
        rm = mat.renderman
        scene = context.scene
        
        if not self.found_shaders(context, rm):
            layout.label("Loading Shaders...")
            return

        row = layout.row()
        row.prop(rm.surface_shaders, "shader_list", text="")
        
        if rm.surface_shaders.shader_list == "custom":
            row.prop(rm.surface_shaders, "active", text="")
        row.operator("shading.refresh_shader_parameters", text="", icon='FILE_REFRESH').shader_type = self.shader_type

        layout.separator()
        
        row = layout.row()
        row.prop(mat, "diffuse_color")
        row.prop(mat, "alpha")
        
        layout.separator()
        
        self._draw_params(scene, mat.renderman, layout)

class MATERIAL_PT_3Delight_shader_displacement(ShaderPanel3dl, bpy.types.Panel):
    bl_context = "material"
    bl_label = "Displacement Shader"
    shader_type = 'displacement'

    def draw(self, context):
        layout = self.layout
        mat = context.material
        rm = mat.renderman
        scene = context.scene

        if not self.found_shaders(context, rm):
            layout.label("Loading Shaders...")
            return
        
        row = layout.row()
        row.prop(rm.displacement_shaders, "shader_list", text="")
        if rm.displacement_shaders.shader_list == "custom":
            row.prop(rm.displacement_shaders, "active", text="")
        row.operator("shading.refresh_shader_parameters", text="", icon='FILE_REFRESH').shader_type = self.shader_type

        layout.separator()
        
        layout.prop(rm, "displacementbound")
        
        layout.separator()
        
        self._draw_params(scene, mat.renderman, layout)

class MATERIAL_PT_3Delight_shader_interior(ShaderPanel3dl, bpy.types.Panel):
    bl_context = "material"
    bl_label = "Interior"
    shader_type = 'interior'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mat = context.material
        rm = mat.renderman
        scene = context.scene
        
        if not self.found_shaders(context, rm):
            layout.label("Loading Shaders...")
            return
        
        row = layout.row()
        row.prop(rm.interior_shaders, "shader_list", text="")
        if rm.interior_shaders.shader_list == "custom":
            row.prop(rm.interior_shaders, "active", text="")
        row.operator("shading.refresh_shader_parameters", text="", icon='FILE_REFRESH').shader_type = self.shader_type
 
        layout.separator()
               
        self._draw_params(scene, mat.renderman, layout)

class MATERIAL_PT_3Delight_shader_atmosphere(ShaderPanel3dl, bpy.types.Panel):
    bl_context = "material"
    bl_label = "Atmosphere"
    shader_type = 'atmosphere'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        mat = context.material
        rm = mat.renderman
        scene = context.scene
        
        layout.label(text="Atmosphere Shader")
        layout.prop(rm, "inherit_world_atmosphere")
        
        col = layout.column()
        col.active = not rm.inherit_world_atmosphere
        row = col.row()
        row.prop(rm.atmosphere_shaders, "active", text="")
        row.operator("shading.refresh_shader_parameters", text="", icon='FILE_REFRESH').shader_type = self.shader_type
        
        col.separator()
        
        self._draw_params(scene, mat.renderman, col)

class WORLD_PT_3Delight_shader_atmosphere(ShaderPanel3dl, bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    bl_label = "Atmosphere"
    shader_type = 'atmosphere'
    
    def draw(self, context):
        layout = self.layout
        world = context.world
        rm = world.renderman
        scene = context.scene
        
        layout.label(text="Atmosphere Shader")
        layout.prop(rm.atmosphere_shaders, "active", text="")
        
        layout.separator()
        
        self._draw_params(scene, world.renderman, layout)

class MATERIAL_PT_3Delight_sss(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_label = "Subsurface Scattering"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.material and rd.engine in {'3DELIGHT_RENDER'})

    def draw_header(self, context):
        rm = context.material.renderman
        self.layout.prop(rm, "sss_do_bake", text="")

    def draw(self, context):
        layout = self.layout
        rm = context.material.renderman
        
        split = layout.split()
        split.active = rm.sss_do_bake
        col = split.column()
        col.prop(rm, "sss_ior")
        col.prop(rm, "sss_scale")
        
        col.prop(rm, "sss_use_reflectance")
        sub = col.column()
        sub.active = rm.sss_use_reflectance
        sub.prop(rm, "sss_reflectance", text="")
        
        col.prop(rm, "sss_meanfreepath", expand=True)
        
        col = split.column()
        col.prop(rm, "sss_shadingrate")
        col.prop(rm, "sss_group")
        
        if rm.sss_do_bake:
            row = layout.row()
            row.label("Requires a shader with subsurface support", icon="INFO")
        

class MATERIAL_PT_3Delight_photons(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_label = "Photons"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.material and rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        rm = context.material.renderman
        
        col = layout.column()
        col.prop(rm, "photon_shadingmodel")

class TexturePanel3dl():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}
    
    @classmethod
    def poll(cls, context):
        tex = context.texture
        rd = context.scene.render
        return tex and (tex.type != 'NONE') and (context.scene.render.engine in cls.COMPAT_ENGINES)

class TEXTURE_PT_3Delight_back(TexturePanel3dl, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.operator("space.back_to_shader", icon='BACK')

class TEXTURE_PT_3Delight_image(TexturePanel3dl, bpy.types.Panel):
    bl_label = "Image Texture"
    
    def trim_path(self, context, path):
        size = blf.dimensions(0, path)[0]
        
        if size > context.region.width - 160:
            while size > context.region.width - 160:
                path = path[1:]
                size = blf.dimensions(0, path)[0]
            
            return '...' + path
        else:
            return path

    def draw(self, context):
        layout = self.layout
        tex = context.texture
        scene = context.scene
        rm = tex.renderman
        anim = rm.anim_settings
        
        col = layout.column()
        col.prop(tex, "name")
        col.prop(rm, "file_path")

        col.separator()
        col.prop(rm, "format")
        col.separator()
        
        col.prop(anim, "animated_sequence")
        if anim.animated_sequence:
            col.prop(anim, "blender_start")
            row = col.row()
            row.prop(anim, "sequence_in")
            row.prop(anim, "sequence_out")
            
            col.label("Current: %s" % self.trim_path(context, tex_source_path(tex, scene.frame_current)))
                    
        col.label("Generated Path: %s" % self.trim_path(context, tex_optimised_path(tex, scene.frame_current)))



class TEXTURE_PT_3Delight_image_sampling(TexturePanel3dl, bpy.types.Panel):
    bl_label = "Sampling"

    def draw(self, context):
        layout = self.layout
        rm = context.texture.renderman
        
        
        split = layout.split()
        
        col = split.column()
        col.label("Wrapping:")
        col.prop(rm, "wrap_s", text="S")
        col.prop(rm, "wrap_t", text="T")
        
        col.prop(rm, "flip_s")
        col.prop(rm, "flip_t")
        
        
        col = split.column()
        col.label("Downsampling Filter:")
        col.prop(rm, "filter_type", text="")
        if rm.filter_type in ('catmull-rom', 'bessel'):
            col.prop(rm, "filter_window")

        col.label("Filter Width:")
        row = col.row(align=True)
        row.prop(rm, "filter_width_s", text="S")
        row.prop(rm, "filter_width_t", text="T")
        col.prop(rm, "filter_blur")
        
class TEXTURE_PT_3Delight_image_color(TexturePanel3dl, bpy.types.Panel):
    bl_label = "Color"
    
    def draw(self, context):
        layout = self.layout
        rm = context.texture.renderman
        
        col = layout.column()
        
        col.label("Source:")
        col.prop(rm, "input_color_space", text="Color Space")
        if rm.input_color_space == 'GAMMA':
            col.prop(rm, "input_gamma", text="Gamma")
            
        col.separator()
        
        col.label("Output:")
        col.prop(rm, "output_color_depth", text="Color Depth")
        col.prop(rm, "output_compression", text="Compression")

class TEXTURE_PT_3Delight_image_generate(TexturePanel3dl, bpy.types.Panel):
    bl_label = "Auto-Generate Optimized"

    def draw_header(self, context):
        rm = context.texture.renderman
        self.layout.prop(rm, "auto_generate_texture", text="")

    def draw(self, context):
        layout = self.layout
        rm = context.texture.renderman
        
        col = layout.column()
        col.active = rm.auto_generate_texture
        col.label("Auto-generate optimized texture if output is:")
        col.prop(rm, "generate_if_nonexistent", text="Non-existent in folder")
        col.prop(rm, "generate_if_older", text="Older than source texture")
        col.separator()
        col.operator("texture.generate_optimised", text="Generate Now", icon='FILE_IMAGE')


class DATA_PT_3Delight_lamp(ShaderPanel3dl, bpy.types.Panel):
    bl_context = "data"
    bl_label = "Lamp"
    shader_type = 'light'
    param_exclude = exclude_lamp_params
    
    def draw(self, context):
        layout = self.layout

        lamp = context.lamp
        rm = context.lamp.renderman
        scene = context.scene
        wide_ui = context.region.width > narrowui

        col = layout.column()
        col.prop(rm.light_shaders, "active")
        sub = col.column()
        sub.active = rm.light_shaders.active not in \
            ('shadowspot', 'spotlight', 'pointlight', 'h_distantshadow', 'ambientlight')

        if wide_ui:            
            sub.row().prop(lamp, "type", expand=True)
        else:
            sub.prop(lamp, "type", text="")

        split = layout.split()

        col = split.column()
        col.prop(lamp, "color", text="")
        col.prop(rm, "emit_photons")
        
        col = split.column()
        col.prop(lamp, "energy")
        
        self._draw_params(scene, lamp.renderman, layout)
        

class DATA_PT_3Delight_lamp_shadow(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Shadow"
    
    def _check_mapsize(self, lamp):
        if lamp.type != 'SPOT' or lamp.renderman.shadow_method != 'SHADOW_MAP':
            return
    
        # round shadow map size to nearest power of 2
        bufsize = lamp.shadow_buffer_size
        exp = int(math.log(bufsize, 2))
        lamp.shadow_buffer_size = int(math.pow(2, exp))
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        try:
            lamp = context.lamp
            rm = lamp.renderman
        except:
            return False

        if not context.lamp: return False

        if rd.engine not in {'3DELIGHT_RENDER'}:
            return False
        
        if rm.light_shaders.active == '':
            if lamp.type not in ('SPOT', 'SUN', 'POINT'): return False
        else:
            if rm.light_shaders.active.find('shadow') == -1: return False
        return True

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp
        rm = lamp.renderman
        wide_ui = context.region.width > narrowui

        layout.prop(rm, "shadow_method", expand=True)

        if rm.shadow_method == 'SHADOW_MAP':
            layout.prop(rm, "shadow_map_generate_auto")
            
            col = layout.column()
            col.active = rm.shadow_map_generate_auto
            col.prop(rm, "shadow_transparent")
            col.prop(rm, "shadow_map_resolution")
            col.prop(rm, "shadingrate")
            
            if rm.shadow_transparent:
                row = col.row()
                row.prop(rm, "pixelsamples_x")
                row.prop(rm, "pixelsamples_y")
                
            if lamp.type == 'SPOT':
                split = col.split()
                subcol = split.column()
                subcol.prop(lamp, "shadow_buffer_clip_start", text="Clip Start")
                subcol = split.column()
                subcol.prop(lamp, "shadow_buffer_clip_end", text="Clip End")  
            elif lamp.type == 'SUN':
                subcol = col.column()
                subcol.prop(rm, "ortho_scale")
                subcol.prop(lamp, "distance")
            col.separator()
            col.prop(rm, "path_shadow_map")
            
        elif rm.shadow_method == 'RAYTRACED':
            pass

class OBJECT_PT_3Delight_object_geometry(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Renderman Geometry"
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.object and rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        ob = context.object
        rm = ob.renderman
        anim = rm.archive_anim_settings
        
        col = layout.column()
        
        col.prop(rm, "geometry_source")
        
        if rm.geometry_source in ('ARCHIVE', 'DELAYED_LOAD_ARCHIVE'):
            col.prop(rm, "path_archive")
            
            col.prop(anim, "animated_sequence")
            if anim.animated_sequence:
                col.prop(anim, "blender_start")
                row = col.row()
                row.prop(anim, "sequence_in")
                row.prop(anim, "sequence_out")

        elif rm.geometry_source == 'PROCEDURAL_RUN_PROGRAM':
            col.prop(rm, "path_runprogram")
            col.prop(rm, "path_runprogram_args")
        elif rm.geometry_source == 'DYNAMIC_LOAD_DSO':
            col.prop(rm, "path_dso")
            col.prop(rm, "path_dso_initial_data")
            
        if rm.geometry_source in ('DELAYED_LOAD_ARCHIVE', 'PROCEDURAL_RUN_PROGRAM', 'DYNAMIC_LOAD_DSO'):
            col.prop(rm, "procedural_bounds")
            
            if rm.procedural_bounds == 'MANUAL':
                colf = layout.column_flow()
                colf.prop(rm, "procedural_bounds_min")
                colf.prop(rm, "procedural_bounds_max")

        if rm.geometry_source == 'BLENDER_SCENE_DATA':
            col.prop(rm, "primitive")
    
            colf = layout.column_flow()
    
            if rm.primitive in ('CONE', 'DISK'):
                colf.prop(rm, "primitive_height")        
            if rm.primitive in ('SPHERE', 'CYLINDER', 'CONE', 'DISK'):
                colf.prop(rm, "primitive_radius")
            if rm.primitive == 'TORUS':
                colf.prop(rm, "primitive_majorradius")
                colf.prop(rm, "primitive_minorradius")
                colf.prop(rm, "primitive_phimin")
                colf.prop(rm, "primitive_phimax")
            if rm.primitive in ('SPHERE', 'CYLINDER', 'CONE', 'TORUS'):
                colf.prop(rm, "primitive_sweepangle")
            if rm.primitive in ('SPHERE', 'CYLINDER'):
                colf.prop(rm, "primitive_zmin")
                colf.prop(rm, "primitive_zmax")
            if rm.primitive == 'POINTS':
                colf.prop(rm, "primitive_point_type")
                colf.prop(rm, "primitive_point_width")
                    
            col.prop(rm, "export_archive")
            #if rm.export_archive:                
            #    col.prop(rm, "export_archive_path")
        

        col = layout.column()
        col.prop(rm, "export_coordsys")
        
        row = col.row()
        row.prop(rm, "motion_segments_override", text="")
        sub = row.row()
        sub.active = rm.motion_segments_override
        sub.prop(rm, "motion_segments")        

                
class OBJECT_PT_3Delight_object_render_shading(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Renderman Shading"
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.object and rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        ob = context.object
        rm = ob.renderman
        
        col = layout.column()
        col.prop(rm, "shadinginterpolation", text="Interpolation")
        
        row = col.row()
        row.prop(rm, "shadingrate_override", text="")
        sub = row.row()
        sub.active = rm.shadingrate_override
        sub.prop(rm, "shadingrate")

        col.separator()

        col.prop(rm, "geometric_approx_motion")
        col.prop(rm, "geometric_approx_focus")


class OBJECT_PT_3Delight_object_render(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Renderman Visibility"
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.object and rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        ob = context.object
        rm = ob.renderman
        
        col = layout.column()
        col.prop(rm, "visibility_camera", text="Camera")
        row = col.row()
        row.prop(rm, "visibility_trace_diffuse", text="Diffuse Rays")
        row.prop(rm, "trace_diffuse_hitmode", text="")
        
        row = col.row()
        row.prop(rm, "visibility_trace_specular", text="Specular Rays")
        row.prop(rm, "trace_specular_hitmode", text="")
        
        row = col.row()
        row.prop(rm, "visibility_trace_transmission", text="Transmission Rays")
        row.prop(rm, "trace_transmission_hitmode", text="")
        
        col.prop(rm, "visibility_photons", text="Photons")
        col.prop(rm, "visibility_shadowmaps", text="Shadow Maps")
        
        col.prop(rm, "trace_displacements")
        col.prop(rm, "trace_samplemotion")
        
        col.separator()
        
        col.prop(rm, "matte")

from bl_ui.properties_particle import ParticleButtonsPanel

class PARTICLE_PT_3Delight_particle(ParticleButtonsPanel, bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"
    bl_label = "Render"
    COMPAT_ENGINES = {'3DELIGHT_RENDER'}

    def draw(self, context):
        layout = self.layout
        
        # XXX todo: handle strands properly
        
        psys = context.particle_system
        rm = psys.settings.renderman
        
        col = layout.column()
        col.prop(rm, "material_id")
        
        if psys.settings.type == 'EMITTER':
            col.row().prop(rm, "particle_type", expand=True)
            if rm.particle_type == 'OBJECT':
                col.prop_search(rm, "particle_instance_object", bpy.data, "objects", text="")

        # XXX: if rm.type in ('sphere', 'disc', 'patch'):
        # implement patchaspectratio and patchrotation   
        
        split = layout.split()
        col = split.column()
        
        #if (psys.settings.type == 'EMITTER' and rm.particle_type == 'particle') or psys.settings.type == 'HAIR':
        col.prop(rm, "constant_width")
        subcol = col.column()
        subcol.active = rm.constant_width
        subcol.prop(rm, "width")


class PARTICLE_PT_3Delight_prim_vars(CollectionPanel3dl, bpy.types.Panel):
    bl_context = "particle"
    bl_label = "Primitive Variables"

    def draw_item(self, layout, context, item):
        ob = context.object
        layout.prop(item, "name")
        
        row = layout.row()
        row.prop(item, "data_source", text="Source")
        
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        if not context.particle_system: return False
        return (rd.engine in {'3DELIGHT_RENDER'})

    def draw(self, context):
        layout = self.layout
        psys = context.particle_system
        rm = psys.settings.renderman
        
        self._draw_collection(context, layout, rm, "Primitive Variables:", "collection.add_remove",
                                        "particle_system.settings", "prim_vars", "prim_vars_index")

        layout.prop(rm, "export_default_size")

def register():
    pass
     #bpy.utils.register_module(__name__)

def unregister():
    pass
     #bpy.utils.unregister_module(__name__)
