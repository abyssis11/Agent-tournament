from config import *

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
        self.friedly_agents = 3
        self.dodge_distance = 5
        self.shoot_distance = 8
        self.regrup_spot = None
        self.holding_flag = False

    def enable_flag_return(self):
        self.pathfinding_world[self.friendly_flag_location[0]][self.friendly_flag_location[1]] = 0
        print("return enabled")


    def update_general_knowlage_base(self, visible_range, agent_pos_row, agent_pos_col, current_vision):
        for row_offset in range(-visible_range, visible_range+1):
            for col_offset in range(-visible_range, visible_range+1):
                if 0 <= agent_pos_row + row_offset < HEIGHT\
                and 0 <= agent_pos_col + col_offset < WIDTH:
                    row, col = agent_pos_row + row_offset, agent_pos_col + col_offset
                    current_vision_row, current_vision_col = row_offset + 4, col_offset + 4
                    if current_vision[current_vision_row][current_vision_col] != "/":
                        self.knowlage_base[row][col] = current_vision[current_vision_row][current_vision_col]
                        #      -1 -> unknown (/)
                        #       0 -> empty space (" ")
                        #       1 -> obstacle (#)
                        #       2 -> mud (enemy)
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
                                    self.regrup_spot = (row, col)
                        

    def enemy_locations(self, agent_pos_row, agent_pos_col):
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
