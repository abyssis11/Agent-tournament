# First name Last name

""" 
Description of the agent (approach / strategy / implementation) in short points,
fictional example / ideas:
- It uses the knowledge base to remember:
     - the position where the enemy was last seen,
     - enemy flag positions,
     - the way to its flag.
- I use a machine learning model that, based on what the agent sees around it, decides:
     - in which direction the agent should take a step (or stay in place),
     - whether and in which direction to shoot.
- One agent always stays close to the flag while the other agents are on the attack.
- Agents communicate with each other:
     - position of seen enemies and in which direction they are moving,
     - the position of the enemy flag,
     - agent's own position,
     - agent's own condition (is it still alive, has it taken the enemy's flag, etc.)
- Agents prefer to maintain a distance from each other (not too close and not too far).
- etc...
"""

import random
from config import *  # contains, amongst other variables, `ASCII_TILES` (which will probably be useful here)
from pathfinding_agent import pathfinding_direction
from knowlage_base import KnowlageBase
import math

FRIENDLY_FLAG = ASCII_TILES["red_flag"]
ENEMY_FLAG = ASCII_TILES["blue_flag"]
ENEMY = ['b', 'B']
FRIEND = ['r', 'R']
DEFEND_POSITION = 1
DOWN_CORNER = (HEIGHT-2, 1)
UP_CORNER = (1, 1)

knowlage_base = KnowlageBase(FRIENDLY_FLAG, ENEMY_FLAG, ENEMY, FRIEND)

class Agent:
    
    # called when this agent is instanced (at the beginning of the game)
    def __init__(self, color, index):
        self.color = color  # "blue" or "red"
        self.index = index  # 0, 1, or 2
        self.visible_range = 4
        self.up_corner_visited = False
        self.down_corner_visited = False

    def shoot(self, agent_pos_row, agent_pos_col, enemys):
        action = None
        direction = None
        closest_enemy = float('inf')
        for enemy in enemys:
            enemy_row = enemy[0]
            enemy_col = enemy[1]
            distance = math.dist((enemy_row, enemy_col), (agent_pos_row, agent_pos_col)) < closest_enemy
            if enemy_col - agent_pos_col == 0 and distance < closest_enemy:
                closest_enemy = distance
                if agent_pos_row < enemy_row:
                    action = "shoot"
                    direction = "down"
                else:
                    action = "shoot"
                    direction = "up"

            elif enemy_row - agent_pos_row == 0 and distance < closest_enemy:
                closest_enemy = distance
                if agent_pos_col < enemy_col:
                    action = "shoot"
                    direction = "right"
                else:
                    action = "shoot"
                    direction = "left"

        return action, direction

    def dodge(self, agent_pos_row, agent_pos_col, bullets):
        action = None
        direction = None
        closest_bullet = float('inf')
        for bullet in bullets:
            bullet_row = bullet[0]
            bullet_col = bullet[1]
            distance = math.dist((bullet_row, bullet_col), (agent_pos_row, agent_pos_col)) < closest_bullet
            if bullet_col - agent_pos_col == 0 and distance < closest_bullet:
                closest_bullet = distance
                action = "move"
                # find closest safe spot
                if knowlage_base.knowlage_base[bullet_row][bullet_col+1] != "#":
                    direction = "right"
                elif knowlage_base.knowlage_base[bullet_row][bullet_col-1] != "#":
                    direction = "left"

            elif bullet_row - agent_pos_row == 0 and distance < closest_bullet:
                closest_bullet = distance
                action = "move"
                if knowlage_base.knowlage_base[bullet_row+1][bullet_col] != "#":
                    direction = "down"
                elif knowlage_base.knowlage_base[bullet_row-1][bullet_col] != "#":
                    direction = "up"

        return action, direction

    def defend_flag(self, agent_pos_row, agent_pos_col, flag, pathfinding_world):
        direction = pathfinding_direction((agent_pos_row, agent_pos_col), (flag[0], flag[1]+DEFEND_POSITION), pathfinding_world)
        action = "move"
        return action, direction

    def search(self, agent_pos_row, agent_pos_col, pathfinding_world):
        action, direction = None, None
        if (agent_pos_row, agent_pos_col) == DOWN_CORNER:
            self.down_corner_visited = True
        if (agent_pos_row, agent_pos_col) == UP_CORNER:
            self.up_corner_visited = True
        if self.index == 1:
            if not self.down_corner_visited:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), DOWN_CORNER, pathfinding_world)
            else:
                while direction == None:
                    row, col = random_left_middle_position()
                    action = "move"
                    direction = pathfinding_direction((agent_pos_row, agent_pos_col), (row, col), pathfinding_world)
        if self.index == 2:
            if not self.up_corner_visited:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), UP_CORNER, pathfinding_world)
            else:
                while direction == None:
                    row, col = random_left_middle_position()
                    action = "move"
                    direction = pathfinding_direction((agent_pos_row, agent_pos_col), (row, col), pathfinding_world)

        return action, direction
        
    def push_for_flag(self, agent_pos_row, agent_pos_col, flag, pathfinding_world):
        action = "move"
        direction = pathfinding_direction((agent_pos_row, agent_pos_col), flag, pathfinding_world)
        return action, direction

    def return_flag(self, agent_pos_row, agent_pos_col, flag, pathfinding_world):
        direction = pathfinding_direction((agent_pos_row, agent_pos_col), (flag[0], flag[1]), pathfinding_world)
        action = "move"
        return action, direction

    def attack(self):
        pass
    def split_up(self):
        pass

    def regrup(self, agent_pos_row, agent_pos_col, flag, pathfinding_world):
        direction = pathfinding_direction((agent_pos_row, agent_pos_col), (flag[0], flag[1]+DEFEND_POSITION), pathfinding_world)
        action = "move"
        return action, direction
    def cover(self):
        pass

    
    # called every "agent frame"
    def update(self, visible_world, position, can_shoot, holding_flag):
        agent_pos_row = position[1]
        agent_pos_col = position[0]
        if holding_flag:
            knowlage_base.holding_flag = True
            knowlage_base.enable_flag_return()
            print("Holding flag")
        knowlage_base.update_general_knowlage_base(self.visible_range, agent_pos_row, agent_pos_col, visible_world)
        pathfinding_world = knowlage_base.pathfinding_world
        friendly_flag = knowlage_base.friendly_flag_location
        enemy_flag = knowlage_base.enemy_flag_location
        regrup_spot = knowlage_base.regrup_spot
        bullets = knowlage_base.bullet_locations(agent_pos_row, agent_pos_col)
        enemys = knowlage_base.enemy_locations(agent_pos_row, agent_pos_col)

        # UVJETI
        dodge_action = len(bullets) > 0
        shoot_action = len(enemys) > 0
        defend_flag_action = friendly_flag != None
        push_for_flag = enemy_flag != None and not holding_flag
        search_action = enemy_flag == None and (not self.up_corner_visited or not self.down_corner_visited) and not holding_flag
        regrup_action = regrup_spot != None and self.up_corner_visited and self.down_corner_visited


        action = None
        direction = None
        # AGENT 0 - DEFENDER
        if self.index == 0:
            
            print("\n===========================\n")
            for row in knowlage_base.knowlage_base:
                print(" " + " ".join(row))

            if dodge_action:
                action, direction = self.dodge(agent_pos_row, agent_pos_col, bullets)

            elif shoot_action:
                action, direction = self.shoot(agent_pos_row, agent_pos_col, enemys)

            elif defend_flag_action:               
                action, direction = self.defend_flag(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world)

        # AGENT 1
        elif self.index == 1:
            if dodge_action:
                print(f'Agent {self.index}: dodge action')
                action, direction = self.dodge(agent_pos_row, agent_pos_col, bullets)

            elif shoot_action:
                print(f'Agent {self.index}: shoot_action')
                action, direction = self.shoot(agent_pos_row, agent_pos_col, enemys)

            elif search_action:
                print(f'Agent {self.index}: visit_up_corner_action')
                action, direction = self.search(agent_pos_row, agent_pos_col, pathfinding_world)

            elif push_for_flag:
                print(f'Agent {self.index}: push_for_flag')
                action, direction = self.push_for_flag(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world)
            
            elif holding_flag:
                print(f'Agent {self.index}: returning_flag')
                action, direction = self.return_flag(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world)

        # AGENT 2
        elif self.index == 2:
            if dodge_action:
                print(f'Agent {self.index}: dodge_action')
                action, direction = self.dodge(agent_pos_row, agent_pos_col, bullets)

            elif shoot_action:
                print(f'Agent {self.index}: shoot_action')
                action, direction = self.shoot(agent_pos_row, agent_pos_col, enemys)

            elif search_action:
                print(f'Agent {self.index}: visit_down_corner_action')
                action, direction = self.search(agent_pos_row, agent_pos_col, pathfinding_world)

            elif push_for_flag:
                print(f'Agent {self.index}: push_for_flag')
                action, direction = self.push_for_flag(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world)

            elif holding_flag:
                print(f'Agent {self.index}: returning_flag')
                action, direction = self.return_flag(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world)
            
        return action, direction
    
    # called when this agent is deleted (either because this agent died, or because the game is over)
    # `reason` can be "died" or if the game is over "blue", "red", or "tied" depending on who won
    def terminate(self, reason):
        if reason == "died":
            print(self.color, self.index, "died")

def random_left_middle_position():
    # Defining the left middle part
    # Horizontal: Left half of the matrix
    col_start = 0
    col_end = WIDTH // 2

    # Vertical: Middle third of the matrix
    row_start = HEIGHT // 3
    row_end = HEIGHT * 2 // 3

    # Generating a random position within the left middle part
    random_row = random.randint(row_start, row_end - 1)
    random_col = random.randint(col_start, col_end - 1)

    return random_row, random_col