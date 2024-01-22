from config import *
import math

class KnowlageBase:
    def __init__(self, friendly_flag, enemy_flag, enemy, friend):
        self.knowlage_base = [["/" for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.pathfinding_world = [[-1 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.friendly_flag = friendly_flag
        self.enemy_flag = enemy_flag
        self.enemy = enemy
        self.friend = friend
        self.enemy_flag_location = None
        self.friendly_flag_location = None
        self.attack_agent1 = True
        self.attack_agent2 = True
        self.defend_agent = True
        self.enemy_agents = 3
        self.dodge_distance = 6
        self.shoot_distance = 8
        self.regrup_spot = None
        self.reserve_regrup_spot = None
        self.regruped = False
        self.agent1_at_position = False
        self.agent2_at_position = False
        self.holding_flag = False
        self.flage_in_danger = False
        self.dangerous_location = []
        self.all_enemy_location = []
        self.defend_cooldown = 200
        self.agent0_action = None
        self.agent1_action = None
        self.agent2_action = None
        self.regrup_radius = 10

    def update_agent_action(self, agent, action):
        """
        Setter function for agent action

        Args:
            agent ( int ): index of the agent
            action ( string ): action that the agent should do (for exp. "move", "shoot")
        """
        match agent:
            case 0:
                self.agent0_action = action
            case 1:
                self.agent1_action = action
            case 2:
                self.agent2_action = action

    def get_agent_action(self, agent):
        """
        Getter function of agents action

        Args:
            agent ( Agent class ): agent instance

        Returns:
            action : the action that agent is currently doing
        """
        match agent:
            case 0:
                return self.agent0_action
            case 1:
                return self.agent1_action
            case 2:
                return self.agent2_action

    def agent_died(self, agent):
        """
        Functions that changes the important variables if agent is killed. If the defending agent dies, 
        changes the defending indicator and sets the indicator for flag in danger. If offensive agents die,
        updates the attack agent as dead.

        Args:
            agent ( int ): index of the agent
        """
        match agent:
            case 0:
                self.defend_agent = False
                self.flage_in_danger = True
            case 1:
                self.attack_agent1 = False
            case 2:
                self.attack_agent2 = False

    def at_positon(self, agent):
        """
        Functions that counts the agents at the target position and demands the regroup

        Args:
            agent ( int ): index of the agent
        """
        if agent == 1:
            self.agent1_at_position = True
        elif agent == 2:
            self.agent2_at_position = True

        if self.agent1_at_position and self.agent2_at_position :
            self.regruped = True
            self.agent1_at_position = False
            self.agent2_at_position = False

    def enable_flag_return(self):
        """
        If the flag is missing from the position, set it's original position as passable
        """
        self.pathfinding_world[self.friendly_flag_location[0]][self.friendly_flag_location[1]] = 0
        print("return enabled")

    def refresh_enemys(self):
        """
        Refreshes the positions of enemies that have moved since the last scan
        """
        enemys = []
        for row in range(len(self.knowlage_base)):
            for col in range(len(self.knowlage_base[row])):
                if self.knowlage_base[row][col] in [self.enemy, '.']:
                    self.knowlage_base[row][col] = ' '
                    if self.knowlage_base[row][col] == self.enemy:
                        enemys.append((row, col))

        # clear dangerous_locations
        for enemy in enemys:
            enemy_row = enemy[0]
            enemy_col = enemy[1]

            # Check the same row within 4 columns of the agent
            # dangerous rows
            for j in range(max(0, enemy_col - self.shoot_distance), min(len(self.knowlage_base[0]), enemy_col + (self.shoot_distance + 1))):
                self.dangerous_location.remove((enemy_row, j))
                self.pathfinding_world[enemy_row][j] = 0
                
            # dangerous cols
            for i in range(max(0, enemy_row - self.shoot_distance), min(len(self.knowlage_base), enemy_row + (self.shoot_distance + 1))):
                self.dangerous_location.remove((i, enemy_col))
                self.pathfinding_world[i][enemy_col] = 0

    def find_dangerous_location(self, agent_pos_row, agent_pos_col):
        """
        Scans the knowledge base for enemies and marks them as dangerous locations for agent
        to avoid and appends them in variable dangerous_locations and pathfinding_world

        Args:
            agent_pos_row ( int ): row index of agent's position
            agent_pos_col ( int ): column index of agent's position
        """
        enemys = []
        for i in range(max(0, agent_pos_row - 4), min(len(self.knowlage_base), agent_pos_row + 5)):
            for j in range(max(0, agent_pos_col - 4), min(len(self.knowlage_base[0]), agent_pos_col + 5)):
                if self.knowlage_base[i][j] == self.enemy[0]:
                    enemys.append((i, j))
        
        for enemy in enemys:
            enemy_row = enemy[0]
            enemy_col = enemy[1]

            # Check the same row within 4 columns of the agent
            # dangerous rows
            for j in range(max(0, enemy_col - self.shoot_distance), min(len(self.knowlage_base[0]), enemy_col + (self.shoot_distance + 1))):
                self.dangerous_location.append((enemy_row, j))
                self.pathfinding_world[enemy_row][j] = 2
                
            # dangerous cols
            for i in range(max(0, enemy_row - self.shoot_distance), min(len(self.knowlage_base), enemy_row + (self.shoot_distance + 1))):
                self.dangerous_location.append((i, enemy_col))
                self.pathfinding_world[i][enemy_col] = 2

    def update_general_knowlage_base(self, visible_range, agent_pos_row, agent_pos_col, current_vision):
        """
        Updates the knowledge base and sets the score of tiles for the pathfinding algorithm to find the
        best path. It updates the changing tiles such as "/" when they are discovered.

        Args:
            visible_range ( int ): number of tiles visible in each direction 
            agent_pos_row ( int ): row index of agent's position
            agent_pos_col ( int ): column index of agent's position
            current_vision ( list of lists / matrix ): the world as the agents sees it. 9x9 square around him
        """
        for row_offset in range(-visible_range, visible_range+1):
            for col_offset in range(-visible_range, visible_range+1):
                if 0 <= agent_pos_row + row_offset < HEIGHT\
                and 0 <= agent_pos_col + col_offset < WIDTH:
                    row, col = agent_pos_row + row_offset, agent_pos_col + col_offset
                    current_vision_row, current_vision_col = row_offset + 4, col_offset + 4
                    if current_vision[current_vision_row][current_vision_col] != "/":
                        self.knowlage_base[row][col] = current_vision[current_vision_row][current_vision_col]
                        if current_vision[current_vision_row][current_vision_col] == self.enemy[0]:
                            self.all_enemy_location.append((row, col))

                        #      -1 -> unknown (/)
                        #       0 -> empty space (" ")
                        #       1 -> obstacle (#)
                        #       2 -> enemy
                        if current_vision[current_vision_row][current_vision_col] in [" ", self.enemy[1], self.friend[0], self.friend[1], self.enemy_flag]:
                            self.pathfinding_world[row][col] = 0
                        elif current_vision[current_vision_row][current_vision_col] == "#":
                            self.pathfinding_world[row][col] = 1
                        elif current_vision[current_vision_row][current_vision_col] == self.friendly_flag:
                            if not self.holding_flag:
                                self.pathfinding_world[row][col] = 1
                            else:
                                self.pathfinding_world[row][col] = 0
                        elif current_vision[current_vision_row][current_vision_col] == self.enemy[0]:
                            self.pathfinding_world[row][col] = 2

                        if current_vision[current_vision_row][current_vision_col] == self.enemy_flag:
                            self.enemy_flag_location = (row, col)
                        if current_vision[current_vision_row][current_vision_col] == self.friendly_flag:
                            self.friendly_flag_location = (row, col)
                        if (HEIGHT/2 - 8) < row < (HEIGHT/2 + 8) and (WIDTH/2 - 8) < col < (WIDTH/2 + 8) and self.regrup_spot == None:
                           if self.pathfinding_world[row][col] == 0:
                                    self.reserve_regrup_spot = (row, col)

    def find_regrup_spot(self, flag):
        """
        Function that is searching for a position where offensive agents will regroup after reaching target

        Args:
            flag ( tupple of ints ) - position (x and y coords on map) where the flag is
        """
        self.regrup_spot = self.reserve_regrup_spot
        center_x = flag[0]
        center_y = flag[1]
        offset_y_start = 0
        offset_y_end = 0
        if self.friend[0] == "r":
            offset_y_start = center_y + int(self.regrup_radius/2)
            offset_y_end =  center_y +  self.regrup_radius + 1
        else:
            offset_y_end = center_y - int(self.regrup_radius/2)
            offset_y_start =  center_y - self.regrup_radius + 1

        for x in range(center_x - self.regrup_radius, center_x +  self.regrup_radius + 1):
            for y in range(offset_y_start, center_y + offset_y_end):
                distance = math.dist(flag, (x, y))
                if distance <= self.regrup_radius:
                     if 0 <= x < HEIGHT and 0 <= y < WIDTH:
                        if self.pathfinding_world[x][y] == 0:
                            self.regrup_spot = (x, y)
                            print(self.regrup_spot)
                            break

    def enemy_locations(self, agent_pos_row, agent_pos_col):
        """
        Scans the row or column for the discovered enemy for agent to dodge it.

        Args:
            agent_pos_row ( int ): row index of agent's position
            agent_pos_col ( int ): column index of agent's position

        Returns:
            indices ( list ): list of positions of discovered bullets
        """
        indices = []

        # Check the same row within 4 columns of the agent
        for j in range(max(0, agent_pos_col - self.shoot_distance), min(len(self.knowlage_base[0]), agent_pos_col + self.shoot_distance + 1)):
            if self.knowlage_base[agent_pos_row][j] in self.enemy:
                if not any(self.knowlage_base[agent_pos_row][k] == '#' for k in range(min(j, agent_pos_col), max(j, agent_pos_col) + 1)):
                    indices.append((agent_pos_row, j))

        # Check the same column within 4 rows of the agent
        for i in range(max(0, agent_pos_row - self.shoot_distance), min(len(self.knowlage_base), agent_pos_row + self.shoot_distance + 1)):
            if self.knowlage_base[i][agent_pos_col] in self.enemy:
                if not any(self.knowlage_base[k][agent_pos_col] == '#' for k in range(min(i, agent_pos_row), max(i, agent_pos_row) + 1)):
                    indices.append((i, agent_pos_col))

        return indices
    
    def bullet_locations(self, agent_pos_row, agent_pos_col):
        """
        Scans the row or column for the discovered bullet for agent to dodge it.

        Args:
            agent_pos_row ( int ): row index of agent's position
            agent_pos_col ( int ): column index of agent's position

        Returns:
            indices ( list ): list of positions of discovered bullets
        """
        indices = []

        # Check the same row within 4 columns of the agent
        for j in range(max(0, agent_pos_col - self.dodge_distance), min(len(self.knowlage_base[0]), agent_pos_col + self.dodge_distance + 1)):
            if self.knowlage_base[agent_pos_row][j] == '.':
                if not any(self.knowlage_base[agent_pos_row][k] == '#' for k in range(min(j, agent_pos_col), max(j, agent_pos_col) + 1)):
                    indices.append((agent_pos_row, j))

        # Check the same column within 4 rows of the agent
        for i in range(max(0, agent_pos_row - self.dodge_distance), min(len(self.knowlage_base), agent_pos_row + self.dodge_distance + 1)):
            if self.knowlage_base[i][agent_pos_col] == '.':
                if not any(self.knowlage_base[k][agent_pos_col] == '#' for k in range(min(i, agent_pos_row), max(i, agent_pos_row) + 1)):
                    indices.append((i, agent_pos_col))

        return indices
