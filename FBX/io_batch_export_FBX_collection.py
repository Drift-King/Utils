bl_info = {
    "name": "Batch Export FBX Collection",
    "author": "XXJOHNATHANXX",
    "version": (0, 1, 0),
    "blender": (3, 5, 0),
    "location": "N-Panel > Tool",
    "description": "Export multiple Collections to individual FBX files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}
import bpy
import os

class BatchExportSettings(bpy.types.PropertyGroup):
    obj_folder_path: bpy.props.StringProperty(
        name="FBX Export Folder Path",
        subtype='DIR_PATH',
        default="",  # Set default to an empty string
    )

class BatchExportOperator(bpy.types.Operator):
    """Batch Export Operator"""
    bl_idname = "obj.batch_export"
    bl_label = "Batch Export"

    def execute(self, context):
        # Get the folder path from the property group
        folder_path = bpy.context.scene.batch_export_settings.obj_folder_path

        # Export each collection as FBX
        for collection in bpy.data.collections:
            export_collection_as_fbx(collection, folder_path)

        return {'FINISHED'}

class BatchExportPanel(bpy.types.Panel):
    """Batch Export FBX Panel"""
    bl_idname = "FBX_batch_export"
    bl_label = "Batch Export FBX Collections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Select a folder Directory:")
        row = layout.row()
        row.prop(context.scene.batch_export_settings, "obj_folder_path", text="Dir")
        row.operator("obj.batch_export", text="", icon="PLAY")

def get_selected_objects():
    # Get the selected objects in the scene
    selected_objects = [obj for obj in bpy.context.selected_objects]
    return selected_objects

def select_objects(objects):
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select the specified objects
    for obj in objects:
        obj.select_set(True)

def export_collection_as_fbx(collection, folder_path):
    # Get the selected objects before exporting
    selected_objects = get_selected_objects()

    # Select objects in the collection
    select_objects(collection.objects)

    # Set the export file path
    file_path = os.path.join(folder_path, f"{collection.name}.fbx")

    # Export the collection as FBX
    bpy.ops.export_scene.fbx(filepath=file_path, use_selection=True)

    # Restore the original selection
    select_objects(selected_objects)

classes = (
    BatchExportSettings,
    BatchExportOperator,
    BatchExportPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.batch_export_settings = bpy.props.PointerProperty(type=BatchExportSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.batch_export_settings

if __name__ == "__main__":
    register()
