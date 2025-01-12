# -*- coding: utf8 -*-
# python
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {"name": "NFS Texture Helper",
           "author": "CDMJ + XXJOHNATHANXX",
           "version": (1, 3, 0),
           "blender": (4, 3, 2),
           "location": "Toolbar > NFS Helper",
           "description": "helper panel for texture alpha assignment and shadows",
           "warning": "",
           "category": "Object"}
            
import bpy

def set_material_render_method(material, method):
    """Set the render method for the given material."""
    if material:
        if method == 'HASHED':
            material.blend_method = 'HASHED'
            if hasattr(material, 'shadow_mode'):
                material.shadow_mode = 'HASHED'
        elif method == 'BLEND':
            material.blend_method = 'BLEND'
            if hasattr(material, 'shadow_mode'):
                material.shadow_mode = 'BLEND'
        material.show_transparent_back = True

class OBJECT_OT_group_alpha_connect(bpy.types.Operator):
    """Connect Texture Node Alpha to Alpha BDSF"""
    bl_idname = "object.group_alpha_connect"


    bl_label = "Connect Selected Alpha to Alpha BDSF"
    bl_options = { 'REGISTER', 'UNDO' }
    
    def execute(self, context):
        active_object = bpy.context.active_object

        # Check if there's an active material and it has nodes
        if active_object is not None and active_object.active_material is not None and active_object.active_material.use_nodes:
            active_material = active_object.active_material
            node_tree = active_material.node_tree
    
            # Find the Principled BSDF node
            principled_node = None
            for node in node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled_node = node
                    break
    
        # Find the first texture node with an alpha channel
            texture_node = None
            for node in node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    if node.image is not None and 'Alpha' in node.outputs:
                        texture_node = node
                        break
    
        # Connect the alpha output of the texture node to the Principled BSDF node
            if principled_node is not None and texture_node is not None:
                node_tree.links.new(texture_node.outputs['Alpha'], principled_node.inputs['Alpha'])
            return {'FINISHED'}  

class OBJECT_OT_group_texstraight(bpy.types.Operator):
    """Set Texture Straight"""
    bl_idname = "object.group_texstraight"
    
    bl_label = "Set Selected material texture alpha mode to straight"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        active_object = bpy.context.active_object
            
        for node in active_object.active_material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                node.image.alpha_mode = 'STRAIGHT'
                    
        return {'FINISHED'}   

class OBJECT_OT_group_alpha_premultiply(bpy.types.Operator):
    """Set Alpha PreMultiply"""
    bl_idname = "object.group_premultiply"


    bl_label = "Set Selected to Alpha PreMultiply"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.active_material is None:
                continue
            
            for node in obj.active_material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    node.image.alpha_mode = 'PREMUL'       
                
        return {'FINISHED'} 

class OBJECT_OT_group_alpha_blended(bpy.types.Operator):
    """Set Alpha Blend"""
    bl_idname = "object.group_blended"
    bl_label = "Set Selected to Alpha Blended"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        material = context.object.active_material
        if material:
            try:
                set_material_render_method(material, 'BLEND')
                self.report({"INFO"}, f"Set {material.name} to Blended")
            except AttributeError as e:
                self.report({"ERROR"}, f"Failed to set Blended: {str(e)}")
        else:
            self.report({"WARNING"}, "No active material found")
        return {'FINISHED'}

class OBJECT_OT_group_alpha_dithered(bpy.types.Operator):
    """Set Alpha Hashed"""
    bl_idname = "object.group_dithered"
    bl_label = "Set Selected to Alpha Dithered/Hashed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        material = context.object.active_material
        if material:
            try:
                set_material_render_method(material, 'HASHED')
                self.report({"INFO"}, f"Set {material.name} to Hashed")
            except AttributeError as e:
                self.report({"ERROR"}, f"Failed to set Hashed: {str(e)}")
        else:
            self.report({"WARNING"}, "No active material found")
        return {'FINISHED'}

class OBJECT_OT_group_alpha_clip(bpy.types.Operator):
    """Set Shader to Alpha Clip"""
    bl_idname = "object.group_clip"
    bl_label = "Set Selected to Alpha Clip"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        active_object = context.active_object
        active_material = active_object.active_material
        if not active_material or not active_material.use_nodes:
            self.report({'ERROR'}, "Active object does not have a material with nodes.")
            return {'CANCELLED'}

        # Get the node tree
        node_tree = active_material.node_tree
        nodes = node_tree.nodes
        links = node_tree.links

        # Find the texture and BSDF nodes
        texture_node = None
        bsdf_node = None

        for node in nodes:
            if node.type == 'TEX_IMAGE' and texture_node is None:
                texture_node = node
            if node.type == 'BSDF_PRINCIPLED' and bsdf_node is None:
                bsdf_node = node

        if not texture_node:
            self.report({'ERROR'}, "No Image Texture node found in the material.")
            return {'CANCELLED'}

        if not bsdf_node:
            self.report({'ERROR'}, "No Principled BSDF node found in the material.")
            return {'CANCELLED'}

        # Check if a Math 'Greater Than' node already exists
        math_node = next((node for node in nodes if node.type == 'MATH' and node.operation == 'GREATER_THAN'), None)

        if not math_node:
            # Create a new Math node
            math_node = nodes.new(type='ShaderNodeMath')
            math_node.operation = 'GREATER_THAN'
            math_node.inputs[0].default_value = 0.0  # Value
            math_node.inputs[1].default_value = 0.0  # Threshold
            math_node.label = "Alpha Greater Than"
            math_node.location = (
                (texture_node.location[0] + bsdf_node.location[0]) / 2,
                (texture_node.location[1] + bsdf_node.location[1]) / 2
            )

        # Connect the nodes
        if not any(link.to_node == math_node and link.from_node == texture_node for link in links):
            # Texture's Alpha -> Math Node Input 0
            links.new(texture_node.outputs['Alpha'], math_node.inputs[0])

        if not any(link.to_node == bsdf_node and link.from_node == math_node for link in links):
            # Math Node Output -> BSDF Alpha Input
            links.new(math_node.outputs['Value'], bsdf_node.inputs['Alpha'])

        self.report({'INFO'}, "Shader addition for Alpha Clip created successfully.")
        return {'FINISHED'}

class OBJECT_OT_group_alpha_clip_remove(bpy.types.Operator):
    """Remove Alpha Clip Shader Setup"""
    bl_idname = "object.group_clip_remove"
    bl_label = "Remove Shader Addition for Alpha Clip"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get the active object
        active_object = context.active_object

        if not active_object:
            self.report({'ERROR'}, "No active object found.")
            return {'CANCELLED'}

        # Ensure the active object has an active material with nodes enabled
        active_material = active_object.active_material
    #    if not active_material or not active_material.use_nodes:
    #        self.report({'ERROR'}, "Active object does not have a material with nodes.")
    #        return {'CANCELLED'}

        # Get the node tree
        node_tree = active_material.node_tree
        nodes = node_tree.nodes
        links = node_tree.links

        # Find the texture and BSDF nodes
        texture_node = None
        bsdf_node = None
        math_node = None

        for node in nodes:
            if node.type == 'TEX_IMAGE' and texture_node is None:
                texture_node = node
            if node.type == 'BSDF_PRINCIPLED' and bsdf_node is None:
                bsdf_node = node
            if node.type == 'MATH' and node.operation == 'GREATER_THAN':
                math_node = node

        if not texture_node or not bsdf_node or not math_node:
            self.report({'ERROR'}, "Required nodes not found in the material.")
            return {'CANCELLED'}

        # Remove links to/from the Math node
        for link in links:
            if link.to_node == math_node or link.from_node == math_node:
                links.remove(link)

        # Connect Texture node directly to BSDF node
        links.new(texture_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])

        # Remove the Math node
        nodes.remove(math_node)

        self.report({'INFO'}, "Shader addition for Alpha Clip removed successfully.")
        return {'FINISHED'}

class OBJECT_OT_group_texinterp(bpy.types.Operator):
    """Change Texture Interpolation"""

    bl_idname = "object.group_texinterp"
    bl_label = "CYCLE TEXT INTERP"
    bl_options = {'REGISTER', 'UNDO'}

    interpolation_modes = ['Linear', 'Closest', 'Cubic', 'Smart']

    def execute(self, context):
        active_material = context.active_object.active_material

        for node in active_material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                # Cycle to the next interpolation mode
                next_mode_index = (self.interpolation_modes.index(node.interpolation) + 1) % len(self.interpolation_modes)
                next_mode = self.interpolation_modes[next_mode_index]
                node.interpolation = next_mode

                # Update the operator label to show the current interpolation mode
                self.report({'INFO'}, f"Interpolation mode changed to: {next_mode}")

        return {'FINISHED'}

class OBJECT_OT_group_material_preview_flat(bpy.types.Operator):
    "Change the material preview to flat"
    bl_idname = "object.group_mat_preview_flat"
    
    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    
    def execute(self, context):
    # Iterate through all materials in the scene
        for material in bpy.data.materials:
            material.preview_render_type = 'FLAT'
            
            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: FLAT")
        return {'FINISHED'}

class OBJECT_OT_group_material_preview_sphere(bpy.types.Operator):
    "Change the material preview to sphere"
    bl_idname = "object.group_mat_preview_sphere"
    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    
    def execute(self, context):
        for material in bpy.data.materials:
            material.preview_render_type = 'SPHERE'

            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: SPHERE")
        return {'FINISHED'}

class OBJECT_OT_group_material_preview_cube(bpy.types.Operator):
    "Change the material preview to cube"
    bl_idname = "object.group_mat_preview_cube"

    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    def execute(self, context):
        for material in bpy.data.materials:
            material.preview_render_type = 'CUBE'

            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: CUBE")
        return {'FINISHED'}
        
class OBJECT_OT_group_material_preview_hair(bpy.types.Operator):
    "Change the material preview to hair"
    bl_idname = "object.group_mat_preview_hair"
    
    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    def execute(self, context):
        for material in bpy.data.materials:
            material.preview_render_type = 'HAIR'
            
            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: HAIR")
        return {'FINISHED'}
    
class OBJECT_OT_group_material_preview_shaderball(bpy.types.Operator):
    "Change the material preview to shaderball"
    bl_idname = "object.group_mat_preview_shaderball"
    
    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    def execute(self, context):
        for material in bpy.data.materials:
            material.preview_render_type = 'SHADERBALL'
            
            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: SHADERBALL")
        return {'FINISHED'}
            
class OBJECT_OT_group_material_preview_cloth(bpy.types.Operator):
    "Change the material preview to cloth"
    bl_idname = "object.group_mat_preview_cloth"
    
    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    def execute(self, context):
        for material in bpy.data.materials:
            material.preview_render_type = 'CLOTH'
            
            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: CLOTH")
        return {'FINISHED'}
            
class OBJECT_OT_group_material_preview_fluid(bpy.types.Operator):
    "Change the material preview to fluid"
    bl_idname = "object.group_mat_preview_fluid"
    
    bl_label = "Set Selected material preview"
    bl_options = { 'REGISTER','UNDO' }
    def execute(self, context):
        for material in bpy.data.materials:
            material.preview_render_type = 'FLUID'
            
            # Update the operator label to show the current interpolation mode
            self.report({'INFO'}, f"Preview mode changed to: FLUID")
        return {'FINISHED'}

# Custom Panel
class PANEL_PT_opacity_panel(bpy.types.Panel):
    """A custom panel in the viewport toolbar"""
    bl_idname = "opacity.settings"
    bl_space_type = 'VIEW_3D'
    bl_label = "NFS Helper"
    bl_region_type = "UI"
    bl_category = "NFS Helper"

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object
        active_material = active_object.active_material if active_object else None

        if not active_material:
            layout.label(text="No active material found.")
            return

        # Alpha Connect Section
        box = layout.box()                             
        col = box.column(align=True)
        col.label(text="Alpha Connect")
        row = col.row(align=True)
        row.operator("object.group_alpha_connect", text="CONNECT ALPHA")

        # Alpha Type Section
        box = layout.box()                             
        col = box.column(align=True)
        col.label(text="Alpha Type")
        row = col.row(align=True)
        row.operator("object.group_texstraight", text="STRAIGHT")
        row.operator("object.group_premultiply", text="PREMULTIPLY")

        # Blend Method Section
        box = layout.box()                             
        col = box.column(align=True)
        col.label(text="Blend Method")
        row = col.row(align=True)
        row.operator("object.group_clip", text="CLIP")
        row.operator("object.group_clip_remove", text="CLIP REMOVE")
        row = col.row(align=True)
        row.operator("object.group_blended", text="BLENDED")
        row.operator("object.group_dithered", text="DITHERED")

        # Texture Interpolation Section
        box = layout.box()                             
        col = box.column(align=True)
        col.label(text="Texture Interpolation")
        row = col.row(align=True)
        row.operator("object.group_texinterp")
        
        # Alpha Threshold Section
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Alpha Threshold")

        # Material Preview Section
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Mat Preview")
        row = col.row(align=True)
        row.operator("object.group_mat_preview_flat", text="FLAT")
        row.operator("object.group_mat_preview_sphere", text="SPHERE")
        row.operator("object.group_mat_preview_cube", text="CUBE")
        row.operator("object.group_mat_preview_hair", text="HAIR")
        row = col.row(align=True)
        row.operator("object.group_mat_preview_shaderball", text="SDRBALL")
        row.operator("object.group_mat_preview_cloth", text="CLOTH")
        row.operator("object.group_mat_preview_fluid", text="FLUID")
        
        # Ensure the material has a node tree and attempt to find the math node
        if active_material and hasattr(active_material, 'node_tree'):
            math_node = self.get_math_node(active_material.node_tree)  # Call the method on the node tree

            if math_node:
                col.prop(context.scene, "alpha_threshold_value", text="Alpha Threshold", slider=True)
                col.operator("object.update_alpha_threshold", text="Update Threshold")
            else:
                col.label(text="No suitable Math Node found.")
    def get_math_node(self, node_tree):
        # Ensure the node_tree exists and search for a Math node
        if node_tree:
            for node in node_tree.nodes:
                if node.type == 'MATH' and node.operation == 'GREATER_THAN':  # Example condition, change as needed
                    return node
        return None


def add_alpha_threshold_property():
    bpy.types.Scene.alpha_threshold_value = bpy.props.FloatProperty(
        name="Alpha Threshold",
        description="The threshold for alpha in the shader",
        default=0.5,  # Default value
        min=0.0,
        max=1.0
    )

class OBJECT_OT_update_alpha_threshold(bpy.types.Operator):
    bl_idname = "object.update_alpha_threshold"
    bl_label = "Update Alpha Threshold"

    def execute(self, context):
        active_object = context.active_object
        active_material = active_object.active_material if active_object else None

        if not active_material:
            self.report({'ERROR'}, "No active material found.")
            return {'CANCELLED'}

        # Fetch the math node
        math_node = self.get_math_node(active_material)

        if not math_node:
            self.report({'WARNING'}, "No suitable Math Node found.")
            return {'CANCELLED'}

        alpha_threshold = context.scene.alpha_threshold_value

        try:
            math_node.inputs[1].default_value = alpha_threshold
            self.report({'INFO'}, f"Threshold updated to: {alpha_threshold}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update threshold: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def get_math_node(self, material):
        # Search for a 'Greater Than' math node in the material's node tree
        nodes = material.node_tree.nodes
        for node in nodes:
            if node.type == 'MATH' and node.operation == 'GREATER_THAN':
                return node
        return None

def register():
    add_alpha_threshold_property()
    bpy.utils.register_class(OBJECT_OT_update_alpha_threshold)
    bpy.utils.register_class(OBJECT_OT_group_alpha_connect)
    bpy.utils.register_class(PANEL_PT_opacity_panel)    # Add property here
    classes = [
        OBJECT_OT_group_alpha_connect,
        OBJECT_OT_group_texstraight,
        OBJECT_OT_group_alpha_premultiply,
        OBJECT_OT_group_alpha_clip,
        OBJECT_OT_group_alpha_clip_remove,
        OBJECT_OT_group_alpha_dithered,
        OBJECT_OT_group_alpha_blended,
        OBJECT_OT_group_texinterp,
        OBJECT_OT_group_material_preview_flat,
        OBJECT_OT_group_material_preview_sphere,
        OBJECT_OT_group_material_preview_cube,
        OBJECT_OT_group_material_preview_hair,
        OBJECT_OT_group_material_preview_shaderball,
        OBJECT_OT_group_material_preview_cloth,
        OBJECT_OT_group_material_preview_fluid,
        PANEL_PT_opacity_panel
    ]
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_update_alpha_threshold)
    bpy.utils.unregister_class(OBJECT_OT_group_alpha_connect)
    bpy.utils.unregister_class(PANEL_PT_opacity_panel)
    del bpy.types.Scene.alpha_threshold_value
if __name__ == "__main__":
    register()