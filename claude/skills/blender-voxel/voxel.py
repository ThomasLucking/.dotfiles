# Voxel model builder. Exec inside Blender, then fill V and call build().
#   V = {}                      # (x, y, z) -> material key; +z up, -y = front
#   box(V, x0, x1, y0, y1, z0, z1, 'skin')   # inclusive ranges
#   blob(V, cx, cy, cz, rx, ry, rz, 'hat')  # filled ellipsoid
#   disc(V, cx, cy, z, r, 'hat')            # one layer of a cylinder/cone
#   mirror_x(V)                             # copy x>0 side onto x<0
#   carve(V, keys)                          # remove voxels (e.g. eye sockets)
#   ob = build('Gnome', V, {'skin': (0.95, 0.62, 0.45), ...}, size=VOXEL_SIZE)['object']
#   export_glb('Gnome', '//gnome.glb')      # '//' = next to the .blend
#   rescale(V, 2.5)                         # resample shape coords (keeps real-world height)
#
# Style: detailed, realistic, hard-edged. Real-world proportions, lots of small parts,
#   NO rounded corners, NO smooth shading, NO bevel/subdivision. Everything is boxes.
#
# Scale: two voxel sizes. VOXEL_SIZE = 1/64 m (1.56 cm) for characters, furniture, large
#   props (person ~110 voxels tall, door ~130, desk ~50). FINE_SIZE = 1/128 m (7.8 mm) for
#   hand-held props (laptop ~42 wide x 28 deep, phone, mug, keyboard). Pick the size so the
#   smallest feature you want (a key, a port, a button) is >= 2 voxels. To change
#   resolution, rescale() the shape coordinates; changing size= alone changes real height.
#
# Detail helpers: hollow() for bezels/frames/trays, tile() for key grids, vents, tiles.
#
# Godot notes:
#   - Blender -Y front exports as glTF +Z, which is Godot's model front (+Z).
#   - 1 Blender unit = 1 m = 1 Godot unit; origin sits at the feet.
#   - materials='palette' gives one shared palette texture -> 1-2 surfaces in Godot
#     instead of one surface (draw call) per colour.
#   - collider=True adds a '<name>-convcolonly' box; Godot turns it into a
#     StaticBody3D + convex shape on import.
import bpy, bmesh, math

VOXEL_SIZE = 1 / 64   # metres per voxel (64 per metre)
FINE_SIZE = 1 / 128   # hand-held props
MAX_FACES = 40000     # warn above this after meshing


# ---------------------------------------------------------------- shapes

def _span(c, r):
    return range(math.floor(c - r), math.ceil(c + r) + 1)


def box(V, x0, x1, y0, y1, z0, z1, m):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                V[(x, y, z)] = m


def hollow(V, x0, x1, y0, y1, z0, z1, m, t=1):
    """Box shell, wall thickness t voxels (bezels, frames, trays, open crates)."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if (min(x - x0, x1 - x, y - y0, y1 - y, z - z0, z1 - z) < t):
                    V[(x, y, z)] = m


def tile(V, x0, x1, y0, y1, z0, z1, m, nx=1, ny=1, nz=1, dx=0, dy=0, dz=0):
    """Repeat a box nx*ny*nz times, stepping (dx, dy, dz) voxels: keys, vents, windows, tiles."""
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                box(V, x0 + i * dx, x1 + i * dx, y0 + j * dy, y1 + j * dy,
                    z0 + k * dz, z1 + k * dz, m)


def blob(V, cx, cy, cz, rx, ry, rz, m):
    """Stair-stepped ellipsoid. Organic parts only (heads, fruit); hard-surface = box()."""
    if min(rx, ry, rz) <= 0:
        raise ValueError('blob radii must be > 0')
    for x in _span(cx, rx):
        for y in _span(cy, ry):
            for z in _span(cz, rz):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1:
                    V[(x, y, z)] = m


def disc(V, cx, cy, z, r, m):
    for x in _span(cx, r):
        for y in _span(cy, r):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                V[(x, y, z)] = m


def mirror_x(V):
    """Copy everything on the +x side onto -x (x=0 column is the centre line)."""
    for (x, y, z), m in list(V.items()):
        if x > 0:
            V[(-x, y, z)] = m


def rescale(V, f):
    """Resample V by factor f (nearest voxel) so the real-world shape is kept when
    the voxel size changes, e.g. size 0.025 -> 0.0625 is rescale(V, 0.4).
    Returns a new dict; the caller reassigns V. Thin parts (< 1/f voxels) can vanish."""
    if f <= 0:
        raise ValueError('scale factor must be > 0')
    xs, ys, zs = ([p[i] for p in V] for i in range(3))
    lo = (min(xs), min(ys), min(zs))
    hi = (max(xs), max(ys), max(zs))
    out = {}
    rng = [range(math.floor(lo[i] * f), math.ceil((hi[i] + 1) * f)) for i in range(3)]
    for x in rng[0]:
        for y in rng[1]:
            for z in rng[2]:
                m = V.get((math.floor((x + .5) / f), math.floor((y + .5) / f), math.floor((z + .5) / f)))
                if m is not None:
                    out[(x, y, z)] = m
    return out


def carve(V, keys):
    """Remove voxels. keys: any iterable of (x, y, z), e.g. a dict built with box()."""
    for k in keys:
        V.pop(k, None)


# ---------------------------------------------------------------- meshing

FACES = [((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
         ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
         ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
         ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
         ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
         ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)])]


def _naive_quads(V):
    """One quad per exposed voxel face: (material_key, [4 lattice corners])."""
    for (x, y, z), m in V.items():
        for (dx, dy, dz), tmpl in FACES:
            if (x + dx, y + dy, z + dz) not in V:
                yield m, [(x + a, y + b, z + c) for a, b, c in tmpl]


def _greedy_quads(V):
    """Merge exposed faces into the largest same-material rectangles per slice.

    Same winding as FACES: each template corner's 0/1 on the two in-plane axes
    is scaled to the rectangle's extent, so normals stay outward.
    """
    for normal, tmpl in FACES:
        ax = next(i for i in range(3) if normal[i])
        u, v = [i for i in range(3) if i != ax]
        slices = {}
        for p, m in V.items():
            q = (p[0] + normal[0], p[1] + normal[1], p[2] + normal[2])
            if q not in V:
                slices.setdefault(p[ax], {})[(p[u], p[v])] = m

        for s, mask in slices.items():
            done = set()
            for a, b in sorted(mask):
                if (a, b) in done:
                    continue
                m = mask[(a, b)]

                def free(cell):
                    return cell not in done and mask.get(cell) == m

                h = 1
                while free((a, b + h)):
                    h += 1
                w = 1
                while all(free((a + w, b + k)) for k in range(h)):
                    w += 1
                for i in range(w):
                    for k in range(h):
                        done.add((a + i, b + k))

                corners = []
                for t in tmpl:
                    c = [0, 0, 0]
                    c[ax] = s + t[ax]
                    c[u] = a + t[u] * w
                    c[v] = b + t[v] * h
                    corners.append(tuple(c))
                yield m, corners


# ---------------------------------------------------------------- materials

def _to_srgb(c):
    c = min(max(c, 0.0), 1.0)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _principled(mat):
    mat.use_nodes = True
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def _set_pbr(bsdf, metal):
    bsdf.inputs['Metallic'].default_value = 1.0 if metal else 0.0
    bsdf.inputs['Roughness'].default_value = 0.3 if metal else 0.7


def _flat_material(name, rgb, metal):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    bsdf = _principled(mat)
    c = (*rgb, 1)
    bsdf.inputs['Base Color'].default_value = c
    _set_pbr(bsdf, metal)
    mat.diffuse_color = c  # solid-view colour
    return mat


def _palette_image(name, keys, colors):
    """1px-per-colour strip. Colours are given linear (like Base Color) and stored sRGB."""
    img = bpy.data.images.get(name)
    if img and tuple(img.size) != (len(keys), 1):
        bpy.data.images.remove(img)
        img = None
    if not img:
        img = bpy.data.images.new(name, len(keys), 1, alpha=False)
    px = []
    for k in keys:
        px += [_to_srgb(ch) for ch in colors[k]] + [1.0]
    img.pixels[:] = px
    try:
        img.pack()  # keep it inside the .blend and embeddable in the .glb
    except RuntimeError:
        pass
    return img


def _palette_material(name, img, metal):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    bsdf = _principled(mat)
    nt = mat.node_tree
    tex = nt.nodes.get('Palette') or nt.nodes.new('ShaderNodeTexImage')
    tex.name = 'Palette'
    tex.image = img
    tex.interpolation = 'Closest'  # exported as a nearest-filter sampler
    tex.location = (bsdf.location.x - 350, bsdf.location.y)
    if not bsdf.inputs['Base Color'].is_linked:
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    _set_pbr(bsdf, metal)
    return mat


# ---------------------------------------------------------------- scene helpers

def _remove_object(ob):
    for child in list(ob.children):
        _remove_object(child)
    me = ob.data
    bpy.data.objects.remove(ob)
    if me and not me.users:
        bpy.data.meshes.remove(me)


def remove_default_cube():
    """Delete Blender's startup cube (object 'Cube', 8-vert mesh) if present. Returns bool."""
    ob = bpy.data.objects.get('Cube')
    if not ob or ob.type != 'MESH' or len(ob.data.vertices) != 8:
        return False
    _remove_object(ob)
    return True


# ---------------------------------------------------------------- build

def build(name, V, colors, size=VOXEL_SIZE, metallic=(), mesh='greedy', materials='palette',
          collider=False, replace=True, remove_cube=True):
    """One mesh object at the origin, centred on x/y, feet on z=0, only exposed faces.

    mesh:      'greedy' (merged rectangles, default), 'faces' (one quad per voxel face),
               or 'dissolve' (Blender's dissolve_limit, may give concave n-gons)
    materials: 'palette' (one palette texture; 1 material, +1 if anything is metallic)
               or 'separate' (one flat material per colour key)
    collider:  add a '<name>-convcolonly' bounding box for Godot's importer
    replace:   delete an existing object called `name` (and its children) first
    """
    if not V:
        raise ValueError('V is empty')
    warnings = []
    if min(abs(size - VOXEL_SIZE), abs(size - FINE_SIZE)) > 1e-9:
        warnings.append(f'size {size} not {VOXEL_SIZE} or {FINE_SIZE}: rescale shape coords instead')
    if mesh not in ('greedy', 'faces', 'dissolve'):
        raise ValueError(f"mesh must be 'greedy', 'faces' or 'dissolve', not {mesh!r}")
    if materials not in ('palette', 'separate'):
        raise ValueError(f"materials must be 'palette' or 'separate', not {materials!r}")
    missing = set(V.values()) - set(colors)
    if missing:
        raise KeyError(f'no colour defined for: {sorted(missing)}')

    removed_cube = remove_default_cube() if remove_cube else False
    if replace and (old := bpy.data.objects.get(name)):
        _remove_object(old)

    keys = list(colors)
    color_index = {k: i for i, k in enumerate(keys)}
    palette = materials == 'palette'

    if palette:
        img = _palette_image(f'{name}_palette', keys, colors)
        mats = [_palette_material(f'{name}_palette', img, False)]
        if any(k in metallic for k in keys):
            mats.append(_palette_material(f'{name}_palette_metal', img, True))
        mat_index = {k: (1 if k in metallic else 0) for k in keys}
    else:
        mats = [_flat_material(f'{name}_{k}', colors[k], k in metallic) for k in keys]
        mat_index = color_index

    xs = [x for x, _, _ in V]
    ys = [y for _, y, _ in V]
    zs = [z for _, _, z in V]
    ox = (min(xs) + max(xs) + 1) / 2
    oy = (min(ys) + max(ys) + 1) / 2
    oz = min(zs)

    def world(p):
        return ((p[0] - ox) * size, (p[1] - oy) * size, (p[2] - oz) * size)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('UVMap') if palette else None
    verts = {}

    def vert(p):
        v = verts.get(p)
        if v is None:
            v = verts[p] = bm.verts.new(world(p))
        return v

    naive_faces = sum(1 for _ in _naive_quads(V))
    quads = _greedy_quads(V) if mesh == 'greedy' else _naive_quads(V)
    for m, corners in quads:
        f = bm.faces.new([vert(c) for c in corners])
        f.material_index = mat_index[m]
        f.smooth = False
        if palette:
            uv_co = ((color_index[m] + 0.5) / len(keys), 0.5)
            for loop in f.loops:
                loop[uv].uv = uv_co

    if mesh == 'dissolve':
        delimit = {'MATERIAL', 'UV'} if palette else {'MATERIAL'}
        bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts[:],
                                 edges=bm.edges[:], delimit=delimit)

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mat in mats:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll = bpy.context.collection
    coll.objects.link(ob)

    col_name = None
    if collider:
        lo = world((min(xs), min(ys), min(zs)))
        hi = world((max(xs) + 1, max(ys) + 1, max(zs) + 1))
        cbm = bmesh.new()
        bmesh.ops.create_cube(cbm, size=1.0)
        for vtx in cbm.verts:
            vtx.co = [(lo[i] + hi[i]) / 2 + vtx.co[i] * (hi[i] - lo[i]) for i in range(3)]
        cme = bpy.data.meshes.new(f'{name}-convcolonly')
        cbm.to_mesh(cme)
        cbm.free()
        col = bpy.data.objects.new(f'{name}-convcolonly', cme)
        col.parent = ob
        col.display_type = 'WIRE'
        col.hide_render = True
        coll.objects.link(col)
        col_name = col.name

    if len(me.polygons) > MAX_FACES:
        warnings.append(f'{len(me.polygons)} faces > {MAX_FACES}: merge noisy colours or drop sub-visible detail')
    return {'object': ob.name, 'voxels': len(V), 'faces_naive': naive_faces,
            'faces': len(me.polygons), 'materials': len(mats),
            'height_voxels': max(zs) - oz + 1, 'size': size,
            'height_m': round((max(zs) - oz + 1) * size, 2), 'warnings': warnings,
            'collider': col_name, 'removed_default_cube': removed_cube}


# ---------------------------------------------------------------- export

def export_glb(obj, filepath):
    """Export one built object (plus its collider child) as a .glb for Godot.

    obj: object or object name. filepath: '//name.glb' saves next to the .blend.
    """
    ob = bpy.data.objects[obj] if isinstance(obj, str) else obj
    path = bpy.path.abspath(filepath)
    if not path.lower().endswith('.glb'):
        path += '.glb'
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in [ob, *ob.children_recursive]:
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True)
    return path