# Financial-Systems-Design
This is a brokerage system for a single stock that tracks the Volume Weighted Average Prices (VWAPs) for long and short calls
This brokerage system works in a pair using ZMQ pairs:

The file <holdings_client.py> serves as the client front that displays the relevant information and sends the client's requests to the server.\
The file <holdings_server.py> serves as the server that receives instructions from the client and does the relevant tabulations/calculations.

To begin, simply run both client and server files.
