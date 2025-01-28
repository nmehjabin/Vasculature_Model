import random
import numpy as np  

class Vasculature:
    def __init__(self, grid, initial_positions, vegf_field, oxygen_field, nutrient_field):
        self.grid = grid
        self.tip_cells = initial_positions  # List of active tip positions
        self.active_tips = [True] * len(initial_positions)  # Track which tips are active
        self.directions = {pos: None for pos in initial_positions}  # Tip cell growth direction
        self.vegf_field = vegf_field  # VEGF concentration field
        self.merged_cells = []  # List to store merged cell locations

        for pos in initial_positions:
            self.grid[pos] = 2  # Mark initial tips on the grid
#adding new here- Jan 27:
        # Initialize oxygen and nutrient fields
        self.oxygen_field = oxygen_field
        self.nutrient_field = nutrient_field

#This function looks at the neighbor grids from the current position, then it checks the 
# boundary condition of the grid and the value of the grid, then we check the direction of tip cell growth
# if the current coordinate != to a location that's prev  direction then we consider those
# empty grid as a valid grid for the tip cell to grow, [tip cell grows only forward] 

    def get_empty_neighbors(self, position, prev_direction=None):
        x, y = position
        neighbors = [
            (x+1, y), (x-1, y), (x, y+1), (x, y-1),  # Cardinal directions
            (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)  # Diagonals
        ]
        empty_neighbors = []
        for n in neighbors:
            if (0 <= n[0] < self.grid.shape[0] and 
                0 <= n[1] < self.grid.shape[1] and 
                self.grid[n] == 0):  # Neighbor is within bounds and empty
                # print("what is n[0]->",n[0])
                # print("what is grid.shape[0]->",self.grid.shape[0])
                # print("what is n[1]->",n[1])
                # print("what is grid.shape[[0]->",self.grid.shape[1])

                if prev_direction is None or (n[0]-x, n[1]-y) != (-prev_direction[0], -prev_direction[1]):
                    # print("what is prev dir:",prev_direction)
                    # print("LHS prev dir---->",(n[0]-x, n[1]-y) )
                    # print("RHS prev dir----->", (-prev_direction[0], -prev_direction[1]))
                    empty_neighbors.append(n)
        # print("Empty_Neighbor::",empty_neighbors)
        return empty_neighbors

#The growth direction of the tip cell will depend on the VEGF concentration, higher concentration
# means growth will be in that direction: The logic is we sort the empty neighbor coordinate based 
# where the VEGF is highest and return the sorted neighbors
    def choose_growth_direction(self, empty_neighbors):
        """Choose the growth direction based on VEGF concentration."""
       
        #new way ->>>>>>
        valid_neighbors = []
        for x,y in empty_neighbors:
            #check if the neighbor is within the grid
            if 0<= x < self.grid.shape[0] and 0<= y < self.grid.shape[1]:
                valid_neighbors.append((x,y))
                print("checking boundary here for tip cells")
        
        if not valid_neighbors:
            return None
        
        #Find the neighbor with the highest VEGF concentration
        max_vegf_neighbor = max(valid_neighbors, key= lambda n: self.vegf_field[n])
        print("vegf neighbor----",max_vegf_neighbor)
        return max_vegf_neighbor
    

#This function: for each tip cell it will check the conditions that's declared in function 
# "get_empty_neighbor" and "choose_growth_direction" then if it checks all condition, the tip cell
# is valid to grow and new tip cell is marked as '2', we keep track of all tip cell pos in a list
# as well as directions 
    def grow(self):
        new_tip_positions = []
        for i, tip in enumerate(self.tip_cells):
            print("tip cells-->",self.tip_cells)
            print("which old tip is running",i,tip)
            if not self.active_tips[i]:
                continue

            # Mark the current tip position as part of the vasculature
            #Assigning variables here:
            self.grid[tip] = 1
            self.vegf_field[tip] *= 0.5  # Consume VEGF at the current position

            prev_direction = self.directions.get(tip, None)
            empty_neighbors = self.get_empty_neighbors(tip, prev_direction)

            # Choose the growth direction based on VEGF concentration
            new_position = self.choose_growth_direction(empty_neighbors)
            

            #Check condition for growing 
            if new_position:
                self.grid[new_position] = 2  # Mark new tip position
                new_tip_positions.append(new_position)
                print("new_tip_positions--:", new_tip_positions)
                self.directions[new_position] = (new_position[0] - tip[0], new_position[1] - tip[1])
            else:
                #check the boundary of the tip cells
                x,y = tip
                if x==0 or x == self.grid.shape[0] - 1 or y==0 or y== self.grid.shape[1]-1 :
                    #stop growth of tip cells if at the boundary
                    print("Boundary condition reached")
                    self.active_tips[i] = False  
                else:
                    # Deactivate if no valid neighbors
                    self.active_tips[i] = False  

        # Update active tips
        self.tip_cells = new_tip_positions
        self.active_tips = [True] * len(new_tip_positions)

#ADDing New here Jan 27:
        # Perform merging and anastomosis after growth
        self.check_anastomosis_and_merge()


#This helper function to merge the tip cells for forming vessels
    def merge_tips(self, tip1, tip2):
        """Merge two tip cells into a single position."""
        merged_x = (tip1[0] + tip2[0]) // 2
        print(merged_x)
        merged_y = (tip1[1] + tip2[1]) // 2
        print(merged_y)
        return (merged_x, merged_y)
    
#This function checks if the tip cells are near each other- Ananstomosis happens, if they are then we mark the grid as 3,
#  to mark it differently, then we merge the tip cells to form vessels, then we include oxygen and nutrient field
    def check_anastomosis_and_merge(self):
        print("Starting anastomosis and merging check...")

        new_tip_cells = []
        skip_indices = set()

        for i, tip in enumerate(self.tip_cells):
            if not self.active_tips[i] or i in skip_indices:
                continue

            merged = False
            for j, other_tip in enumerate(self.tip_cells):
                #check condition if tip cells are near each other
                if i != j and self.active_tips[j] and self.is_near(tip, other_tip):
                    print(f"Merging tips at {tip} and {other_tip}")
                    merged_tip = self.merge_tips(tip, other_tip)
                    new_tip_cells.append(merged_tip)
                    self.merged_cells.append(merged_tip)  # Add to merged cells
                    print("merged_tip-->",merged_tip)
                    print("merged_cells-->",self.merged_cells)

                    # Update oxygen and nutrient fields
                    # Supply oxygen and nutrients at the merged vessel
                    self.oxygen_field[merged_tip] += 1.0  # Initial oxygen supply
                    self.nutrient_field[merged_tip] += 1.0  # Initial nutrient supply

                    self.grid[merged_tip] = 3  # Mark merged tip
                    skip_indices.add(i)
                    skip_indices.add(j)
                    merged = True
                    break

            if not merged:
                new_tip_cells.append(tip)

        # Update tip cells and active tips
        self.tip_cells = new_tip_cells
        self.active_tips = [True] * len(new_tip_cells)


#This is a helper function to check if the tip cells are near each other
    def is_near(self, tip1, tip2, distance=1):
        """Check if two tips are within a certain distance."""
        return abs(tip1[0] - tip2[0]) <= distance and abs(tip1[1] - tip2[1]) <= distance

#now we need a function to simulate oxygen and nutrient diffusion
    def diffuse(self):
        """Diffuse oxygen and nutrients in the grid."""
        # Diffusion parameters
        diffusion_rate = 0.1
        decay_rate = 0.01

        # Copy fields to avoid updating in-place
        new_oxygen_field = np.copy(self.oxygen_field)
        new_nutrient_field = np.copy(self.nutrient_field)

        for x in range(1, self.grid.shape[0] - 1):
            for y in range(1, self.grid.shape[1] - 1):
                # Compute diffusion for oxygen
                neighbors = [
                    self.oxygen_field[x+1, y], self.oxygen_field[x-1, y],
                    self.oxygen_field[x, y+1], self.oxygen_field[x, y-1]
                ]
                new_oxygen_field[x, y] = self.oxygen_field[x, y] + diffusion_rate * (
                    sum(neighbors) - 4 * self.oxygen_field[x, y]) - decay_rate * self.oxygen_field[x, y]

                # Compute diffusion for nutrients
                neighbors = [
                    self.nutrient_field[x+1, y], self.nutrient_field[x-1, y],
                    self.nutrient_field[x, y+1], self.nutrient_field[x, y-1]
                ]
                new_nutrient_field[x, y] = self.nutrient_field[x, y] + diffusion_rate * (
                    sum(neighbors) - 4 * self.nutrient_field[x, y]) - decay_rate * self.nutrient_field[x, y]

        # Update fields
        self.oxygen_field = new_oxygen_field
        print("oxygen_field-->",self.oxygen_field)
        self.nutrient_field = new_nutrient_field
        print("nutrient_field-->",self.nutrient_field)

        




    
    