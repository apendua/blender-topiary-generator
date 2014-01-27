bl_info = {
  "name": "Topiary Generator",
  "author": "apendua",
  "version": (0, 0, 1),
  "blender": (2, 6, 9),
  "location": "",
  "description": "Allows you to generate topiaries of arbitrary shapes",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Object",
}

if 'bpy' in locals():
  import imp
  imp.reload(topiary)
else:
  from . import topiary
  
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty

class GenerateTopiary(bpy.types.Operator):
    """Generate topiary mesh"""
    bl_idname = "object.generate_topiary"
    bl_label = "Generate Topiary"
    bl_options = {'REGISTER', 'UNDO'}

    iterations = IntProperty(
      name="Iterations",
      description="number of iterations",
      min=1, max=5,
      default=3,
    )
    
    seed = IntProperty(
      name="Seed",
      description="seed for random numbers generator",
      min=0, default=0,
    )
    
    def invoke(self, context, event): 
      self.root_name = context.active_object.name   
      selected = [base.object for base in context.selected_bases if base.object.name != self.root_name] 
      try:
        self.boundary_name = selected[0].name
      except IndexError: # TODO: maybe some fallback solution or error message (?)
        return {'FINISHED'}
      
      return self.execute(context)
    
    def execute(self, context): 
        import random
        
        try:
          root = context.scene.objects[self.root_name]
          boundary = context.scene.objects[self.boundary_name]
        except KeyError: # TODO: error message
          return {'FINISHED'}
        
        random.seed(self.seed)
                
        # TODO: think if we can use more selected objects
        
        context.scene.update() # make sure ray_cast works fine
        mesh = topiary.generate_tree_mesh(root, boundary,
          iterations = self.iterations,
        )
        
        self.add_object(context, mesh, root)
        
        return {'FINISHED'}
        
    def add_object(self, context, mesh, root=None):
        # TODO: make active
        
        obj = bpy.data.objects.new(mesh.name, mesh)
        context.scene.objects.link(obj)
        
        if root is not None:
          obj.location = root.location
        
        return obj
    
#end: GenerateTopiary

def register():  
    bpy.utils.register_class(GenerateTopiary)

def unregister():
    bpy.utils.unregister_class(GenerateTopiary)

if __name__ == "__main__":
    register()
