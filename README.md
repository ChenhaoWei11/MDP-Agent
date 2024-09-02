# MDPAgent.py


## Overview
This script contains an implementation of a Markov Decision Process (MDP) agent for the PacMan AI projects. The agent makes decisions based on a combination of rewards and penalties to guide PacMan through the environment. It uses custom weights to determine the best actions by considering the presence of ghosts, food, and capsules.

## Project Structure
- **`mdpAgents.py`**: Contains the implementation of the `MDPAgent` class, which makes decisions for PacMan based on a variety of factors.

## Features
- **MDPAgent Class**: Implements an agent that uses MDP to make decisions in the PacMan game environment.
  - `__init__()`: Initializes the agent with default settings including rewards and penalties.
  - `registerInitialState(state)`: Sets up the agent with the initial game state.
  - `final(state)`: Executes upon game completion.
  - `getAction(state)`: Chooses the best action for PacMan based on current state.
  - `calculateBestAction(state, legal_actions)`: Determines the best action based on weights for different positions.
  - **Weight Calculation Methods**:
    - `ghostWeights(state, positions, current_pacman_position, weights)`: Computes weights based on the presence and distance of ghosts.
    - `foodWeights(state, positions, current_pacman_position, weights)`: Adjusts weights based on the location of food.
    - `capsuleWeights(state, positions, current_pacman_position, weights)`: Computes weights based on the presence of capsules.
    - `setGhostWeights(ghost, walls, weights)`: Uses breadth-first search to calculate weights around ghosts.
    - `getDistance(pos1, pos2, state)`: Calculates the shortest distance between two points considering walls.

## How to Use
1. **Setup**: Ensure you have the PacMan AI environment set up as specified on [AI Berkeley's PacMan projects page](http://ai.berkeley.edu/).

2. **Integration**: Import the `MDPAgent` class into your PacMan AI code:
   ```python
   from mdpAgents import MDPAgent
