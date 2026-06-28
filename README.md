# -crane-webar-demo

Procedural rough-terrain crane WebAR prototype.

## Contents

- `index.html`: Three.js/WebXR demo UI
- `webar_crane_generated.glb`: generated crane model
- `webar_crane_generated.usdz`: iPhone/iPad AR Quick Look model
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

## Mobile AR Support

- Android Chrome: uses WebXR AR through the `AR` button.
- iPhone/iPad Safari: uses Apple AR Quick Look through the `iPhone AR` button.

iPhone Safari does not currently provide the same WebXR `immersive-ar` path used by
Android Chrome. Because of that, the iPhone AR mode opens the USDZ model in AR Quick
Look. The web UI controls are available in the browser preview, but not inside Quick Look.

## Regenerate The Model

Run inside Blender:

```powershell
blender --background --python create_webar_crane.py
```

The script generates:

- `webar_crane_generated.blend`
- `webar_crane_generated.glb`
- `webar_crane_generated.usdz`

## Notes

The crane shape is a generic commercial rough-terrain crane style. It intentionally avoids
copying any specific manufacturer logo, trademark, or exact product geometry.
