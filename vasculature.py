import random
import numpy as np  

class Vasculature:
    def __init__(self, grid, initial_tip_positions, vegf_field):
        self.grid = grid
        self.tip_cells = initial_tip_positions  # List of active tip positions
        self.active_tips = [True] * len(initial_tip_positions)  # Track which tips are active
        self.directions = {pos: None for pos in initial_tip_positions}  # Tip cell growth direction
        self.vegf_field = vegf_field  # VEGF concentration field
        self.vas_positions = []  # Store grown Vasculature
        
        for pos in initial_tip_positions:
            self.grid[pos] = 2  # Mark initial tips position on the grid

        
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
        new_tip_cells = [] #store new tip positions 
        
        for i, tip in enumerate(self.tip_cells):
            print("Tip cells before growth:", self.tip_cells)
            print("which old tip is running",i,tip)
            if not self.active_tips[i]:
                continue

            # Mark the current tip position as part of the vasculature
            #Assigning variables here:
            self.grid[tip] = 1 #matured vasculature
            #add them to vas_positions
            self.vas_positions.append(tip)
    
            self.vegf_field[tip] *= 0.5  # Consume VEGF at the current position

            prev_direction = self.directions.get(tip, None)
            empty_neighbors = self.get_empty_neighbors(tip, prev_direction)

            # Choose the growth direction based on VEGF concentration
            new_position = self.choose_growth_direction(empty_neighbors)
            

            #Check condition for growing 
            if new_position:
                self.grid[new_position] = 2  # Mark new tip position
                new_tip_cells.append(new_position) #I should be adding them to tip_cells??
                print("grown-vasculature--:", new_tip_cells)
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
        self.tip_cells = new_tip_cells
        self.active_tips = [True] * len(self.tip_cells)


    def check_anastomosis(self):
        
        print("Starting anastomosis check...")
        tips_to_remove = []  # List of tips to be removed after the loop
    
#looping through list tip_cells: stores current active tip cells position
        for i, tip in enumerate(self.tip_cells):
            print("in ananst func",i,tip)
#if the tip is not active we pass
            if not self.active_tips[i]:
                continue
            
            # Check if the tip is near another tip: Condition 1
            print("checking if one tip cell is near another tip")

            for other_tip in self.tip_cells:
                # Check if the tip is near another tip: Condition 1
                if tip != other_tip and self.is_near(tip, other_tip):
                    print(f"Anastomosis detected between tips at {tip} and {other_tip}")
                    # Hnadling merging : those tip cells are now part of vasculature marked as 1, we add tip and other_tip to matured vasculature array
                    #and remove their positions from the tip_cells array
                    self.grid[tip] = 1
                    self.grid[other_tip] = 1

                    #add them to the vasculature array
                    self.vas_positions.append(tip)
                    self.vas_positions.append(other_tip)
                    # remove them to the tip_cells array
                    tips_to_remove.append(tip)
                    tips_to_remove.append(other_tip)
            
            # Check if the tip is near pre-existing vasculature (Condition 2)
            if tip in self.tip_cells and self.grid[tip] == 1:
                print(f"Tip at {tip} has collided with existing vasculature")
                self.vas_positions.append(tip)
                tips_to_remove.append(tip)

        # Remove tips that have collided with other tips or vasculature
        self.tip_cells = [tip for tip in self.tip_cells if tip not in tips_to_remove]
        self.active_tips = [True] * len(self.tip_cells)

        print("Updated vasculature positions:", self.vas_positions)
        print("Remaining tip cells after anastomosis:", self.tip_cells)
                    
#This is a helper function to check if the tip cells are near each other
    def is_near(self, tip1, tip2, distance=2):
        """Check if two tips are within a certain distance."""
        return abs(tip1[0] - tip2[0]) < distance and abs(tip1[1] - tip2[1]) < distance

    