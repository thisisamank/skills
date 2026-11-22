"""Rebuild a mascot in Blender from the rig JSON that the preview page exports.

The result is one armature, one skinned mesh with shape keys for the face, and one
action per animation (each also on its own NLA track, so a glTF export keeps them all).

From a terminal:
    blender --background --python rebuild_in_blender.py -- pip-rig.json --blend pip.blend --glb pip.glb --verify

In Blender: open this file in the Scripting tab, set RIG_JSON below, and run it. The script adds
a new collection. It does not delete your objects unless you pass --clear (background mode clears).

--verify compares part positions in Blender with the positions the page recorded.
"""
import bpy, json, os, sys
from mathutils import Matrix, Vector

RIG_JSON = ""        # path to the rig JSON, for runs from the Scripting tab
BONE_LENGTH = 0.2

# three.js is Y-up, Blender is Z-up: (x, y, z) -> (x, -z, y)
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
C_INV = C.inverted()


def to_matrix(e):
    """16 numbers from three.js (column-major) -> a Blender matrix in Blender axes."""
    return C @ Matrix((e[0::4], e[1::4], e[2::4], e[3::4])) @ C_INV


def to_point(p, i):
    return Vector((p[i * 3], -p[i * 3 + 2], p[i * 3 + 1]))


def srgb_to_linear(hex_color):
    out = []
    for k in (1, 3, 5):
        c = int(hex_color[k:k + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out + [1.0]


def make_material(name, color, slot, style):
    mat = bpy.data.materials.new(name)
    if not mat.node_tree:
        mat.use_nodes = True                     # old versions only; new ones always have nodes
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    rgba = srgb_to_linear(color)
    mat.diffuse_color = rgba
    if bsdf:
        def put(key, value):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
        glossy = style == "toy" or slot == "dark"
        put("Base Color", rgba)
        put("Roughness", 0.3 if glossy else 0.95)
        put("Coat Weight", 1.0 if glossy else 0.0)
        put("Coat Roughness", 0.18)
        if slot == "light":                      # the eye shine must stay white in any light
            put("Emission Color", rgba)
            put("Emission Strength", 1.0)
    return mat


def assign(anim_data, action):
    """Make an action the active one. Blender 4.4 and later also need a slot."""
    anim_data.action = action
    if action and hasattr(anim_data, "action_slot") and anim_data.action_slot is None and len(getattr(action, "slots", [])):
        anim_data.action_slot = action.slots[0]


def build(rig, clear):
    name = rig["name"]
    if clear:
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    scene = bpy.context.scene
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)

    # ----- armature: one bone per animated group, all pointing up -----
    arm = bpy.data.armatures.new(name + "_rig")
    arm_obj = bpy.data.objects.new(name + "_rig", arm)
    col.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    rest_world = {}
    for b in rig["bones"]:
        rest_world[b["name"]] = to_matrix(b["rest"])
        eb = arm.edit_bones.new(b["name"])
        eb.head = rest_world[b["name"]].translation
        eb.tail = eb.head + Vector((0, 0, BONE_LENGTH))
        eb.roll = 0
        if b["parent"]:
            eb.parent = arm.edit_bones[b["parent"]]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    rest = {b.name: b.matrix_local.copy() for b in arm.bones}

    # ----- one mesh: every part keeps its vertex range, its material and its bone -----
    verts, faces, face_mat, groups, ranges, materials = [], [], [], {}, {}, []
    for part in rig["meshes"]:
        base, p = len(verts), part["positions"]
        n = len(p) // 3
        verts += [to_point(p, i) for i in range(n)]
        key = part["slot"] + part["color"]
        if key not in [m[0] for m in materials]:
            materials.append((key, make_material("%s_%s" % (name, part["slot"]), part["color"], part["slot"], rig.get("material", "toy"))))
        mi = [m[0] for m in materials].index(key)
        idx = part["index"]
        for i in range(0, len(idx), 3):
            faces.append((base + idx[i], base + idx[i + 1], base + idx[i + 2]))
            face_mat.append(mi)
        groups.setdefault(part["bone"], []).extend(range(base, base + n))
        ranges[part["name"]] = (base, n)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for _, m in materials:
        me.materials.append(m)
    for poly, mi in zip(me.polygons, face_mat):
        poly.material_index = mi
        poly.use_smooth = True
    me.update()
    obj = bpy.data.objects.new(name, me)
    col.objects.link(obj)
    for bone, idxs in groups.items():
        obj.vertex_groups.new(name=bone).add(idxs, 1.0, "REPLACE")
    obj.parent = arm_obj
    obj.modifiers.new("Armature", "ARMATURE").object = arm_obj

    # ----- shape keys: one per face channel -----
    obj.shape_key_add(name="Basis", from_mix=False)
    for ch in rig["faceChannels"]:
        kb = None
        for part in rig["meshes"]:
            if ch in part["shapeKeys"]:
                if kb is None:
                    kb = obj.shape_key_add(name=ch, from_mix=False)    # from the basis, not from the keys made so far
                    kb.slider_min, kb.slider_max = -1.0, 1.0
                    kb.value = 0.0
                base, n = ranges[part["name"]]
                p = part["shapeKeys"][ch]
                for i in range(n):
                    kb.data[base + i].co = to_point(p, i)
    keys = me.shape_keys

    # ----- animation: one action for the bones and one for the shape keys, per clip -----
    scene.render.fps = rig["fps"]
    arm_obj.animation_data_create()
    keys.animation_data_create()
    for pb in arm_obj.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rest_world_inv = {n: m.inverted() for n, m in rest_world.items()}
    for clip in rig["clips"]:
        act = bpy.data.actions.new(clip["name"])
        face_act = bpy.data.actions.new(clip["name"] + "_face")
        assign(arm_obj.animation_data, act)
        assign(keys.animation_data, face_act)
        last = {}
        for f in range(clip["frames"]):
            pose = {}
            for b in rig["bones"]:
                n, parent = b["name"], b["parent"]
                # where the bone is now, written as a change from its rest place
                pose[n] = to_matrix(clip["bones"][n][f * 16:(f + 1) * 16]) @ rest_world_inv[n] @ rest[n]
                if parent:
                    basis = (rest[parent].inverted() @ rest[n]).inverted() @ pose[parent].inverted() @ pose[n]
                else:
                    basis = rest[n].inverted() @ pose[n]
                loc, rot, scale = basis.decompose()
                if n in last and last[n].dot(rot) < 0:
                    rot.negate()                 # keep the quaternion on one side, or the bone spins the long way
                last[n] = rot.copy()
                pb = arm_obj.pose.bones[n]
                pb.location, pb.rotation_quaternion, pb.scale = loc, rot, scale
                for path in ("location", "rotation_quaternion", "scale"):
                    pb.keyframe_insert(path, frame=f + 1)
            for ch in rig["faceChannels"]:
                kb = keys.key_blocks.get(ch)
                if kb:
                    kb.value = clip["shapes"][ch][f]
                    kb.keyframe_insert("value", frame=f + 1)
        for anim_data, action in ((arm_obj.animation_data, act), (keys.animation_data, face_act)):
            action.use_fake_user = True
            anim_data.action = None
            track = anim_data.nla_tracks.new()
            track.name = clip["name"]            # the same track name on both makes one glTF animation
            strip = track.strips.new(clip["name"], 1, action)
            if hasattr(strip, "action_slot") and strip.action_slot is None and len(getattr(action, "slots", [])):
                strip.action_slot = action.slots[0]
            track.mute = True

    for pb in arm_obj.pose.bones:
        pb.location, pb.rotation_quaternion, pb.scale = (0, 0, 0), (1, 0, 0, 0), (1, 1, 1)
    for kb in keys.key_blocks:
        kb.value = 0
    show(arm_obj, keys, "idle")
    idle = next((c for c in rig["clips"] if c["name"] == "idle"), rig["clips"][0])
    scene.frame_start, scene.frame_end = 1, idle["frames"] - 1
    return arm_obj, obj, ranges


def show(arm_obj, keys, clip_name):
    """Make one clip the active action, so it plays in the viewport."""
    if clip_name in bpy.data.actions:
        assign(arm_obj.animation_data, bpy.data.actions[clip_name])
        assign(keys.animation_data, bpy.data.actions[clip_name + "_face"])


def verify(rig, arm_obj, obj, ranges):
    face_parts = {p["name"] for p in rig["meshes"] if p["shapeKeys"]}
    worst = {"body": (0, ""), "face": (0, "")}
    for v in rig["verify"]:
        show(arm_obj, obj.data.shape_keys, v["clip"])
        bpy.context.scene.frame_set(v["frame"] + 1)
        deps = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(deps)
        me = ev.to_mesh()
        for part, want in v["centres"].items():
            base, n = ranges[part]
            got = Vector((0, 0, 0))
            for i in range(base, base + n):
                got += me.vertices[i].co
            err = (ev.matrix_world @ (got / n) - to_point(want, 0)).length
            kind = "face" if part in face_parts else "body"
            if err > worst[kind][0]:
                worst[kind] = (err, "%s, %s, frame %d" % (part, v["clip"], v["frame"]))
        ev.to_mesh_clear()
    print("VERIFY body parts: largest error %.5f (%s)" % worst["body"])
    print("VERIFY face parts: largest error %.5f (%s)" % worst["face"])
    # bones must match the page. Shape keys are straight-line versions of small face turns, so they get more room.
    ok = worst["body"][0] < 0.002 and worst["face"][0] < 0.05
    print("VERIFY " + ("OK" if ok else "FAILED"))
    show(arm_obj, obj.data.shape_keys, "idle")
    return ok


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    path = next((a for a in argv if not a.startswith("--")), RIG_JSON)
    if not path:
        raise SystemExit("Give the rig JSON path after --, or set RIG_JSON in the script.")

    def option(flag):
        return argv[argv.index(flag) + 1] if flag in argv else None

    with open(path, encoding="utf-8") as f:
        rig = json.load(f)
    arm_obj, obj, ranges = build(rig, clear=bpy.app.background or "--clear" in argv)
    print("built %s: %d bones, %d vertices, %d shape keys, %d clips" % (
        rig["name"], len(arm_obj.data.bones), len(obj.data.vertices), len(obj.data.shape_keys.key_blocks) - 1, len(rig["clips"])))
    ok = verify(rig, arm_obj, obj, ranges) if "--verify" in argv else True
    if option("--blend"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(option("--blend")))
        print("saved " + option("--blend"))
    if option("--glb"):
        bpy.ops.export_scene.gltf(filepath=os.path.abspath(option("--glb")), export_format="GLB",
                                  export_animations=True, export_animation_mode="NLA_TRACKS", export_morph=True)
        print("saved " + option("--glb"))
    if not ok:
        raise SystemExit(1)


main()
