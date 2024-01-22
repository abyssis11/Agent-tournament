# Deni Kernjus i Dino Ladavac

""" 
Python file with the logic for agents in the Capture the flag game.
The agents are separated as follows:
- 2 agents are offensive
- 1 agent is defensive


Offensive logic:
    - Goal to find the enemy flag, capture it, and bring it to its own base
    - The agents separate at the beginning and try to visit up-and-down corners in hopes of finding the enemy flag quicker
    - If the flag is not found, they search for it in a random right-middle position
    - When the flag is discovered, they regroup and attack the enemy base
    - After the flag is captured, they return to their own base
    - If the defensive agent is killed, they decide if they become offensive or defensive according to the distance between their and the enemy flag
    - If the enemy flag is closer, they remain offensive; otherwise, they become defensive
    - After some time of defending their flag, one agent becomes offensive
    - They dodge the enemy if they can otherwise, they shoot at the enemy
    - Dodge bullets
Defensive logic:
    - Goal is to find our own flag and defend it
    - When the flag is discovered, walk around it and try to find enemy agents
    - If neraby enemy agents are discovered, shoot at them
    - If both offensive agents die, become offensive
    - Dodge bullets
Agents use a pathfinding algorithm to find the best path and a shared knowledge base to share important information.
Pathfinding:
    - uses the A* algorithm
    - calculates the heuristic (euclidean) distance between agent and target on unexplored tiles
    - uses cost and heuristis distance on explored tiles
    - Algorithm avoids walls, unexplored positions, and enemy agents if it can
Shared knowledge base and information:
    - Knowledge base is a mattrix (HEIGHT*WIDTH) of a map
    - If one agent discovers some tiles, all agents can see them
    - Agent's own position is shared
    - Agent's action is shared
    - Flags positions are shared
    - Enemy agent positions are shared
    - Regroup position is shared
    - Agent's condition is shared (alive / dead)
Agents shoot at enemies only if they can't avoid them (for example, if there are walls on each side).
If the agent returns to their own base with the enemy flag and their enemy flag is taken, they wait for the enemy agent to find them because there is a higher probability of shooting at them.
Agents are using action to declare if they are moving or shooting and direction to declare which side they are doing the action (up, down, left, right).
"""

import random
from config import *  # contains, amongst other variables, `ASCII_TILES` (which will probably be useful here)
from pathfinding_agent import pathfinding_direction
from knowlage_base import KnowlageBase
import math

FRIENDLY_FLAG = ASCII_TILES["blue_flag"]
ENEMY_FLAG = ASCII_TILES["red_flag"]
ENEMY = ['r', 'R']
FRIEND = ['b', 'B']
DEFEND_POSITION = -1
DOWN_CORNER = (HEIGHT-2, WIDTH-2)
UP_CORNER = (1, WIDTH-2)
FRAMES_PER_SEC = 1 / TICK_RATE
FRAME = 0

knowlage_base = KnowlageBase(FRIENDLY_FLAG, ENEMY_FLAG, ENEMY, FRIEND)

class Agent:
    
    # called when this agent is instanced (at the beginning of the game)
    def __init__(self, color, index):
        self.color = color  # "blue" or "red"
        self.index = index  # 0, 1, or 2
        self.visible_range = 4
        self.up_corner_visited = False
        self.down_corner_visited = False
        self.waypoint = None
        self.holding_flag = False
        self.random_position_counter = 0

    def shoot(self, agent_pos_row, agent_pos_col, enemys):
        """
        Functions that get the list of enemy positions, calculate the distance to them, and then shoot
        in the direction of the closest enemy.


        If the enemy's and agents vertical position is aligned, they shoot up or down, and if their
        horizontal position is aligned, then shoots left or right. If none of the positions align,
        The agent returns "None" as direction and action.

        Args:
            agent_pos_row (int): Row index of agent position in pathfinding world
            agent_pos_col (int): Column index of agent position in pathfinding world
            enemys (list of tuples): List of tuples (x,y) of nearby enemies positions.

        Returns:
            action (str): "shoot" as an indicator for agent to shoot
            direction (str): ("up", "down", "left", "right") depending on enemy position 
        """
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
        """
        Function that gets the list of nearby bullet positions and calculates which one is the closest,
        then moves away from it.
        
        If the bullet's vertical position alligns with the agent's vertical position then the agent moves
        left or right. If the bullet's horizontal position alligns with the agent's horizontal position, then
        the agent moves up and down. 

        Args:
            agent_pos_row (int): Row index of agent position in pathfinding world
            agent_pos_col (int): Column index of agent position in pathfinding world
            bullets (list of tuples): List of positions (x,y) of nearby enemies

        Returns:
            action (str) : "move" as an indicator for agent to move
            direction (str) : "up","down","left" or "right" for the direction to move away of the bullet
        """
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

    def defend_flag(self, agent_pos_row, agent_pos_col, flag, pathfinding_world, all_enemys):
        """
        Function that is used to position the agent in the defending position of its own flag.
        Calculates the path to own flag and gets the direction where to move according to the path

        Args:
            agent_pos_row (int): Row index of agent position in pathfinding world
            agent_pos_col (int): Column index of agent position in pathfinding world
            flag (tuple of ints):  The tuple of row and column indexes representing the position of flag
                                    in pathfinding world
            pathfinding_world (list of lists / matrix): Shared knowledge base matrix
            all_enemys (list of tuples):  List of tuples represented as positions of all enemies
                                            detected and stored in knowledge base

        Returns:
            action (str) : "move" as an indicator for agent to move
            direction (str) : "up","down","left" or "right" for the direction to move towards the flag
        """
        flag_row = flag[0]
        flag_col = flag[1]
        waypoints = [(flag_row-1, flag_col-1), (flag_row+1, flag_col-1), (flag_row+1, flag_col+1), (flag_row-1, flag_col+1)]
        
        if (agent_pos_row, agent_pos_col) == self.waypoint or self.waypoint == None:
            self.waypoint = random.choice(waypoints)

        direction = pathfinding_direction((agent_pos_row, agent_pos_col), self.waypoint, pathfinding_world, all_enemys)
        action = "move"
        return action, direction

    def search(self, agent_pos_row, agent_pos_col, pathfinding_world, all_enemys):
        """
        Function that searches the equivalent target for agent to reach. If the enemy flag is not yet discovered
        the targets are Top and Down corners of the other side of map. The function calculates the path to them and
        guides the agent. If the corners are reached, it marks them as visited and searches for a random position on the
        other side of map where the agents need to go. This increases their probability of discovering the enemy flag. 

        Args:
            agent_pos_row (int): Row index of agent position in pathfinding world
            agent_pos_col (int): Column index of agent position in pathfinding world
            pathfinding_world (list of lists / matrix): Shared knowledge base matrix
            all_enemys (list of tuples):  List of tuples represented as positions of all enemies
                                            detected and stored in knowledge base

        Returns:
            action (str) : "move" as an indicator for agent to move
            direction (str) : "up","down","left" or "right" for the direction to move towards the next step in generated path
        """
        action, direction = None, None
        if (agent_pos_row, agent_pos_col) == DOWN_CORNER:
            self.down_corner_visited = True
        if (agent_pos_row, agent_pos_col) == UP_CORNER:
            self.up_corner_visited = True

        if self.index == 1:
            if not self.down_corner_visited:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), DOWN_CORNER, pathfinding_world, all_enemys)
            elif self.waypoint != None:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), self.waypoint, pathfinding_world, all_enemys)
                if (agent_pos_row, agent_pos_col) == self.waypoint or direction == None:
                    self.waypoint = None
            elif self.random_position_counter < 10:
                while direction == None:
                    row, col = random_left_middle_position()
                    self.waypoint = (row, col)
                    action = "move"
                    direction = pathfinding_direction((agent_pos_row, agent_pos_col), self.waypoint, pathfinding_world, all_enemys)
                self.random_position_counter += 1
            else:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), UP_CORNER, pathfinding_world, all_enemys)
                self.random_position_counter = 0

        if self.index == 2:
            if not self.up_corner_visited:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), UP_CORNER, pathfinding_world, all_enemys)
            elif self.waypoint != None:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), self.waypoint, pathfinding_world, all_enemys)
                if (agent_pos_row, agent_pos_col) == self.waypoint or direction == None:
                    self.waypoint = None
            elif self.random_position_counter < 10:
                while direction == None:
                    row, col = random_left_middle_position()
                    self.waypoint = (row, col)
                    action = "move"
                    direction = pathfinding_direction((agent_pos_row, agent_pos_col), self.waypoint, pathfinding_world, all_enemys)
                self.random_position_counter += 1
            else:
                action = "move"
                direction = pathfinding_direction((agent_pos_row, agent_pos_col), DOWN_CORNER, pathfinding_world, all_enemys)
                self.random_position_counter = 0

        return action, direction

    def go_to_position(self, agent_pos_row, agent_pos_col, position, pathfinding_world, all_enemys):
        """
        Moves the agent to the next position according to the direction of the calculated path to the flag

        Args:
            agent_pos_row (int): Row index of agent position in pathfinding world
            agent_pos_col (int): Column index of agent position in pathfinding world
            flag (tuple of ints):  The tuple of row and column indexes representing the position of flag
                                    in pathfinding world
            pathfinding_world ( list of lists / matrix): Shared knowledge base matrix
            all_enemys (list of tuples):  List of tuples represented as positions of all enemies
                                            detected and stored in knowledge base

        Returns:
            action (str) : "move" as an indicator for agent to move
            direction (str) : "up","down","left" or "right" for the direction to move towards the path to flag
        """
        direction = pathfinding_direction((agent_pos_row, agent_pos_col), position, pathfinding_world, all_enemys)
        action = "move"
        return action, direction
    
    # called every "agent frame"
    def update(self, visible_world, position, can_shoot, holding_flag):
        """
        Function that is called every frame. It updates the variables and calls the functions for agents holding the
        flag, finding the path to corners and flags, shooting , dodging, defending and moving.

        Args:
            visible_world (list of lists, matrix ): the world as the agents sees it. 9x9 square around him
            position (tuple of ints ): position of the agent in pathfinding world
            can_shoot (bool): True if the delay for shooting has counted down, False otherwise
            holding_flag (bool): True if the agent is holding the enemy flag, False otherwise 

        Returns:
            action (str) : "move" or "shoot" as an indicator for agent on what to do
            direction (str) : "up","down","left" or "right" for the direction that the agent is going to face 
        """
        global FRAME
        FRAME += 1
        agent_pos_row = position[1]
        agent_pos_col = position[0]
        action = None
        direction = None

        if holding_flag:
            self.holding_flag = True
            knowlage_base.holding_flag = True
            knowlage_base.enable_flag_return()
            print("Holding flag")

        if FRAME % int(FRAMES_PER_SEC * 2) == 0:
            knowlage_base.refresh_enemys()

        knowlage_base.update_general_knowlage_base(self.visible_range, agent_pos_row, agent_pos_col, visible_world)
        knowlage_base.find_dangerous_location(agent_pos_row, agent_pos_col)
        
        # VARS - KNOWLAGE BASE
        pathfinding_world = knowlage_base.pathfinding_world
        friendly_flag = knowlage_base.friendly_flag_location
        enemy_flag = knowlage_base.enemy_flag_location
        regruped = knowlage_base.regruped
        close_bullets = knowlage_base.bullet_locations(agent_pos_row, agent_pos_col)
        close_enemys = knowlage_base.enemy_locations(agent_pos_row, agent_pos_col)
        all_enemys = knowlage_base.all_enemy_location
        defender_alive = knowlage_base.defend_agent
        attacker1_alive = knowlage_base.attack_agent1
        attacker2_alive = knowlage_base.attack_agent2
        defend_cooldown = knowlage_base.defend_cooldown

        if defend_cooldown <= 0:
            knowlage_base.flage_in_danger = False

        # CONDTIONS
        dodge_action = len(close_bullets) > 0
        shoot_action = len(close_enemys) > 0 and can_shoot
        defend_flag_action = friendly_flag != None
        regrup_action = enemy_flag != None and not holding_flag and not regruped and attacker1_alive and attacker2_alive
        push_for_flag_action = enemy_flag != None and not knowlage_base.holding_flag and (regruped or not attacker1_alive or not attacker2_alive)
        search_action = enemy_flag == None and (not self.up_corner_visited or not self.down_corner_visited) and not holding_flag
        defender_attack_action = not attacker1_alive and not attacker2_alive and enemy_flag != None
        return_flag_action = attacker1_alive and attacker2_alive and knowlage_base.holding_flag
        flage_in_danger_action = knowlage_base.flage_in_danger
        change_defender_action = not knowlage_base.flage_in_danger and defend_cooldown  <= 0 and attacker1_alive and attacker2_alive
        cover_action = knowlage_base.holding_flag and not self.holding_flag and not flage_in_danger_action and attacker1_alive and attacker2_alive
        wait_for_enemy_action = knowlage_base.holding_flag and not self.holding_flag and flage_in_danger_action

        # AGENT 0 - DEFENDER
        if self.index == 0:         
            '''
            print("\n===========================\n")
            for row in knowlage_base.knowlage_base:
                print(" " + " ".join(row))
            '''
            if defender_attack_action:
                knowlage_base.update_agent_action(self.index, "defender_attack_action")
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world, all_enemys)

            elif defend_flag_action:    
                knowlage_base.update_agent_action(self.index, "defend_flag_action")         
                action, direction = self.defend_flag(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world, all_enemys)

        # AGENT 1 - ATTACKER/SCOUT
        elif self.index == 1:
            if change_defender_action:
                knowlage_base.update_agent_action(self.index, "change_defender_action")
                self.index = 0
                knowlage_base.defend_agent = True
                knowlage_base.attack_agent1 = False

            elif search_action:
                knowlage_base.update_agent_action(self.index, "search_action")
                action, direction = self.search(agent_pos_row, agent_pos_col, pathfinding_world, all_enemys)

            elif regrup_action:
                knowlage_base.update_agent_action(self.index, "regrup_action")
                if knowlage_base.regrup_spot == None:
                    knowlage_base.find_regrup_spot(enemy_flag)
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, knowlage_base.regrup_spot, pathfinding_world, all_enemys)
                if (agent_pos_row, agent_pos_col) == knowlage_base.regrup_spot:
                    knowlage_base.at_positon(self.index)

            elif push_for_flag_action:
                knowlage_base.update_agent_action(self.index, "push_for_flag_action")
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world, all_enemys)
            
            elif wait_for_enemy_action:
                knowlage_base.update_agent_action(self.index, "wait_for_enemy_action")         
                action, direction = self.defend_flag(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world, all_enemys)

            elif cover_action:
                knowlage_base.update_agent_action(self.index, "cover_action")
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world, all_enemys)


        # AGENT 2 - ATTACKER/SCOUT
        elif self.index == 2:
            if search_action:
                knowlage_base.update_agent_action(self.index, "search_action")
                action, direction = self.search(agent_pos_row, agent_pos_col, pathfinding_world, all_enemys)

            elif regrup_action:
                knowlage_base.update_agent_action(self.index, "regrup_action")
                if knowlage_base.regrup_spot == None:
                    knowlage_base.find_regrup_spot(enemy_flag)
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, knowlage_base.regrup_spot, pathfinding_world, all_enemys)
                if (agent_pos_row, agent_pos_col) == knowlage_base.regrup_spot:
                    knowlage_base.at_positon(self.index)
                print(direction)

            elif push_for_flag_action:
                knowlage_base.update_agent_action(self.index, "push_for_flag_action")
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world, all_enemys)

            elif wait_for_enemy_action:
                knowlage_base.update_agent_action(self.index, "wait_for_enemy_action")         
                action, direction = self.defend_flag(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world, all_enemys)

            elif cover_action:
                knowlage_base.update_agent_action(self.index, "cover_action")
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world, all_enemys)

            
        # REFLEKSI - ALL AGENTS
        if dodge_action:
            knowlage_base.update_agent_action(self.index, "dodge_action")
            action, direction = self.dodge(agent_pos_row, agent_pos_col, close_bullets)

        elif shoot_action:
            knowlage_base.update_agent_action(self.index, "shoot_action")
            action, direction = self.shoot(agent_pos_row, agent_pos_col, close_enemys)

        elif holding_flag:
            knowlage_base.update_agent_action(self.index, "holding_flag")
            action, direction = self.go_to_position(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world, all_enemys)

        elif flage_in_danger_action:
            knowlage_base.update_agent_action(self.index, "flage_in_danger_action")
            knowlage_base.defend_cooldown -= 1
            if enemy_flag != None and math.dist((agent_pos_row, agent_pos_col), enemy_flag ) < math.dist((agent_pos_row, agent_pos_col), friendly_flag) and not holding_flag:
                action, direction = self.go_to_position(agent_pos_row, agent_pos_col, enemy_flag, pathfinding_world, all_enemys)
            else:
                action, direction = self.defend_flag(agent_pos_row, agent_pos_col, friendly_flag, pathfinding_world, all_enemys)

        if self.index == 2 or self.index == 1:
            print(f'Agent {self.index}: {knowlage_base.get_agent_action(self.index)}')

        return action, direction
    
    # called when this agent is deleted (either because this agent died, or because the game is over)
    # `reason` can be "died" or if the game is over "blue", "red", or "tied" depending on who won
    def terminate(self, reason):
        if reason == "died":
            knowlage_base.agent_died(self.index)
            if self.holding_flag:
                knowlage_base.holding_flag = False
            print(self.color, self.index, "died")

def random_left_middle_position():
    """
    Calculates a random position on the other side of map for where the agents need to go after they reach corners

    Returns:
        random_row (int): index for row in pathfinding world
        random_col (int): index for column in pathfinding world
    """
    # Defining the left middle part
    # Horizontal: Left half of the matrix
    col_start = WIDTH // 2
    col_end = WIDTH

    # Vertical: Middle third of the matrix
    row_start = HEIGHT // 3
    row_end = HEIGHT * 2 // 3

    # Generating a random position within the left middle part
    random_row = random.randint(row_start, row_end - 1)
    random_col = random.randint(col_start, col_end - 1)

    return random_row, random_col