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

oxygen_field = np.zeros_like(grid, dtype=float)
nutrient_field = np.zeros_like(grid, dtype=float)

# Set initial positions for tip cells- here 2 tip cells
# initial_positions = [(5,5),(2,7),(1,6)]-anast happend on 10/10 grid
initial_positions = [(4,3),(2,4),(3,3)]
num_of_tip_cells = len(initial_positions)
vasculature = Vasculature(grid, initial_positions, vegf_field, oxygen_field, nutrient_field)

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
plot_file_name = "vasculature_growth_vegf+anas+merged.png"

log_file_path = os.path.join(folder_path, log_file_name)
plot_file_path = os.path.join(folder_path, plot_file_name)

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
            vasculature.check_anastomosis_and_merge()

        # Update grid with current tip cells
        for tip in vasculature.tip_cells:
            grid[tip] = 2
#ADDing new here:
        # Mark anastomosis points in the grid as '3' (red in the plot)
        for merge in vasculature.merged_cells:  # Assuming `vasculature.merged_cells` stores anastomosis locations
            grid[merge] = 3

        # Step 3: Simulate diffusion of oxygen and nutrients from vessels (merged cells)
        vasculature.diffuse()
        
        # Check if any active tips remain after growth and anastomosis check
        if not any(vasculature.active_tips):
            print("No active tips remaining. Simulation complete.")
            break

    sys.stdout = sys.__stdout__  # Reset stdout to default


# Plotting the grid with anastomosis in red
plt.figure(figsize=(16, 8))

# Plot vasculature growth with anastomosis highlighted
plt.subplot(2, 2, 1)
plt.imshow(grid, cmap="viridis", vmin=0, vmax=3)
plt.title("Vasculature Growth")
plt.suptitle(f'Num of steps: {steps}, Num of tip cells: {num_of_tip_cells}')
cbar = plt.colorbar(label="Cell State (0=empty, 1=vasculature, 2=tip cell, 3=anastomosis)")
cbar.set_ticks([0, 1, 2, 3])
cbar.set_ticklabels(['Empty', 'Vasculature', 'Tip Cell', 'Anastomosis'])
plt.xlabel("X-axis (Grid Columns)")
plt.ylabel("Y-axis (Grid Rows)")
plt.grid(True, color='white', linestyle='--', linewidth=0.5)
plt.gca().set_facecolor('white')

# Plot VEGF field
plt.subplot(2, 2, 2)
plt.imshow(vegf_field, cmap="plasma")
plt.title("VEGF Concentration")
plt.colorbar(label="VEGF Level")
plt.xlabel("X-axis (Grid Columns)")
plt.ylabel("Y-axis (Grid Rows)")
plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
plt.gca().set_facecolor('white')


# Plot Oxygen field
plt.subplot(2, 2, 3)
plt.imshow(oxygen_field, cmap="coolwarm")
plt.title("Oxygen Concentration")
plt.colorbar(label="Oxygen Level")
plt.xlabel("X-axis (Grid Columns)")
plt.ylabel("Y-axis (Grid Rows)")
plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
plt.gca().set_facecolor('white')

# Plot Nutrient field
plt.subplot(2, 2, 4)
plt.imshow(nutrient_field, cmap="YlGnBu")
plt.title("Nutrient Concentration")
plt.colorbar(label="Nutrient Level")
plt.xlabel("X-axis (Grid Columns)")
plt.ylabel("Y-axis (Grid Rows)")
plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
plt.gca().set_facecolor('white')

# Adjust layout to prevent overlap
plt.subplots_adjust(wspace=0.3, hspace=0.3)


plt.tight_layout()
plt.savefig(plot_file_path, dpi=300, bbox_inches="tight")
print(f"Figure saved to {plot_file_path}")
plt.show()




