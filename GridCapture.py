import bpy
import os
from mathutils import Vector

# ============================================================
# --- 1. USER SETTINGS ---
# ============================================================

rows = 24          # Number of positions along the local Y-axis
cols = 56          # Number of positions along the local X-axis
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
# (This position will now act as the CENTER of the grid)
start_matrix = camera.matrix_world.copy()

# Create folder if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Calculate the center indices of the grid.
# For odd dimensions (e.g., 21), this gives the exact middle index (10.0).
# For even dimensions (e.g., 20), this gives the middle between two indices (9.5).
center_r = (rows - 1) / 2.0
center_c = (cols - 1) / 2.0


# ============================================================
# --- 3. EXECUTION ---
# ============================================================

for r in range(rows):
    for c in range(cols):

        # ----------------------------------------------------
        # Define the offset vector in local space.
        #
        # By subtracting the center indices (center_c, center_r), 
        # we ensure the initial camera position (0 offset) 
        # corresponds to the center of the grid.
        #
        # X: Moves left -> right
        # Y: Reversed so rendering starts at the TOP and moves downward.
        # ----------------------------------------------------

        local_offset = Vector((
            (c - center_c) * spacing,
            -(r - center_r) * spacing,
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


# Reset the camera back to its original starting position (Center)
camera.matrix_world = start_matrix