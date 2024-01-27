bl_info = {
    "name": "Batch Import Dae Collection",
    "author": "XXJOHNATHANXX",
    "version": (1, 0, 0),
    "blender": (4, 0, 2),
    "location": "File > Import-Export",
    "description": "Import multiple DAE files, UV's, materials",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy
from pathlib import Path

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup

def read_some_data(self, context, filepath, use_some_setting, import_as_collection):
    print("running read_some_data...")
    folder = Path(filepath)

    for selection in self.files:
        fp = Path(folder.parent, selection.name)

        # Check if a collection with the same name already exists
        collection_name = selection.name.split('.')[0]
        existing_collection = bpy.data.collections.get(collection_name)

        if existing_collection:
            # Collection already exists, switch to it
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection_name]
        else:
            # Collection does not exist, create a new one
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection_name]

        # Import the DAE file
        bpy.ops.wm.collada_import(filepath=str(fp))

        # Move the imported objects to the collection
        if import_as_collection:
            imported_objects = bpy.context.selected_objects
            for obj in imported_objects:
                # Check if the object is already in the collection
                if obj.name not in bpy.context.view_layer.active_layer_collection.collection.objects:
                    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)

        # Switch back to the main collection
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection

    return {'FINISHED'}

class ImportSomeData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import DAE(s)"
    bl_description = "Batch import DAE files and create collections"
    # ImportHelper mixin class uses this
    filename_ext = "*.dae"

    filter_glob: StringProperty(
        default=filename_ext,
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    prop_import_units: BoolProperty(
        name="Import Units",
        description="If disabled match import to Blender's current Unit settings, otherwise use the settings from the Imported scene.",
        default=False,
    )
    
    prop_import_as_collection: BoolProperty(
        name="Import as Collection",
        description="Import each DAE file as its own collection",
        default=False,
    )
    
    files: CollectionProperty(type = PropertyGroup)

    def execute(self, context):
        return read_some_data(self, context, self.filepath, True, self.prop_import_as_collection)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Batch import DAE(s) as collection")


# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access).
def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.import_test.some_data('INVOKE_DEFAULT')