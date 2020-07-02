from tkinter import *
from tkinter import ttk
import tkinter as tk
import os
import time
import serial

def writeOutput(output):
    charInLine = 20
    parts = int(output / 20)
    for i in range(parts):
        Label(firstOutput.scrollable_frame, text = ">>" + out[(i*charInLine):(i*(charinLine + 1))], width = 20).pack(side = BOTTOM)

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

def outputSetup():
    global firstOutput
    firstOutput = ScrollableFrame(frame4)
    firstOutput.pack(side = LEFT)

    global secondOutput
    secondOutput = ScrollableFrame(frame4)
    secondOutput.pack(side = LEFT)

    global thirdOutput
    thirdOutput = ScrollableFrame(frame4)
    thirdOutput.pack(side = LEFT)

def comportDisplayLabels():
    Label(frame2, text = "ComPort1: " + comPort1, width = 20).pack(side = LEFT)
    Label(frame2, text = "ComPort2: " + comPort2, width = 20).pack(side = LEFT)
    Label(frame2, text = "ComPort3: " + comPort3, width = 20).pack(side = LEFT)

def updateComPort1():
    global ser1
    global comPort1
    for widget in frame2.winfo_children():
        widget.destroy()
    comPort1 = comPort1_send.get()
    comPort1_entry.delete(0, END)
    comportDisplayLabels()
    ser1 = serial.Serial(
    	port="COM" + comPort1,
    	baudrate=9600,
    	parity=serial.PARITY_NONE,
    	stopbits=serial.STOPBITS_ONE,
    	bytesize=serial.EIGHTBITS
    )
    ser1.open()
    ser1.isOpen()

def updateComPort2():
    global comPort2
    global ser2
    for widget in frame2.winfo_children():
        widget.destroy()
    comPort2 = comPort2_send.get()
    comPort2_entry.delete(0, END)
    comportDisplayLabels()
    ser2 = serial.Serial(
    	port="COM" + comPort2,
    	baudrate=9600,
    	parity=serial.PARITY_NONE,
    	stopbits=serial.STOPBITS_ONE,
    	bytesize=serial.EIGHTBITS
    )
    ser2.open()
    ser2.isOpen()

def updateComPort3():
    global comPort3
    global ser3
    for widget in frame2.winfo_children():
        widget.destroy()
    comPort3 = comPort3_send.get()
    comPort3_entry.delete(0, END)
    comportDisplayLabels()
    ser3 = serial.Serial(
    	port="COM" + comPort3,
    	baudrate=9600,
    	parity=serial.PARITY_NONE,
    	stopbits=serial.STOPBITS_ONE,
    	bytesize=serial.EIGHTBITS,
    )
    ser3.open()
    ser3.isOpen()

def send_to_all():
    for widget in frame.winfo_children():
        widget.destroy()
    frame.pack_forget()
    frame.pack()
    command = command_send.get()
    command_entry.delete(0, END)

    #labelA = Label(frame, text = command + "_A", width = 20)
    #labelA.pack( side = LEFT)

    #labelB = Label(frame, text = command + "_B", width = 20)
    #labelB.pack( side = LEFT )

    #labelC = Label(frame, text = command + "_C", width = 20)
    #labelC.pack( side = LEFT )

    #We're just gonna have the command be given in the scrolalble frame instead of its own label

    ttk.Label(firstOutput.scrollable_frame, text = "Command: " + command + "_A", width = 20).pack(side = TOP)
    ttk.Label(secondOutput.scrollable_frame, text = "Command: " + command + "_B", width = 20).pack(side = TOP)
    ttk.Label(thirdOutput.scrollable_frame, text = "Command: " + command + "_C", width = 20).pack(side = TOP)

    ser1.write(command + "_A" + '\r\n')
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while ser1.inWaiting() > 0:
        out += ser1.read(1)
    if out != '':
        writeOutput(out)
        Label(firstOutput.scrollable_frame, text = ">>" + out, width = 20).pack(side = BOTTOM)

    ser2.write(command + "_B" + '\r\n')
    out = ''
    time.sleep(1)
    while ser2.inWaiting() > 0:
        out += ser2.read(1)
    if out != '':
        Label(secondOutput.scrollable_frame, text = ">>" + out, width = 20).pack(side = BOTTOM)

    ser3.write(command + "_C" + '\r\n')
    out = ''
    time.sleep(1)
    while ser3.inWaiting() > 0:
        out += ser3.read(1)
    if out != '':
        Label(thirdOutput.scrollable_frame, text = ">>" + out, width = 20).pack(side = BOTTOM)

def main_screen():
    global first
    global screen
    screen = Tk()
    screen.geometry("600x500")
    screen.title("Schneider 1.0")
    Label(text = "Schneider 1.0", bg = "grey", width = "600", height = "2", font = ("Calibri", 13)).pack()
    Label(text = "").pack()

    global command_send
    global command_entry
    command_send = StringVar()
    command_entry = StringVar()
    Label(screen, text = "Command").pack()
    command_entry = Entry(screen, textvariable = command_send)
    command_entry.pack()
    Label(text = "").pack()

    #Command Button
    Button(screen, text="Send to All", width = 10, height = 1, command = send_to_all).pack()
    Label(text = "").pack()

    global frame
    global frame1
    global frame2
    global frame3
    global frame4
    frame = Frame(screen)
    frame.pack()
    frame1 = Frame(screen)
    frame1.pack()
    frame2 = Frame(screen)
    frame2.pack()
    frame3 = Frame(screen)
    frame3.pack()
    frame4 = Frame(screen)
    frame4.pack()

    firstLabel = Label(frame, text = "Awaiting Command")
    firstLabel.pack()

    global comPort1_send
    global comPort1_entry
    comPort1_send = StringVar()
    comPort1_entry = StringVar()
    Label(frame2, text = "ComPort1: " + comPort1, width = 20).pack(side = LEFT)
    comPort1_entry = Entry(frame1, textvariable = comPort1_send)
    comPort1_entry.pack(side = LEFT)

    global comPort2_send
    global comPort2_entry
    comPort2_send = StringVar()
    comPort2_entry = StringVar()
    Label(frame2, text = "ComPort2: " + comPort2, width = 20).pack(side = LEFT)
    comPort2_entry = Entry(frame1, textvariable = comPort2_send)
    comPort2_entry.pack(side = LEFT)

    global comPort3_send
    global comPort3_entry
    comPort3_send = StringVar()
    comPort3_entry = StringVar()
    Label(frame2, text = "ComPort3: " + comPort3, width = 20).pack(side = LEFT)
    comPort3_entry = Entry(frame1, textvariable = comPort3_send)
    comPort3_entry.pack(side = LEFT)
    Label(text = "").pack()

    Button(frame3, text="Update ComPort1", width = 20, height = 1, command = updateComPort1).pack(side = LEFT)
    Button(frame3, text="Update ComPort2", width = 20, height = 1, command = updateComPort2).pack(side = LEFT)
    Button(frame3, text="Update ComPort3", width = 20, height = 1, command = updateComPort3).pack(side = LEFT)

    outputSetup()

    '''
    container = ttk.Frame(screen)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    for i in range(50):
        ttk.Label(scrollable_frame, text="Sample scrolling label").pack()

    container.pack()
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    '''

    screen.mainloop()


comPort1 = "None"
comPort2 = "None"
comPort3 = "None"
main_screen()

"""
# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
	port='/dev/ttyUSB1',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_TWO,
	bytesize=serial.SEVENBITS
)

ser.open()
ser.isOpen()

Print('Enter your commands below.\r\nInsert "exit" to leave the application.')

input=1
while 1 :
	# get keyboard input
	input = raw_input(">> ")
        # Python 3 users
        # input = input(">> ")
	if input == 'exit':
		ser.close()
		exit()
	else:
		# send the character to the device
		# (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
		ser.write(input + '\r\n')
		out = ''
		# let's wait one second before reading output (let's give device time to answer)
		time.sleep(1)
		while ser.inWaiting() > 0:
			out += ser.read(1)

		if out != '':
			Print(">>" + out)
"""
