import collections
import numpy as np
import heapq
import time

class PriorityQueue:
    """
    A priority queue implementation using heapq to manage entries by priority.
    """
    def  __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

class SokobanSolver:
    """
    A class to solve Sokoban puzzles using various search strategies.
    """
    def __init__(self, level_path):
        with open(level_path, "r") as f:
            map = f.readlines()
        self.gameState = self.transferToGameState(map)
        self.posWalls = self.PosOfWalls()
        self.posTargets = self.PosOfTargets()

    def transferToGameState(self, map):
        """
        Parses the level map into a game state array.
        """
        map = [x.replace('\n','') for x in map]
        map = [','.join(map[i]) for i in range(len(map))]
        map = [x.split(',') for x in map]
        maxColsNum = max([len(x) for x in map])
        for irow in range(len(map)):
            for icol in range(len(map[irow])):
                if map[irow][icol] == ' ': map[irow][icol] = 0   # Space
                elif map[irow][icol] == '#': map[irow][icol] = 1 # Wall
                elif map[irow][icol] == '@': map[irow][icol] = 2 # Man
                elif map[irow][icol] == '$': map[irow][icol] = 3 # Box
                elif map[irow][icol] == '.': map[irow][icol] = 4 # Target
                elif map[irow][icol] == '*': map[irow][icol] = 5 # Box on target
            colsNum = len(map[irow])
            if colsNum < maxColsNum:
                map[irow].extend([1 for _ in range(maxColsNum-colsNum)]) 
        return np.array(map)
    
    def PosOfMan(self):
        """
        Return the position of agent
        """
        return tuple(np.argwhere(self.gameState == 2)[0]) # e.g. (2, 2)

    def PosOfBoxes(self):
        """
        Return the positions of boxes
        """
        return tuple(tuple(x) for x in np.argwhere((self.gameState == 3) | (self.gameState == 5))) 

    def PosOfWalls(self):
        """
        Return the positions of walls
        """
        return tuple(tuple(x) for x in np.argwhere(self.gameState == 1)) # e.g. like those above

    def PosOfTargets(self):
        """
        Return the positions of targets
        """
        return tuple(tuple(x) for x in np.argwhere((self.gameState == 4) | (self.gameState == 5)))
    
    def isEndState(self, posBox):
        """
        Check if all boxes are on the targets, indicating the puzzle is solved.

        Args:
            posBox (tuple of tuples): Current positions of all boxes.

        Returns:
            bool: True if all boxes are on target positions, False otherwise.
        """
        return sorted(posBox) == sorted(self.posTargets)
    
    def isLegalMove(self, move, posMan, posBox):
        """
        Check if the given move is legal based on the man's and boxes' positions.

        Args:
            move (tuple): The move to check.
            posMan (tuple): Current position of the man.
            posBox (tuple of tuples): Current positions of all boxes.

        Returns:
            bool: True if the move does not result in collisions with walls or boxes.
        """
        x_man, y_man = posMan
        dx, dy = move[0], move[1]
        new_x, new_y = x_man + dx, y_man + dy

        # Checking for push move
        if move[-1].isupper():
            new_x += dx
            new_y += dy

        return (new_x, new_y) not in posBox and self.gameState[new_x, new_y] != 1

    def legalMoves(self, posMan, posBox):
        """
        Return all legal moves for the man given the current game state.

        Args:
            posMan (tuple): Current position of the man.
            posBox (tuple of tuples): Current positions of all boxes.

        Returns:
            tuple of tuples: A tuple containing all the legal moves.
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        move_labels = ['u', 'd', 'l', 'r']
        legal_moves = []

        for (dx, dy), label in zip(directions, move_labels):
            new_x, new_y = posMan[0] + dx, posMan[1] + dy
            move = (dx, dy, label.upper() if (new_x, new_y) in posBox else label)

            if self.isLegalMove(move, posMan, posBox):
                legal_moves.append(move)

        return tuple(legal_moves)
    
    def updateState(self, posMan, posBox, move):
        """
        Update the game state after an move is taken.

        Args:
            posMan (tuple): Current position of the man.
            posBox (tuple of tuples): Current positions of all boxes.
            move (tuple): Move taken by the man.

        Returns:
            tuple: A tuple containing the new position of the man and boxes.
        """
        dx, dy = move[0], move[1]
        new_pos_man = (posMan[0] + dx, posMan[1] + dy)
        pos_box = list(posBox)

        if move[-1].isupper():  # Move involves pushing a box
            box_index = pos_box.index(new_pos_man)
            pos_box[box_index] = (pos_box[box_index][0] + dx, pos_box[box_index][1] + dy)

        return new_pos_man, tuple(pos_box)

    def isFailed(self, posBox):
        """
        Check if the game state is potentially failed (deadlock situation).

        Args:
            poBox (tuple of tuples): Current positions of all boxes.

        Returns:
            bool: True if any box is in an irrecoverable position.
        """
        rotatePattern = [[0,1,2,3,4,5,6,7,8],
                        [2,5,8,1,4,7,0,3,6],
                        [0,1,2,3,4,5,6,7,8][::-1],
                        [2,5,8,1,4,7,0,3,6][::-1]]
        flipPattern = [[2,1,0,5,4,3,8,7,6],
                        [0,3,6,1,4,7,2,5,8],
                        [2,1,0,5,4,3,8,7,6][::-1],
                        [0,3,6,1,4,7,2,5,8][::-1]]
        allPattern = rotatePattern + flipPattern

        for box in posBox:
            if box not in self.posTargets:
                board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                        (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                        (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
                for pattern in allPattern:
                    newBoard = [board[i] for i in pattern]
                    if newBoard[1] in self.posWalls and newBoard[5] in self.posWalls: return True
                    elif newBoard[1] in posBox and newBoard[2] in self.posWalls and newBoard[5] in self.posWalls: return True
                    elif newBoard[1] in posBox and newBoard[2] in self.posWalls and newBoard[5] in posBox: return True
                    elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                    elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in self.posWalls and newBoard[3] in self.posWalls and newBoard[8] in self.posWalls: return True
        return False
    
    def breadthFirstSearch(self):
        """
        Implement breadthFirstSearch approach
        """
        beginBox = self.PosOfBoxes()
        beginMan = self.PosOfMan()

        startState = (beginMan, beginBox) # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
        frontier = collections.deque([[startState]]) # store states
        moves = collections.deque([[0]]) # store moves
        exploredSet = set()
        while frontier:
            node = frontier.popleft()
            node_move = moves.popleft() 
            if self.isEndState(node[-1][-1]):
                return ','.join(node_move[1:]).replace(',','')
                #break
            if node[-1] not in exploredSet:
                exploredSet.add(node[-1])
                for move in self.legalMoves(node[-1][0], node[-1][1]):
                    newPosMan, newPosBox = self.updateState(node[-1][0], node[-1][1], move)
                    if self.isFailed(newPosBox):
                        continue
                    frontier.append(node + [(newPosMan, newPosBox)])
                    moves.append(node_move + [move[-1]])
        
        return "No solution found"

    def depthFirstSearch(self):
        """
        Implement depthFirstSearch approach
        """
        beginBox = self.PosOfBoxes()
        beginMan = self.PosOfMan()

        startState = (beginMan, beginBox)
        frontier = collections.deque([[startState]])
        exploredSet = set()
        moves = [[0]] 
        while frontier:
            node = frontier.pop()
            node_move = moves.pop()
            if self.isEndState(node[-1][-1]):
                return ','.join(node_move[1:]).replace(',','')
                #break
            if node[-1] not in exploredSet:
                exploredSet.add(node[-1])
                for move in self.legalMoves(node[-1][0], node[-1][1]):
                    newPosMan, newPosBox = self.updateState(node[-1][0], node[-1][1], move)
                    if self.isFailed(newPosBox):
                        continue
                    frontier.append(node + [(newPosMan, newPosBox)])
                    moves.append(node_move + [move[-1]])
        return "No solution found"  
    
    def heuristic(self, posMan, posBox):
        """
        A heuristic function to calculate the overall distance between the else boxes and the else targets"""
        distance = 0
        completes = set(self.posTargets) & set(posBox)
        sortposBox = list(set(posBox).difference(completes))
        sortposTargets = list(set(self.posTargets).difference(completes))
        for i in range(len(sortposBox)):
            distance += (abs(sortposBox[i][0] - sortposTargets[i][0])) + (abs(sortposBox[i][1] - sortposTargets[i][1]))
        return distance

    def cost(self, moves):
        return len([x for x in moves if x.islower()])
    
    def uniformCostSearch(self):
        """
        Implement uniformCostSearch approach
        """
        beginBox = self.PosOfBoxes()
        beginMan = self.PosOfMan()

        startState = (beginMan, beginBox)
        frontier = PriorityQueue()
        frontier.push([startState], 0)
        exploredSet = set()
        moves = PriorityQueue()
        moves.push([0], 0)
        while frontier:
            node = frontier.pop()
            node_move = moves.pop()
            if self.isEndState(node[-1][-1]):
                return ','.join(node_move[1:]).replace(',','')
                break
            if node[-1] not in exploredSet:
                exploredSet.add(node[-1])
                Cost = self.cost(node_move[1:])
                for move in self.legalMoves(node[-1][0], node[-1][1]):
                    newPosMan, newPosBox = self.updateState(node[-1][0], node[-1][1], move)
                    if self.isFailed(newPosBox):
                        continue
                    frontier.push(node + [(newPosMan, newPosBox)], Cost)
                    moves.push(node_move + [move[-1]], Cost)

        return "No solution found"
    
    def aStarSearch(self):
        """
        Implement aStarSearch approach
        """
        beginBox = self.PosOfBoxes()
        beginMan = self.PosOfMan()

        start_state = (beginMan, beginBox)
        frontier = PriorityQueue()
        frontier.push([start_state], self.heuristic(beginMan, beginBox))
        exploredSet = set()
        moves = PriorityQueue()
        moves.push([0], self.heuristic(beginMan, start_state[1]))
        while frontier:
            node = frontier.pop()
            node_move = moves.pop()
            if self.isEndState(node[-1][-1]):
                return ','.join(node_move[1:]).replace(',','')
                break
            if node[-1] not in exploredSet:
                exploredSet.add(node[-1])
                Cost = self.cost(node_move[1:])
                for move in self.legalMoves(node[-1][0], node[-1][1]):
                    newPosMan, newPosBox = self.updateState(node[-1][0], node[-1][1], move)
                    if self.isFailed(newPosBox):
                        continue
                    Heuristic = self.heuristic(newPosMan, newPosBox)
                    frontier.push(node + [(newPosMan, newPosBox)], Heuristic + Cost) 
                    moves.push(node_move + [move[-1]], Heuristic + Cost)
        return "No solution found"
    
    def solve(self, method='bfs'):
        """
        Solves the Sokoban puzzle using the specified search method.

        Args:
            method (str): The search method to use. Options are 'astar', 'dfs', 'bfs', and 'ucs'.

        Returns:
            str: A string representation of the solution or a message indicating failure.
        """
        method = method.lower()
        search_methods = {
            'astar': self.aStarSearch,
            'dfs': self.depthFirstSearch,
            'bfs': self.breadthFirstSearch,
            'ucs': self.uniformCostSearch
        }

        if method in search_methods:
            return search_methods[method]()
        else:
            return "Invalid search method specified."

        
if __name__ == '__main__':
    solver = SokobanSolver("easy/level2.txt")
    method = 'astar'

    time_start = time.time()
    solution = solver.solve(method)
    print("Solution:", solution)
    time_end=time.time()
    print('Runtime of %s: %.2f second.' %(method, time_end-time_start))