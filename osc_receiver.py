# Import necessary libraries from python-osc
from pythonosc import dispatcher
from pythonosc import osc_server

# Define a function to handle incoming OSC messages
def print_message(address, *args):
    """Prints the received OSC message to the console."""
    print(f"Received new message from {address}: {args}")

# --- Main execution block ---
if __name__ == "__main__":
    # -- Configuration --
    # Set the IP address and port for the OSC server.
    # Use "0.0.0.0" to listen on all available network interfaces.
    # You can change the port number if needed.
    ip = "0.0.0.0"
    port = 5005

    # -- OSC Server Setup --
    # Create a dispatcher to map OSC addresses to functions.
    osc_dispatcher = dispatcher.Dispatcher()

    # Map all incoming OSC addresses to the print_message function.
    # You can also map specific addresses to different functions, for example:
    # osc_dispatcher.map("/filter", print_filter_message)
    osc_dispatcher.map("/*", print_message)

    # Create the OSC server.
    server = osc_server.ThreadingOSCUDPServer((ip, port), osc_dispatcher)

    # -- Start Server --
    print(f"Serving on {server.server_address}")
    print("Listening for OSC messages...")
    print("Press Ctrl+C to exit.")

    # Start the server and keep it running until interrupted.
    server.serve_forever()