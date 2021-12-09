from tkinter import *
from tkinter import ttk
import tkinter as tk
import os
import time
from time import sleep
import serial
from threading import Timer
from apscheduler.schedulers.background import BackgroundScheduler

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((200, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

def updateCom(serialLetter):
    global repeatIntervalInt
    repeatIntervalInt = int(repeatIntervalSend.get())
    port = portSend.get()
    par = serial.PARITY_NONE
    speed = speedSend.get()
    if (paritySend.get().upper() == "ODD"):
        par = serial.PARITY_ODD
    if (paritySend.get().upper() == "EVEN"):
        par = serial.PARITY_EVEN
    if (paritySend.get().upper() == "MARK"):
        par = serial.PARITY_MARK
    if (paritySend.get().upper() == "SPACE"):
        par = serial.PARITY_SPACE
    stop = serial.STOPBITS_ONE
    #if (firstStop_send.get().upper() == "ONE 5"):
    #    ???
    if (stopSend.get().upper() == "TWO" or stopSend.get() == 2):
        stop = serial.STOPBITS_TWO
    data = serial.EIGHTBITS
    if (dataSend.get().upper() == "FIVE" or dataSend.get() == 5):
        data = serial.FIVEBITS
    if (dataSend.get().upper() == "SIX" or dataSend.get() == 6):
        data = serial.SIXBITS
    if (dataSend.get().upper() == "SEVEN" or dataSend.get() == 7):
        data = serial.SEVENBITS
    configureScreen.destroy()
    try:
        serialLetter = serial.Serial(
        	port= "COM" + port,
        	baudrate=int(speed),
        	parity= par,
        	stopbits= stop,
        	bytesize= data
        )
    except:
        print("Invalid Parameters")
    try:
        serialLetter.open()
        serialLetter.isOpen()
    except:
        return

def configureSerial(serialLetter):
    global configureScreen
    configureScreen = Toplevel(mainScreen)
    configureScreen.title("Configure COM")
    configureScreen.geometry("300x500")
    Label(configureScreen, text = "Configure the COM").pack()
    portSettings = Frame(configureScreen)
    portSettings.pack()

    global portSend
    global portEntry
    portSend = StringVar()
    portEntry = StringVar()
    Label(portSettings, text = "Port: ").pack()
    portEntry = Entry(portSettings, textvariable = portSend)
    portSend.set("")
    try:
        portEntry.insert(END, serialLetter.port)
    except:
        portEntry.insert(END, 3)
    portEntry.pack()

    global speedSend
    global speedEntry
    speedSend = StringVar()
    speedEntry = StringVar()
    Label(portSettings, text = "Speed: ").pack()
    speedEntry = Entry(portSettings, textvariable = speedSend)
    speedSend.set("")
    try:
        speedEntry.insert(END, serialLetter.baudrate)
    except:
        speedEntry.insert(END, 9600)
    speedEntry.pack()

    global dataSend
    global dataEntry
    dataSend = StringVar()
    dataEntry = StringVar()
    Label(portSettings, text = "Data bits: ").pack()
    dataEntry = Entry(portSettings, textvariable = dataSend)
    dataSend.set("")
    try:
        dataEntry.insert(END, serialLetter.bytesize)
    except:
        dataEntry.insert(END, "Eight")
    dataEntry.pack()

    global stopSend
    global stopEntry
    stopSend = StringVar()
    stopEntry = StringVar()
    Label(portSettings, text = "Stop bits: ").pack()
    stopEntry = Entry(portSettings, textvariable = stopSend)
    stopSend.set("")
    try:
        stopEntry.insert(END, serialLetter.stopbits)
    except:
        stopEntry.insert(END, "One")
    stopEntry.pack()

    """
    global flowSend
    global flowEntry
    flowSend = StringVar()
    flowEntry = StringVar()
    Label(portSettings, text = "Flow control: ").pack()
    flowEntry = Entry(portSettings, textvariable = flowSend)
    flowSend.set("")

    try:
        return
    except:
        firstFlow_entry.insert(END, "None")

    firstFlow_entry.pack()
    """

    global paritySend
    global parityEntry
    paritySend = StringVar()
    parityEntry = StringVar()
    Label(portSettings, text = "Parity bits: ").pack()
    parityEntry = Entry(portSettings, textvariable = paritySend)
    paritySend.set("")
    try:
        parityEntry.insert(END, serialLetter.parity)
    except:
        parityEntry.insert(END, "None")
    parityEntry.pack()

    global repeatIntervalSend
    global repeatIntervalEntry
    repeatIntervalEntry = StringVar()
    repeatIntervalSend = StringVar()
    Label(portSettings, text = "Repeat Interval (in seconds): ").pack()
    repeatIntervalEntry = Entry(portSettings, textvariable = repeatIntervalSend)
    repeatIntervalEntry.insert(END, repeatIntervalInt)
    repeatIntervalEntry.pack()

    Label(portSettings, text = "").pack()
    Button(portSettings, text = "OK", width = 30, height = 1, command=lambda : updateCom(serialLetter)).pack()

def writeOutput(output, theFrame):
    charInLine = 20
    parts = int(len(output) / charInLine)
    for i in range(0, parts):
        print(parts)
        Label(theFrame, text = ">>" + output[(i*charInLine):(i*charInLine + charInLine)], width = 20).pack(side = BOTTOM)

def sendCommand(command, output, serialLetter):
    if (repeatStatusA == "OFF" and schedA.running):
        schedA.shutdown()
    if (repeatStatusB == "OFF" and schedB.running):
        schedB.shutdown()
    if (repeatStatusC == "OFF" and schedC.running):
        schedC.shutdown()

    ttk.Label(output.scrollable_frame, text = "Command: " + command + "_A", width = 20).pack(side = TOP)
    serialLetter.write(command + "_A" + '\r\n')
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while serialLetter.inWaiting() > 0:
        out += serialLetter.read(1)
    if out != '':
        writeOutput(command, output.scrollable_frame)

def sendToAll():
    global schedA
    global schedB
    global schedC
    schedA = BackgroundScheduler()
    schedB = BackgroundScheduler()
    schedC = BackgroundScheduler()

    command = commandSend.get()
    commandSend.set("")
    ttk.Label(outputA.scrollable_frame, text = "Command: " + command + "_A", width = 20).pack(side = TOP)
    ttk.Label(outputB.scrollable_frame, text = "Command: " + command + "_B", width = 20).pack(side = TOP)
    ttk.Label(outputC.scrollable_frame, text = "Command: " + command + "_C", width = 20).pack(side = TOP)

    if(repeatStatusA == "ON"):
        #sendRepeat(2, command, outputA)
        schedA.add_job(lambda: sendCommand(command, outputA, serialA), 'interval', seconds = repeatIntervalInt)
        schedA.start()
    if(repeatStatusB == "ON"):
        #sendRepeat(2, command, outputB)
        schedB.add_job(lambda: sendCommand(command, outputB, serialB), 'interval', seconds = repeatIntervalInt)
        schedB.start()
    if(repeatStatusC == "ON"):
        #sendRepeat(2, command, outputC)
        schedC.add_job(lambda: sendCommand(command, outputC, serialC), 'interval', seconds = repeatIntervalInt)
        schedC.start()

    serialA.write(command + "_A" + '\r\n')
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while serialA.inWaiting() > 0:
        out += serialA.read(1)
    if out != '':
        writeOutput(out, outputA.scrollable_frame)

    serialB.write(command + "_B" + '\r\n')
    out = ''
    time.sleep(1)
    while serialB.inWaiting() > 0:
        out += serialB.read(1)
    if out != '':
        writeOutput(out, outputB.scrollable_frame)

    serialC.write(command + "_C" + '\r\n')
    out = ''
    time.sleep(1)
    while serialC.inWaiting() > 0:
        out += serialC.read(1)
    if out != '':
        writeOutput(out, outputC.scrollable_frame)

def sendToA():
    global schedA
    global schedB
    global schedC
    schedA = BackgroundScheduler()
    schedB = BackgroundScheduler()
    schedC = BackgroundScheduler()

    command = commandSend.get()
    commandSend.set("")
    ttk.Label(outputA.scrollable_frame, text = "Command: " + command + "_A", width = 20).pack(side = TOP)

    if(repeatStatusA == "ON"):
        #sendRepeat(2, command, outputA)
        schedA.add_job(lambda: sendCommand(command, outputA, serialA), 'interval', seconds = repeatIntervalInt)
        schedA.start()

    serialA.write(command + "_A" + '\r\n')
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while serialA.inWaiting() > 0:
        out += serialA.read(1)
    if out != '':
        writeOutput(out, outputA.scrollable_frame)

def sendToB():
    global schedA
    global schedB
    global schedC
    schedA = BackgroundScheduler()
    schedB = BackgroundScheduler()
    schedC = BackgroundScheduler()

    command = commandSend.get()
    commandSend.set("")
    ttk.Label(outputB.scrollable_frame, text = "Command: " + command + "_B", width = 20).pack(side = TOP)

    if(repeatStatusB == "ON"):
        #sendRepeat(2, command, outputA)
        schedB.add_job(lambda: sendCommand(command, outputB, serialB), 'interval', seconds = repeatIntervalInt)
        schedB.start()

    serialB.write(command + "_B" + '\r\n')
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while serialB.inWaiting() > 0:
        out += serialB.read(1)
    if out != '':
        writeOutput(out, outputB.scrollable_frame)

def sendToC():
    global schedA
    global schedB
    global schedC
    schedA = BackgroundScheduler()
    schedB = BackgroundScheduler()
    schedC = BackgroundScheduler()


    command = commandSend.get()
    commandSend.set("")
    ttk.Label(outputC.scrollable_frame, text = "Command: " + command + "_C", width = 20).pack(side = TOP)

    if(repeatStatusC == "ON"):
        #sendRepeat(2, command, outputA)
        schedC.add_job(lambda: sendCommand(command, outputC, serialC), 'interval', seconds = repeatIntervalInt)
        schedC.start()

    serialC.write(command + "_C" + '\r\n')
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while serialC.inWaiting() > 0:
        out += serialC.read(1)
    if out != '':
        writeOutput(out, outputC.scrollable_frame)

def actuallyChangeRepeatStatus(repeatStatus, outputLetter):
    global repeatStatusA
    global repeatStatusB
    global repeatStatusC
    if (outputLetter == 'A'):
        repeatStatusA = repeatStatus
    if (outputLetter == 'B'):
        repeatStatusB = repeatStatus
    if (outputLetter == 'C'):
        repeatStatusC = repeatStatus

def repeatChange(repeatStatus, repeatButton, frame, outputLetter):
    if (repeatStatus == "ON"):
        repeatStatus = "OFF"
    else:
        repeatStatus = "ON"
    actuallyChangeRepeatStatus(repeatStatus, outputLetter)
    repeatButton.destroy()
    repeatButton = Button(frame, text = "Repeat: " + repeatStatus, command=lambda : repeatChange(repeatStatus, repeatButton, frame, outputLetter), width = 10)
    repeatButton.pack(side = TOP)

def outputSetup():
    global serialA
    global serialB
    global serialC
    serialA = serial.Serial()
    serialB = serial.Serial()
    serialC = serial.Serial()

    global outputA
    global outputB
    global outputC
    global repeatStatusA
    global repeatStatusB
    global repeatStatusC
    repeatStatusA = "OFF"
    repeatStatusB = "OFF"
    repeatStatusC = "OFF"

    repeatButtonA = Button(frameA, text = "Repeat: " + repeatStatusA, command=lambda : repeatChange(repeatStatusA, repeatButtonA, frameA, 'A'), width = 10)
    repeatButtonA.pack(side = TOP)
    outputA = ScrollableFrame(frameA)
    outputA.pack(side = BOTTOM)
    Button(frameA, text = "Configure", width = 20, command=lambda : configureSerial(serialA)).pack(side=BOTTOM)

    repeatButtonB = Button(frameB, text = "Repeat: " + repeatStatusB, command=lambda : repeatChange(repeatStatusB, repeatButtonB, frameB, 'B'), width = 10)
    repeatButtonB.pack(side = TOP)
    outputB = ScrollableFrame(frameB)
    outputB.pack(side = BOTTOM)
    Button(frameB, text = "Configure", width = 20, command=lambda : configureSerial(serialB)).pack(side=BOTTOM)

    repeatButtonC = Button(frameC, text = "Repeat: " + repeatStatusC, command=lambda : repeatChange(repeatStatusC, repeatButtonC, frameC, 'C'), width = 10)
    repeatButtonC.pack(side = TOP)
    outputC = ScrollableFrame(frameC)
    outputC.pack(side = BOTTOM)
    Button(frameC, text = "Configure", width = 20, command=lambda : configureSerial(serialC)).pack(side=BOTTOM)

def mainScreen():
    global mainScreen
    mainScreen = Tk()
    mainScreen.geometry("1000x600")
    mainScreen.title("Schneider 1.0")
    Label(text = "Schneider 1.0", bg = "grey", width = "600", height = "2", font = ("Calibri", 13)).pack()
    Label(text = "").pack()

    global commandSend
    global commandEntry
    commandSend = StringVar()
    commandEntry = StringVar()
    Label(mainScreen, text = "Command").pack()
    commandEntry = Entry(mainScreen, textvariable = commandSend)
    commandEntry.pack()
    Label(text = "").pack()
    Button(mainScreen, text="Send to All", width = 10, height = 1, command = sendToAll).pack()

    frameThatHoldsSendButtons = Frame(mainScreen)
    frameThatHoldsSendButtons.pack()
    Button(frameThatHoldsSendButtons, text="Send to A", width = 10, height = 1, command = sendToA).pack(side = LEFT)
    Button(frameThatHoldsSendButtons, text="Send to B", width = 10, height = 1, command = sendToB).pack(side = LEFT)
    Button(frameThatHoldsSendButtons, text="Send to C", width = 10, height = 1, command = sendToC).pack(side = LEFT)

    global frameA
    global frameB
    global frameC

    frameA = Frame(mainScreen)
    frameB = Frame(mainScreen)
    frameC = Frame(mainScreen)
    frameA.pack(side = LEFT)
    frameB.pack(side = LEFT)
    frameC.pack(side = LEFT)

    outputSetup()
    mainScreen.mainloop()

global repeatIntervalInt
repeatIntervalInt = 1
mainScreen()
