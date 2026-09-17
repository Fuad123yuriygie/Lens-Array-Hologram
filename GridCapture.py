import bpy
import os
from mathutils import Vector

# ============================================================
# --- 1. USER SETTINGS ---
# ============================================================

rows = 20          # Number of positions along the local Y-axis
cols = 20          # Number of positions along the local X-axis
spacing = 0.1     # Distance between each grid point

output_dir = "C:\\Users\\FuadFaruk\\Desktop\\Images"

# Change this to "PNG" or "JPEG"
IMAGE_FORMAT = "JPEG"


# ============================================================
# --- IMAGE FORMAT SETUP ---
# ============================================================

IMAGE_FORMAT = IMAGE_FORMAT.upper()

if IMAGE_FORMAT == "PNG":
    image_extension = ".png"
elif IMAGE_FORMAT == "JPEG":
    image_extension = ".jpg"
else:
    raise ValueError("IMAGE_FORMAT must be either 'PNG' or 'JPEG'")

bpy.context.scene.render.image_settings.file_format = IMAGE_FORMAT


# ============================================================
# --- 2. SETUP ---
# ============================================================

camera = bpy.context.scene.camera

# Store the camera's original starting matrix
start_matrix = camera.matrix_world.copy()

# Create folder if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# ============================================================
# --- 3. EXECUTION ---
# ============================================================

for r in range(rows):
    for c in range(cols):

        # ----------------------------------------------------
        # Define the offset vector in local space.
        #
        # X:
        #   Moves left -> right
        #
        # Y:
        #   Reversed so rendering starts at the TOP
        #   and moves downward.
        #
        # row 0 = TOP
        # row 1 = below row 0
        # row 2 = below row 1
        # etc.
        # ----------------------------------------------------

        local_offset = Vector((
            c * spacing,
            -r * spacing,
            0.0
        ))

        # Convert local offset into global space
        global_offset = start_matrix.to_3x3() @ local_offset

        # Apply global offset to original camera location
        camera.location = start_matrix.to_translation() + global_offset

        # Make sure Blender updates the scene matrix immediately
        bpy.context.view_layer.update()

        # Define unique filename for this grid position
        filename = f"render_row{r}_col{c}{image_extension}"
        filepath = os.path.join(output_dir, filename)

        bpy.context.scene.render.filepath = filepath

        # Perform the render and save it automatically
        bpy.ops.render.render(write_still=True)


# Reset the camera back to its original starting position
camera.matrix_world = start_matrix


# ============================================================
# --- 4. FLIP ALL FINISHED IMAGES USING BLENDER'S VSE ---
# ============================================================

scene = bpy.context.scene

# Remove any existing sequence editor data
if scene.sequence_editor:
    scene.sequence_editor_clear()

seq = scene.sequence_editor_create()

# Save current settings
original_frame_start = scene.frame_start
original_frame_end = scene.frame_end
original_filepath = scene.render.filepath
original_file_format = scene.render.image_settings.file_format

# Make sure post-processing uses the selected format
scene.render.image_settings.file_format = IMAGE_FORMAT

for r in range(rows):
    for c in range(cols):

        filename = f"render_row{r}_col{c}{image_extension}"
        filepath = os.path.join(output_dir, filename)

        if not os.path.exists(filepath):
            print(f"Skipping missing file: {filepath}")
            continue

        # Temporary output file
        temp_filepath = os.path.join(
            output_dir,
            f"_flipping_temp_row{r}_col{c}{image_extension}"
        )

        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        # ----------------------------------------------------
        # Add the already-saved image as a VSE image strip
        # ----------------------------------------------------

        strip = seq.strips.new_image(
            name=f"Flip_{r}_{c}",
            filepath=filepath,
            channel=1,
            frame_start=1
        )

        # Single-frame image
        strip.frame_final_duration = 1

        # Flip horizontally AND vertically
        strip.use_flip_x = True
        strip.use_flip_y = True

        # Render only this single frame
        scene.frame_start = 1
        scene.frame_end = 1
        scene.frame_set(1)

        # Save flipped image to temporary file
        scene.render.filepath = temp_filepath

        bpy.ops.render.render(
            animation=False,
            write_still=True
        )

        # Remove strip after processing
        seq.strips.remove(strip)

        # Replace original image with flipped version
        if os.path.exists(temp_filepath):
            os.replace(temp_filepath, filepath)

        print(f"Flipped: {filename}")


# ============================================================
# --- 5. CLEANUP ---
# ============================================================

scene.sequence_editor_clear()

# Restore original settings
scene.frame_start = original_frame_start
scene.frame_end = original_frame_end
scene.render.filepath = original_filepath
scene.render.image_settings.file_format = original_file_format

print("============================================================")
print("DONE")
print(f"Rendered {rows * cols} images")
print(f"Format: {IMAGE_FORMAT}")
print("Pan direction: TOP -> BOTTOM")
print("All images flipped on X and Y axes")
print("============================================================")