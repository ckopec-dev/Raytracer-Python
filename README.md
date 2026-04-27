# Raytracer-Python

## Engine features (raytracer.py)

- Vec3 math (dot, cross, reflect, normalize)
- Ray, Camera with configurable FOV and look-at
- Geometry: Sphere, Plane, CheckerPlane
- Material with ambient, diffuse, specular (Blinn-Phong), reflectivity
- PointLight with color and intensity
- Hard shadows, recursive reflections (configurable max depth)
- Gamma correction (√ tone mapping)

## Three sample scenes (render_samples.py)

- Classic spheres — large mirror ball, red matte, gold metallic, small cyan sphere over a checkerboard floor
- Bubble cluster — six colourful reflective spheres in a dark environment
- Minimalist room — three primary-coloured balls on a white floor with a back wall

To add your own scene, just instantiate Scene, drop in Sphere/Plane objects with custom Materials, add PointLights, aim a Camera, and call render(). Increasing max_depth gives deeper mirror bounces; increasing samples gives anti-aliasing (at a linear time cost).
