# Inspired by PyQt5 Creating Paint Application In 40 Minutes
#  https://www.youtube.com/watch?v=qEgyGyVA1ZQ

# NB If the menus do not work then click on another application and then click back
# and they will work https://python-forum.io/Thread-Tkinter-macOS-Catalina-and-Python-menu-issue

# PyQt documentation links are prefixed with the word 'documentation' in the code below and can be accessed automatically
#  in PyCharm using the following technique https://www.jetbrains.com/help/pycharm/inline-documentation.html

from PyQt6.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QFileDialog, QDockWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox, QLineEdit, QHBoxLayout, QComboBox
from PyQt6.QtGui import QCursor, QIcon, QPainter, QPen, QAction, QPixmap
import sys
import csv, random
from PyQt6.QtCore import Qt, QPoint

# a window that pops when the application starts to setup the game
class PlayerSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # set up the dialog window
        self.setWindowTitle("New Game Setup")
        # Set icon
        self.setWindowIcon(
            QIcon("./icons/paint-brush.png"))  # documentation: https://doc.qt.io/qt-6/qwidget.html#windowIcon-prop

        # set the windows dimensions
        top = 200
        left = 200
        width = 200
        height = 200
        self.setGeometry(top, left, width, height)

        # Layouts
        main_layout = QVBoxLayout()

        # Player 1 name input
        player1_label = QLabel("Player 1 Name:")
        self.player1_name = QLineEdit()
        player1_layout = QHBoxLayout()
        player1_layout.addWidget(player1_label)
        player1_layout.addWidget(self.player1_name)
        main_layout.addLayout(player1_layout)

        # Player 2 name input
        player2_label = QLabel("Player 2 Name:")
        self.player2_name = QLineEdit()
        player2_layout = QHBoxLayout()
        player2_layout.addWidget(player2_label)
        player2_layout.addWidget(self.player2_name)
        main_layout.addLayout(player2_layout)

        # difficulty selection
        difficulty_label = QLabel("Select Difficulty")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Hard"])  # Add difficulty levels
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(self.difficulty_combo)
        main_layout.addLayout(difficulty_layout)
        self.difficulty_combo.setStyleSheet("height:30px")

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Start")
        cancel_button = QPushButton("Cancel")

        # style for the buttons
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #bd2020;  /* Default background color */
            }
            QPushButton:hover {
                background-color: #a81a1a;  /* Darker red on hover */
            }
        """)


        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        # connect buttons
        ok_button.clicked.connect(self.accept)  # Close dialog and accept input
        cancel_button.clicked.connect(self.reject)  # Close dialog without saving input

        self.setLayout(main_layout)

    def accept(self):
        # Check if both names are provided
        if not self.player1_name.text().strip() or not self.player2_name.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter names for both players.")
        else:
            super().accept()  # If names are valid, accept and close the dialog

    # method to return the data entered
    def get_data(self):
        return {
            "player1": self.player1_name.text(),
            "player2": self.player2_name.text(),
            "difficulty": self.difficulty_combo.currentText()
        }


class PictionaryGame(QMainWindow):  # documentation https://doc.qt.io/qt-6/qwidget.html
    '''
    Painting Application class
    '''

    def __init__(self):
        super().__init__()
        self.black()
        self.tries = 3
        self.player1_score = 0
        self.player2_score = 0
        self.difficulty_label = QLabel("Difficulty: -")
        self.player1_label = QLabel("Player 1")
        self.player2_label = QLabel("Player 2")
        self.sketcher_label = QLabel("Player 1")
        self.guesser_label = QLabel("Player 2")
        self.currentSketcher = ""
        self.currentGuesser = ""
        self.currentWord = None


        # Show the setup dialog at the start
        if not self.show_setup_dialog():
            sys.exit()  # Exit the application if setup is canceled
        # set window title
        self.setWindowTitle("Pictionary Game")

        # set the windows dimensions
        top = 400
        left = 400
        width = 800
        height = 600
        self.setGeometry(top, left, width, height)

        # set the icon
        # windows version
        self.setWindowIcon(
            QIcon("./icons/paint-brush.png"))  # documentation: https://doc.qt.io/qt-6/qwidget.html#windowIcon-prop
        # mac version - not yet working
        # self.setWindowIcon(QIcon(QPixmap("./icons/paint-brush.png")))

        # image settings (default)
        self.image = QPixmap("./icons/canvas.png")  # documentation: https://doc.qt.io/qt-6/qpixmap.html
        self.image.fill(Qt.GlobalColor.white)  # documentation: https://doc.qt.io/qt-6/qpixmap.html#fill
        mainWidget = QWidget()
        mainWidget.setMaximumWidth(300)

        # draw settings (default)
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.GlobalColor.black  # documentation: https://doc.qt.io/qt-6/qt.html#GlobalColor-enum

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()  # documentation: https://doc.qt.io/qt-6/qpoint.html

        # set up menus
        mainMenu = self.menuBar()  # create a menu bar
        mainMenu.setStyleSheet("background-color:black; color:white;") # changed the background color and text color to force visibility in different window themes
        mainMenu.setNativeMenuBar(False)
        gameMenu = mainMenu.addMenu("Game")  # add the game menu to start new game
        fileMenu = mainMenu.addMenu(" File")  # add the file menu to the menu bar, the space is required as "File" is reserved in Mac
        brushSizeMenu = mainMenu.addMenu(" Brush Size")  # add the "Brush Size" menu to the menu bar
        brushColorMenu = mainMenu.addMenu(" Brush Colour")  # add the "Brush Colour" menu to the menu bar

        # set up the eraser menu item
        eraserAction = QAction("Eraser", self)
        eraserAction.setShortcut("Ctrl+E")
        eraserAction.triggered.connect(self.erase)
        self.menuBar().addAction(eraserAction)

        # new Game menu item
        newGameAction = QAction("start new game" , self)
        gameMenu.addAction(newGameAction)  # add the easy action to the difficulty menu, documentation: https://doc.qt.io/qt-6/qwidget.html#addAction
        newGameAction.triggered.connect(self.newGame)

        # save menu item
        saveAction = QAction(QIcon("./icons/save.png"), "Save", self)  # create a save action with a png as an icon, documentation: https://doc.qt.io/qt-6/qaction.html
        saveAction.setShortcut("Ctrl+S")  # connect this save action to a keyboard shortcut, documentation: https://doc.qt.io/qt-6/qaction.html#shortcut-prop
        fileMenu.addAction(saveAction)  # add the save action to the file menu, documentation: https://doc.qt.io/qt-6/qwidget.html#addAction
        saveAction.triggered.connect(self.save)  # when the menu option is selected or the shortcut is used the save slot is triggered, documentation: https://doc.qt.io/qt-6/qaction.html#triggered

        # clear
        clearAction = QAction(QIcon("./icons/clear.png"), "Clear", self)  # create a clear action with a png as an icon
        clearAction.setShortcut("Ctrl+C")  # connect this clear action to a keyboard shortcut
        fileMenu.addAction(clearAction)  # add this action to the file menu
        clearAction.triggered.connect(self.clear)  # when the menu option is selected or the shortcut is used the clear slot is triggered

        # brush thickness
        threepxAction = QAction(QIcon("./icons/threepx.png"), "3px", self)
        threepxAction.setShortcut("Ctrl+3")
        brushSizeMenu.addAction(threepxAction)  # connect the action to the function below
        threepxAction.triggered.connect(self.threepx)

        fivepxAction = QAction(QIcon("./icons/fivepx.png"), "5px", self)
        fivepxAction.setShortcut("Ctrl+5")
        brushSizeMenu.addAction(fivepxAction)
        fivepxAction.triggered.connect(self.fivepx)

        sevenpxAction = QAction(QIcon("./icons/sevenpx.png"), "7px", self)
        sevenpxAction.setShortcut("Ctrl+7")
        brushSizeMenu.addAction(sevenpxAction)
        sevenpxAction.triggered.connect(self.sevenpx)

        ninepxAction = QAction(QIcon("./icons/ninepx.png"), "9px", self)
        ninepxAction.setShortcut("Ctrl+9")
        brushSizeMenu.addAction(ninepxAction)
        ninepxAction.triggered.connect(self.ninepx)

        # brush colors
        blackAction = QAction(QIcon("./icons/black.png"), "Black", self)
        blackAction.setShortcut("Ctrl+B")
        brushColorMenu.addAction(blackAction);
        blackAction.triggered.connect(self.black)

        redAction = QAction(QIcon("./icons/red.png"), "Red", self)
        redAction.setShortcut("Ctrl+R")
        brushColorMenu.addAction(redAction);
        redAction.triggered.connect(self.red)

        greenAction = QAction(QIcon("./icons/green.png"), "Green", self)
        greenAction.setShortcut("Ctrl+G")
        brushColorMenu.addAction(greenAction);
        greenAction.triggered.connect(self.green)

        yellowAction = QAction(QIcon("./icons/yellow.png"), "Yellow", self)
        yellowAction.setShortcut("Ctrl+Y")
        brushColorMenu.addAction(yellowAction);
        yellowAction.triggered.connect(self.yellow)

        # Side Dock
        self.dockInfo = QDockWidget()
        #removing the title bar so that the dock is always connected to the window
        self.dockInfo.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockInfo)

        #widget inside the Dock
        playerInfo = QWidget()
        self.vbdock = QVBoxLayout()
        playerInfo.setLayout(self.vbdock)
        playerInfo.setMaximumSize(150, self.height())
        #add controls to custom widget
        self.difficulty_label = QLabel(f"Difficulty: {self.difficulty}")
        # set difficulty style
        if self.difficulty == "Easy":
            self.difficulty_label.setStyleSheet("color: green; font-weight: bold;font-size : 16px")
        elif self.difficulty == "Hard":
            self.difficulty_label.setStyleSheet("color: red; font-weight: bold;font-size : 16px")
        self.player1_label = QLabel(f"{self.player1Name}: {self.player1_score}")
        self.player2_label = QLabel(f"{self.player2Name}: {self.player2_score}")

        self.vbdock.addWidget(self.difficulty_label)
        # adding spacing
        self.vbdock.addSpacing(50)
        self.vbdock.addWidget(QLabel("Current Turn:").setStyleSheet("font-size : 15px"))
        self.vbdock.addWidget(self.sketcher_label)
        self.vbdock.addWidget(self.guesser_label)
        # adding spacing
        self.vbdock.addSpacing(70)

        score_title = QLabel("Scores:")
        score_title.setStyleSheet("font-size:15px")
        self.vbdock.addWidget(score_title)
        self.vbdock.addWidget(self.player1_label)
        self.vbdock.addWidget(self.player2_label)
        self.vbdock.addStretch(1)
        self.answer_button = QPushButton("Finish drawing")
        self.answer_button.clicked.connect(self.answer)
        self.vbdock.addWidget(self.answer_button)

        #Setting colour of dock to gray
        playerInfo.setAutoFillBackground(True)
        p = playerInfo.palette()
        p.setColor(playerInfo.backgroundRole(), Qt.GlobalColor.gray)
        playerInfo.setPalette(p)

        #set widget for dock
        self.dockInfo.setWidget(playerInfo)
        self.startNewTurn(self.currentSketcher)
    # method to show the game setup dialog
    def show_setup_dialog(self):
        dialog = PlayerSetupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # getting the data
            data = dialog.get_data()
            self.player1Name = data["player1"]
            self.player2Name = data["player2"]
            self.difficulty = data["difficulty"]
            # printing to debug
            print(f"Player 1: {self.player1Name}, Player 2: {self.player2Name}, Difficulty: {self.difficulty}")
            # updating the UI with the new data
            self.update_ui_for_new_game()
            return True
        else:
            print("Game setup was cancelled")
            return False
    # method called to start a new game
    def newGame(self):
        if self.show_setup_dialog():
            self.clear()
            self.update_ui_for_new_game()
            self.startNewTurn(self.currentSketcher)
    def update_ui_for_new_game(self):
        # update labels with new player names and difficulty
        self.difficulty_label.setText(f"Difficulty: {self.difficulty}")
        self.tries = 3
        # debugging
        print("changing the score back to 0 because game was restarted")
        self.player1_score , self.player2_score = 0 , 0
        self.updateScoreDisplay()
        # set difficulty style
        if self.difficulty == "Easy":
            self.difficulty_label.setStyleSheet("color: green; font-weight: bold;font-size : 16px")
        elif self.difficulty == "Hard":
            self.difficulty_label.setStyleSheet("color: red; font-weight: bold;font-size : 16px")
        # get list based on the difficulty chosen by the player in the menu
        self.getList(self.difficulty)

        # randomly select a sketcher and make the other player the guesser
        self.currentSketcher = random.choice([self.player1Name, self.player2Name])
        if self.currentSketcher == self.player1Name:
            self.currentGuesser = self.player2Name
        else:
            self.currentGuesser = self.player1Name
        # update the ui with the new data
        self.updateTurnsUi()
    def updateScoreDisplay(self):
        print("updating score")
        # update score display with color based on value
        if self.player1_score > 0:
            self.player1_label.setStyleSheet("font-size:13px; color: green; font-weight: bold;")
        if self.player1_score < 0:
            self.player1_label.setStyleSheet(" font-size:13px; color: red; font-weight: bold;")

        if self.player2_score > 0:
            self.player2_label.setStyleSheet("font-size:13px; color: green; font-weight: bold;")
        if self.player2_score < 0:
            self.player2_label.setStyleSheet("font-size:13px; color: red; font-weight: bold;")
        self.player1_label.setText(f"{self.player1Name}: {self.player1_score}")
        self.player2_label.setText(f"{self.player2Name}: {self.player2_score}")
    # method that shopws the hiden word pop up to let the sketcher reveal his word
    def showWordPopup(self,player):
        word_dialog = QDialog(self)
        # setting up the title
        word_dialog.setWindowTitle(f"{player}, Check Your Word")

        # creating the labels and buttons
        instruction_label = QLabel("Don't let others see. Press 'Show Word' to reveal it.")
        # making the word hidden at first
        word_label = QLabel("*******")
        # button to toggle the word between hiden and visible
        toggle_button = QPushButton("Show Word")
        toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #ee8510;  /* Default background color */
            }
            QPushButton:hover {
                background-color: #c56f0e;  /* Darker red on hover */
            }
        """)
        ok_button = QPushButton("OK")

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(instruction_label)
        layout.addWidget(word_label)
        layout.addWidget(toggle_button)
        layout.addWidget(ok_button)
        word_dialog.setLayout(layout)

        # toggle function to show or hide the word
        def toggle_word_visibility():
            # check if the word is currently hidden if yest show the word and change the button value
            if word_label.text() == "*******":
                word_label.setText(self.currentWord)
                toggle_button.setText("Hide Word")
            else:
                # hide the word
                word_label.setText("*****")
                toggle_button.setText("Show Word")

        # connect the buttons
        toggle_button.clicked.connect(toggle_word_visibility)
        ok_button.clicked.connect(word_dialog.accept)

        word_dialog.exec()
    def answer(self):
        self.showAnswerPopup(self.currentGuesser)

    def showAnswerPopup(self, player):
        # create a dialog for answering
        word_dialog = QDialog(self)
        word_dialog.setWindowTitle(f"{player}, Try to guess the word")

        # create labels and buttons
        instruction_label = QLabel(f"Enter a word that describes the drawing.\nYou have {self.tries} guesses left.")
        answer_input = QLineEdit()
        answer_button = QPushButton("Submit Answer")

        layout = QVBoxLayout()
        layout.addWidget(instruction_label)
        layout.addWidget(answer_input)
        layout.addWidget(answer_button)
        word_dialog.setLayout(layout)

        def submit_answer():
            answer = answer_input.text()
            # check if the answer is correct
            correct = self.checkAnswer(answer, player)
            if correct or self.tries <= 0:
                # end turn if correct or out of tries
                word_dialog.accept()
                # check if the word is correct or out of tries to print different messages
                if correct:
                    self.messageBox("Correct Answer!!!")
                else:
                    self.messageBox("Couldn't Figure it out x_x")
                self.endTurn()
            else:
                # update instructions if there are tries left
                instruction_label.setText(f"Incorrect! Try again. You have {self.tries} guesses left.")

        # connect the button
        answer_button.clicked.connect(submit_answer)
        word_dialog.exec()

    def checkAnswer(self, answer, player):
        #print(f"checking answer '{answer}' against current word '{self.currentWord}'")
        #if not self.currentWord:
            #print("current word not set")
            #return False
        # make the comparison case-insensitive and check if correct
        if answer.strip().lower() == self.currentWord.strip().lower():
            print("Correct answer")
            # award points
            if player == self.player1Name:
                self.player1_score += 5
                self.player2_score += 10
            else:
                self.player2_score += 5
                self.player1_score += 10
            print(f"score {self.player1_score} , {self.player2_score}")
            self.updateScoreDisplay()
            return True  # return true for correct answer
        else:
            # remove one try
            self.tries -= 1
            # minus a point for wrong answer
            if player == self.player1Name:
                self.player1_score -= 1
            else:
                self.player2_score -= 1
            # check score is chaning
            print(f"score {self.player1_score} , {self.player2_score}")
            self.updateScoreDisplay()
            return False  # return false for wrong answer
    def messageBox(self , message):
        # create a dialog for showing a message
        word_dialog = QDialog(self)
        word_dialog.setWindowTitle(message)
        word_dialog.setFixedWidth(200)
        # create labels and buttons
        instruction_label = QLabel("Current Score:")
        instruction_label.setStyleSheet("font-weight:bold ; font-size:18px")
        score_label1 = QLabel(f"{self.player1Name}: {self.player1_score}")
        score_label2 = QLabel(f"{self.player2Name}: {self.player2_score}")

        # style the players score based on the value
        if self.player1_score < 0:
            score_label1.setStyleSheet("color:red; font-size:15px")
        if self.player1_score > 0:
            score_label1.setStyleSheet("color:green; font-size:15px")
        if self.player2_score < 0:
            score_label2.setStyleSheet("color:red; font-size:15px")
        if self.player2_score > 0:
            score_label2.setStyleSheet("color:green; font-size:15px")
        ok_button = QPushButton("Next Round")

        # layout setup
        layout = QVBoxLayout()
        layout.addSpacing(10)
        layout.addWidget(instruction_label)
        layout.addSpacing(10)
        layout.addWidget(score_label1)
        layout.addWidget(score_label2)
        layout.addSpacing(10)
        layout.addWidget(ok_button)
        word_dialog.setLayout(layout)

        # connect the button to close the dialog
        ok_button.clicked.connect(word_dialog.accept)

        word_dialog.exec()

    def endTurn(self):
        # adding 3 tries for the next turn
        self.tries = 3
        # swapping the players roles
        self.currentGuesser, self.currentSketcher = self.currentSketcher, self.currentGuesser
        #update labels
        self.updateTurnsUi()
        # starting next turn
        self.startNewTurn(self.currentSketcher)

    def startNewTurn(self, player):
        # clearing the board
        self.clear()
        # get a new word
        self.currentWord = self.getWord()
        # show the word popup for the sketcher
        self.showWordPopup(player)
    # method to update the roles
    def updateTurnsUi(self):
        self.sketcher_label.setText(f"Sketcher: {self.currentSketcher}")
        self.sketcher_label.setStyleSheet("font-size:13px; font-weight: bold;")  # Set color for sketcher
        self.guesser_label.setText(f"Guesser: {self.currentGuesser}")
        self.guesser_label.setStyleSheet("font-size:13px; font-weight: bold;")
    # event handlers
    def mousePressEvent(self, event):  # when the mouse is pressed, documentation: https://doc.qt.io/qt-6/qwidget.html#mousePressEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the pressed button is the left button
            self.drawing = True  # enter drawing mode
            self.lastPoint = event.pos()  # save the location of the mouse press as the lastPoint
            print(self.lastPoint)  # print the lastPoint for debugging purposes

    def mouseMoveEvent(self, event):  # when the mouse is moved, documenation: documentation: https://doc.qt.io/qt-6/qwidget.html#mouseMoveEvent
        if self.drawing:
            painter = QPainter(self.image)  # object which allows drawing to take place on an image
            # allows the selection of brush colour, brish size, line type, cap type, join type. Images available here http://doc.qt.io/qt-6/qpen.html
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())  # draw a line from the point of the orginal press to the point to where the mouse was dragged to
            self.lastPoint = event.pos()  # set the last point to refer to the point we have just moved to, this helps when drawing the next line segment
            self.update()  # call the update method of the widget which calls the paintEvent of this class

    def mouseReleaseEvent(self, event):  # when the mouse is released, documentation: https://doc.qt.io/qt-6/qwidget.html#mouseReleaseEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the released button is the left button, documentation: https://doc.qt.io/qt-6/qt.html#MouseButton-enum ,
            self.drawing = False  # exit drawing mode

    # paint events
    def paintEvent(self, event):
        # you should only create and use the QPainter object in this method, it should be a local variable
        canvasPainter = QPainter(self)  # create a new QPainter object, documentation: https://doc.qt.io/qt-6/qpainter.html
        canvasPainter.drawPixmap(QPoint(), self.image)  # draw the image , documentation: https://doc.qt.io/qt-6/qpainter.html#drawImage-1

    # resize event - this function is called
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

    # slots
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if the file path is empty
            return  # do nothing and return
        self.image.save(filePath)  # save file image to the file path

    def clear(self):
        self.image.fill(
            Qt.GlobalColor.white)  # fill the image with white, documentation: https://doc.qt.io/qt-6/qimage.html#fill-2
        self.update()  # call the update method of the widget which calls the paintEvent of this class

    def threepx(self):  # the brush size is set to 3
        self.brushSize = 3

    def fivepx(self):
        self.brushSize = 5

    def sevenpx(self):
        self.brushSize = 7

    def ninepx(self):
        self.brushSize = 9

    def black(self):  # the brush color is set to black
        self.brushColor = Qt.GlobalColor.black
        brushIcon = QPixmap("./icons/paint-brush.png")  # Path to your eraser icon
        customCursor = QCursor(brushIcon.scaled(25, 25), 0, 23)  # Adjust size and hot spot if needed
        self.setCursor(customCursor)

    def red(self):
        self.brushColor = Qt.GlobalColor.red
        brushIcon = QPixmap("./icons/red-brush.png")  # Path to your eraser icon
        customCursor = QCursor(brushIcon.scaled(25, 25), 0, 23)  # Adjust size and hot spot if needed
        self.setCursor(customCursor)

    def green(self):
        self.brushColor = Qt.GlobalColor.green
        brushIcon = QPixmap("./icons/green-brush.png")  # Path to your eraser icon
        customCursor = QCursor(brushIcon.scaled(25, 25), 0, 23)  # Adjust size and hot spot if needed
        self.setCursor(customCursor)

    def yellow(self):
        self.brushColor = Qt.GlobalColor.yellow
        brushIcon = QPixmap("./icons/yellow-brush.png")  # Path to your eraser icon
        customCursor = QCursor(brushIcon.scaled(25, 25), 0, 23)  # Adjust size and hot spot if needed
        self.setCursor(customCursor)
    def erase(self):
        self.brushColor = Qt.GlobalColor.white
        eraserIcon = QPixmap("./icons/eraser.png")  # Path to your eraser icon
        customCursor = QCursor(eraserIcon.scaled(25, 25), 3, 20)  # Adjust size and hot spot if needed
        self.setCursor(customCursor)
    def defaultBrush(self):
        brushIcon = QPixmap("./icons/paint-brush.png")  # Path to your eraser icon
        customCursor = QCursor(brushIcon.scaled(25, 25), 0, 23)  # Adjust size and hot spot if needed
        self.setCursor(customCursor)
    #Get a random word from the list read from file
    def getWord(self):
        if not self.wordList:
            print("Error: Word list is empty!")
            return None
        randomWord = random.choice(self.wordList)
        print(f"Debug: Word chosen from list is '{randomWord}'")
        return randomWord

    #read word list from file
    def getList(self, mode):
        with open(mode + 'mode.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                #print(row)
                self.wordList = row
                line_count += 1
            #print(f'Processed {line_count} lines.')

    # open a file
    def open(self):
        '''
        This is an additional function which is not part of the tutorial. It will allow you to:
         - open a file dialog box,
         - filter the list of files according to file extension
         - set the QImage of your application (self.image) to a scaled version of the file)
         - update the widget
        '''
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if not file is selected exit
            return
        with open(filePath, 'rb') as f:  # open the file in binary mode for reading
            content = f.read()  # read the file
        self.image.loadFromData(content)  # load the data into the file
        width = self.width()  # get the width of the current QImage in your application
        height = self.height()  # get the height of the current QImage in your application
        self.image = self.image.scaled(width, height)  # scale the image from file and put it in your QImage
        self.update()  # call the update method of the widget which calls the paintEvent of this class


# this code will be executed if it is the main module but not if the module is imported
#  https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # adding style
    app.setStyleSheet("""
            QDialog {
            background-color: #ebebeb;  /* Light gray background */
            }
            QLabel, QComboBox {
                color: #333333;  /* Dark gray text */
                font-size: 12px;
                font-family: Arial;
                font-weight: bold;
            }
            QMenuBar {
                color: black;  /* White text color */
            }
            QMenuBar::item:selected {
                background-color: #444444;  /* Darker gray on hover */
            }
            QPushButton {
                background-color: #3079b5;  
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #07477e;  /* Darker green on hover */
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;  /* White input backgrounds */
                border-bottom: 1px solid black;
                height : 25px;
                width : 100px;
                border-radius: 5px;
            }
            QComboBox:hover {
                border-bottom:0;
            } 
            QComboBox::drop-down {
                border: none; 
            }
        """)
    window = PictionaryGame()
    window.show()
    app.exec()  # start the event loop running
