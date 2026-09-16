# Lens Array Hologram

Tooling for creating **integral / lenticular-style hologram content** for a lens array (fly's-eye lens sheet).

A Blender script captures the same scene from every position of a regular grid, and a single-file web page displays all captures as one uniform mosaic that can be nudged, scaled and rotated so it lands exactly on the lens array.

## How it works

```
Blender (GridCapture.py)          Browser (index.html)
  scene + camera grid   ──▶  render_rowR_colC.png   ──▶  20×20 mosaic + alignment controls
```

1. **Capture** — the camera is stepped through a grid of positions inside Blender, one render per position. Each render is a view of the scene from a slightly different angle, and the set together encodes the parallax that the lens array decodes back into a 3D image.
2. **Assemble** — the web page loads those renders as a `rows × cols` grid with no gaps, so neighbouring views are pixel-adjacent, exactly as they must be under the lenslets.
3. **Align** — the mosaic is translated, scaled and rotated with precision wheels until it is registered to the physical lens array (print/substrate alignment is never perfect, so this is where the last fraction of a millimetre is dialled in).

## Files

| File | Purpose |
| --- | --- |
| `GridCapture.py` | Blender script that renders the camera-position grid |
| `index.html` | Standalone viewer + alignment tool for the captured grid |

## 1. Capturing the grid — `GridCapture.py`

### Requirements

- Blender 2.8+ (uses `bpy`, `mathutils`)
- A saved `.blend` with a **camera already assigned** to the scene (the script reads `bpy.context.scene.camera`) and positioned/rotated to the centre of the intended grid

### Usage

1. Open the scene in Blender.
2. Open the **Scripting** workspace, load `GridCapture.py`, press **Run Script**.

### Settings

Edit the user settings block at the top of the file:

| Setting | Default | Meaning |
| --- | --- | --- |
| `rows` | `20` | Positions along the camera's local **Y** axis (up/down in view) |
| `cols` | `20` | Positions along the camera's local **X** axis (left/right in view) |
| `spacing` | `0.1` | Distance between grid points, in Blender units |
| `output_dir` | `C:\Users\FuadFaruk\Desktop\Images` | Destination folder (created if missing) |

### Behaviour notes

- Offsets are applied in the camera's **local** space, so the grid stays parallel to the camera's original facing regardless of how it was rotated. The camera is not re-aimed between shots.
- Movement is purely lateral (`local Z = 0`), giving a flat, evenly spaced viewpoint plane — the geometry an integral lens array expects.
- Filenames are `render_row{r}_col{c}.png`.
- The whole grid is `rows × cols` renders, so the defaults produce **400 images**. Use low samples / small resolution while iterating.
- The camera is returned to its original transform when the loop finishes.
- Set the render resolution and output format in Blender's **Output Properties** (this script only sets the file path per frame, not the resolution).

## 2. Viewing and aligning — `index.html`

### Requirements

- Any modern browser (Chrome, Edge, Firefox, Safari). No server, no build step, no dependencies.
- Images placed **next to `index.html`** — the page requests `render_row0_col0.jpg` … `render_row19_col19.jpg` from the same folder.

> **Format mismatch to be aware of:** the Blender script writes `.png`, while the viewer requests `.jpg` (`index.html:280`). Either switch Blender's output format to JPEG, or change the filename extension in the script (or in the viewer) so the two agree.

### Usage

1. Copy the renders and `index.html` into the same folder.
2. Open `index.html` in a browser.
3. Drag the wheels until the mosaic matches the lens array, then read the values off and use them for the final print/placement.

### Controls

| Control | Range | Step | Description |
| --- | --- | --- | --- |
| **X** | −2000 … 2000 px | 0.1 px | Horizontal shift |
| **Y** | −2000 … 2000 px | 0.1 px | Vertical shift |
| **Scale** | 0.05 … 20× | 0.001× | Overall size — used to make one lenslet pitch equal one image cell |
| **Rot** | −180 … 180° | 0.1° | Rotation, for arrays that are not perfectly axis-aligned |

Interactions:

- **Drag a wheel** left/right to change its value (`pixelsPerStep` sets how far a drag must travel per step).
- **Double-click / double-tap a wheel** to reset it to `0` (X, Y, Rot).
- **Pinch** on a touch device to zoom; the Scale wheel stays in sync.
- The value readouts are tabular-aligned, so values can be transcribed without jitter.

Ticks are virtualised — only the ticks visible in the wheel are drawn — so the 0.001× scale resolution does not cost performance.

### Layout assumptions

- Grid size is hard-coded as **20 × 20** in three places: the CSS `grid-template-columns/rows` (`index.html:52`) and the image-generation loop (`index.html:275`), plus the `rows`/`cols` values in `GridCapture.py`. Change all of them together if you capture a different grid.
- The mosaic is sized to `min(100vw, 100vh)` and centred, so it stays square on any screen.
- Images use `object-fit: cover` and zero gap, which is what makes the tiles seamless.

## Typical workflow

1. Set up the scene in Blender and place the camera at the grid centre.
2. Set a low resolution and run `GridCapture.py` to verify the views look right.
3. Re-run at final resolution / samples and with the output format set to JPEG.
4. Put the renders and `index.html` in one folder; open the page.
5. Tune **Scale** until one cell matches one lenslet pitch, then **X / Y / Rot** to register the mosaic to the array.
6. Record the final values for production.
