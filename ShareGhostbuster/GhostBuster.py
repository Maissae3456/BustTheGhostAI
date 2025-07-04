import tkinter as tk
import random
from tkinter import messagebox

# Initialize main application window
root = tk.Tk()
root.title("Bust the Ghost")

# Game Variables
grid_rows = 8
grid_cols = 13
initial_score = 10  # You can adjust this value
bust_attempts = 2

# Random ghost location (row, col)
ghost_location = (random.randint(0, grid_rows - 1), random.randint(0, grid_cols - 1))

# Track probabilities and scores
score = initial_score
probabilities = [[1 / (grid_rows * grid_cols) for _ in range(grid_cols)] for _ in range(grid_rows)]
show_probabilities = False
selected_location = None  # Track the last clicked cell for bust attempts

# Function to toggle the probability view
def toggle_view():
    global show_probabilities
    show_probabilities = not show_probabilities
    update_grid()

# Function to update grid colors based on ghost proximity
def update_grid():
    for row in range(grid_rows):
        for col in range(grid_cols):
            btn_text = f"{probabilities[row][col]:.2f}" if show_probabilities else ""
            buttons[row][col].config(text=btn_text)

# Function for distance-based color sensing
def distance_sense(x, y):
    dist = abs(x - ghost_location[0]) + abs(y - ghost_location[1])
    if dist == 0:
        return "red"
    elif dist <= 2:
        return "orange"
    elif dist <= 4:
        return "yellow"
    else:
        return "green"

# Function for direction sensing
def direction_sense(x, y):
    gx, gy = ghost_location
    if x < gx:
        return "south"
    elif x > gx:
        return "north"
    elif y < gy:
        return "east"
    else:
        return "west"

# Function to handle grid button click
def on_grid_click(x, y):
    global score, selected_location
    if score <= 0:
        return

    # Distance-based color feedback
    color = distance_sense(x, y)
    buttons[x][y].config(bg=color)
    
    # Direction feedback
    direction = direction_sense(x, y)
    messagebox.showinfo("Direction", f"The ghost is to the {direction}!")

    # Reduce score with each click
    score -= 1
    score_label.config(text=f"Score: {score}")
    
    # Update the selected location for bust attempts
    selected_location = (x, y)
    
    # Update probabilities here (using Bayesian inference with both sensors)
    update_posterior_probabilities(x, y, color, direction)

# Bayesian update for posterior probabilities
def update_posterior_probabilities(x, y, color, direction):
    global probabilities

    # Here, we implement Bayesian updating based on both distance (color) and direction.
    for row in range(grid_rows):
        for col in range(grid_cols):
            dist = abs(row - x) + abs(col - y)
            direction_match = (direction == direction_sense(row, col))
            
            # Simple example probability update based on color and direction
            if dist == 0 and color == "red":
                probabilities[row][col] *= 0.9 if direction_match else 0.1
            elif dist <= 2 and color == "orange":
                probabilities[row][col] *= 0.5 if direction_match else 0.2
            elif dist <= 4 and color == "yellow":
                probabilities[row][col] *= 0.3 if direction_match else 0.1
            else:
                probabilities[row][col] *= 0.1 if direction_match else 0.05
    
    # Normalize probabilities
    total_prob = sum(sum(row) for row in probabilities)
    probabilities = [[p / total_prob for p in row] for row in probabilities]
    update_grid()

# Function to handle "Bust" attempt
def bust_attempt():
    global bust_attempts, selected_location
    if selected_location is None:
        messagebox.showinfo("Error", "Select a cell before attempting to bust!")
        return

    if bust_attempts > 0:
        x, y = selected_location
        if (x, y) == ghost_location:
            messagebox.showinfo("Success", "You caught the ghost!")
            root.quit()  # End the game if the player wins
        else:
            bust_attempts -= 1
            bust_attempts_label.config(text=f"Bust Attempts: {bust_attempts}")
            if bust_attempts == 0:
                messagebox.showinfo("Game Over", "Out of bust attempts!")

# Creating grid buttons
buttons = []
for row in range(grid_rows):
    button_row = []
    for col in range(grid_cols):
        button = tk.Button(root, width=4, height=2, command=lambda r=row, c=col: on_grid_click(r, c))
        button.grid(row=row, column=col)
        button_row.append(button)
    buttons.append(button_row)

# Labels and Buttons
score_label = tk.Label(root, text=f"Score: {score}")
score_label.grid(row=grid_rows, column=0, columnspan=grid_cols//2, sticky="w")

bust_attempts_label = tk.Label(root, text=f"Bust Attempts: {bust_attempts}")
bust_attempts_label.grid(row=grid_rows, column=grid_cols//2, columnspan=grid_cols//2, sticky="e")

# The Toggle View button
view_button = tk.Checkbutton(root, text="View Probabilities", command=toggle_view)
view_button.grid(row=grid_rows+1, column=0, columnspan=grid_cols//2, sticky="w")

# Bust-The-Ghost Button
bust_button = tk.Button(root, text="Bust", command=bust_attempt)
bust_button.grid(row=grid_rows+1, column=grid_cols//2, columnspan=grid_cols//2, sticky="e")

# Run the main loop
root.mainloop()
