from random import sample, shuffle, randint, choice
from mymodule import get_integer
from PyQt5.QtMultimedia import QSound
from PyQt5 import QtCore
import pickle


class World():

    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.locations = self.create_locations()
        self.connect_locations()
        self.worms = []
        self.deadWorms = []
        self.segments = []

    def add_worm(self,worm):
        self.worms.append(worm)

    def test(self):
        computerWorms = 3
        humanWorms = 1
        #
        # Create computer controlled worms.
        #
        for count in range(computerWorms):
            name = '<worm '+str(count)+'>'
            location = next(self.random_location())
            direction = randint(0,6)
            worm = ComputerControlledWorm(name,location,direction,'blue')
            self.worms.append(worm)
            print(name,location)
        #
        # Create human comtrolled worms.
        #
        for count in range(humanWorms):
            name = input('Enter a name for your worm: ')
            location = next(self.random_location())
            worm = HumanControlledWorm(name,location,0,'white')
            self.worms.append(worm)
            print(name,location)
        #
        # Run the world until all the worms are dead.
        #
        while len(self.worms):
            for worm in self.worms:
                segment = worm.move()
                self.segments.append(segment)
                #print(worm.name,"moved in direction:",worm.direction)
                print(worm.statsString())
                if not worm.is_alive():
                    self.deadWorms.append(worm)
                    self.worms.remove(worm)
                    print('\n',worm.name,"died!\n")

    def random_location(self):
        """Returns a location that has not previously been used.
           usage: newLocation = next(self.random_location()) """
        maxLocations = self.width * self.height
        allLocations = []
        for x in range(0,self.width):
            for y in range(0,self.height):
                allLocations.append((x,y))
        shuffle(allLocations)
        counter = 0
        while counter < maxLocations:
            x,y = allLocations[counter]
            yield self.locations[y][x]
            counter += 1

    def create_locations(self):
        """Add locations to the world."""
        locations = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                location = Location(x,y)
                row.append(location)
            locations.append(row)
        return locations

    def connect_locations(self):
        """Loop though the locations, populating their list of neighbors."""
        for row in self.locations:
            for location in row:
                location.connect_to_neighbors(self)

class Location():

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.passageways = [None,None,None,None,None,None]
        
    def __repr__(self):
        return "("+str(self.x)+","+str(self.y)+")"

    def connect_to_neighbors(self,world):
        """Connect to nearby locations."""
        #
        # This order of offsets is important, it corresponds to worm directions.
        # The offsets are different for even and odd rows, and it took me a long
        # time to figure that out.
        #
        if self.y % 2 == 0:
            neighborOffsets = [(-1,0),(-1,-1),(0,-1),(1,0),(0,+1),(-1,+1)]
        else:
            neighborOffsets = [(-1,0),(0,-1),(1,-1),(1,0),(1,1),(0,1)]
            
        for offset in neighborOffsets:
            neighborX = self.x + offset[0]
            neighborY = self.y + offset[1]
            #
            # Correct for the boundaries. We only have to do this on two
            # sides because lists wrap arround with negative indexes.
            #
            if neighborX == world.width: neighborX = 0
            if neighborY == world.height: neighborY = 0
            self.neighbors.append(world.locations[neighborY][neighborX])

    def view(self):
        """Returns the current view of the location as seen from
           direction 0 (looking due east)."""
        viewString = ''
        #
        # Arbitrary view from direction 0.
        #
        for passageway in self.passageways:
            if passageway == None:
                viewString += '0'
            else:
                viewString += '1'
        return viewString

    def leave(self,worm):
        """Close that path once a worm leaves that way. Return the
           new location."""
        passageway = (worm.direction + 3) % 6
        #
        # Put a reference to the worm in the passage location instead
        # of simply indicating it is blocked with a value so that we
        # can make decisions about turns based who whether or not
        # the worm sees its own tracks in a later version.
        #
        self.passageways[passageway] = worm
        newLocation = self.neighbors[passageway]
        return newLocation

    def arrive(self,worm):
        """Close the path that a worm arrives from."""
        #
        # Put a reference to the worm in the passage location instead
        # of simply indicating it is blocked with a value so that we
        # can make decisions about turns based who whether or not
        # the worm sees its own tracks in a later version.
        #
        self.passageways[worm.direction] = worm

            
class Worm():
    #                            1   2
    #                             \ /                                     
    # Where directions are:    0-->X<--3                                      
    # (absolute toward)           / \
    #                            5   4
    #
    #                            1   2
    #                             \ /                                     
    # Where turns are:     ---->>> X--3                                      
    # (relative)                  / \
    #                            5   4
    # 1: hard left
    # 2: left
    # 3: straight
    # 4: right
    # 5: hard right
    #
    # turnTranslations let you go from (direction + turnTranslations[turn]) to new direction
    #
    turnTranslations = {0:None,1:4,2:5,3:0,4:1,5:2}
    directionHeading = [0, 60, 120, 180, 240, 300]
    #
    #
    #

    def __init__(self, name, location, direction=None, color='blue', sounds=None):
        self.name = name
        self.location = location
        self.direction = direction
        self.color = color
        self.rules = {}
        self.segments = []
        self.sounds = sounds
        self.waitingForInstructions = False
        self.turnCompleted = False
        #
        # Scoring variables
        #
        self.segmentCount = 0
        self.triangleCount = 0 
        self.asteriskCount = 0

    def __repr__(self):
        return "Worm("+self.name+","+str(self.location)+","+str(self.direction)+")"
    
    def __repr__(self):
        return '{:} At:{:} Heading:{:} T:{:2.0f}% S:{:d} T:{:d} A:{:d} '.format(self.name,
                                                                                str(self.location),
                                                                                str(self.direction),
                                                                                self.percent_programmed(),
                                                                                self.segmentCount,
                                                                                self.triangleCount,
                                                                                self.asteriskCount)


    def save(self, filename):
        """Save the worm to the designated file."""
        newWorm = Worm(self.name, None, None, self.color, self.sounds)
        newWorm.rules = self.rules
        file = open(filename,'wb')
        pickle.dump(newWorm,file)
        file.close()

    def load(self, filename):
        """Load the worm at filename into this worm. We assume that this worm
           already has a location and direction."""
        file = open(filename,'rb')
        savedWorm = pickle.load(file)
        self.name = savedWorm.name
        self.color = savedWorm.color
        self.sounds = savedWorm.sounds
        self.rules = savedWorm.rules
        self.location = location
        self.direction = randint(0,6)
        self.segments = []
        self.waitingForInstructions = False
        self.turnCompleted = False
        #
        # Scoring variables
        #
        self.segmentCount = 0
        self.triangleCount = 0
        self.asteriskCount = 0

    def score(self):
        return self.segmentCount + (3 * self.triangleCount) + (6 * self.asteriskCount)

    def statsString(self):
        return '{:>15.15}:    {:2.0f}%     |   {:4d}      {:4d}        {:4d} '.format(self.name,
                                                                                      self.percent_programmed(),
                                                                                      self.segmentCount,
                                                                                      self.triangleCount,
                                                                                      self.asteriskCount)
    
    def percent_programmed(self):
        totalRules = 31
        return len(self.rules)/totalRules*100
    
    def move(self):
        """The worm moves according to its rules or asks for a new rule."""
        view = self.look()
        if self.is_alive():
            if self.has_rule():
                turn = self.rules[view]
            else:
                turn = self.choose_turn()
                self.rules[view] = turn
            #
            # Based on the current direction and the turn, find the new direction.
            #
            self.direction = (self.direction + Worm.turnTranslations[turn]) % 6
            #
            # Store legal moves before and after the actual movement. We use this to
            # see if we just made a triangle.
            #
            legalMovesBefore = self.legal_moves_list()
            newLocation = self.location.leave(self)
            #
            # Store the segment we just completed to display later.
            #
            segment = Segment(self.location, newLocation, self.color)
            self.segments.append(segment)
            #
            # Save the new location and tell it that we have arrived there.
            #
            self.location = newLocation
            legalMovesAfter = self.legal_moves_list()
            self.location.arrive(self)
            self.update_stats(legalMovesBefore,legalMovesAfter)
            return segment
        else:
            #
            # If you're not alive, you've just created an asterisk.
            # I think we don't have to worry about having created
            # any segments or triangles, because they would have been
            # counted last turn.
            #
            self.asteriskCount += 1
        
    def update_stats(self, legalMovesBefore, legalMovesAfter):
        """Increment the segments, trianges and asterisks as necessary."""
        #
        # Always increment the number of segments.
        #
        self.segmentCount += 1
        #
        # If there is only one path out of the location we just
        # left, then we have taken it, and that will complete an
        # asterisk.
        #
        if len(legalMovesBefore) == 1:
            self.asteriskCount += 1
        newView = self.look()
        #
        # If 2 (left) was not a legal move before we moved and 1 (hard left)
        # is not a legal move after we move, then those two segments are already
        # completed and we have just now completed the third side of that triangle.
        #
        if (2 not in legalMovesBefore) and (1 not in legalMovesAfter):
            self.triangleCount += 1
        #
        # If 4 (right) was not a legal move before we moved and 5 (hard right)
        # is not a legal move after we move, then those two segments are already
        # completed and we have just now completed the third side of that triangle.
        #
        if (4 not in legalMovesBefore) and (5 not in legalMovesAfter):
            self.triangleCount += 1
            

    def look(self):
        """Returns a list indicating which passageways are open and closed.
           '000000' = all open '111111' = all closed."""
        view = self.location.view()
        #
        # Change from the generic view returned by the location to the view in the
        # direction we are traveling, then remove the pathageway we are coming from.
        #
        rotation = 5 - self.direction
        view = rotate_string(view,rotation)
        view = view[:-1]
        return view
        
    def is_alive(self):
        if self.look() == '11111': #no open passageways
            alive = False
        else:
            alive = True
        return alive

    def has_rule(self):
        """Returns True is the worm has a rule for its current situation."""
        view = self.look()
        if view in self.rules:
            hasRule = True
        else:
            hasRule = False
        return hasRule

    def choose_turn(self):
        """Generic worm class can not choose a turn. Subclass has to override
           this method."""
        pass

    def legal_moves_string(self):
        """Return the legal moves for the worm as a prompt."""
        moves = ["1:hard left\n",
                 "2:left\n",
                 "3:straight\n",
                 "4:right\n",
                 "5:hard right\n"]
        string = "\n"
        view = self.look()
        for direction in [1,2,3,4,5]:
            if view[direction-1] == '0':
                string += moves[direction-1]
        return string
        
    def legal_moves_list(self):
        """Return the legal moves for the worm as a list of legal moves."""
        legalMoves = []
        view = self.look()
        for direction in [1,2,3,4,5]:
            if view[direction-1] == '0':
                legalMoves.append(direction)
        return legalMoves

class HumanControlledWorm(Worm):

    def choose_turn(self):
        """Display the legal moves and get a move from the user."""
        self.waitingForInstructions = True
        legalString = self.legal_moves_string()
        legalList = self.legal_moves_list()
        print(legalString)
        prompt = "Which turn would you like ***"+self.name+"*** to make? "
        turn = -1
        while turn not in legalList:
            turn = int(get_integer(prompt))
        return turn

    def type(self):
        return 'human'

class ComputerControlledWorm(Worm):
    
    def choose_turn(self):
        """Choose a legal move at random from all legal moves."""
        legalList = self.legal_moves_list()
        turn = choice(legalList)
        return turn

    def type(self):
        return 'computer'

class WildWorm(Worm):

    def has_rule(self):
        return False
    
    def choose_turn(self):
        """Choose a legal move at random from all legal moves."""
        legalList = self.legal_moves_list()
        turn = choice(legalList)
        return turn

    def percent_programmed(self):
        return 0

    def type(self):
        return 'wild'
        
class Segment():

    def __init__(self,startLocation,endLocation,color=0xECD078):
        self.xStart = startLocation.x
        self.yStart = startLocation.y
        self.xEnd = endLocation.x
        self.yEnd = endLocation.y
        self.color = color

    def __repr__(self):
        return "<segment from: ("+str(self.xStart)+","+str(self.yStart)+") to: ("+str(self.xEnd)+","+str(self.yEnd)+") >"

def rotate_string(string,steps=1,direction='right'):
    """Returns the string rotated steps in direction."""
    length=len(string)
    for step in range(steps):
        if direction == 'right':
            string = string[length-1] + string[0:length-1]
        else:
            string = string[1:length] + string[0]
    return string

if __name__ == "__main__":          
    world = World(20,20)
    world.test()
    
    #print(world.locations)
    #print(world.locations[0][0],world.locations[0][0].neighbors)
    #print(world.locations[9][9],world.locations[9][9].neighbors)
    #print(world.locations[5][5],world.locations[5][5].neighbors)
    #print(world.locations[5][5].view())
##    fred_home = world.locations[13][13]
##    fred_direction = 0
##    ginger_home = world.locations[17][17 ]
##    ginger_direction = 3
##    fred = Worm('Fred',fred_home,fred_direction,'blue','human')
##    ginger = Worm('Ginger',ginger_home,ginger_direction,'red','random')
##    print(fred)
    #print("view",fred.look())
##    while fred.is_alive() or ginger.is_alive():
##        fred.move()
##        ginger.move()
##        if not fred.is_alive():
##            print('Fred died......')
##        if not ginger.is_alive():
##            print('Ginger died......')

