from flask import Flask, render_template
import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
import random
import math

app = Flask(__name__)

# Initialize game state
grid_size = 8
grid = np.zeros((grid_size, grid_size))
shape_position = [0, 7]

def reset_game():
    global shape_position, food_position, poison_position, grid
    
    # Reset shape position
    shape_position = [0, 7]
    
    # Reset grid
    grid = np.zeros((grid_size, grid_size))
    
    # Place new food and poison
    food_position, poison_position = place_food_poison(grid_size)
    grid[food_position[0], food_position[1]] = 2  # Food is represented by 2
    grid[poison_position[0], poison_position[1]] = 3  # Poison is represented by 3
    
    return plot_grid()

# Place food and poison
def place_food_poison(grid_size):
    food_position = [random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)]
    poison_position = [random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)]
    
    while poison_position == food_position:
        poison_position = [random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)]
    
    return food_position, poison_position

food_position, poison_position = place_food_poison(grid_size)
grid[food_position[0], food_position[1]] = 2  # Food is represented by 2
grid[poison_position[0], poison_position[1]] = 3  # Poison is represented by 3

# Initial distances
dist_to_food = math.dist(shape_position, food_position)
dist_to_poison = math.dist(shape_position, poison_position)

def move(direction):
    global shape_position, grid, dist_to_food, dist_to_poison
    prev_shape_position = shape_position.copy()
    
    if direction == "up" and shape_position[0] > 0:
        shape_position[0] -= 1
    elif direction == "down" and shape_position[0] < grid_size - 1:
        shape_position[0] += 1
    elif direction == "left" and shape_position[1] > 0:
        shape_position[1] -= 1
    elif direction == "right" and shape_position[1] < grid_size - 1:
        shape_position[1] += 1
    
    new_dist_to_food = math.dist(shape_position, food_position)
    new_dist_to_poison = math.dist(shape_position, poison_position)
    
    towards_life = new_dist_to_food < dist_to_food
    towards_death = new_dist_to_poison < dist_to_poison
    
    dist_to_food = new_dist_to_food
    dist_to_poison = new_dist_to_poison

    result = ""
    if shape_position == food_position:
        result = "You win!!!"
    elif shape_position == poison_position:
        result = "You dead!!!"
    
    return plot_grid(), result, towards_life, towards_death

def plot_grid():
    fig, ax = plt.subplots()
    
    # Initialize grid with all white cells
    grid_copy = np.ones((grid_size, grid_size))  # All cells are white by default
    
    # Display the shape (S) at the current position
    grid_copy[shape_position[0], shape_position[1]] = 1  # Shape position
    
    # Plot the grid
    ax.imshow(grid_copy, cmap="Greys", vmin=0, vmax=1)
    
    # Display the shape (S), food (F), and poison (P) conditionally
    for i in range(grid_size):
        for j in range(grid_size):
            if [i, j] == shape_position:
                ax.text(j, i, 'S', ha="center", va="center", color="blue", fontsize=12)
            elif [i, j] == food_position:
                ax.text(j, i, 'F', ha="center", va="center", color="green", fontsize=12)
            elif [i, j] == poison_position:
                ax.text(j, i, 'P', ha="center", va="center", color="red", fontsize=12)
    
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.close(fig)
    return fig

def gradio_interface(direction, reset=False):
    if reset:
        return reset_game(), "Game reset", False, False
    
    fig, result, towards_life, towards_death = move(direction)
    return fig, result, towards_life, towards_death

# Create Gradio interface
gradio_app = gr.Interface(
    fn=gradio_interface, 
    inputs=[
        gr.Radio(["up", "down", "left", "right"], label="Move Direction"),
        gr.Checkbox(label="Reset Game")
    ], 
    outputs=[
        gr.Plot(label="Game Grid"),
        gr.Textbox(label="Result"),
        gr.Checkbox(label="Towards Life"),
        gr.Checkbox(label="Towards Death")
    ],
    live=True
)

@app.route("/")
def index():
    return gradio_app.launch(inbrowser=False, server_name="0.0.0.0", server_port=8080)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
