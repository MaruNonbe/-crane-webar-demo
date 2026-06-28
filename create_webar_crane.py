import math
from pathlib import Path
from mathutils import Vector
import bpy


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_BLEND = str(SCRIPT_DIR / "webar_crane_generated.blend")
OUTPUT_GLB = str(SCRIPT_DIR / "webar_crane_generated.glb")
OUTPUT_USDZ = str(SCRIPT_DIR / "webar_crane_generated.usdz")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def mat(name, color, metallic=0.0, roughness=0.55):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def set_origin_to_cursor(obj, location):
    bpy.context.scene.cursor.location = location
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    obj.select_set(False)


def cube_obj(name, size, location, material, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("soft_edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.affect = "EDGES"
        obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    if parent:
        obj.parent = parent
    return obj


def cyl_obj(name, radius, depth, location, material, parent=None, vertices=48, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    return obj


def empty(name, location, parent=None, display="PLAIN_AXES", size=0.35):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = display
    obj.empty_display_size = size
    obj.location = location
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def add_text_label(name, text, location, parent, material):
    font_curve = bpy.data.curves.new(name, "FONT")
    font_curve.body = text
    font_curve.align_x = "CENTER"
    font_curve.align_y = "CENTER"
    font_curve.size = 0.18
    obj = bpy.data.objects.new(name, font_curve)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)
    obj.parent = parent
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_wheel(name, x, z, parent, rubber, rim, steerable):
    pivot_name = name if steerable else name.replace("FrontWheel", "RearWheel")
    pivot = empty(pivot_name, (x, 0.48, z), parent=parent, display="ARROWS", size=0.28)
    tire = cyl_obj(f"{pivot_name}_Tire", 0.48, 0.38, (0, 0, 0), rubber, parent=pivot, rotation=(0, math.radians(90), 0))
    rim_a = cyl_obj(f"{pivot_name}_Rim_outer", 0.27, 0.405, (0, 0, 0), rim, parent=pivot, vertices=40, rotation=(0, math.radians(90), 0))
    rim_b = cyl_obj(f"{pivot_name}_Hub", 0.11, 0.43, (0, 0, 0), rim, parent=pivot, vertices=32, rotation=(0, math.radians(90), 0))
    for obj in (tire, rim_a, rim_b):
        obj["webar_role"] = "wheel_mesh"
    pivot["webar_role"] = "front_steer_wheel" if steerable else "rear_wheel"
    pivot["axis"] = "Y"
    return pivot


def create_model():
    clear_scene()

    crane_yellow = mat("industrial_yellow", (1.0, 0.68, 0.08, 1))
    dark = mat("matte_black", (0.015, 0.017, 0.018, 1), roughness=0.7)
    glass = mat("blue_gray_glass", (0.08, 0.17, 0.24, 0.58), roughness=0.08)
    steel = mat("brushed_steel", (0.48, 0.51, 0.52, 1), metallic=0.35, roughness=0.32)
    hydraulic = mat("hydraulic_chrome", (0.82, 0.86, 0.84, 1), metallic=0.55, roughness=0.18)
    red = mat("safety_red", (0.88, 0.06, 0.04, 1))
    white = mat("marker_white", (0.95, 0.95, 0.9, 1))

    root = empty("CraneVehicle_ROOT", (0, 0, 0), display="CUBE", size=0.8)
    root.rotation_euler = (math.radians(90), 0, 0)
    root["webar_role"] = "root"
    root["description"] = "Procedural rough-terrain crane model. Named pivots are prepared for WebAR UI control."

    chassis = empty("Chassis", (0, 0, 0), parent=root, display="CUBE", size=0.6)
    chassis["webar_role"] = "vehicle_body"
    cube_obj("Chassis_MainFrame", (2.2, 0.34, 5.6), (0, 0.72, 0), crane_yellow, parent=chassis, bevel=0.04)
    cube_obj("Chassis_UnderFrame", (2.0, 0.26, 5.2), (0, 0.5, -0.05), dark, parent=chassis, bevel=0.03)
    cube_obj("Front_Bumper", (2.25, 0.32, 0.22), (0, 0.72, 2.92), dark, parent=chassis, bevel=0.03)
    cube_obj("Rear_Counter_Bumper", (2.25, 0.28, 0.24), (0, 0.68, -2.92), dark, parent=chassis, bevel=0.03)

    make_wheel("FrontWheel_FL", -1.24, 1.95, chassis, dark, steel, True)
    make_wheel("FrontWheel_FR", 1.24, 1.95, chassis, dark, steel, True)
    make_wheel("FrontWheel_RL", -1.24, -1.85, chassis, dark, steel, False)
    make_wheel("FrontWheel_RR", 1.24, -1.85, chassis, dark, steel, False)

    cab = empty("DriverCab", (-0.62, 1.12, 1.25), parent=chassis, display="CUBE", size=0.25)
    cab["webar_role"] = "cockpit"
    cube_obj("DriverCab_Body", (0.95, 0.9, 1.15), (0, 0, 0), crane_yellow, parent=cab, bevel=0.07)
    cube_obj("DriverCab_Windshield", (0.78, 0.46, 0.035), (0, 0.16, 0.59), glass, parent=cab, bevel=0.015)
    cube_obj("DriverCab_SideGlass_L", (0.035, 0.42, 0.55), (-0.49, 0.12, 0.04), glass, parent=cab, bevel=0.012)
    cube_obj("DriverCab_SideGlass_R", (0.035, 0.42, 0.55), (0.49, 0.12, 0.04), glass, parent=cab, bevel=0.012)
    cube_obj("DriverCab_RoofLight", (0.5, 0.07, 0.09), (0, 0.49, 0.36), red, parent=cab, bevel=0.02)
    cockpit = empty("Camera_Cockpit_View", (-0.62, 1.55, 1.85), parent=chassis, display="SINGLE_ARROW", size=0.3)
    cockpit["webar_role"] = "camera_anchor"

    for side, sign in (("L", -1), ("R", 1)):
        for end, z in (("Front", 2.55), ("Rear", -2.55)):
            outrigger = empty(f"Outrigger_{end}_{side}", (0, 0, z), parent=chassis, display="ARROWS", size=0.2)
            outrigger["webar_role"] = "outrigger"
            cube_obj(f"Outrigger_{end}_{side}_Mount", (0.82, 0.28, 0.4), (sign * 1.0, 0.72, 0), crane_yellow, parent=outrigger, bevel=0.025)
            cube_obj(f"Outrigger_{end}_{side}_Beam", (2.2, 0.2, 0.24), (sign * 1.18, 0.62, 0), steel, parent=outrigger, bevel=0.02)
            cube_obj(f"Outrigger_{end}_{side}_Jack", (0.16, 0.64, 0.16), (sign * 2.18, 0.28, 0), steel, parent=outrigger, bevel=0.018)
            cube_obj(f"Outrigger_{end}_{side}_Foot", (0.56, 0.1, 0.56), (sign * 2.18, -0.08, 0), dark, parent=outrigger, bevel=0.03)

    turntable = empty("Turntable_Yaw", (0, 1.05, -0.35), parent=root, display="ARROWS", size=0.5)
    turntable["webar_role"] = "turntable"
    turntable["axis"] = "Y"
    turntable["min_deg"] = -180
    turntable["max_deg"] = 180
    cyl_obj("Turntable_BaseRing", 0.82, 0.22, (0, 0, 0), steel, parent=turntable, rotation=(math.radians(90), 0, 0))
    cube_obj("UpperHouse_Main", (1.75, 0.85, 1.45), (0.18, 0.43, -0.18), crane_yellow, parent=turntable, bevel=0.06)
    cube_obj("UpperHouse_ServiceDoor", (0.04, 0.58, 0.64), (-0.73, 0.48, -0.18), dark, parent=turntable, bevel=0.015)
    cube_obj("Counterweight_Block", (1.55, 0.66, 0.5), (0.18, 0.34, -1.05), dark, parent=turntable, bevel=0.04)
    cube_obj("MachineryDeck_Railing", (1.95, 0.08, 1.7), (0.18, 0.95, -0.16), steel, parent=turntable, bevel=0.015)

    boom_pitch = empty("BoomPitch_X", (0, 1.72, 0.34), parent=turntable, display="ARROWS", size=0.45)
    boom_pitch["webar_role"] = "boom_pitch"
    boom_pitch["axis"] = "X"
    boom_pitch["min_deg"] = -20
    boom_pitch["max_deg"] = 72
    cube_obj("BoomBase_Section", (0.58, 0.42, 3.1), (0, 0, 1.55), crane_yellow, parent=boom_pitch, bevel=0.035)
    cube_obj("BoomBase_TopStripe", (0.62, 0.055, 2.95), (0, 0.23, 1.62), white, parent=boom_pitch, bevel=0.01)

    boom_extend = empty("BoomExtend_Z", (0, 0, 2.45), parent=boom_pitch, display="SINGLE_ARROW", size=0.4)
    boom_extend["webar_role"] = "boom_extend"
    boom_extend["axis"] = "Z"
    boom_extend["min"] = 0
    boom_extend["max"] = 3.2
    cube_obj("Boom_SecondStage", (0.44, 0.32, 2.45), (0, 0, 1.18), crane_yellow, parent=boom_extend, bevel=0.03)
    boom_second_extend = empty("BoomSecondExtend_Z", (0, 0, 0), parent=boom_extend, display="SINGLE_ARROW", size=0.34)
    boom_second_extend["webar_role"] = "boom_second_extend"
    boom_second_extend["axis"] = "Z"
    boom_second_extend["min"] = 0
    boom_second_extend["max"] = 1.15
    cube_obj("Boom_ThirdStage", (0.33, 0.24, 2.15), (0, 0, 2.28), crane_yellow, parent=boom_second_extend, bevel=0.025)
    cube_obj("Boom_TipHead", (0.54, 0.52, 0.22), (0, 0, 3.48), steel, parent=boom_second_extend, bevel=0.025)
    cyl_obj("Boom_TipSheave", 0.18, 0.56, (0, -0.03, 3.6), dark, parent=boom_second_extend, vertices=32, rotation=(0, math.radians(90), 0))

    for side, x in (("L", -0.34), ("R", 0.34)):
        cube_obj(f"BoomLiftCylinder_BaseBracket_{side}", (0.16, 0.2, 0.24), (x, 0.9, 0.28), steel, parent=turntable, bevel=0.018)
        cyl_obj(
            f"BoomLiftCylinder_Barrel_{side}",
            0.07,
            1.15,
            (x, 1.08, 0.72),
            steel,
            parent=turntable,
            vertices=24,
            rotation=(math.radians(60), 0, 0),
        )
        cyl_obj(
            f"BoomLiftCylinder_Rod_{side}",
            0.04,
            1.18,
            (x, 1.42, 1.28),
            hydraulic,
            parent=turntable,
            vertices=24,
            rotation=(math.radians(60), 0, 0),
        )
        cube_obj(f"BoomLiftCylinder_BoomBracket_{side}", (0.14, 0.18, 0.2), (x, -0.24, 0.88), steel, parent=boom_pitch, bevel=0.016)

    hook_hoist = empty("HookHoist_Y", (0, -0.05, 3.64), parent=boom_second_extend, display="SINGLE_ARROW", size=0.3)
    hook_hoist["webar_role"] = "hook_hoist"
    hook_hoist["axis"] = "Y"
    hook_hoist["min"] = -2.8
    hook_hoist["max"] = 0.8
    cable = cyl_obj("Hook_Cable", 0.018, 1.35, (0, -0.62, 0), dark, parent=hook_hoist, vertices=16, rotation=(math.radians(90), 0, 0))
    cable["webar_role"] = "cable"
    hook = empty("HookBlock_Swing", (0, -1.32, 0), parent=hook_hoist, display="ARROWS", size=0.25)
    hook["webar_role"] = "hook_swing"
    hook["axis"] = "Z"
    cube_obj("HookBlock_Body", (0.34, 0.28, 0.24), (0, 0, 0), dark, parent=hook, bevel=0.03)
    cyl_obj("HookBlock_Sheave", 0.12, 0.38, (0, 0.04, 0), steel, parent=hook, vertices=32, rotation=(0, math.radians(90), 0))
    cube_obj("Hook_Geometry", (0.08, 0.42, 0.16), (0, -0.35, 0), red, parent=hook, bevel=0.035)

    add_text_label("Demo_Label_Left", "WEBAR CRANE", (-1.12, 1.0, 0.15), chassis, dark)

    bpy.ops.object.light_add(type="AREA", location=(0, 7, 1.5))
    light = bpy.context.object
    light.name = "Studio_AreaLight"
    light.data.energy = 650
    light.data.size = 5

    bpy.ops.object.camera_add(location=(8.2, 4.8, 9.2))
    camera = bpy.context.object
    look_at(camera, (0, 1.05, 0.1))
    camera.data.lens = 24
    bpy.context.scene.camera = camera
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1000

    # Add simple demo keyframes so Blender users can preview the intended motion.
    for frame, yaw, pitch, extend, hook_y in [
        (1, 0, 12, 0.0, 0.0),
        (70, 55, 36, 1.4, -0.7),
        (130, -42, 58, 2.8, -1.35),
        (190, 0, 18, 0.3, -0.15),
    ]:
        bpy.context.scene.frame_set(frame)
        turntable.rotation_euler = (0, math.radians(yaw), 0)
        boom_pitch.rotation_euler = (math.radians(-pitch), 0, 0)
        boom_extend.location.z = 2.45 + min(extend, 1.15)
        boom_second_extend.location.z = min(extend, 1.15)
        hook_hoist.location.y = hook_y
        for obj in (turntable, boom_pitch, boom_extend, boom_second_extend, hook_hoist):
            obj.keyframe_insert(data_path="rotation_euler")
            obj.keyframe_insert(data_path="location")

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 190

    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_GLB,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
    )
    bpy.ops.wm.usd_export(
        filepath=OUTPUT_USDZ,
        export_animation=True,
        export_materials=True,
        export_textures=True,
        export_lights=False,
        export_cameras=False,
    )


if __name__ == "__main__":
    create_model()
