import bpy
import bmesh
import mathutils
import random

from mathutils import Vector, Matrix

def generate_tree_mesh(base_obj, ref_obj, iterations=4):

  def project(vertex, center_of_projection):
    intersection_point, _, index = \
        ref_obj.ray_cast(center_of_projection,
          vertex + 10 * (vertex - center_of_projection).normalized())
    if index >= 0:
      return intersection_point
    return vertex   
  
  def do_triangle():
    pass
    
  def do_quad():
    pass
    
  def do_polygon():
    pass
  
  def do_recursive(root, polygon, level, projected=None):
  
    # if len(polygon) != 3:
    #  raise ValueError
 
    p = projected # convenience alias
 
    if p is None:
      p = [project(vert.co, root) for vert in polygon]
    
    nVerts = len(polygon)
    
    # find center
    center = Vector((0,0,0))
    for vert in p[:nVerts]:
      center += 1/nVerts * vert

    # and new root
    alpha = (0.9 + random.random()) / nVerts # randomize
    newRoot = (1-alpha) * center + alpha * root
      
    # subdivide
    if nVerts <= 4:
      p.append(p[0]) # sentinel
      p = p[:-1] + [project(1/2*(p[i] + p[i+1]), newRoot) for i in range(nVerts)]
      if nVerts == 4:
        p.append(project(center, newRoot))
    else:
      p = p + [project(1/2*(p[i] + newRoot), newRoot) for i in range(nVerts)]      
    
    # scale down
    scaled = []
    for vert in p:
      scaled.append(
        bm.verts.new(newRoot + 0.02 * (vert - newRoot)))
    
    t = polygon; s = scaled
    
    bm.faces.new([t[0], s[0], s[2], t[2]])
    bm.faces.new([t[1], s[1], s[0], t[0]])
    bm.faces.new([t[2], s[2], s[1], t[1]])
    
    bm.faces.new([s[0], s[1], s[3]])
    bm.faces.new([s[1], s[2], s[4]])
    bm.faces.new([s[2], s[0], s[5]])
    
    if level > 0:   
      do_recursive(newRoot, [s[0], s[3], s[5]], level - 1, projected=[p[0], p[3], p[5]])
      do_recursive(newRoot, [s[1], s[4], s[3]], level - 1, projected=[p[1], p[4], p[3]])
      do_recursive(newRoot, [s[2], s[5], s[4]], level - 1, projected=[p[2], p[5], p[4]])
      do_recursive(newRoot, [s[3], s[4], s[5]], level - 1, projected=[p[3], p[4], p[5]])
      
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
      
  for face in cache:
    do_recursive(root, face, iterations)
  
  tree_mesh = bpy.data.meshes.new('tree_mesh')
  
  bm.to_mesh(tree_mesh) 
  bm.free()
  
  tree_mesh.update()
  
  return tree_mesh
#end: generate_tree_mesh
