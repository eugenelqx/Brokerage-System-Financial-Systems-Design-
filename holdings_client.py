# The client code for 40.317 Homework 1.  This code is complete.
# It assumes the server runs on the same machine.

import zmq
import sys
import time
import PySimpleGUI as sg
from datetime import datetime
import threading

port = "5890"  # Our default server port.
if len(sys.argv) > 1:
    port = sys.argv[1]
    print("Overriding default port to", port)
    ignored = int(port)

context = zmq.Context()
# Using "zmq.PAIR" means there is exactly one server for each client
# and vice-versa.  For this application, zmq.PAIR is more appropriate
# than zmq.REQ + zmq.REP (make sure you understand why!).
socket = context.socket(zmq.PAIR)
print("Connecting to server...")
socket.connect("tcp://localhost:" + port)

# Part 3 GUI


share_balance = 0
cash_balance = '0.00'
vwap_pair = ['N/A', 'N/A']
vwap_cmd = 'get_latest_vwaps'

sg.theme('Default')

layout = [[sg.Text('Balances',font=('Gotham Bold',14),pad=((85,0),(10,8)))],
          [sg.Text('Shares',font=('Gotham Book',14),pad=(105,0)),
           sg.Text('Cash',font=('Gotham Book',14),pad=(40,0))],
          [sg.Text(share_balance,key='-Shares-',font=('Gotham Book',14),pad=((105,0),(0,0)),size=(16,0),background_color='white'),
           sg.Text(cash_balance,key='-Cash-',font=('Gotham Book',14),pad=(18,0),size=(16,0),background_color='white')],   

          [sg.Text('Deposit Cash',font=('Gotham Bold',14),pad=((125,0),(15,8)))],   
          [sg.Input(key='-Deposit Cash-',font=('Gotham Book',14),size=(18,18),pad=((145,5),(0,0))),
           sg.Button('Deposit', key='-Deposit-', button_color=('white', '#00008b'),font=('Gotham Bold',14))],

          [sg.Text('Buy Shares',font=('Gotham Bold',14),pad=((20,0),(15,8)))],
          [sg.Text('Quantity',font=('Gotham Book',14),pad=((40,0),(0,0))),
           sg.Text('Price Per Share',font=('Gotham Book',14),pad=((180,0),(0,0)))],
          [sg.Input(key='-Quantity1-',font=('Gotham Book',14),size=(18,18),pad=((44,5),(0,0))),
           sg.Input(key='-Price Per Share1-',font=('Gotham Book',14),size=(18,18)),
           sg.Button('Buy', button_color=('white', '#00008b'), key='-Buy-',font=('Gotham Bold',14),pad=((5,10),(0,0)))],  

          [sg.Text('Sell Shares',font=('Gotham Bold',14),pad=((20,0),(15,8)))],
          [sg.Text('Quantity',font=('Gotham Book',14),pad=((40,0),(0,0))),
          sg.Text('Price Per Share',font=('Gotham Book',14),pad=((180,0),(0,0)))],
          [sg.Input(key='-Quantity2-',font=('Gotham Book',14),size=(18,18),pad=((44,5),(0,0))),
           sg.Input(key='-Price Per Share2-',font=('Gotham Book',14),size=(18,18)),
           sg.Button('Sell', button_color=('white', '#00008b'), key='-Sell-',font=('Gotham Bold',14),pad=((5,10),(0,0)))],

          [sg.Exit('Close Server & Quit',button_color=('white', 'firebrick4'), key='Exit',font=('Gotham Bold',14),pad=((212,0),(18,5)))],
          [sg.Text('{}: Buy VWAP={}, sell VWAP={}'.format(datetime.now().strftime("%H:%M:%S"),
                   vwap_pair[0],vwap_pair[1]),font=('Gotham Book',14),key='-vwap-',pad=(97,0),size=(40,0))]]      

window = sg.Window('Holdings Manager', layout, background_color='#ECECEC') 

# create a thread to keep requesting for the vwap every 1s

def daemon():
    global vwap_pair
    while True:
        socket.send_string(vwap_cmd)
        # the server will then send back the vwaps
        # eg '[OK'] <buy_vwap> <sell_vwap>
        message = socket.recv()
        decoded = message.decode("utf-8")
        tokens = decoded.split()
        vwap_pair = tokens[1:]
        time.sleep(1)

    return

d = threading.Thread(name='daemon', target=daemon)
# start daemon to True
d.setDaemon(True)
# start the daemon thread
d.start()

while True:
   
    event, values = window.read(timeout=10) 
    
    if event == sg.WIN_CLOSED or event == 'Exit':
        cmd = 'shutdown_server'
        socket.send_string(cmd)
        message = socket.recv()
        break

    if event=='-Deposit-':

        # checks to ensure correct input
        if ' ' in values['-Deposit Cash-']:
            sg.popup("[ERROR] Inaccurate inputs. Input should not have any spaces")
        try:
            if float(values['-Deposit Cash-'])<0:
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Inaccurate inputs. Ensure that deposited cash is a positive real number")

        # first you send the command "deposit_cash <amt>"
        cmd = 'deposit_cash ' + str(values['-Deposit Cash-'])
        socket.send_string(cmd)
        message = socket.recv()
        # after you deposit cash, update the cash balance
        cmd = 'get_cash_balance'
        socket.send_string(cmd)
        # the server will then send back the cash balance
        message = socket.recv()
        decoded = message.decode("utf-8")
        tokens = decoded.split()
        cash_balance = tokens[1]
        window['-Cash-'].update(cash_balance)

    if event=='-Buy-':

        # checks to ensure correct input
        if ' ' in values['-Quantity1-']:
            sg.popup("[ERROR] Inaccurate inputs. Quantity input should not have any spaces")
        if ' ' in values['-Price Per Share1-']:
            sg.popup("[ERROR] Inaccurate inputs. Price input should not have any spaces")
        try:
            if int(values['-Quantity1-'])<0:
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Inaccurate inputs. Ensure that quantity input is a positive integer")

        try:
            if float(values['-Price Per Share1-'])<0:
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Inaccurate inputs. Ensure that price input is a positive real number")
        # ensure that i have enough cash
        try:
            if float(cash_balance)< int(values['-Quantity1-'])*float(values['-Price Per Share1-']):
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Insufficient funds or you may have entered an incorrect input")

        # first send the command "buy <# of shares> <price per share>"
        cmd = 'buy ' + str(values['-Quantity1-']) + ' ' + str(values['-Price Per Share1-'])
        socket.send_string(cmd)
        message = socket.recv()
        # after buying need to update cash balance
        cmd = 'get_cash_balance'
        socket.send_string(cmd)
        # the server will then send back the cash balance
        message = socket.recv()
        decoded = message.decode("utf-8")
        tokens = decoded.split()
        cash_balance = tokens[1]
        window['-Cash-'].update(cash_balance)

        # need to update the share balance
        cmd = 'get_share_balance'
        socket.send_string(cmd)
        # the server will then send back the share balance
        message = socket.recv()
        decoded = message.decode("utf-8")
        tokens = decoded.split()
        share_balance = tokens[1]
        window['-Shares-'].update(share_balance)

    if event=='-Sell-':

        # checks to ensure correct input
        if ' ' in values['-Quantity2-']:
            sg.popup("[ERROR] Inaccurate inputs. Quantity input should not have any spaces")
        if ' ' in values['-Price Per Share2-']:
            sg.popup("[ERROR] Inaccurate inputs. Price input should not have any spaces")
        try:
            if int(values['-Quantity2-'])<0:
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Inaccurate inputs. Ensure that quantity input is a positive integer")

        try:
            if float(values['-Price Per Share2-'])<0:
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Inaccurate inputs. Ensure that price input is a positive real number")
         # ensure that i have enough shares
        try:
            if int(share_balance)< int(values['-Quantity2-']):
                raise ValueError
        except ValueError:
            sg.popup("[ERROR] Insufficient shares or you may have entered an incorrect input")

        # first send the command "buy <# of shares> <price per share>"
        cmd = 'sell ' + str(values['-Quantity2-']) + ' ' + str(values['-Price Per Share2-'])
        socket.send_string(cmd)
        message = socket.recv()
        # after buying need to update cash balance
        cmd = 'get_cash_balance'
        socket.send_string(cmd)
        # the server will then send back the cash balance
        message = socket.recv()
        decoded = message.decode("utf-8")
        tokens = decoded.split()
        cash_balance = tokens[1]
        window['-Cash-'].update(cash_balance)

        # need to update the share balance
        cmd = 'get_share_balance'
        socket.send_string(cmd)
        # the server will then send back the share balance
        message = socket.recv()
        decoded = message.decode("utf-8")
        tokens = decoded.split()
        share_balance = tokens[1]
        window['-Shares-'].update(share_balance)

    window['-vwap-'].update('{}: Buy VWAP={}, sell VWAP={}'.format(datetime.now().strftime("%H:%M:%S"),vwap_pair[0],vwap_pair[1]))

window.close()


