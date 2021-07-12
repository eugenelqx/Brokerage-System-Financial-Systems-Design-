# The server code for 40.317 Homework 1.  This code is not complete.

import zmq
import sys
from decimal import Decimal, DecimalException
import threading
import time
import collections


# To run the server at a non-default port, the user provides the alternate port
# number on the command line.
port = "5890"  # Our default port.
if len(sys.argv) > 1:
    port = sys.argv[1]
    print("Overriding default port to", port)
    _ = int(port)

context = zmq.Context()
# Using "zmq.PAIR" means there is exactly one server for each client
# and vice-versa.  For this application, zmq.PAIR is more appropriate
# than zmq.REQ + zmq.REP (make sure you understand why!).
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:" + port)
print("I am the server, now alive and listening on port", port)

# This server maintains two quantities:
# - the number of shares we currently hold, and
share_balance = 0
# - the amount of cash we currently hold.
cash_balance = 0.0

# (You might find this useful for rounding off cash amounts:)
penny = Decimal('0.01')

# supported_commands
supported_cmd = ["buy", "sell", "deposit_cash", "get_share_balance",
                 "get_cash_balance", "help", "shutdown_server",
                 "get_latest_vwaps"]

help_text = ["buy <# of shares> <price per share>",
             "sell <# of shares> <price per share>",
             "deposit_cash <amount>", "get_share_balance",
             "get_cash_balance", "help", "shutdown_server",
             "get_latest_vwaps"]

# PART 2
# create an empty global deque to store the buy and sell logs
# we will store the price first then the quantity
# eg if we have 3 purchases, we will have the following deque:
# [<price 1>, <qty 1>, <price 2>, <qty 2>, <price 3>, <qty 3>]
buy_log = collections.deque()
sell_log = collections.deque()

# create an empty global deque to store the VWAP pairs
# we will always update this when there is a new purchase or sale
# the pairs are contained in the following format:
# deque([<buy_vwap>, <sell_vwap>])
vwap_pair = collections.deque(["N/A", "N/A"])

# This server must support the following commands:
# - "buy <# of shares> <price per share>"
# - "sell <# of shares> <price per share>"
# - "deposit_cash <amount>"
# - "get_share_balance"
# - "get_cash_balance"
# - "shutdown_server"
# - "help"

# Each of these commands must always return a one-line string.
# This string must begin with "[ERROR] " if any error occurred,
# otherwise it must begin with "[OK] ".

# Any command other than the above must generate the return string
# "[ERROR] Unknown command" .

# The behaviour of each of the above commands, in more detail:

# - "buy <# of shares> <price per share>"
#   Must perform the appropriate validations on these two quantities,
#   then must modify share_balance and cash_balance to reflect the
#   purchase, and return the string "[OK] Purchased" .

# - "sell <# of shares> <price per share>"
#   Must perform the appropriate validations on these two quantities,
#   then must modify share_balance and cash_balance to reflect the
#   sale, and return the string "[OK] Sold" .

# - ""deposit_cash <amount>"
#   Must perform the appropriate validations, i.e. ensure <amount>
#   is a positive number; then must add <amount> to cash_balance, and
#   return the string "[OK] Deposited" .

# - "get_share_balance"
#   Must return "[OK] " followed by the number of shares on hand.

# - "get_cash_balance"
#   Must return "[OK] " followed by the amount of cash on hand.

# - "shutdown_server"
#   Must return the string "[OK] Server shutting down" and then exit.

# - "help"
#   Must return the string "[OK] Supported commands: " followed by
#   a comma-separated list of the above commands.

# function to check whether command is correct
# this function will then activate the other functions


def check_cmd(cmd_input, options_input):

    global supported_cmd

    if cmd_input not in supported_cmd:
        output = "[ERROR] Unknown command"
        return output
    else:
        # return the various functions
        if cmd_input == "buy":
            return buy(options_input)
        elif cmd_input == "sell":
            return sell(options_input)
        elif cmd_input == "deposit_cash":
            return deposit_cash(options_input)
        elif cmd_input == "help":
            return help(options_input)
        elif cmd_input == "get_share_balance":
            return get_share_balance(options_input)
        elif cmd_input == "get_cash_balance":
            return get_cash_balance(options_input)
        else:
            return get_latest_vwaps(options_input)


# function to buy shares
def buy(options_input):
    global share_balance
    global cash_balance
    global buy_log

    # check that the command is correct
    if len(options_input) != 2:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should have exactly 2 inputs"

        return output
    else:
        # check that the quantity input is correct
        try:
            qty = int(options_input[0])
            if qty <= 0:
                raise ValueError
        except ValueError:
            output = "[ERROR] Inaccurate type of inputs.\
                Ensure that quantity input is a positive integer"

            return output
        # check that the price input is correct
        try:
            price_per_share = float(options_input[1])
            if price_per_share <= 0:
                raise ValueError
        except ValueError:
            output = "[ERROR] Inaccurate type of inputs.\
                Ensure that price input is a positive real number"

            return output
        # proceed if the inputs are correct
        # check if i have enough balance
        total_amt = round((float(qty))*price_per_share, 2)
        if cash_balance >= total_amt:
            # deduct total_amt and update
            cash_balance -= total_amt
            # update share_balance
            share_balance += qty
            output = "[OK] Purchased"
            # append the data into the buy deque
            # append price first
            buy_log.append(price_per_share)
            # append qty next
            buy_log.append(qty)

            return output
        else:
            output = "[ERROR] Insufficient cash balance"
            return output

# function to sell shares


def sell(options_input):
    global share_balance
    global cash_balance
    global sell_log

    # check that the command is correct
    if len(options_input) != 2:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should have exactly 2 inputs"

        return output
    else:
        # check that the quantity input is correct
        try:
            qty = int(options_input[0])
            if qty <= 0:
                raise ValueError
        except ValueError:
            output = "[ERROR] Inaccurate type of inputs.\
                Ensure that quantity input is a positive integer"

            return output
        # check that the price input is correct
        try:
            price_per_share = float(options_input[1])
            if price_per_share <= 0:
                raise ValueError
        except ValueError:
            output = "[ERROR] Inaccurate type of inputs.\
                Ensure that price input is a positive real number"

            return output
        # proceed if the inputs are correct
        # check if i have enough shares
        total_amt = round((float(qty))*price_per_share, 2)
        if share_balance >= qty:
            # deduct share_balance and update
            share_balance -= qty
            # update cash_balance
            cash_balance += total_amt
            output = "[OK] Sold"
            # append the data into the sell deque
            # append price first
            sell_log.append(price_per_share)
            # append qty next
            sell_log.append(qty)

            return output
        else:
            output = "[ERROR] Insufficient shares"
            return output

# function to get share_balance


def get_share_balance(options_input):
    global share_balance
    # check that no extra inputs
    if len(options_input) != 0:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should not have any inputs"

        return output
    else:
        output = "[OK] " + str(share_balance)

        return output

# function to get cash_balance


def get_cash_balance(options_input):
    global cash_balance

    # check that no extra inputs
    if len(options_input) != 0:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should not have any inputs"

        return output
    else:
        output = "[OK] " + str("{:.2f}".format(cash_balance))
        return output

# function to deposit cash


def deposit_cash(options_input):
    global cash_balance

    # check that the inputs are correct
    if len(options_input) != 1:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should have exactly 1 inputs"

        return output
    else:
        # check that the quantity input is correct
        try:
            deposit = float(options_input[0])
            if deposit <= 0:
                raise ValueError
        except ValueError:
            output = "[ERROR] Inaccurate type of inputs.\
                Ensure that cash deposit input is a positive real number"

            return output

        # proceed if correct
        cash_balance += deposit
        output = "[OK] Deposited"

        return output

# help function


def help(options_input):

    # check that no extra inputs
    if len(options_input) != 0:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should not have any inputs"

        return output

    else:
        output = "[OK] Supported commands: " + str(help_text)
        return output

# vwaps function


def get_latest_vwaps(options_input):

    # check that no extra inputs
    if len(options_input) != 0:
        output = "[ERROR] Inaccurate number of inputs.\
            Command should not have any inputs"

        return output
    else:
        output = "[OK] " + str(vwap_pair[0]) + " "\
            + str(vwap_pair[1])

        return output


# PART2 CREATING THE DAEMON THREAD


def daemon():
    global buy_log
    global sell_log
    global vwap_pair

    # declare the variables needed to compute the VWAP
    buy_count = 0
    sell_count = 0
    buy_vwap = 0
    buy_price_vwap = 0
    buy_qty_vwap = 0
    sell_vwap = 0
    sell_price_vwap = 0
    sell_qty_vwap = 0
    while True:
        # calculate the buy_vwap
        # only update the VWAP when there is a new purchase
        if len(buy_log) != buy_count:
            # update the buy counter
            buy_count = len(buy_log)
            # recalculate buy_vwap
            buy_price_vwap = 0
            buy_qty_vwap = 0
            for i in range(0, len(buy_log), 2):
                buy_price_vwap += buy_log[i]*buy_log[i+1]
                buy_qty_vwap += buy_log[i+1]
            buy_vwap = buy_price_vwap/buy_qty_vwap
        else:
            # do nothing if there is no new purchase
            pass

        # calcuate the sell_vwap
        # only update the VWAP when there is a new sale
        if len(sell_log) != sell_count:
            # update the sell counter
            sell_count = len(sell_log)
            # recalculate sell_vwap
            sell_price_vwap = 0
            sell_qty_vwap = 0
            for i in range(0, len(sell_log), 2):
                sell_price_vwap += sell_log[i]*sell_log[i+1]
                sell_qty_vwap += sell_log[i+1]
            sell_vwap = sell_price_vwap/sell_qty_vwap
        else:
            # do nothing if there is no new sale
            pass
        # for checking the deque
        # print("buy_log: ", buy_log)
        # PRINTING FOR PART 2 Q1 PART 1C
        # print("BUY VWAP: ", buy_vwap)

        # for checking the sell deque
        # print("sell_log: ", sell_log)
        # PRINTING FOR PART 2 Q1 PART 1C
        # print("SELL VWAP: ", sell_vwap)

        # update the vwap_pair global variable
        # we aim to update the buy_vwap first then the sell_vwap
        # update the buy_vwap
        if len(buy_log) > 0:
            vwap_pair.popleft()
            vwap_pair.appendleft(str("{:.2f}".format(buy_vwap)))
        # update the sell_vwap
        if len(sell_log) > 0:
            vwap_pair.pop()
            vwap_pair.append(str("{:.2f}".format(sell_vwap)))
        # sleep the function for 10s
        time.sleep(10)

    return


d = threading.Thread(name='daemon', target=daemon)
# start daemon to True
d.setDaemon(True)
# start the daemon thread
d.start()

while True:
    message = socket.recv()
    decoded = message.decode("utf-8")
    tokens = decoded.split()
    if len(tokens) == 0:
        continue
    cmd = tokens[0]
    if cmd == "shutdown_server":
        socket.send_string("[OK] Server shutting down")
        sys.exit(0)
    else:
        options = tokens[1:]
        # The response is a function of cmd and options:
        response = check_cmd(cmd, options)
        socket.send_string(response)
