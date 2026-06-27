# Crane WebAR Demo

Procedural rough-terrain crane WebAR prototype.

## Contents

- `index.html`: Three.js/WebXR demo UI
- `webar_crane_generated.glb`: generated crane model
- `create_webar_crane.py`: Blender Python generator
- `preview_0001.png`: rendered preview

## Features

- Forward/reverse/left/right/brake controls
- Front wheel steering
- Turntable slew
- Boom luffing
- Boom telescoping
- Hook up/down
- Hook swing while slewing
- Cockpit, outside, and top-down camera views
- Model scale control

## Local Run

Run from this directory:

```powershell
python -m http.server 8091 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8091/index.html
```

The demo currently loads Three.js from a CDN, so internet access is required.

## Regenerate The Model

Run inside Blender:

```powershell
blender --background --python create_webar_crane.py
```

The script generates:

- `webar_crane_generated.blend`
- `webar_crane_generated.glb`

## Notes

The crane shape is a generic commercial rough-terrain crane style. It intentionally avoids
copying any specific manufacturer logo, trademark, or exact product geometry.
