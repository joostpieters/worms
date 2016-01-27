import sys, random
from time import sleep, clock
from copy import copy
from PyQt5 import QtGui, QtCore, QtWidgets, QtMultimedia

import worm_class

class WormDisplay(QtWidgets.QWidget):

    def __init__(self, mainWindow, parent=None):
        super(WormDisplay, self).__init__(parent)

        self.mainWindow = mainWindow
        self.timer = QtCore.QBasicTimer()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #
        # This next section is specific to our worm application. 
        #
        self.timerBaseSpeed = 500
        self.new_game()

    def new_game(self, h=20, w=20, cW=3, hW=1, wW=0):
        #
        # Setting random seed just for testing.
        #
        self.timer.stop()
        random.seed(3)
        self.time = clock()
        self.worldWidth = h
        self.worldHeight = w
        self.world = worm_class.World(self.worldWidth, self.worldHeight)
        self.computerControlledWorms = cW
        self.humanControlledWorms = hW
        self.wildWorms = wW
        randomParts = Random_Worm_Parts()
        self.pixmap = randomParts.background()
        self.rectangle = 0 #arbitrary initial value to check changes against
        #
        # Add computer worms
        #
        for x in range(0,self.computerControlledWorms):
            name = randomParts.dancer()
            location = next(self.world.random_location())
            direction = random.randint(0,6)
            color = randomParts.color()
            control = 'random'
            sounds = randomParts.sounds()
            worm = worm_class.ComputerControlledWorm(name, location, direction, color, sounds)
            self.world.add_worm(worm)
        #
        # add wild worms
        #
        for x in range(0,self.wildWorms):
            name = randomParts.dancer()
            location = next(self.world.random_location())
            direction = random.randint(0,6)
            color = randomParts.color()
            control = 'random'
            sounds = randomParts.sounds()
            worm = worm_class.WildWorm(name, location, direction, color, sounds)
            self.world.add_worm(worm)
        #
        # Add human worms
        #
        for x in range(0,self.humanControlledWorms):
            label = 'Worm '+str(x+1)
            textDialog = QtWidgets.QInputDialog()
            textDialog.setModal(True)
            text, ok = textDialog.getText(textDialog, label, "Enter your worm's name:")
            if ok:
                name = text
            else:
                name = 'Trent'
            colorDialog = QtWidgets.QColorDialog()
            colorDialog.setModal(True)
            color = colorDialog.getColor()
            if not color.isValid():
                color = randomParts.color()
            location = next(self.world.random_location())
            direction = random.randint(0,6)
            sounds = randomParts.sounds()
            worm = worm_class.HumanControlledWorm(name,location,direction,color,sounds)
            self.world.add_worm(worm)
        self.turns = 0
        self.waitingForHuman = False
        self.waitingWorm = None
        self.set_timer()
        self.update()

    def set_timer(self):
        maximumSlowDownForMultipleWorms = 6
        if len(self.world.worms) < maximumSlowDownForMultipleWorms:
            updateSpeed = self.timerBaseSpeed * len(self.world.worms)
        else:
            updateSpeed = self.timerBaseSpeed * maximumSlowDownForMultipleWorms       
        self.timer.start(updateSpeed, self)

    def set_timer_base_speed(self, speed):
        """This is called when something needs to change self.baseSpeed."""
        self.mainWindow.statusBar().showMessage("Base speed changed to: "+str(speed))
        self.timerBaseSpeed = speed
        self.set_timer()

    def run_game(self):
        """Process one 'turn' where all worms that are able to move without
           a user decision are moved. If you get to a human controlled worm
           AND that worm needs a new rule, then break so the user input can be
           processed."""
        wormsToRun = [worm for worm in self.world.worms if worm.turnCompleted == False]
        for worm in wormsToRun:
            if worm.is_alive():
                if worm.type() == 'human' and not worm.has_rule():
                    #self.get_human_move_rule(worm)
                    self.waitingForHuman = True
                    self.waitingWorm = worm
                    self.waitingBlinkOn = True
                    self.waitingTurn = None
                    self.timer.start(500, self)
                    break
                segment = worm.move()
                self.world.segments.append(segment)
            else:
                self.world.deadWorms.append(worm)
                self.world.worms.remove(worm)
            worm.turnCompleted = True


    def timerEvent(self, event):
        """Each time our timer goes off, this event is called."""
        #
        # First check to see if it was called for our timer.
        #
        if event.timerId() == self.timer.timerId():
            #
            # If there are living worms, move them. Otherwise we're all done.
            #
            if len(self.world.worms) > 0:
                if self.waitingForHuman:
                    print('waiting for human')
                    self.waitingBlinkOn = not self.waitingBlinkOn
                    self.update()
                else:
                    wormsToRun = [worm for worm in self.world.worms if worm.turnCompleted == False]
                    if len(wormsToRun) == 0:
                        for worm in self.world.worms:
                            worm.turnCompleted = False
                        self.turns += 1
                        self.set_timer()
                        self.show_stats()
                    self.run_game()
                    self.update()
                    self.play_sounds()
            else:
                self.timer.stop()
                print(clock()-self.time)
        #
        # If it wasn't called for our timer, maybe the main windows
        # called it, so we will pass it on up the chain.
        #
        else:
            super(WormDisplay, self).timerEvent(event)

    def show_stats(self):
        allWorms = self.world.worms + self.world.deadWorms
        statString = ''
        statString += '\n           Worm:    training     segments  triangles   asterisks'
        statString += '\n---------------------------------------------------------------'
        for worm in allWorms:
            statString += '\n' + worm.statsString()
        statString += '\n---------------------------------------------------------------'
        print(statString)
            
    def play_sounds(self):
        for worm in self.world.worms[:4]:
            d = worm.direction-1
            worm.sounds[d].play()

    def minimumSizeHint(self):
        return QtCore.QSize(100, 100)

    def sizeHint(self):
        return QtCore.QSize(400, 200)
        
    def paintEvent(self, event):
        """By magic, this event occasionally gets called. Maybe on self.update()?"""
        painter = QtGui.QPainter(self)
        rectangle = self.contentsRect()
        #
        # Redraw everything if the screen size changes (or on first run)
        #
        if rectangle != self.rectangle:
            self.background = self.pixmap.copy()
            backgroundPainter = QtGui.QPainter(self.background)
            self.draw_locations_hexes(backgroundPainter)
            self.draw_all_segments(backgroundPainter)
        #
        # Set Background
        #
        painter.drawPixmap(rectangle, self.background, rectangle)
        #
        # Draw the last (ultimate) segment and the head.
        #
        for worm in self.world.worms:
            self.draw_head(painter,worm)
            self.draw_ultimate_segment(painter, worm)
        if self.waitingForHuman:
            print('painting waiting for human.')
            #print(self.waitingWorm)
            #
            # Prefer to show next choice as straight, but if that is not legal then
            # just pick the first legal move. We only pick one the first time. After
            # that we wait for the human to change it
            #
            if not self.waitingTurn:
                legalMoves = self.waitingWorm.legal_moves_list()
                straight = 3
                if straight in legalMoves:
                    self.waitingTurn = straight
                else:
                    self.waitingTurn = legalMoves[0]
            #
            # Based on the current direction and the turn, find the new direction.
            #
            newDirection = (self.waitingWorm.direction + worm_class.Worm.turnTranslations[self.waitingTurn]) % 6
            newLocation = self.waitingWorm.location.leave_just_checking(newDirection)
            #print(newLocation)

            if self.waitingBlinkOn:
                self.draw_head(painter, worm)
                color = self.waitingWorm.color
                segment = worm_class.Segment(self.waitingWorm.location, newLocation, color)

                if (abs(segment.xStart - segment.xEnd) <= 2) and (abs(segment.yStart - segment.yEnd) <= 2):
                    x1, y1 = self.world_location_to_screen_coord(segment.xStart, segment.yStart)
                    x2, y2 = self.world_location_to_screen_coord(segment.xEnd, segment.yEnd)
                    for width, alpha in [(11,4),(9,8),(7,16),(5,32),(3,64),(1,255)]:
                        color.setAlpha(alpha)
                        pen = QtGui.QPen(color, width)
                        painter.setPen(pen)
                        painter.drawLine(x1,y1,x2,y2)

        else:
            print('painting not waiting for human')
            #
            # Add the next to last (penultimate) segment to the background
            #
            backgroundPainter = QtGui.QPainter(self.background)
            self.draw_penultimate_segment(backgroundPainter)
            self.rectangle = rectangle

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Right, QtCore.Qt.Key_Left, QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
            if event.key() in [QtCore.Qt.Key_Right, QtCore.Qt.Key_Up]:
                turnDirection = +1
            else:
                turnDirection = -1
            self.waitingTurn = (self.waitingTurn + turnDirection) % 6
            if self.waitingTurn == 0:
                if event.key() [QtCore.Qt.Key_Right, QtCore.Qt.Key_Up]:
                    self.waitingTurn = 1
                else:
                    self.waitingTurn = 5
        elif event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Space]:
            view = self.waitingWorm.look()
            self.waitingWorm.rules[view] = self.waitingTurn
            self.waitingForHuman = False
            self.waitingTurn = None

        print('key press in worm_display')

    def draw_head(self, painter, worm):
        """Draw a little head on each worm."""
        x, y = self.world_location_to_screen_coord(worm.location.x,worm.location.y)
        center = QtCore.QPoint(x,y)
        color = QtGui.QColor(worm.color).lighter()
        for width, radius, alpha in [(7,12,4),(6,10,8),(5,8,16),(4,6,32),(3,4,64),(2,2,128),(1,1,255)]:
            color.setAlpha(alpha)
            pen = QtGui.QPen(color, width)
            painter.setPen(pen)
            painter.drawEllipse(center,radius,radius)
            

    def draw_ultimate_segment(self, painter, worm):
        """Draw the newest segment of each worm in a different color."""
        if worm.segments:
            segment = worm.segments[-1]
            #
            # I can't draw across the screen correctly yet, so this is the
            # temporary fix to just not draw the literal edge case.
            #
            if (abs(segment.xStart - segment.xEnd) <= 2) and (abs(segment.yStart - segment.yEnd) <= 2):
                x1, y1 = self.world_location_to_screen_coord(segment.xStart, segment.yStart)
                x2, y2 = self.world_location_to_screen_coord(segment.xEnd, segment.yEnd)
                color = QtGui.QColor(worm.color).lighter()
                color.setAlpha(64)
                pen = QtGui.QPen(color, 3)
                painter.setPen(pen)
                painter.drawLine(x1,y1,x2,y2)
                color.setAlpha(255)
                pen = QtGui.QPen(color, 1)
                painter.setPen(pen)
                painter.drawLine(x1,y1,x2,y2)
            else:
                pass
            
    def draw_penultimate_segment(self, painter):
        """Draw the newest segment of each worm in a different color."""
        numberOfWorms = len(self.world.worms)
        latestSegments = self.world.segments[-numberOfWorms:]
        for segment in latestSegments:
            #
            # I can't draw across the screen correctly yet, so this is the
            # temporary fix to just not draw the literal edge case.
            #
            if (abs(segment.xStart - segment.xEnd) <= 2) and (abs(segment.yStart - segment.yEnd) <= 2):
                x1, y1 = self.world_location_to_screen_coord(segment.xStart, segment.yStart)
                x2, y2 = self.world_location_to_screen_coord(segment.xEnd, segment.yEnd)
                color = QtGui.QColor(segment.color)
                for width,alpha in [(11,4),(9,8),(7,16),(5,32),(3,64),(1,255)]:
                    color.setAlpha(alpha)
                    pen = QtGui.QPen(color, width)
                    painter.setPen(pen)
                    painter.drawLine(x1,y1,x2,y2)
            else:
                pass

    def draw_all_segments(self, painter):
        """Draw the paths taken by the worms so far."""
        allWorms = self.world.worms + self.world.deadWorms
        for worm in allWorms:
            if worm.is_alive():
                color = QtGui.QColor(worm.color)
            else:
                color = QtGui.QColor(worm.color).darker(150)
            for segment in worm.segments:
                #
                # I can't draw across the screen correctly yet, so this is the
                # temporary fix to just not draw the literal edge case.
                #
                if (abs(segment.xStart - segment.xEnd) <= 2) and (abs(segment.yStart - segment.yEnd) <= 2):
                    x1, y1 = self.world_location_to_screen_coord(segment.xStart, segment.yStart)
                    x2, y2 = self.world_location_to_screen_coord(segment.xEnd, segment.yEnd)
                    for width, alpha in [(11,4),(9,8),(7,16),(5,32),(3,64),(1,255)]:
                        color.setAlpha(alpha)
                        pen = QtGui.QPen(color, width)
                        painter.setPen(pen)
                        painter.drawLine(x1,y1,x2,y2)
                else:
                    pass

    def draw_segments_old(self, painter):
        """Draw the paths taken by the worms so far."""
        for segment in self.world.segments:
            #
            # I can't draw across the screen correctly yet, so this is the
            # temporary fix to just not draw the literal edge case.
            #
            if (abs(segment.xStart - segment.xEnd) <= 2) and (abs(segment.yStart - segment.yEnd) <= 2):
                x1, y1 = self.world_location_to_screen_coord(segment.xStart, segment.yStart)
                x2, y2 = self.world_location_to_screen_coord(segment.xEnd, segment.yEnd)
                color = QtGui.QColor(segment.color)
                for width,alpha in [(11,4),(9,8),(7,16),(5,32),(3,64),(1,255)]:
                    color.setAlpha(alpha)
                    pen = QtGui.QPen(color, width)
                    painter.setPen(pen)
                    painter.drawLine(x1,y1,x2,y2)
            else:
                pass

    def draw_locations_hexes(self, painter):
        """Draw the hexogonal locations for the worms."""
        color = QtGui.QColor(0xFFFFFF)
        color.setAlpha(16)
        width = 1
        pen = QtGui.QPen(color, width)
        painter.setPen(pen)

        for row in self.world.locations:
            for location in row:
                xStartWorld = location.x
                yStartWorld = location.y
                for neighbor in location.neighbors:
                    xEndWorld = neighbor.x
                    yEndWorld = neighbor.y
                    #
                    # Don't draw hexes across outer boarders, because I'm not doing that yet.
                    #
                    if (abs(xStartWorld - xEndWorld) <= 2) and (abs(yStartWorld - yEndWorld) <= 2):
                        x1, y1 = self.world_location_to_screen_coord(xStartWorld, yStartWorld)
                        x2, y2 = self.world_location_to_screen_coord(xEndWorld, yEndWorld)
                        painter.drawLine(x1,y1,x2,y2)
                    else:
                        pass

    def world_location_to_screen_coord(self,xWorld,yWorld):
        """Given a world x,y return the screen x,y values."""
        rectangle = self.contentsRect()
        xResolution = rectangle.right()
        yResolution = rectangle.bottom()
        xStep = round(xResolution / self.world.width)
        yStep = round(yResolution / self.world.height)
        #
        # 1. Make sure the first row & column are not on the edge.
        # 2. To make squares into hexagons, offset every other row.
        #
        if (yWorld % 2) == 0: #even numbered rows
            xOffsetFromEdge = 0.5*xStep
        else:
            xOffsetFromEdge = 1.0*xStep

        yOffsetFromEdge = 0.5*yStep

        xScreen = (xWorld * xStep) + xOffsetFromEdge 
        yScreen = (yWorld * yStep) + yOffsetFromEdge

        return xScreen, yScreen

       
class Random_Worm_Parts():

    def __init__(self):

        root = QtCore.QFileInfo(__file__).absolutePath()
        bg1 = QtGui.QPixmap()
        bg1.load(root+'/graphics/background1.jpg')
        bg2 = QtGui.QPixmap()
        bg2.load(root+'/graphics/background2.jpg')
        bg3 = QtGui.QPixmap()
        bg3.load(root+'/graphics/background3.jpg')
        bg4 = QtGui.QPixmap()
        bg4.load(root+'/graphics/background4.jpg')
        bg5 = QtGui.QPixmap()
        bg5.load(root+'/graphics/background5.jpg')
        bg6 = QtGui.QPixmap()
        bg6.load(root+'/graphics/background6.jpg')
        self.allBackgrounds = [bg1, bg2, bg3, bg4, bg5, bg6]
        random.shuffle(self.allBackgrounds)

        
        self.dancers = ['Astaire','Rogers','Pavalona','Graham','Kelly','Davis','Baryshnikov','Jackson',
                        'Nijinsky','Baker','Guillem','Cortes','Nureyev','Robbins','Charisse','Pan',
                        'Loring','Fosse','Tamblyn','de Mille','Alexander','Castle','Cole','Rivera',
                        'Travolta','Elliot','Timberlake','Madonna']

        self.titles = ['', ', Jr.', ' The Third', ' IV', ' the younger', ' the elder', ' von Stapelhurst']
        
        self.maxBaseNames = len(self.dancers)
        self.maxNames = self.maxBaseNames * len(self.titles)
        random.shuffle(self.dancers)

    ##    new = [0x, 0x, 0x, 0x, 0x, 0x, 0x, 0x]
        thoughtProvoking = [0xECD078, 0xD95B43, 0xC02942, 0x542437, 0x53777A, 0xC1C6B4, 0x9CA0AE, 0xB47E8D]
        cheerUpEmoKid = [0x556270, 0x4ECDC4, 0xC7F464, 0xFF6B6B, 0xC44D58, 0x999999, 0x336699, 0x9966CC]
        #neon = [0xF433FF, 0x3DFF33, 0xFFF533, 0x33FFF5, 0xFF333D, 0x81FF33, 0xB133FF, 0xFFBB3D, 0xC2FF3D]
        neon = [0x6FFF00, 0xFF00FF, 0xFFFF00, 0x4D4DFF, 0xFE0001, 0xFF4105, 0x993CF3]
        primaryColors = neon
        secondaryColors = thoughtProvoking + cheerUpEmoKid
        random.shuffle(primaryColors)
        random.shuffle(secondaryColors)
        self.allColors = primaryColors + secondaryColors


        e = [QtMultimedia.QSound(root+"/notes/44728__casualdave__101elow.wav"),
             QtMultimedia.QSound(root+"/notes/44729__casualdave__201a.wav"),
             QtMultimedia.QSound(root+"/notes/44730__casualdave__301d.wav"),
             QtMultimedia.QSound(root+"/notes/44731__casualdave__401g.wav"),
             QtMultimedia.QSound(root+"/notes/44733__casualdave__601e.wav"),
             QtMultimedia.QSound(root+"/notes/44733__casualdave__601e.wav")]

        d = [QtMultimedia.QSound(root+"/notes/11073__angstrom__a2.wav"),
             QtMultimedia.QSound(root+"/notes/11077__angstrom__c1.wav"),
             QtMultimedia.QSound(root+"/notes/11078__angstrom__c2.wav"),
             QtMultimedia.QSound(root+"/notes/11081__angstrom__d1.wav"),
             QtMultimedia.QSound(root+"/notes/11082__angstrom__d2.wav"),
             QtMultimedia.QSound(root+"/notes/11083__angstrom__e1.wav"),
             QtMultimedia.QSound(root+"/notes/11084__angstrom__e2.wav"),
             QtMultimedia.QSound(root+"/notes/11088__angstrom__g1.wav")]

        c = [QtMultimedia.QSound(root+"/notes/4189__realrhodessounds__d1.wav"),
             QtMultimedia.QSound(root+"/notes/4190__realrhodessounds__d2.wav"),
             QtMultimedia.QSound(root+"/notes/4191__realrhodessounds__d3.wav"),
             QtMultimedia.QSound(root+"/notes/4192__realrhodessounds__d4.wav"),
             QtMultimedia.QSound(root+"/notes/4193__realrhodessounds__d5.wav"),
             QtMultimedia.QSound(root+"/notes/4194__realrhodessounds__d6.wav")]

        b = [QtMultimedia.QSound(root+"/notes/95326__ramas26__a.wav"),
             QtMultimedia.QSound(root+"/notes/95328__ramas26__c.wav"),
             QtMultimedia.QSound(root+"/notes/95329__ramas26__d.wav"),
             QtMultimedia.QSound(root+"/notes/95330__ramas26__e.wav"),
             QtMultimedia.QSound(root+"/notes/95332__ramas26__g.wav"),
             QtMultimedia.QSound(root+"/notes/95332__ramas26__g.wav")]
        
        a = [QtMultimedia.QSound(root+"/notes/68447__pinkyfinger__piano-g.wav"),
             QtMultimedia.QSound(root+"/notes/68437__pinkyfinger__piano-a.wav"),
             QtMultimedia.QSound(root+"/notes/68441__pinkyfinger__piano-c.wav"),
             QtMultimedia.QSound(root+"/notes/68442__pinkyfinger__piano-d.wav"),
             QtMultimedia.QSound(root+"/notes/68443__pinkyfinger__piano-e.wav"),
             QtMultimedia.QSound(root+"/notes/68448__pinkyfinger__piano-g.wav")]
        self.allSounds = [a, b, c, d, e]
        random.shuffle(self.allSounds)

        self.dancerCounter = -1
        self.colorCounter = -1
        self.soundCounter = -1
        self.backgroundCounter = -1
        pass

    def dancer(self):
        self.dancerCounter += 1
        dancer = self.dancers[self.dancerCounter % self.maxBaseNames]
        title = self.titles[self.dancerCounter // self.maxBaseNames]
        return dancer + title

    def color(self):
        """Returns a "random" color choice."""
        self.colorCounter += 1
        #
        # If we run out of colors, just start over.
        #
        if self.colorCounter >= len(self.allColors):
            self.colorCounter = 0
        return self.allColors[self.colorCounter]

    def sounds(self):
        """Returns a "random" sound scheme."""
        self.soundCounter += 1
        if self.soundCounter >= len(self.allSounds):
            self.soundCounter = 0
        someSounds = self.allSounds[self.soundCounter]
        someSounds = someSounds[:]
        random.shuffle(someSounds)
        return someSounds

    def background(self):
        self.backgroundCounter += 1
        #
        # If we run out of colors, just start over.
        #
        if self.backgroundCounter >= len(self.allBackgrounds):
            self.backgroundCounter = 0
        return self.allBackgrounds[self.backgroundCounter]
