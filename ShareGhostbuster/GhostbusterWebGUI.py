from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Game Variables
def reset_game_variables():
    global ghost_location, score, bust_attempts_left, probabilities
    ghost_location = (random.randint(0, grid_rows - 1), random.randint(0, grid_cols - 1))
    score = initial_score
    bust_attempts_left = bust_attempts
    probabilities = [[1 / (grid_rows * grid_cols) for _ in range(grid_cols)] for _ in range(grid_rows)] 

grid_rows = 8
grid_cols = 13
initial_score = 10
bust_attempts = 2
reset_game_variables()

show_probabilities = False


# Helper function to determine direction
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

# Helper function to update probabilities
def update_posterior_probabilities(x, y, color, direction):
    global probabilities

    print(f"Updating probabilities for ({x}, {y}) with color {color} and direction {direction}")

    for row in range(grid_rows):
        for col in range(grid_cols):
            dist = abs(row - x) + abs(col - y)
            direction_match = (direction == direction_sense(row, col))
            
            # Probability updates based on distance and direction
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

    print("Probabilities after update:", probabilities)

@app.route('/')
def index():
    return render_template('index.html', grid_rows=grid_rows, grid_cols=grid_cols, initial_score=score, bust_attempts=bust_attempts)

@app.route('/get_direction', methods=['POST'])
def get_direction():
    global score, probabilities

    # Extract the clicked coordinates from the request
    data = request.json
    x, y = data['x'], data['y']
    
    if score <= 0:
        return jsonify({'message': 'No score left! You lose!', 'game_over': True, 'success': False})

    # Reduce the score
    score -= 1

    # Calculate the direction and distance
    gx, gy = ghost_location
    direction = direction_sense(x, y)

    distance = abs(x - gx) + abs(y - gy)
    color = 'green'
    if distance == 0:
        color = 'red'
    elif distance <= 2:
        color = 'orange'
    elif distance <= 4:
        color = 'yellow'

    # Update probabilities dynamically
    update_posterior_probabilities(x, y, color, direction)

    # Debugging log to ensure the probabilities are updated
    print(f"Clicked on ({x}, {y}), Color: {color}, Direction: {direction}")
    print(f"Updated Probabilities: {probabilities}")

    return jsonify({'direction': direction, 'color': color, 'score': score})


@app.route('/attempt_bust', methods=['POST'])
def attempt_bust():
    global bust_attempts_left, ghost_location, score, probabilities

    data = request.json
    x, y = data['x'], data['y']

    if bust_attempts_left <= 0:
        return jsonify({'message': 'No bust attempts left!', 'game_over': True})

    bust_attempts_left -= 1

    if (x, y) == ghost_location:
        return jsonify({'message': 'You caught the ghost!', 'game_over': True, 'success': True})

    if bust_attempts_left == 0:
        return jsonify({'message': 'Out of bust attempts!', 'game_over': True, 'success': False})

    return jsonify({'message': 'Missed the ghost!', 'bust_attempts_left': bust_attempts_left, 'game_over': False})

@app.route('/get_probabilities', methods=['GET'])
def get_probabilities():
    print("Probabilities sent to frontend:", probabilities)
    return jsonify(probabilities)

@app.route('/toggle_probabilities', methods=['POST'])
def toggle_probabilities():
    global show_probabilities
    show_probabilities = not show_probabilities
    return jsonify({'show_probabilities': show_probabilities})

@app.route('/reset_game', methods=['POST'])
def reset_game():
    reset_game_variables()
    return jsonify({'score': score, 'bust_attempts_left': bust_attempts_left})


if __name__ == '__main__':
    app.run(debug=True)
