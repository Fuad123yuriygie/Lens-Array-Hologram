# Lens Array Hologram

Tooling for creating **integral / lenticular-style hologram content** for a lens array (fly's-eye lens sheet).

A Blender script captures the same scene from every position of a regular grid, and a single-file web page displays all captures as one uniform mosaic that can be nudged, scaled and rotated so it lands exactly on the lens array.

## How it works

```
Blender (GridCapture.py)                     Browser (index.html)
  scene + camera grid  ──▶  render_rowR_colC  ──▶  20×20 mosaic + alignment controls
                            (flipped X + Y)
```

1. **Capture** — the camera is stepped through a grid of positions inside Blender, one render per position. Each render is a view of the scene from a slightly different angle, and the set together encodes the parallax that the lens array decodes back into a 3D image.
2. **Flip** — Blender's Video Sequence Editor is then used to flip every saved render on both the X and Y axes and write the result back over the original file. Flipping both axes is equivalent to a 180° rotation, so the mosaic is rotated half a turn relative to the raw renders.
3. **Assemble** — the web page loads those renders as a `rows × cols` grid with no gaps, so neighbouring views are pixel-adjacent, exactly as they must be under the lenslets.
4. **Align** — the mosaic is translated, scaled and rotated with precision wheels until it is registered to the physical lens array (print/substrate alignment is never perfect, so this is where the last fraction of a millimetre is dialled in).

## Files

| File | Purpose |
| --- | --- |
| `GridCapture.py` | Blender script that renders the camera-position grid, then flips and overwrites the results |
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
| `rows` | `20` | Positions along the camera's local **Y** axis (top/bottom in view) |
| `cols` | `20` | Positions along the camera's local **X** axis (left/right in view) |
| `spacing` | `0.1` | Distance between grid points, in Blender units |
| `output_dir` | `C:\Users\FuadFaruk\Desktop\Images` | Destination folder (created if missing) |
| `IMAGE_FORMAT` | `"JPEG"` | Output format — `"PNG"` or `"JPEG"` only; anything else raises a `ValueError` |

`IMAGE_FORMAT` is applied to the scene's render settings and also determines the file extension (`.png` / `.jpg`), so the extension the script writes follows this one setting. It is separate from the viewer, which always asks for `.jpg`.

### Behaviour notes

- Offsets are applied in the camera's **local** space, so the grid stays parallel to the camera's original facing regardless of how it was rotated. The camera is not re-aimed between shots.
- Movement is purely lateral (`local Z = 0`), giving a flat, evenly spaced viewpoint plane — the geometry an integral lens array expects.
- The **Y offset is negated** (`-r * spacing`) so iteration order matches image order: `row 0` is the **top** row and each subsequent row moves downward. Rows are therefore written top-to-bottom, matching how the grid is laid out in the viewer.
- Filenames are `render_row{r}_col{c}` plus the extension for the chosen format.
- The whole grid is `rows × cols` renders, so the defaults produce **400 images**. Use low samples / small resolution while iterating.
- The camera is returned to its original transform when the capture loop finishes.

### Post-processing (automatic flip)

After the capture loop, the script does a second pass over every rendered file:

1. Any existing sequence editor data is cleared, then the VSE is created fresh.
2. Each image is added as a single-frame image strip (`frame_final_duration = 1`) with both `use_flip_x` and `use_flip_y` enabled.
3. Frame range is forced to a single frame, the scene is rendered to a temporary `_flipping_temp_rowR_colC` file, and the strip is removed.
4. The temporary file replaces the original with `os.replace`, so the filename the viewer expects is unchanged.
5. Every file is reported as it is flipped; missing files are skipped with a `Skipping missing file: …` message instead of aborting the run.

Scene state (frame range, output filepath, format) is saved before this pass and restored afterwards, and the sequence editor is cleared again at the end. A summary is printed on completion:

```
DONE
Rendered 400 images
Format: JPEG
Pan direction: TOP -> BOTTOM
All images flipped on X and Y axes
```

Because the flip pass re-renders each image through the VSE, it re-encodes the files using the scene's current render settings. Two consequences:

- Capture and flip happen in the same run, so an interrupted run can leave a folder that is only partly flipped; re-running the script regenerates and re-flips everything.
- Re-running the script against a folder that already holds flipped images flips them a second time, returning them to their original orientation.


## 2. Viewing and aligning — `index.html`

### Requirements

- Any modern browser (Chrome, Edge, Firefox, Safari). No server, no build step, no dependencies.
- Images placed **next to `index.html`** — the page requests `render_row0_col0.jpg` … `render_row19_col19.jpg` (`.jpg`, hard-coded at `index.html:280`) from the same folder.

> **Format must match:** the viewer always asks for `.jpg`, which is what `IMAGE_FORMAT = "JPEG"` (the script default) produces. If you set `IMAGE_FORMAT = "PNG"`, also update the extension in the viewer's image loop, otherwise every tile will 404.

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
- Row order matters: `GridCapture.py` writes `row 0` as the top row (negated Y offset), which is the order the viewer fills the grid in. If you change the capture direction, the mosaic will come out vertically mirrored.
- The mosaic is sized to `min(100vw, 100vh)` and centred, so it stays square on any screen.
- Images use `object-fit: cover` and zero gap, which is what makes the tiles seamless.

## Typical workflow

1. Set up the scene in Blender and place the camera at the grid centre.
2. Set `IMAGE_FORMAT` and a low resolution in Blender, then run `GridCapture.py` to verify the views look right (the flip pass runs automatically, so the output is already in final orientation).
3. Re-run at the final resolution / samples once the framing is correct.
4. Put the renders and `index.html` in one folder; open the page.
5. Tune **Scale** until one cell matches one lenslet pitch, then **X / Y / Rot** to register the mosaic to the array.
6. Record the final values for production.
