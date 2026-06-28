# crane-ky-demo

Crane KY 3D playback demo copied from the crane WebAR project.

## Purpose

This copy adds three hazard prediction examples for crane operation training.

1. KY1: outrigger not deployed
2. KY2: worker entering under suspended load
3. KY3: worker entering crane slew radius

## Files

- `index.html`: Three.js demo with KY playback UI
- `webar_crane_generated.glb`: crane model
- `webar_crane_generated.usdz`: iPhone/iPad AR Quick Look model
- `create_webar_crane.py`: Blender Python generator
- `preview_0001.png`: rendered preview

## Local Run

Run from this directory:

```powershell
python -m http.server 8092 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8092/index.html
```

The demo loads Three.js from a CDN, so internet access is required.
