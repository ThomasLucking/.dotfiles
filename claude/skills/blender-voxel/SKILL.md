---
name: blender-voxel
description: Build a detailed, realistic, hard-edged blocky 3D model (character, prop, device, furniture, creature) with its materials in the connected Blender via the blender MCP, optionally exported as a Godot-ready .glb. Use when asked for a voxel model, voxel asset or blocky game model in Blender.
---

Deliverable: **one mesh object plus its materials** (and, only if asked, a `.glb`). The scene around it stays as the user has it: camera, lights, world, render settings, other objects and collections untouched; no ground plane. The one exception: `build` deletes Blender's default startup cube (object `Cube`) if it is still there (`remove_cube=False` keeps it).

## Style (applies to every step)

Blocky but detailed: the result must read as the real thing (a laptop looks like a laptop: hinge, bezel, screen, keyboard with individual keys, trackpad, ports), not as a chunky pixel-art icon.

- **Hard edges only.** Every part is built from boxes. No rounded corners, no bevels, no subdivision, no smooth shading (`build` writes flat-shaded faces). Round things are stepped boxes at fine resolution. `blob` and `disc` stair-step and read as soft: use them only for organic parts such as heads or fruit, never for hard-surface props.
- **Real proportions.** Use real-world dimensions (a 14" laptop is ~32 × 22 × 1.5 cm closed), not cartoon proportions.
- **Three detail layers.** (1) primary forms, (2) secondary parts: bezels, hinges, buttons, handles, straps, (3) tertiary detail: individual keys, ports, vents, screws, seams, labels, stitching, wear.
- **Real colour breakdown.** 15–30 material keys: separate keys for trim, seams, glass, screen, rubber, metal, labels. A darker 1-voxel seam line or a recessed gap between parts sells realism more than extra bulk.

## Steps

1. **Design the palette and grid.** Pick 15–30 material keys with RGB colours (0–1, linear). Two voxel sizes, +z up, -y is the front, model centred on x/y with feet on z=0:
   - `VOXEL_SIZE` = 1/64 m (1.56 cm): characters (~110 voxels tall), doors (~130), furniture, large props.
   - `FINE_SIZE` = 1/128 m (7.8 mm): hand-held props (laptop ~42 wide × 28 deep, phone, mug, keyboard) and anything with small parts.
   - Choose the size so the smallest feature you want (a key, a port, a button) is at least 2 voxels. To change resolution, `V = rescale(V, f)` the shape coordinates; changing `size=` alone changes the real-world height.
   - Write down real dimensions per part converted to voxels. Done when every part has a voxel range and a key.
2. **Build it in one `execute_blender_code` call.** Exec the helper first, then fill `V` with the shape helpers (later writes overwrite earlier ones, so lay down the large forms first and paint details like keys, ports, eyes and buttons last), then call `build`:

   - `box(V, x0, x1, y0, y1, z0, z1, key)`: inclusive ranges; the workhorse
   - `hollow(V, x0, x1, y0, y1, z0, z1, key, t=1)`: box shell of thickness `t` (bezels, frames, trays)
   - `tile(V, x0, x1, y0, y1, z0, z1, key, nx, ny, nz, dx, dy, dz)`: repeat a box on a grid (keys, vents, windows, tiles)
   - `blob(V, cx, cy, cz, rx, ry, rz, key)`: stepped ellipsoid, organic parts only
   - `disc(V, cx, cy, z, r, key)`: one layer of a cylinder or cone, organic parts only
   - `mirror_x(V)`: copies the x>0 side onto x<0 (x=0 is the centre line), so model one half only
   - `carve(V, keys)`: removes voxels, e.g. recessed gaps, eye sockets, port openings
   - `rescale(V, f)`: nearest-voxel resample, returns a new dict

   ```python
   exec(open('/Users/thomaslucking/.claude/skills/blender-voxel/voxel.py').read())
   V = {}
   # laptop at FINE_SIZE, base 42 x 28 x 2, lid hinged open
   box(V, -21, 20, -14, 13, 0, 1, 'chassis')
   box(V, -19, 18, -12, 2, 2, 2, 'deck')                      # keyboard well
   tile(V, -18, -17, -11, -10, 3, 3, 'key', nx=14, ny=4, dx=3, dy=3)   # key grid
   box(V, -5, 4, 6, 12, 2, 2, 'trackpad')
   hollow(V, -21, 20, 13, 14, 2, 27, 'bezel', t=1)            # lid frame
   box(V, -19, 18, 13, 13, 4, 25, 'screen')
   mirror_x(V)  # only if the model was built on x>0 only
   result = build('Laptop', V, {...}, size=FINE_SIZE, metallic=('chassis',))
   ```

   `build` options:
   - `materials='palette'` (default): one shared palette texture, material `<Name>_palette` (plus `<Name>_palette_metal` if `metallic` is used). Fewest draw calls.
   - `materials='separate'`: one flat material `<Name>_<key>` per key. Use when the user wants to tweak colours per material in Blender.
   - `mesh='greedy'` (default, merged rectangles), `'faces'` (one quad per voxel face) or `'dissolve'` (may give concave n-gons).
   - `collider=True`: adds a `<Name>-convcolonly` bounding box child, which Godot imports as a convex collision shape.
   - `replace=True` (default): deletes an existing object of the same name first.

   It returns `{object, voxels, faces_naive, faces, materials, height_voxels, size, height_m, warnings, collider, removed_default_cube}`. Done when it returns without error, `height_m` matches the real-world height, and `warnings` is empty (size not 1/64 or 1/128, over 40000 faces).
3. **Look at it from several angles.** `jump_to_view3d_object_by_name` on the new object, then `get_screenshot_of_area_as_image` of the 3D view: front, a 3/4 view, and a close-up of the finest detail. Fix floating voxels, hidden parts, missing detail layers or wrong proportions by re-running step 2 under the same name (`replace` removes the old object). Done when each view reads as the requested real-world object and no detail layer (primary, secondary, tertiary) is missing.

## Export (only when asked)

`export_glb('Laptop', '//laptop.glb')` writes the object (and its collider child) as a `.glb`; `//` means next to the `.blend`, so the file must be saved first. Blender -Y front exports as glTF +Z, which is Godot's model front; 1 Blender unit is 1 Godot unit and the origin sits at the feet. Never save or export unprompted.

## Report

Object name, voxel count, height in metres, the material list. Offer `.glb` export as the next action.
