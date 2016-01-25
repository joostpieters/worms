import sys, random
from time import sleep
from PyQt5 import QtGui, QtCore, QtWidgets, QtMultimedia

from worm_display import WormDisplay

from ui_new_world_dialog import Ui_Dialog as Ui_NewWorldDialog


class NewWorldDialog(QtWidgets.QDialog, Ui_NewWorldDialog):
    def __init__(self):
        super(NewWorldDialog, self).__init__()

        # Set up the user interface from Designer.
        self.setupUi(self)

        # Make some local modifications.
        #self.colorDepthCombo.addItem("2 colors (1 bit per pixel)")

        # Connect up the buttons.
##        self.okButton.clicked.connect(self.accept)
##        self.cancelButton.clicked.connect(self.reject)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,app):
        #
        # MainWindow is, as you might expect, the main window
        # of an application. It supports menus, statusbars,
        # toolbars and probably other stuff.
        #
        # Call __init__ for the parent class to initialize things.
        super(MainWindow, self).__init__()
        # Keep a reference to the app so we can explicitly call self.app.processEvents()
        self.app = app
        # Initialize the widget that will act as the display.
        self.display = WormDisplay(self)
        self.setCentralWidget(self.display)
        #
        # Create actions, menus, toolbars and statusbar
        #
        self.create_actions()
        self.create_menus()
        self.create_tool_bars()
        self.create_status_bar()
        # Setup the main display window.
        self.setup_window()
        #
        # I don't know if we need this stuff or not. Tutorials vary.
        #
        #
        # Create a seperate widget to control the layout of our window.
        # This example shows the Vertical Box Layout (QVBoxLayout). You
        # could also do a horizontal box (QHBoxLayout) or a grid layout
        # (QGridLayout).
        #
        #mainWidget = QtWidgets.QWidget(self) 
        #self.setCentralWidget(mainWidget)
        #mainLayout = QtWidgets.QVBoxLayout()
        #mainLayout.addWidget(self.display)
        #self.setLayout(mainLayout)
        self.display.show()

    def setup_window(self):
        """Just putting a bunch of loosely related window setup stuff together here."""
        # Starting size of window. I don't think this is required.
        xSize = 750
        ySize = 885
        self.resize(xSize, ySize)
        # Starting coordinates of the window will be centered.
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        xLocation = (screen.width()-size.width())/2
        yLocation = (screen.height()-size.height())/2
        self.move(xLocation,yLocation)
        # Get things ready
        self.setWindowTitle("Paterson's worms")
        self.setWindowIcon(QtGui.QIcon('./icons/hexagon.png'))
        self.statusBar().showMessage('Ready')


    def create_actions(self):
        """Setup an action that can be associated with menus, buttons,
           shortcuts and taskbars."""
        #
        # Root is where the application exists in the directory structure.
        #
        root = QtCore.QFileInfo(__file__).absolutePath()
        
        self.exitAction = QtWidgets.QAction("E&xit", self,
                                            shortcut="Ctrl+Q",
                                            statusTip="Exit the application",
                                            triggered=self.close_game)

        self.newAction = QtWidgets.QAction(QtGui.QIcon(root + '/icons/new.png'),
                                           "&New", self,
                                           shortcut=QtGui.QKeySequence.New,
                                           statusTip="Start a new game",
                                           triggered=self.new_game)

        self.repeatAction = QtWidgets.QAction(QtGui.QIcon(root + '/icons/new.png'),
                                           "&Repeat", self,
                                           statusTip="Repeat with the same parameters",
                                           triggered=self.repeat_game)

        self.openAction = QtWidgets.QAction(QtGui.QIcon(root + '/icons/open.png'),
                                           "&Open", self,
                                           shortcut=QtGui.QKeySequence.Open,
                                           statusTip="Open a previous game",
                                           triggered=self.open_game)

        self.saveAction = QtWidgets.QAction(QtGui.QIcon(root + '/icons/save.png'),
                                           "&Save", self,
                                           shortcut=QtGui.QKeySequence.Save,
                                           statusTip="Save the current game",
                                           triggered=self.save_game)

        self.saveAsAction = QtWidgets.QAction("Save &As", self,
                                           shortcut=QtGui.QKeySequence.SaveAs,
                                           statusTip="Save the current game under a new name",
                                           triggered=self.save_game_as)

        self.aboutAction = QtWidgets.QAction("&About", self,
                                           statusTip="More information about Paterson's Worms",
                                           triggered=self.about)

        self.saveWormAction = QtWidgets.QAction(QtGui.QIcon(root + '/icons/save.png'),
                                           "&Save", self,
                                           statusTip="Save a worm",
                                           triggered=self.save_worm)

        self.loadWormAction = QtWidgets.QAction(QtGui.QIcon(root + '/icons/open.png'),
                                           "&Load", self,
                                           statusTip="Load a worm",
                                           triggered=self.load_worm)

        self.preset1Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "5x5 1 worms", self,
                                               statusTip="",
                                               triggered=self.preset1)

        self.preset2Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "10x10 2 worms", self,
                                               statusTip="",
                                               triggered=self.preset2)

        self.preset3Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "20x20 4 worms (classic)", self,
                                               statusTip="",
                                               triggered=self.preset3)

        self.preset4Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "30x30 10 worms", self,
                                               statusTip="",
                                               triggered=self.preset4)

        self.preset5Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "50x50 4 worms", self,
                                               statusTip="",
                                               triggered=self.preset5)

        self.preset6Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "50x50 50 worms", self,
                                               statusTip="",
                                               triggered=self.preset6)

        self.preset7Action = QtWidgets.QAction(QtGui.QIcon(root + '/icons/paste.png'),
                                               "50x50 1 worm", self,
                                           statusTip="",
                                           triggered=self.preset7)


        self.openAction.setEnabled(False)
        self.saveAction.setEnabled(False)
        self.saveAsAction.setEnabled(False)

    def create_menus(self):
        """Create a menubar and add a menu and an action."""

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        self.menuBar().addSeparator()

        self.wormMenu = self.menuBar().addMenu("&Worms")
        self.wormMenu.addAction(self.saveWormAction)
        self.wormMenu.addAction(self.loadWormAction)

        self.presetMenu = self.menuBar().addMenu("&Presets")
        self.presetMenu.addAction(self.preset1Action)
        self.presetMenu.addAction(self.preset2Action)
        self.presetMenu.addAction(self.preset3Action)
        self.presetMenu.addAction(self.preset4Action)
        self.presetMenu.addAction(self.preset5Action)
        self.presetMenu.addAction(self.preset6Action)
        self.presetMenu.addAction(self.preset7Action)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAction)

    def create_tool_bars(self):
        """Create a toolbar and add an action to it."""
        
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.repeatAction)
        self.fileToolBar.addAction(self.newAction)
        self.fileToolBar.addAction(self.openAction)
        self.fileToolBar.addAction(self.saveAction)
        
        self.speedSlider = QtWidgets.QSlider()
        self.speedSlider.setOrientation(QtCore.Qt.Horizontal)
        self.speedSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.speedSlider.setTickInterval(100)
        self.speedSlider.setMinimum(5)
        self.speedSlider.setMaximum(1000)
        self.speedSlider.setValue(self.display.timerBaseSpeed)
        self.speedSlider.valueChanged.connect(self.display.set_timer_base_speed)
        self.fileToolBar.addWidget(self.speedSlider)

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")
        #
        #You can also add widgets to the statusBar
        #
        #self.progressBar = QtWidgets.QProgressBar(self.statusBar())
        #self.progressBar.hide()
        #self.statusBar().addPermanentWidget(self.progressBar)


    def save_worm(self):
        worms = self.display.world.worms + self.display.world.deadWorms
        names = []
        wormDictionary = {}
        for worm in worms:
            color = QtGui.QColor(worm.color)
            print('poop')
            print(color)
            print('poop')
            print(color.rgb())
#            name = "<font color='#{:}'>{:}</font>".format(color.rgb(),str(worm))
            name = str(worm)
            wormDictionary[name] = worm
            names.append(name)
        print(names)
        if names:
            name, ok = QtWidgets.QInputDialog.getItem(self, "Which worm would you like to save?",
                                                      "Which worm:", names, 0, False)
            if ok and name:
                fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save worm as?",
                                                                    None, "All Files (*);;Worm Files (*.worm)")
                if fileName:
                    wormDictionary[name].save(fileName)
            
    def load_worm(self):
        pass
    
    def new_game(self):
        dialog = NewWorldDialog()
        dialog.width.setValue(self.display.worldWidth)
        dialog.height.setValue(self.display.worldHeight)
        dialog.computer.setValue(self.display.computerControlledWorms)
        dialog.human.setValue(self.display.humanControlledWorms)
        dialog.wild.setValue(self.display.wildWorms)        
        result = dialog.exec_()
        if result:
            self.statusBar().showMessage("New game!")
            width = dialog.width.value()
            height = dialog.height.value()
            cWorms = dialog.computer.value()
            hWorms = dialog.human.value()
            wWorms = dialog.wild.value()
            self.display.new_game(width, height, cWorms, hWorms, wWorms)

    def repeat_game(self):
        self.statusBar().showMessage("Repeat game!")
        width = self.display.worldWidth
        height = self.display.worldHeight
        cWorms = self.display.computerControlledWorms
        hWorms = self.display.humanControlledWorms
        wWorms = self.display.wildWorms
        self.display.new_game(width, height, cWorms, hWorms, wWorms)

    def preset1(self):
            self.display.new_game(5,5,1,0,0)

    def preset2(self):
            self.display.new_game(10,10,2,0,0)

    def preset3(self):
            self.display.new_game(20,20,4,0,0)

    def preset4(self):
            self.display.new_game(30,30,10,0,0)

    def preset5(self):
            self.display.new_game(50,50,4,0,0)

    def preset6(self):
            self.display.new_game(50,50,50,0,0)

    def preset7(self):
            self.display.new_game(50,50,1,0,0)

    def open_game(self):
        pass

    def save_game(self):
        pass

    def save_game_as(self):
        pass

    def close_game(self):
        self.display.timer.stop()
        self.close()


    def about(self):
        QtWidgets.QMessageBox.about(self, "Paterson's Worms",
                "I should <b>probably</b> put some "
                "real text in here.")

    def mousePressEvent(self, event):
        print("click")

    def mouseReleaseEvent(self, event):
        print("release")

    def keyPressEvent(self, event):
        print("key press")

    def keyReleaseEvent(self, event):
        print("key release")

if __name__ == '__main__':
    #
    # Setup the application and pass it any command line
    # arguments that might be present.
    #
    app = QtWidgets.QApplication(sys.argv)
    #
    # Create a new window and show it to the user. Then
    # start the applications main event loop.
    #
    mainWin = MainWindow(app)
    mainWin.show()
    #
    # Capture any result (exit) codes from the application
    # and pass them to whoever called your program.
    #
    result = app.exec_()
    sys.exit(result)

