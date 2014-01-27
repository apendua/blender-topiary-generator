import bpy
import bmesh
import mathutils
import random

from mathutils import Vector, Matrix

def generate_tree_mesh(base_obj, ref_obj, iterations=4):

  def project(vertex, center):
    intersection_point, _, index = \
        ref_obj.ray_cast(center, vertex + 10 * (vertex - center).normalized())
    if index >= 0:
      return intersection_point
    return vertex   
  
  def do_recursive(root, triangle, level, projected=None):
  
    # if len(triangle) != 3:
    #  raise ValueError
    
    if projected is None:
      projected = [project(vert.co, root) for vert in triangle]

    # find center
    alpha = (0.9 + random.random()) / 3 # randomize
    center = alpha * root
    for vert in projected[:3]:
      center += (1 - alpha)/3 * vert
        
    # subdivide
    projected.append(project(1/2*(projected[0] + projected[1]), center))
    projected.append(project(1/2*(projected[1] + projected[2]), center))
    projected.append(project(1/2*(projected[2] + projected[0]), center))
        
    # scale down
    scaled = []
    for vert in projected:
      scaled.append(
        bm.verts.new(center + 0.02 * (vert - center)))
    
    t = triangle; s = scaled; p = projected
    
    bm.faces.new([t[0], s[0], s[2], t[2]])
    bm.faces.new([t[1], s[1], s[0], t[0]])
    bm.faces.new([t[2], s[2], s[1], t[1]])
    
    bm.faces.new([s[0], s[1], s[3]])
    bm.faces.new([s[1], s[2], s[4]])
    bm.faces.new([s[2], s[0], s[5]])
    
    if level > 0:   
      do_recursive(center, [s[0], s[3], s[5]], level - 1, projected=[p[0], p[3], p[5]])
      do_recursive(center, [s[1], s[4], s[3]], level - 1, projected=[p[1], p[4], p[3]])
      do_recursive(center, [s[2], s[5], s[4]], level - 1, projected=[p[2], p[5], p[4]])
      do_recursive(center, [s[3], s[4], s[5]], level - 1, projected=[p[3], p[4], p[5]])
      
    else:  
      bm.faces.new([s[0], s[3], s[5]])
      bm.faces.new([s[1], s[4], s[3]])
      bm.faces.new([s[2], s[5], s[4]])
      bm.faces.new([s[3], s[4], s[5]]) 
  #end: do_recursive
  
  # TODO: use center of mass
  bm = bmesh.new()
  bm.from_mesh(base_obj.data)
  
  root = Vector((0,0,0))
  # TODO: use this for optimization
  # proj = [None] * len(bm.verts)
  
  for vert in bm.verts:
    vert.co = root + 0.04 * (vert.co - root).normalized()
    # proj[vert.index] = project(vert.co, root)
  
  cache = []
  
  for face in bm.faces:
    if len(face.verts) == 3:
      cache.append(list(face.verts))
      
  for triangle in cache:
    do_recursive(root, triangle, iterations)
  
  tree_mesh = bpy.data.meshes.new('tree_mesh')
  
  bm.to_mesh(tree_mesh) 
  bm.free()
  
  tree_mesh.update()
  
  return tree_mesh
#end: generate_tree_mesh
