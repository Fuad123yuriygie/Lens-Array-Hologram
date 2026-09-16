import bpy
import os
from mathutils import Vector

# --- 1. USER SETTINGS ---
rows = 20          # Number of positions along the local Y-axis (up/down relative to view)
cols = 20          # Number of positions along the local X-axis (left/right relative to view)
spacing = 0.1     # Distance (in Blender units) between each grid point
output_dir = "C:\\Users\\FuadFaruk\\Desktop\\Images"  

# --- 2. SETUP ---
camera = bpy.context.scene.camera

# Store the camera's original starting matrix (captures position and rotation)
start_matrix = camera.matrix_world.copy()

# Create folder if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- 3. EXECUTION ---
for r in range(rows):
    for c in range(cols):
        # 1. Define the offset vector in local space
        # Local X = horizontal shift, Local Y = vertical shift, Local Z = 0 (no forward/backward)
        local_offset = Vector((c * spacing, r * spacing, 0.0))
        
        # 2. Convert the local offset into global space based on original camera rotation
        global_offset = start_matrix.to_3x3() @ local_offset
        
        # 3. Apply the global offset to the original camera location
        camera.location = start_matrix.to_translation() + global_offset
        
        # Make sure Blender updates the scene matrix immediately
        bpy.context.view_layer.update()
        
        # Define unique filename for this grid position
        filename = f"render_row{r}_col{c}.png"
        bpy.context.scene.render.filepath = os.path.join(output_dir, filename)
        
        # Perform the render and save it automatically
        bpy.ops.render.render(write_still=True)

# Optional: Reset the camera back to its original starting position after rendering is done
camera.matrix_world = start_matrix
