# StreamToRasp - OSC Data Receiver

This project provides a simple Python-based OSC (Open Sound Control) server designed to run on a Raspberry Pi or any other computer. It listens for incoming OSC messages on a specified port and prints them to the console.

## Prerequisites

- Python 3
- pip (Python package installer)

## Setup and Installation

1.  **Clone or download the project:**

    If you have git installed, you can clone the repository. Otherwise, you can download the files directly.

2.  **Install the required Python libraries:**

    Navigate to the project directory in your terminal and run the following command to install the necessary dependencies from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

## How to Run the OSC Server

1.  **Start the server:**

    Run the `osc_receiver.py` script from your terminal:

    ```bash
    python osc_receiver.py
    ```

2.  **Server Status:**

    Once running, you will see a message indicating that the server is active and listening for messages:

    ```
    Serving on ('0.0.0.0', 5005)
    Listening for OSC messages...
    Press Ctrl+C to exit.
    ```

    The server is now ready to receive OSC data on port `5005`.

## Sending Test Messages

You can use any OSC client to send messages to the server. Here are some examples:

- **TouchOSC:** A popular mobile app for sending OSC.
- **Processing:** A creative coding environment with an OSC library.
- **Max/MSP or Pure Data:** Visual programming languages for multimedia.

When configuring your client, use the IP address of the device running the server (your Raspberry Pi) and the port `5005`.

For example, if your Raspberry Pi's IP address is `192.168.1.10`, you would send OSC messages to `192.168.1.10:5005`.

Any message sent to any OSC address (e.g., `/test/message`, `/sensor/value`) will be printed in the console where the server is running.

## Customization

You can modify the `osc_receiver.py` script to:

-   Change the listening port.
-   Handle specific OSC addresses differently by adding more mappings to the `dispatcher`.