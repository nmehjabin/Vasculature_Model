#run the code in python 3.10.11 version
import sys
import os  # For constructing the desktop path
from datetime import datetime  # For generating the date in the filename

import numpy as np
import random
import matplotlib.pyplot as plt
from vasculature import Vasculature  # Importing the class from vasculature.py

# Initialize grid and VEGF field
grid_size = (5,5)
grid = np.zeros(grid_size, dtype=int)

# Initialize VEGF field with random concentrations or a gradient
vegf_field = np.random.uniform(0, 1, grid_size)  # Random VEGF values between 0 and 1

# Set initial positions for tip cells- here 2 tip cells
# initial_positions = [(5,5),(2,7),(1,6)]-anast happend on 10/10 grid
initial_positions = [(4,3),(2,4),(3,3)]
num_of_tip_cells = len(initial_positions)
vasculature = Vasculature(grid, initial_positions, vegf_field)

# Simulation parameters
steps = 10
# Generate dynamic folder name with the current date and time
current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_name = f"Simulation_{current_date}"
desktop_path = os.path.expanduser("~/Desktop/sproj'24-'25/code v2/figures") 
folder_path = os.path.join(desktop_path, folder_name)

# Create the folder
os.makedirs(folder_path, exist_ok=True)

# Define file names for the log and plot
log_file_name = "simulation_log.txt"
plot_file_name = "vasculature_growth_vegf.png"

log_file_path = os.path.join(folder_path, log_file_name)
plot_file_path = os.path.join(folder_path, plot_file_name)

# Simulation loop
# for step in range(steps):
#     print(f"Step {step}: Active tips = {sum(vasculature.active_tips)}")
#     #step 1
#     vasculature.grow()
#     # Optionally update VEGF field (e.g., diffusion or decay)
#     vegf_field *= 0.9  # Simple decay model to reduce VEGF over time

#     #step2
#     # vasculature.check_anastomosis()

#     if not any(vasculature.active_tips):
#         print("No active tips remaining. Simulation complete.")
#         break

# for step in range(steps):
#     print("checking anast in diff iteration")
#     vasculature.check_anastomosis()

###Trying alternative step check for simulation:
# Redirect print statements to the log file
with open(log_file_path, "w") as log_file:
    sys.stdout = log_file
        
    # Simulation loop
    for step in range(steps):
        if step % 2 == 0:
            # Step 1: Grow vasculature
            print(f"Step {step}: Growth phase")
            print(f"Active tips before growth: {sum(vasculature.active_tips)}")
            vasculature.grow()
            
            # Optionally update VEGF field (e.g., diffusion or decay)
            vegf_field *= 0.9  # Simple decay model to reduce VEGF over time

        else:
            # Step 2: Check for anastomosis
            print(f"Step {step}: Anastomosis check phase")
            vasculature.check_anastomosis()
        
        # Check if any active tips remain after growth and anastomosis check
        if not any(vasculature.active_tips):
            print("No active tips remaining. Simulation complete.")
            break

    sys.stdout = sys.__stdout__  # Reset stdout to default


# Visualize the grid- subplot 
plt.figure(figsize=(12, 6))

# Plot vasculature growth
plt.subplot(1, 2, 1)
plt.imshow(grid, cmap="viridis")  # Use 'viridis' colormap to distinguish values
plt.title("Vasculature Growth")
plt.suptitle('Num of steps: %d, Num of tip cells: %d' % (steps, num_of_tip_cells))
plt.colorbar(label="Cell State (0=empty, 1=vasculature, 2=tip cell)")
plt.xlabel("X-axis (Grid Columns)")
plt.ylabel("Y-axis (Grid Rows)")

# Plot VEGF field
plt.subplot(1, 2, 2)
plt.imshow(vegf_field, cmap="plasma")  # Use a 'plasma' colormap for VEGF
plt.title("VEGF Concentration")
plt.colorbar(label="VEGF Level")
plt.xlabel("X-axis (Grid Columns)")
plt.ylabel("Y-axis (Grid Rows)")

plt.tight_layout()

# # Generate dynamic file name with the current date
# current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Format: YYYY-MM-DD
# file_name = f"{current_date}_vasculature_growth_vegf.png"

# # Save the plot to the desktop

# desktop_path = os.path.expanduser("~/Desktop/sproj'24-'25/code v2/figures")  # Automatically resolves to your desktop
# os.makedirs(desktop_path, exist_ok=True)  # Ensure the directory exists

# output_path = os.path.join(desktop_path, file_name)
# plt.savefig(output_path, dpi=300, bbox_inches="tight")
# print(f"Figure saved to {output_path}")
# print(f"Desktop path: {desktop_path}")
# print(f"Output path: {output_path}")

plt.show()