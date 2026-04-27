"""
Sample scenes for the ray tracer.
Run:  python render_samples.py
"""

import os
from raytracer import *

OUTPUT = "."
os.makedirs(OUTPUT, exist_ok=True)

W, H = 1280, 1024


# ────────────────────────────────────────────────────────────────
# Scene 1 – Classic spheres on a checker floor
# ────────────────────────────────────────────────────────────────

def scene_classic():
    scene = Scene()
    scene.background = Vec3(0.4, 0.7, 1.0)

    # Floor
    mat_a = Material(color=Vec3(0.9,0.9,0.9), diffuse=0.8, specular=0.1, reflectivity=0.05)
    mat_b = Material(color=Vec3(0.2,0.2,0.2), diffuse=0.8, specular=0.1, reflectivity=0.05)
    scene.add(CheckerPlane(Vec3(0,-1,0), Vec3(0,1,0), mat_a, mat_b, scale=1.5))

    # Large mirror sphere
    mirror = Material(color=Vec3(0.9,0.9,1.0), diffuse=0.05, specular=1.0,
                      shininess=200, reflectivity=0.9)
    scene.add(Sphere(Vec3(0, 0.5, -4), 1.5, mirror))

    # Red matte sphere
    red = Material(color=RED, diffuse=0.9, specular=0.3, shininess=40)
    scene.add(Sphere(Vec3(-3, 0, -5), 1.0, red))

    # Gold metallic sphere
    gold = Material(color=GOLD, diffuse=0.6, specular=1.0, shininess=150, reflectivity=0.4)
    scene.add(Sphere(Vec3(3, 0, -5), 1.0, gold))

    # Small cyan sphere
    cyan_m = Material(color=CYAN, diffuse=0.8, specular=0.5, shininess=64)
    scene.add(Sphere(Vec3(-1.2, -0.5, -2.5), 0.5, cyan_m))

    # Lights
    scene.add_light(PointLight(Vec3(-5, 8, 2),  Vec3(1,1,1),   1.2))
    scene.add_light(PointLight(Vec3( 5, 4, 0),  Vec3(1,0.9,0.7), 0.6))

    cam = Camera(Vec3(0, 2, 3), Vec3(0, 0, -4), Vec3(0,1,0), fov_deg=55, aspect=W/H)
    return scene, cam


# ────────────────────────────────────────────────────────────────
# Scene 2 – Colourful bubble cluster
# ────────────────────────────────────────────────────────────────

def scene_bubbles():
    scene = Scene()
    scene.background = Vec3(0.05, 0.02, 0.12)

    specs = [
        (Vec3( 0.0,  0.0, -5), 1.2, Vec3(1,0.3,0.3), 0.5),
        (Vec3( 2.2,  0.5, -5), 0.9, Vec3(0.3,0.6,1), 0.6),
        (Vec3(-2.2,  0.3, -5), 0.9, Vec3(0.3,1,0.5), 0.55),
        (Vec3( 1.1, -0.7, -3.5),0.5, GOLD,            0.7),
        (Vec3(-1.0, -0.8, -3.5),0.5, MAGENTA,         0.6),
        (Vec3( 0.0,  1.8, -4), 0.6, CYAN,             0.65),
    ]
    for center, r, col, refl in specs:
        mat = Material(color=col, ambient=0.08, diffuse=0.5,
                       specular=1.0, shininess=120, reflectivity=refl)
        scene.add(Sphere(center, r, mat))

    # Dark floor
    floor = Material(color=Vec3(0.1,0.1,0.15), diffuse=0.4, specular=0.6,
                     shininess=80, reflectivity=0.3)
    scene.add(Plane(Vec3(0,-2,0), Vec3(0,1,0), floor))

    scene.add_light(PointLight(Vec3(-4, 6, 2), Vec3(1,0.8,0.6), 1.5))
    scene.add_light(PointLight(Vec3( 4, 3,-2), Vec3(0.4,0.6,1), 1.0))
    scene.add_light(PointLight(Vec3( 0, 1, 2), WHITE, 0.4))

    cam = Camera(Vec3(0, 1, 2), Vec3(0, 0, -4), Vec3(0,1,0), fov_deg=60, aspect=W/H)
    return scene, cam


# ────────────────────────────────────────────────────────────────
# Scene 3 – Minimalist room: three coloured balls on a white plane
# ────────────────────────────────────────────────────────────────

def scene_minimalist():
    scene = Scene()
    scene.background = Vec3(0.95, 0.95, 0.95)

    white_floor = Material(color=WHITE, diffuse=0.9, specular=0.2,
                           shininess=32, reflectivity=0.1)
    scene.add(Plane(Vec3(0,-1,0), Vec3(0,1,0), white_floor))

    # Back wall
    back = Material(color=Vec3(0.85,0.85,0.85), diffuse=0.9, specular=0.0)
    scene.add(Plane(Vec3(0,0,-9), Vec3(0,0,1), back))

    balls = [
        (Vec3(-2.5, 0, -5), 1.0, Vec3(0.9, 0.15, 0.15), 0.05),
        (Vec3( 0.0, 0, -5), 1.0, Vec3(0.15, 0.50, 0.90), 0.3),
        (Vec3( 2.5, 0, -5), 1.0, Vec3(0.15, 0.80, 0.30), 0.05),
    ]
    for c, r, col, refl in balls:
        mat = Material(color=col, diffuse=0.85, specular=0.6,
                       shininess=80, reflectivity=refl)
        scene.add(Sphere(c, r, mat))

    scene.add_light(PointLight(Vec3( 0, 6, 0), WHITE, 1.5))
    scene.add_light(PointLight(Vec3(-4, 3, 2), Vec3(1,0.95,0.8), 0.5))

    cam = Camera(Vec3(0, 2, 4), Vec3(0, 0, -4), Vec3(0,1,0), fov_deg=50, aspect=W/H)
    return scene, cam


# ────────────────────────────────────────────────────────────────
# Render all scenes
# ────────────────────────────────────────────────────────────────

scenes_info = [
    ("classic_spheres",  scene_classic,    16),
    ("bubble_cluster",   scene_bubbles,    16),
    ("minimalist_room",  scene_minimalist, 16),
]

output_paths = []

for name, builder, depth in scenes_info:
    print(f"\n▶  Rendering '{name}' ...")
    sc, cam = builder()
    img = render(sc, cam, W, H, samples=4, max_depth=depth)
    path = f"{OUTPUT}/{name}.png"
    img.save(path)
    output_paths.append(path)
    print(f"   Saved → {path}")

print("\n✓ All done!")
