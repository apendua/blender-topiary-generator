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
  
  def do_triangle(newRoot, s, p, level):
    """
        2
      5   4
    0   3   1       
    """
    do_recursive(newRoot, [s[0], s[3], s[5]], projected=[p[0], p[3], p[5]], level=level)
    do_recursive(newRoot, [s[1], s[4], s[3]], projected=[p[1], p[4], p[3]], level=level)
    do_recursive(newRoot, [s[2], s[5], s[4]], projected=[p[2], p[5], p[4]], level=level)
    do_recursive(newRoot, [s[3], s[4], s[5]], projected=[p[3], p[4], p[5]], level=level)
    
  def do_quad(newRoot, s, p, level):
    """
    3  6  2
    7  8  5
    0  4  1
    """
    do_recursive(newRoot, [s[0], s[4], s[8], s[7]], projected=[p[0], p[4], p[8], p[7]], level=level)
    do_recursive(newRoot, [s[4], s[1], s[5], s[8]], projected=[p[4], p[1], p[5], p[8]], level=level)
    do_recursive(newRoot, [s[8], s[5], s[2], s[6]], projected=[p[8], p[5], p[2], p[6]], level=level)
    do_recursive(newRoot, [s[7], s[8], s[6], s[3]], projected=[p[7], p[8], p[6], p[3]], level=level)
    
  def do_polygon(newRoot, s, p, level):
    """
    3     2
      7 6
      4 5
    0     1
    """
    nVerts = int(len(s)/2) # it should be even
    for i in range(nVerts-1):
      do_recursive(newRoot, [s[i], s[i+1], s[i+1+nVerts], s[i+nVerts]],
        projected=[p[i], p[i+1], p[i+1+nVerts], p[i+nVerts]], level=level)
    # special case
    do_recursive(newRoot, [s[nVerts-1], s[0], s[nVerts], s[2*nVerts-1]],
      projected=[p[nVerts-1], p[0], p[nVerts], p[2*nVerts-1]], level=level)
    # the polygon on the center
    do_recursive(newRoot, s[nVerts:], projected=p[nVerts:], level=level)
  #end: do_polygon
  
  def do_recursive(root, polygon, projected=None, level=0):
  
    # if len(polygon) != 3:
    #  raise ValueError
    
    p = projected # convenience alias
 
    if p is None:
      p = [project(vert.co, root) for vert in polygon]

    if level <= 0:
      return
      #bm.faces.new(projected) # don't subdivide just draw face
     
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
      p = p + [project(1/5 * p[i] + 4/5 * center , newRoot) for i in range(nVerts)]      
    
    # scale down
    scaled = []
    for vert in p:
      scaled.append(
        bm.verts.new(newRoot + 0.02 * (vert - newRoot)))
    
    t = polygon; s = scaled
    
    for i in range(0, nVerts-1):
      bm.faces.new([t[i+1], s[i+1], s[i], t[i]])
    bm.faces.new([t[0], s[0], s[nVerts-1], t[nVerts-1]])

    if nVerts <= 4:
      for i in range(0, nVerts-1):
        bm.faces.new([s[i], s[i+1], s[i+nVerts]])
      bm.faces.new([s[nVerts-1], s[0], s[2*nVerts-1]])
    else: # no need for additional faces
      pass
    
    if nVerts == 3:
      do_triangle(newRoot, s, p, level-1)
    elif nVerts == 4:
      do_quad(newRoot, s, p, level-1)
    else:
      print(len(s), len(p))
      do_polygon(newRoot, s, p, level-1)     
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
    cache.append(list(face.verts))
      
  for face in cache:
    do_recursive(root, face, level=iterations)
  
  tree_mesh = bpy.data.meshes.new('tree_mesh')
  
  bm.to_mesh(tree_mesh) 
  bm.free()
  
  tree_mesh.update()
  
  return tree_mesh
#end: generate_tree_mesh
