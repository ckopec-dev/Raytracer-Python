"""
Simple Ray Tracer Engine
Supports: spheres, planes, point lights, shadows, reflections, ambient/diffuse/specular shading
"""

import math
from dataclasses import dataclass, field
from typing import Optional
from PIL import Image


# ─── Math primitives ───────────────────────────────────────────────────────────

class Vec3:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def __add__(self, o): return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, s):
        if isinstance(s, Vec3): return Vec3(self.x*s.x, self.y*s.y, self.z*s.z)
        return Vec3(self.x*s, self.y*s, self.z*s)
    def __rmul__(self, s): return self.__mul__(s)
    def __truediv__(self, s): return Vec3(self.x/s, self.y/s, self.z/s)
    def __neg__(self): return Vec3(-self.x, -self.y, -self.z)

    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o):
        return Vec3(self.y*o.z - self.z*o.y,
                    self.z*o.x - self.x*o.z,
                    self.x*o.y - self.y*o.x)

    def length(self): return math.sqrt(self.dot(self))
    def normalize(self):
        l = self.length()
        return self / l if l > 1e-9 else Vec3(0, 0, 0)

    def reflect(self, normal):
        return self - normal * 2 * self.dot(normal)

    def clamp(self, lo=0.0, hi=1.0):
        return Vec3(max(lo, min(hi, self.x)),
                    max(lo, min(hi, self.y)),
                    max(lo, min(hi, self.z)))

    def to_rgb(self):
        c = self.clamp()
        return (int(c.x*255), int(c.y*255), int(c.z*255))

    def __repr__(self): return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


BLACK   = Vec3(0, 0, 0)
WHITE   = Vec3(1, 1, 1)
RED     = Vec3(1, 0, 0)
GREEN   = Vec3(0, 1, 0)
BLUE    = Vec3(0, 0, 1)
YELLOW  = Vec3(1, 1, 0)
CYAN    = Vec3(0, 1, 1)
MAGENTA = Vec3(1, 0, 1)
ORANGE  = Vec3(1, 0.5, 0)
PURPLE  = Vec3(0.5, 0, 0.5)
GOLD    = Vec3(1, 0.84, 0)


# ─── Ray ───────────────────────────────────────────────────────────────────────

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3   # should be normalised

    def at(self, t: float) -> Vec3:
        return self.origin + self.direction * t


# ─── Materials ────────────────────────────────────────────────────────────────

@dataclass
class Material:
    color:      Vec3  = field(default_factory=lambda: Vec3(0.8, 0.8, 0.8))
    ambient:    float = 0.1
    diffuse:    float = 0.8
    specular:   float = 0.5
    shininess:  float = 32.0
    reflectivity: float = 0.0
    transparency: float = 0.0
    ior:        float = 1.5   # index of refraction


# ─── Geometry ─────────────────────────────────────────────────────────────────

@dataclass
class HitRecord:
    t:        float
    point:    Vec3
    normal:   Vec3
    material: Material
    front_face: bool = True

    def set_face_normal(self, ray: Ray, outward_normal: Vec3):
        self.front_face = ray.direction.dot(outward_normal) < 0
        self.normal = outward_normal if self.front_face else -outward_normal


class Sphere:
    def __init__(self, center: Vec3, radius: float, material: Material):
        self.center   = center
        self.radius   = radius
        self.material = material

    def intersect(self, ray: Ray, t_min=1e-4, t_max=1e9) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a  = ray.direction.dot(ray.direction)
        hb = oc.dot(ray.direction)
        c  = oc.dot(oc) - self.radius * self.radius
        disc = hb*hb - a*c
        if disc < 0:
            return None
        sq = math.sqrt(disc)
        for t in ((-hb - sq) / a, (-hb + sq) / a):
            if t_min < t < t_max:
                pt = ray.at(t)
                n  = (pt - self.center) / self.radius
                rec = HitRecord(t=t, point=pt, normal=n, material=self.material)
                rec.set_face_normal(ray, n)
                return rec
        return None


class Plane:
    """Infinite plane defined by a point and a normal."""
    def __init__(self, point: Vec3, normal: Vec3, material: Material):
        self.point    = point
        self.normal   = normal.normalize()
        self.material = material

    def intersect(self, ray: Ray, t_min=1e-4, t_max=1e9) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-9:
            return None
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t_min < t < t_max:
            pt  = ray.at(t)
            rec = HitRecord(t=t, point=pt, normal=self.normal, material=self.material)
            rec.set_face_normal(ray, self.normal)
            return rec
        return None


class CheckerPlane(Plane):
    """Checkerboard-patterned infinite plane."""
    def __init__(self, point, normal, mat_a: Material, mat_b: Material, scale=1.0):
        super().__init__(point, normal, mat_a)
        self.mat_a = mat_a
        self.mat_b = mat_b
        self.scale = scale

    def intersect(self, ray: Ray, t_min=1e-4, t_max=1e9) -> Optional[HitRecord]:
        rec = super().intersect(ray, t_min, t_max)
        if rec is None:
            return None
        ix = int(math.floor(rec.point.x / self.scale))
        iz = int(math.floor(rec.point.z / self.scale))
        rec.material = self.mat_a if (ix + iz) % 2 == 0 else self.mat_b
        return rec


# ─── Lights ───────────────────────────────────────────────────────────────────

@dataclass
class PointLight:
    position:  Vec3
    color:     Vec3 = field(default_factory=lambda: Vec3(1, 1, 1))
    intensity: float = 1.0


# ─── Scene ────────────────────────────────────────────────────────────────────

class Scene:
    def __init__(self):
        self.objects: list = []
        self.lights:  list = []
        self.background: Vec3 = Vec3(0.05, 0.05, 0.15)

    def add(self, obj):
        self.objects.append(obj)
        return self

    def add_light(self, light):
        self.lights.append(light)
        return self

    def nearest_hit(self, ray: Ray, t_min=1e-4, t_max=1e9) -> Optional[HitRecord]:
        closest = None
        for obj in self.objects:
            hit = obj.intersect(ray, t_min, t_max)
            if hit and (closest is None or hit.t < closest.t):
                closest = hit
                t_max = hit.t
        return closest

    def is_shadowed(self, point: Vec3, light: PointLight) -> bool:
        to_light = light.position - point
        dist     = to_light.length()
        shadow_r = Ray(point, to_light.normalize())
        hit = self.nearest_hit(shadow_r, 1e-4, dist - 1e-4)
        return hit is not None


# ─── Renderer ─────────────────────────────────────────────────────────────────

class Camera:
    def __init__(self, origin: Vec3, look_at: Vec3, up: Vec3,
                 fov_deg: float, aspect: float):
        self.origin = origin
        theta  = math.radians(fov_deg)
        h      = math.tan(theta / 2)
        vp_w   = 2 * h * aspect
        vp_h   = 2 * h
        w = (origin - look_at).normalize()
        u = up.cross(w).normalize()
        v = w.cross(u)
        self.lower_left = origin - u*(vp_w/2) - v*(vp_h/2) - w
        self.horizontal = u * vp_w
        self.vertical   = v * vp_h

    def get_ray(self, s: float, t: float) -> Ray:
        target = self.lower_left + self.horizontal*s + self.vertical*t
        return Ray(self.origin, (target - self.origin).normalize())


def shade(ray: Ray, scene: Scene, depth: int = 0, max_depth: int = 4) -> Vec3:
    if depth > max_depth:
        return BLACK

    hit = scene.nearest_hit(ray)
    if hit is None:
        # Sky gradient
        t = 0.5 * (ray.direction.y + 1.0)
        return Vec3(1,1,1)*(1-t) + scene.background*t

    mat   = hit.material
    color = mat.color * mat.ambient          # ambient term

    for light in scene.lights:
        if scene.is_shadowed(hit.point, light):
            continue

        to_light  = (light.position - hit.point).normalize()
        light_col = light.color * light.intensity

        # Diffuse (Lambertian)
        diff = max(0.0, hit.normal.dot(to_light))
        color = color + mat.color * light_col * (mat.diffuse * diff)

        # Specular (Blinn-Phong)
        view_dir  = (-ray.direction).normalize()
        half_vec  = (to_light + view_dir).normalize()
        spec      = max(0.0, hit.normal.dot(half_vec)) ** mat.shininess
        color = color + light_col * (mat.specular * spec)

    # Reflection
    if mat.reflectivity > 0 and depth < max_depth:
        ref_dir = ray.direction.reflect(hit.normal).normalize()
        ref_ray = Ray(hit.point, ref_dir)
        ref_col = shade(ref_ray, scene, depth+1, max_depth)
        color = color * (1 - mat.reflectivity) + ref_col * mat.reflectivity

    return color


def render(scene: Scene, camera: Camera,
           width: int, height: int,
           samples: int = 1,
           max_depth: int = 4) -> Image.Image:
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for j in range(height):
        for i in range(width):
            col = BLACK
            for _ in range(samples):
                u = (i + 0.5) / width
                v = (height - j - 0.5) / height   # flip Y
                r = camera.get_ray(u, v)
                col = col + shade(r, scene, max_depth=max_depth)
            col = col / samples
            # simple gamma correction (gamma 2)
            col = Vec3(math.sqrt(max(0, col.x)),
                       math.sqrt(max(0, col.y)),
                       math.sqrt(max(0, col.z)))
            pixels[i, j] = col.to_rgb()
        if j % 50 == 0:
            print(f"  row {j}/{height}")
    return img
