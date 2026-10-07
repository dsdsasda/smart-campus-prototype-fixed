"""
Improved A* Path Planning Algorithm
Optimizes path selection with weight factors for campus scenarios
"""
import heapq
import numpy as np


class ImprovedAStarPlanner:
    def __init__(self, campus_map):
        self.map = campus_map  # 2D grid map: 0=passable, 1=obstacle, 2=crowded area
        self.rows = len(campus_map)
        self.cols = len(campus_map[0])
        # Movement directions (8 directions: up, down, left, right, and diagonals)
        self.directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    
    def heuristic(self, a, b):
        """Euclidean distance heuristic function"""
        return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    
    def get_cost(self, current, next_node):
        """Calculate movement cost (add weights for crowded areas)"""
        base_cost = np.sqrt((current[0]-next_node[0])**2 + (current[1]-next_node[1])**2)
        # Add penalty for crowded areas (cost × 2)
        if self.map[next_node[0]][next_node[1]] == 2:
            return base_cost * 2
        return base_cost
    
    def can_move_directly(self, start, goal):
        """Check if we can move directly from start to goal without hitting obstacles"""
        # Use Bresenham's line algorithm to check if direct path is clear
        x0, y0 = start
        x1, y1 = goal
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            # Check if current point is obstacle
            if 0 <= x < self.rows and 0 <= y < self.cols:
                if self.map[x][y] == 1:  # Obstacle found
                    return False
            else:
                return False
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True
    
    def simplify_path(self, path):
        """Remove unnecessary waypoints to create a shorter, smoother path"""
        if len(path) <= 2:
            return path
        
        simplified = [path[0]]  # Always keep start
        
        i = 0
        while i < len(path) - 1:
            # Try to skip as many points as possible
            j = len(path) - 1
            while j > i + 1:
                if self.can_move_directly(path[i], path[j]):
                    # Can skip all points between i and j
                    simplified.append(path[j])
                    i = j
                    break
                j -= 1
            else:
                # Can't skip, add next point
                simplified.append(path[i + 1])
                i += 1
        
        return simplified
    
    def plan(self, start, goal):
        """Path planning: start and goal are (x,y) coordinates"""
        # First check if direct path is possible (shortest path)
        if self.can_move_directly(start, goal):
            return [start, goal]  # Return direct path
        
        # Priority queue: (total cost, current position, path)
        open_set = []
        heapq.heappush(open_set, (0, start, [start]))
        # Visited set: record the minimum cost to reach each position
        visited = {start: 0}
        
        while open_set:
            current_cost, current_pos, path = heapq.heappop(open_set)
            
            # Reach goal, simplify and return path
            if current_pos == goal:
                # Simplify path to remove unnecessary waypoints
                simplified = self.simplify_path(path)
                return simplified
            
            # Explore all directions
            for dx, dy in self.directions:
                next_x = current_pos[0] + dx
                next_y = current_pos[1] + dy
                next_pos = (next_x, next_y)
                
                # Check if next position is within map bounds and passable
                if 0 <= next_x < self.rows and 0 <= next_y < self.cols:
                    if self.map[next_x][next_y] == 1:  # Obstacle, skip
                        continue
                    
                    # Calculate new cost
                    new_cost = current_cost + self.get_cost(current_pos, next_pos)
                    # Update if next position not visited or new cost is lower
                    if next_pos not in visited or new_cost < visited[next_pos]:
                        visited[next_pos] = new_cost
                        total_cost = new_cost + self.heuristic(next_pos, goal)
                        heapq.heappush(open_set, (total_cost, next_pos, path + [next_pos]))
        
        return None  # No path found
    
    def grid_to_coordinates(self, grid_x, grid_y, origin_lat=34.0520, origin_lon=-118.2430, grid_size=0.0001):
        """Convert grid coordinates to latitude/longitude"""
        # Ensure grid coordinates are within bounds
        grid_x = max(0, min(self.rows - 1, grid_x))
        grid_y = max(0, min(self.cols - 1, grid_y))
        lat = origin_lat + grid_x * grid_size
        lon = origin_lon + grid_y * grid_size
        return (lat, lon)
    
    def coordinates_to_grid(self, lat, lon, origin_lat=34.0520, origin_lon=-118.2430, grid_size=0.0001):
        """Convert latitude/longitude to grid coordinates"""
        grid_x = int((lat - origin_lat) / grid_size)
        grid_y = int((lon - origin_lon) / grid_size)
        # Clamp to map bounds to prevent out-of-bounds errors
        grid_x = max(0, min(self.rows - 1, grid_x))
        grid_y = max(0, min(self.cols - 1, grid_y))
        return (grid_x, grid_y)
    
    def is_valid_coordinate(self, lat, lon, origin_lat=34.0520, origin_lon=-118.2430, max_distance=0.01):
        """Check if coordinates are within reasonable campus distance (approximately 1km)"""
        lat_diff = abs(lat - origin_lat)
        lon_diff = abs(lon - origin_lon)
        return lat_diff <= max_distance and lon_diff <= max_distance

