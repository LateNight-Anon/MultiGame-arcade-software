from threading import Thread as thread
from tkinter import Tk, Button, Label, Entry, Text, messagebox
from time import sleep, time
from matplotlib.pyplot import plot, xlabel, ylabel, show, title
from random import randrange, choice
from typing import List, Dict, Tuple
from csv import reader
from hashlib import sha3_384
from os import stat as fileProps, environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #stops the pygame welcome message from printing
from pygame import mixer

class isFloatError(Exception): pass
class outOfRangeError(Exception): pass
class correctPassword(Exception): pass

playSound = lambda sound: [mixer.music.load(sound), mixer.music.play()]

def fatalErrorHandle(errorID: str) -> None:
    messagebox.showinfo(title = "fatal error", message = "fatal error detected\ncontact admins with error code\nerrorCode: " + errorID)
    exit()

def encryptNumber(number: str | float) -> str:
    number = str(number)
    randomValue: int = randrange(45, 75)
    endResult: str = str(randomValue)
    for item in number: endResult += chr(int(item) + randomValue)
    return endResult
    
def decryptNumber(number: str) -> float:
    endResult: str = ""
    randomValue: int = int(number[0] + number[1])
    number = number[2:]
    for item in number: endResult += str(ord(item) - randomValue)
    return float(endResult)

def addToFile(fileName: str, value: int) -> None:
    try:
        with open(fileName, 'a') as file:
            if fileProps(fileName).st_size: file.write(", " + encryptNumber(round(value)))
            else: file.write(encryptNumber(round(value)))
    except FileNotFoundError: fatalErrorHandle("001")

def createErrorMessage(window: Tk, txt: str, X: int, Y: int, fontSize: int) -> None:
    errorLabel = Label(window, text = txt, font = ("Arial", fontSize), fg = "red")
    errorLabel.place(x = X, y = Y)
    [sleep(1.5), errorLabel.destroy()]

def createLoginScreen() -> None:
    clearFile = lambda fileName: open(fileName, 'w').close()

    def graphData(fileName: str, graphTitle: str) -> None:
        try:
            with open(fileName, 'r') as file:
                if fileProps(fileName).st_size: 
                    plot([decryptNumber(item) for item in next(reader(file))])
                else: print("fileSize = " + str(fileProps(fileName).st_size))
                [title(graphTitle), ylabel("value"), xlabel("iteration"), show()]
        except FileNotFoundError: fatalErrorHandle("002")
        except ValueError: fatalErrorHandle("003")

    def callGraphDataForAllFiles() -> None:
        for data in (("mathGameResults.csv", "math game results"), ("clickGameResults.csv", "click game results"), ("reactionGameResults.csv", "reaction game results")):
            graphData(data[0], data[1])

    def clearAllFile() -> None:
        for fileName in ("mathGameResults.csv", "clickGameResults.csv", "reactionGameResults.csv"): clearFile(fileName)

    def signIn(userInput: str) -> None:
        inputHash = sha3_384()
        inputHash.update(userInput.encode('utf-8') * 2)
        inputHash = inputHash.hexdigest()
        try:
            with open("passwords.csv", 'r') as file:
                for password in next(reader(file)):
                    if password == inputHash: raise correctPassword()
            return thread(target = createErrorMessage, args = (loginScreen, "incorrect password", 50, 400, 35)).start()
        except FileNotFoundError: fatalErrorHandle("004")
        except correctPassword:
            loginScreen.geometry("300x500")
            titleLabel.configure(text = "admin panel", font = ("Arial", 35))
            [passwordLabel.destroy(), passwordEntry.destroy(), submitButton.destroy()]
            Button(loginScreen, text = "graph scores", font = ("Arial", 15), bg = "light green", relief = "solid", borderwidth = 3, command = callGraphDataForAllFiles).pack(pady = 15)
            Button(loginScreen, text = "clear all files", font = ("Arial", 15), bg = "red", relief = "solid", borderwidth = 3, command = clearAllFile).pack(pady = 20)
            Button(loginScreen, text = "clear math file", font = ("Arial", 15), bg = "orange", relief = "solid", borderwidth = 3, command = lambda: clearFile("mathGameResults.csv")).pack(pady = 20)
            Button(loginScreen, text = "clear click file", font = ("Arial", 15), bg = "orange", relief = "solid", borderwidth = 3, command = lambda: clearFile("clickGameResults.csv")).pack(pady = 20)
            Button(loginScreen, text = "clear reaction file", font = ("Arial", 15), bg = "orange", relief = "solid", borderwidth = 3, command = lambda: clearFile("reactionGameResults.csv")).pack(pady = 20)

    loginScreen = Tk()
    loginScreen.title("login as an admin")
    loginScreen.geometry("500x500")
    loginScreen.resizable(width = False, height = False)
    titleLabel = Label(loginScreen, text = "Data admin login", font = ("Arial", 25), bg = "white", borderwidth = 4, relief = "solid")
    titleLabel.pack(pady = 10)
    passwordLabel = Label(loginScreen, text = "password:", font = ("Arial", 15))
    passwordLabel.pack(pady = 30)
    passwordEntry = Entry(loginScreen, width = 28, borderwidth = 3, relief = "solid", show = '⚫', bg = "white", font = ("Arial", 15))
    passwordEntry.pack(pady = 2)
    submitButton = Button(loginScreen, text = "sign in", borderwidth = 4, relief = "solid", bg = "white", font = ("Arial", 20), command = lambda: signIn(passwordEntry.get()))
    submitButton.pack(pady = 30)

    loginScreen.mainloop()

def mathGame() -> None:
    def submitDifficulty(entryInput: str | int) -> None:
        def minMaxAssignment(minV: int, maxV: int) -> None:
            global minVal, maxVal
            minVal = minV
            maxVal = maxV

        def mathGameMain() -> None:
            global points, timeLeft, sumStr
            points = 0 #int
            timeLeft = 10 #int

            generateSum = lambda: str(randrange(minVal, maxVal)) + ' ' + choice(symbols) + ' ' + str(randrange(minVal, maxVal))
            sumStr = generateSum()

            def submitAns(ans: str) -> None:
                global points, sumStr
                try:
                    if float(ans) == eval(sumStr): points += 1
                    else: raise ValueError()
                except ValueError: thread(target = createErrorMessage, args = (mathApp, "WRONG!!", 155, 300, 25)).start()
                finally: 
                    sumStr = generateSum()
                    sumLabel.configure(text = sumStr)

            def timer() -> None:
                global timeLeft, points
                for i in range(timeLeft):
                    sleep(1)
                    timeLeft -= 1
                    timerLabel.configure(text = str(timeLeft))
                timerLabel.destroy()
                mathEntry.destroy()
                submitSum.destroy()
                sumLabel.destroy()   
                title.configure(text = "game over")
                pointLabel = Label(mathApp, text = points, font = ("Arial", 75))
                pointLabel.place(x = 210, y = 110)
                addToFile("mathGameResults.csv", points)

            timerLabel = Label(mathApp, text = timeLeft, font = ("Arial", 25))
            timerLabel.place(x = 220, y = 50)
            mathEntry = Entry(mathApp, font = ("Arial", 25), width = 5, relief = "solid", borderwidth = 2)
            mathEntry.place(x = 120 , y = 100)
            submitSum = Button(mathApp, text = "submit", font = ("Arial", 25), borderwidth = 2, relief = "solid", bg = "white", command = lambda: submitAns(mathEntry.get()))
            submitSum.place(x = 235, y = 90)
            sumLabel = Label(mathApp, text = sumStr, font = ("Arial", 25))
            sumLabel.place(x = 195, y = 190)
            thread(target = timer).start()

        def defineSymbolsAndAssign(minimum: int, maximum: int, *symbols) -> Tuple[chr]:
            minMaxAssignment(minimum, maximum)
            return [symbol for symbol in symbols]

        try:
            floatCheck = float(entryInput)
            convertedVal = int(entryInput)
            if floatCheck != convertedVal: raise isFloatError()
            elif convertedVal < 1 or convertedVal > 4: raise outOfRangeError()
        except ValueError: thread(target = createErrorMessage, args = (mathApp, "input is not a number", 20, 450, 25)).start()
        except isFloatError: thread(target = createErrorMessage, args = (mathApp, "input is not an integer", 20, 450, 25)).start()
        except outOfRangeError: thread(target = createErrorMessage, args = (mathApp, "input is not between 1 and 10", 20, 450, 25)).start()
        else:
            diffLabel.destroy()
            submitButton.destroy()
            difficulty.destroy()
            title.configure(text = "gaming sauce")
            global minVal, maxVal
            match convertedVal:
                case 1: symbols: Tuple[chr] = tuple(defineSymbolsAndAssign(1, 10, '+', '-'))
                case 2: symbols: Tuple[chr] = tuple(defineSymbolsAndAssign(1, 35, '+', '-'))
                case 3: symbols: Tuple[chr] = tuple(defineSymbolsAndAssign(2, 45, '+', '-', '*'))
                case 4: symbols: Tuple[chr] = tuple(defineSymbolsAndAssign(3, 999, '+', '-', '*', '/'))
            mathGameMain()

    mathApp = Tk()
    mathApp.title("math game")
    mathApp.resizable(width = False, height = False)
    mathApp.geometry("500x500")
    title = Label(mathApp, text = "select your difficulty", font = ("Arial", 25))
    title.pack()
    difficulty = Entry(mathApp, font = ("Arial", 25), relief = "solid", borderwidth = 2, bg = "white", width = 3)
    difficulty.place(x = 160, y = 70)
    submitButton = Button(mathApp, text = "submit", font = ("Arial", 25), relief = "solid", borderwidth = 2, bg = "white", command = lambda: thread(target = submitDifficulty, args = (difficulty.get(),)).start())
    submitButton.place(x = 250, y = 60)
    diffLabel = Label(mathApp, text = "enter difficulty: ", font = ("Arial", 10))
    diffLabel.place(x = 50, y = 80)

    mathApp.mainloop()

def clickReaction() -> None:
    global canPlayerPress, startTime, gameIsRunning, displayedTime
    canPlayerPress = False
    startTime = None
    gameIsRunning = True
    displayedTime = 0.0
    def clickReactionMain() -> None:
        def placeTimer(dispTime) -> None:
            pass

        def buttonPressed() -> None:
            global canPlayerPress, gameIsRunning, displayedTime
            if canPlayerPress:
                canPlayerPress = False
                gameIsRunning = False
                titleLabel.configure(text = "well done!", bg = "white")
                clickApp.configure(bg = "white")
                winButton.configure(text = "wow!", bg = "light grey")
                winButton.place(x = 110, y = 205)
                addToFile("reactionGameResults.csv", displayedTime)

        def increaseTimer() -> None:
            global gameIsRunning, displayedTime
            while gameIsRunning:
                sleep(0.01)
                displayedTime = round(displayedTime + 0.01, 2)
                timeLabel.configure(text = displayedTime)

        def switchCols() -> None:
            global canPlayerPress, startTime
            sleep(randrange(4,12))
            clickApp.configure(bg = "light green")
            winButton.configure(text = "CLICK ME!!!!", bg = "red")
            winButton.place(x = 50, y = 205)
            titleLabel.configure(bg = "light green")
            startTime = time()
            canPlayerPress = True
            thread(target = increaseTimer).start()

        startButton.destroy()
        titleLabel.configure(text = "wait until the bg and button change color!", font = ("Arial", 18), bg = "red")
        clickApp.configure(bg = "red")
        winButton = Button(clickApp, text = "DONT CLICK", font = ("Arial", 45), bg = "light green", command = buttonPressed)
        winButton.place(x = 40, y = 205)
        timeLabel = Label(clickApp, text = displayedTime, font = ("Arial", 45))
        timeLabel.place(x = 160, y = 100)
        thread(target = switchCols).start()

    clickApp = Tk()
    clickApp.title("reaction test")
    clickApp.resizable(width = False, height = False)
    clickApp.geometry("500x500")
    titleLabel = Label(clickApp, text = "reaction test", font = ("Arial", 25))
    titleLabel.pack()
    startButton = Button(clickApp, text = "begin", bg = "white", relief = "solid", borderwidth = 2, font = ("Arial", 25), command = clickReactionMain)
    startButton.place(x = 190, y = 65)

    clickApp.mainloop()
    gameIsRunning = False

def CPSGame() -> None:
    def CPSmain() -> None:
        global clicks #int
        clicks = 0
        def timer() -> None:
            time: int = 20
            timerLabel = Label(CPSApp, text = time, font = ("Arial", 25))
            timerLabel.pack(pady = 20)
            for _ in range(20):
                time -= 1
                sleep(1)
                timerLabel.configure(text = time)
            [mainButton.destroy(), timerLabel.destroy()]
            Label(CPSApp, text = "clicks per second = " + str(clicks / 20), font = ("Arial", 25)).pack(pady = 40)
            addToFile("clickGameResults.csv", clicks / 20)

        def increaseClicks() -> None:
            global clicks
            clicks += 1

        def countDown() -> None:
            for i in range(3):
                timeLabel.configure(text = 3 - i)
                sleep(1)
            timeLabel.destroy()
            global mainButton
            mainButton = Button(CPSApp, text = "click me!", font = ("Arial", 25), bg = "grey", borderwidth = 3, relief = "solid", command = increaseClicks)
            [mainButton.pack(), thread(target = timer).start()]

        timeLabel = Label(CPSApp, text = "3", font = ("Arial", 25))
        [timeLabel.pack(), startButton.destroy()]
        thread(target = countDown).start()

    CPSApp = Tk()
    CPSApp.title("clicks per second")
    CPSApp.resizable(width = False, height = False)
    CPSApp.geometry("500x500")
    Label(CPSApp, text = "clicks per second", font = ("Arial", 25)).pack()
    startButton = Button(CPSApp, text = "start", font = ("Arial", 25), borderwidth = 3, relief = "solid", command = CPSmain)
    startButton.place(x = 200, y = 120)

    CPSApp.mainloop()

def timer() -> None:
    def incrament() -> None:
        global count
        while isAppOpen:
            sleep(1)
            if isRunning:
                count += 1
                countLabel.configure(text = count)

    def reset() -> None:
        global count
        count = 0
        countLabel.configure(text = count)

    def startAndStop(boolVar: bool) -> None:
        global isRunning
        isRunning = boolVar

    def load() -> None:
        global count
        with open("timerSave.csv", 'r') as file:
            try:
                count = int(file.readline())
                countLabel.configure(text = count)
            except Exception:
                thread(target = createErrorMessage).start()
                exit()

    def save() -> None: 
        with open("timerSave.csv", 'w') as file: 
            if fileProps("timerSave.csv").st_size: file.write(", " + str(count))
            else: file.write(str(count))

    isAppOpen: bool = True
    count: int = 0
    isRunning: bool = False
    thread(target = incrament).start()

    timeApp = Tk()
    timeApp.title("counter")
    timeApp.resizable(width = False, height = False)
    timeApp.geometry("250x350")
    timeApp.configure(bg = "light grey")
    Label(timeApp, text = "counter", bg = "light grey", font = ("Arial", 35)).place(x = 40, y = 10)
    countLabel = Label(timeApp, text = count, bg = "light grey", font = ("Arial", 35))
    countLabel.place(x=105, y=70)
    Button(timeApp, text = "start", font = ("Arial", 15), borderwidth = 2, relief = "solid", command = lambda: startAndStop(True)).place(x=20,y=200)
    Button(timeApp, text = "pause", font = ("Arial", 15), borderwidth = 2, relief = "solid", command = lambda: startAndStop(False)).place(x=90,y=200)
    Button(timeApp, text = "reset", font = ("Arial", 15), borderwidth = 2, relief = "solid", command = reset).place(x=170,y=200)
    Button(timeApp, text = "save", font = ("Arial", 15), borderwidth = 2, relief = "solid", command = save).place(x=50,y=250)
    Button(timeApp, text = "load", font = ("Arial", 15), borderwidth = 2, relief = "solid", command = load).place(x=135,y=250)

    timeApp.mainloop()
    isAppOpen = False

mixer.init()

app = Tk()
app.title("main menu")
app.geometry("500x500")
app.resizable(width = False, height = False)
Label(text = "select your challenge", font = ("Arial", 25)).place(x = 95, y = 20)
Button(text = "maths", font = ("Arial", 25), bg = "red", borderwidth = 3, relief = "solid", command = mathGame).place(x = 40, y = 100)
Button(text = "reaction", font = ("Arial", 25), bg = "green", borderwidth = 3, relief = "solid", command = clickReaction).place(x = 180, y = 100)
Button(text = "clicks", font = ("Arial", 25), bg = "blue", borderwidth = 3, relief = "solid", command = CPSGame).place(x = 340, y = 100)
Button(text = "counter", font = ("Arial", 25), bg = "yellow", borderwidth = 3, relief = "solid", command = timer).place(x = 180, y = 185)
Button(text = "login as admin", font = ("Arial", 25), bg = "grey78", borderwidth = 5, relief = "solid", command = createLoginScreen).place(x = 130, y = 340)

app.mainloop()
