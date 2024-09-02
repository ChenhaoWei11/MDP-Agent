# coding: utf-8
# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util


class MDPAgent(Agent):


    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        self.values = util.Counter()
        self.ghost_penalty = -100
        self.ghost_penalty_nearby = 10
        self.forbidden_zones = -90
        self.food_rewards = 1
        self.capsule_rewards = 3
        self.ghost_stealth = 5
        self.width = 0
        self.height = 0
        self.ghost_range = 0

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.width = state.data.layout.width
        self.height = state.data.layout.height
        self.ghost_range = 5

    def final(self, state):
        print "Looks like the game just ended!"

    def getAction(self, state):
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        best_action = self.calculateBestAction(state, legal)

        return api.makeMove(best_action, legal)

    # Calculates the best actions for Pacman    
    # Assign weight to positions，choose positon with the biggest weight
    # and return corresponding best action. 
    def calculateBestAction(self, state, legal_actions):
        current_pacman_position = api.whereAmI(state)
        action_d = {}
        for a in legal_actions:
            action_d[game.Actions.getSuccessor(current_pacman_position, a)] = a
        positions = [game.Actions.getSuccessor(current_pacman_position, action) for action in legal_actions]

        weights = {}
        self.ghostWeights(state, positions, current_pacman_position, weights)
        self.foodWeights(state, positions, current_pacman_position, weights)
        self.capsuleWeights(state, positions, current_pacman_position, weights)
        best_position = max(positions, key=lambda position: weights.get(position, 0))

        return action_d[best_position]


    # Calculate weights based on the presence of ghosts
    # The closer with the ghost, the larger the weight
    def ghostWeights(self, state, positions, current_pacman_position, weights):
        ghosts = api.ghostStatesWithTimes(state)
        # Stealth ghosts(time value >5)
        stealth_ghosts = [ghost for ghost in ghosts if ghost[1] > 5]
        for ghost in stealth_ghosts:
            ghost_position = ghost[0]
            if self.getDistance(current_pacman_position, ghost_position, state) > 8:
                continue
            closest_position = min(positions, key=lambda position: self.getDistance(position, ghost_position, state))
            weights[closest_position] = weights.get(closest_position, 0) + self.ghost_stealth

        # Visible ghosts(time value <= 5)
        visible_ghosts = [ghost for ghost in ghosts if ghost[1] <= 5]
        walls = api.walls(state)
        for ghost in visible_ghosts:
            self.setGhostWeights(ghost[0], walls, weights)


    # Calculate weights based on the presence of food.
    # Adjusts weights for optimal food gathering in specific scenarios.
    def foodWeights(self, state, positions, current_pacman_position, weights):
        foods = api.food(state)
        # In smallGrid, if only 2 food left, take the one on bottom right first
        if self.width <= 7 and len(foods) == 2:
            min_position = min(positions, key=lambda position: self.getDistance(position, (1, 1), state))
            weights[min_position] = weights.get(min_position, 0) + self.food_rewards

        else:
            closest_food = min(foods, key=lambda food: self.getDistance(current_pacman_position, food, state))
            # Calculate the location closest to closest_food
            distance = self.getDistance(current_pacman_position, closest_food, state)
            closest_position = min(positions, key=lambda position: self.getDistance(position, closest_food, state))
            weights[closest_position] = weights.get(closest_position, 0) + (self.food_rewards * 50 if (len(foods) == 1 and distance <= 2) else self.food_rewards)



    # Calculate weights based on the presence of capsules.
    # Don't eat capsules under the following conditions: 
    def capsuleWeights(self, state, positions, current_pacman_position, weights):
        capsules = api.capsules(state)
        if len(capsules) == 0:
            return
        # If stealth ghosts exist
        ghosts = api.ghostStates(state)
        for ghost in ghosts:
            if ghost[1] > 0:
                return
        # If distance between ghosts and current_pacman_position > 10
        for ghost in ghosts:
            if util.manhattanDistance(current_pacman_position, ghost[0]) < 5:
                return

        closest_capsule = min(capsules, key=lambda capsule: self.getDistance(current_pacman_position, capsule, state))
        closest_position = min(positions, key=lambda position: self.getDistance(position, closest_capsule, state))
        weights[closest_position] = weights.get(closest_position, 0) + self.capsule_rewards


    # Use breadth-first search to calculate weights based on the presence of ghosts in range 4
    # The closer with the ghost, the larger the weight
    # Weight of the location of ghost is -100(ghost_penalty), and weight of n away from ghost is ghost_penalty(-100) + n * ghost_penalty_nearby(10)
    def setGhostWeights(self, ghost, walls, weights):
        ghost = (int(ghost[0]), int(ghost[1]))
        x, y = ghost
        queue = util.Queue()
        visited = set()
        queue.push((x, y, 1))
        weights[(x, y)] = self.ghost_penalty
        visited.add((x, y))
        while not queue.isEmpty():
            x, y, distance = queue.pop()
            if distance == 6:
                break
            for dx, dy in [(0, 1), (1, 0), (0, -1),  (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                if (
                        0 <= next_x < self.width
                        and 0 <= next_y < self.height
                        and (next_x, next_y) not in walls
                        and (next_x, next_y) not in visited
                ):
                    queue.push((next_x, next_y, distance + 1))
                    visited.add((next_x, next_y))
                    weights[(next_x, next_y)] = (self.ghost_penalty + distance * self.ghost_penalty_nearby)


    # Use breadth-first search to get the shortest distance between two points, considering walls.
    def getDistance(self, pos1, pos2, state):
        walls = api.walls(state)
        pos1 = (int(pos1[0]), int(pos1[1]))
        pos2 = (int(pos2[0]), int(pos2[1]))
        x1, y1 = pos1
        x2, y2 = pos2

        if x1 == x2 and y1 == y2:
            return 0

        queue = util.Queue()
        visited = set()
        queue.push((x1, y1, 0))
        visited.add((x1, y1))

        while not queue.isEmpty():
            x, y, distance = queue.pop()
            if x == x2 and y == y2:
                return distance
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                if (
                        0 <= next_x < self.width
                        and 0 <= next_y < self.height
                        and (next_x, next_y) not in walls
                        and (next_x, next_y) not in visited
                ):
                    queue.push((next_x, next_y, distance + 1))
                    visited.add((next_x, next_y))

        return float("inf")

