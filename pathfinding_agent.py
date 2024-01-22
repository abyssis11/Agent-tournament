import heapq
import math 

EMPTY_STEP_COST = 1
MUD_STEP_COST = 10 # 10
FEAR_OF_UNKNOWN = 6.66
UNKNOWN_STEP_COST = max(EMPTY_STEP_COST, MUD_STEP_COST) * FEAR_OF_UNKNOWN  # for unknown positions (not visible)
FEAR_OF_ENEMY = 10

# Function to find the shortest path from agent_pos to target_pos on the given grid,
#   and return direction in which the agent should move
def pathfinding_direction(agent_pos, target_pos, grid, enemy_pos = (None, None)):
    # args:
    #   agent_pos (tuple): agent coordinates
    #   target_pos (tuple): target coordinates
    #   enemy_pos (tuple): enemy coordinates
    #   grid (2D list): 2D grid describing the world
    #      -1 -> unknown (/)
    #       0 -> empty space (" ")
    #       1 -> obstacle (#)
    #       2 -> enemy
    # return: direction, shortest_path
    #   direction: direction in which the agent will move, such as 'RIGHT', 'LEFT', 'UP', or 'DOWN'
    #   shortest_path: a list of coordinates (tuples) for visualization of the path, such as [(1, 3), (2, 3), ...]
    
    shortest_path = astar(agent_pos, target_pos, enemy_pos, grid)
    direction = get_direction(agent_pos, shortest_path)
    return direction

# Determine the direction from the current position to the next position along the shortest path:
def get_direction(current_pos, shortest_path):
    '''
    Return None if shortest_path isn't a path (contains only one or zero positions).
    Compare the row and column values of the current and next positions.
    Return 'UP' if the next position is above, 'DOWN' if below, 'LEFT' if to the left, and 'RIGHT' if to the right.
    '''
    if len(shortest_path) < 2: return None
    next_pos = shortest_path[1]
    if next_pos[0] < current_pos[0]:
        return 'up'
    elif next_pos[0] > current_pos[0]:
        return 'down'
    elif next_pos[1] < current_pos[1]:
        return 'left'
    elif next_pos[1] > current_pos[1]:
        return 'right'


# A* algorithm for pathfinding:
def astar(agent_pos, target_pos, enemy_pos, grid):
    # Initialize start position and goal position
    start = agent_pos
    goal = target_pos

    # Create an open set as a priority queue and push the start position with priority 0
    open_set = []  # Priority queue to store nodes to be explored
    heapq.heappush(open_set, (0, start))  # Push start node with priority 0

    # Initialize dictionaries to track the parent of each position and the cost to reach each position
    came_from = {}  # Key: position, value: its parent (previous position on the path)
    g_cost = {start: 0}

    '''
    While the open set is not empty:
        Pop the position with the lowest priority from the open set (which is the current position).
            Hint: `heappop()`

        If the current position is the goal (found the shortest path):
            Reconstruct the path from the start to the goal using the parent information.
                Hint: `reconstruct_path()`
            Return the path.

        Generate neighboring positions of the current position.

        For each neighbor:
            If the neighbor is a valid position on the grid:
                Calculate the tentative cost to reach the neighbor.
                    Hint: tentative_g_cost = g_cost for the current position + 1

                If the neighbor is not in the g_cost dictionary or the tentative_g_cost is lower than its recorded g_cost:
                    Update the g_cost to reach the neighbor.
                    Calculate the combined (total) cost for the neighbor position (g_cost + heuristic cost).
                        Hint: `heuristic()`
                    Push the neighbor position and its total cost (as its priority) to the open set.
                    Update the parent of the neighbor.
                        Hint: `came_from`
    '''
    while open_set:
       current_cost, current = heapq.heappop(open_set)

       x, y = current

       if current == goal:
            return reconstruct_path(came_from, start, goal)
       
       neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

       for neighbor in neighbors:
           x, y = neighbor
           if is_valid(neighbor, grid):
               tentative_g_cost = g_cost[current]+1
               if grid[x][y] == 2:
                   tentative_g_cost += MUD_STEP_COST
               elif grid[x][y] == -1:
                   tentative_g_cost += UNKNOWN_STEP_COST

               if neighbor not in g_cost or tentative_g_cost < g_cost[neighbor]:
                    g_cost[neighbor] = tentative_g_cost
                    if enemy_pos == (None, None):
                        total_cost = tentative_g_cost + heuristic(neighbor, goal)
                    else:
                        total_fear_of_enemy = 0
                        for enemy in enemy_pos:
                            total_fear_of_enemy += fear_of_enemy(neighbor, enemy)
                        total_cost = tentative_g_cost + heuristic(neighbor, goal) + total_fear_of_enemy
                    heapq.heappush(open_set, (total_cost, neighbor))
                    came_from[neighbor] = current

    # If the goal is not reached, return an empty path
    return []  # Target not reachable

# Reconstruct the path from the target to the start using parent information:
def reconstruct_path(came_from, start, target):
    '''
    Create the path by traversing positions backwards from target until you reach the start position.
    Return the reversed path (to get the correct order).
    '''
    current = target
    path = []
    if target not in came_from:
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

# Check if a given position is within the grid boundaries and corresponds to an empty space:
def is_valid(pos, grid):
    '''
    Return true if the row and column are within grid boundaries and the grid value at that position is 0.
    '''
    x, y = pos
    return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != 1

# Estimate the cost from position 'a' to position 'b' using the euclidian distance:
def heuristic(a, b):
    return math.dist(a, b)


def fear_of_enemy(current, enemy):
    dist = heuristic(current, enemy)
    if dist > FEAR_OF_ENEMY:
        return 0
    multiplier = FEAR_OF_ENEMY / ((dist + 1))
    return  multiplier * FEAR_OF_ENEMY *1000
