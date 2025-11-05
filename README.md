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

## Configurazione per Raspberry Pi

### Sul Raspberry Pi:

1. **Trova l'indirizzo IP del Raspberry Pi:**
   ```bash
   hostname -I
   ```

2. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Avvia il server:**
   ```bash
   python app.py
   ```

### Sul Windows (TouchDesigner/Altro):

1. **Configura il client OSC per inviare a:**
   ```
   [IP_DEL_RASPBERRY]:10000
   ```
   
   Esempio: se il Raspberry ha IP `192.168.1.100`, invia a `192.168.1.100:10000`

2. **Assicurati che entrambi i dispositivi siano sulla stessa rete locale**

### Verifica la connessione:

- Il server OSC è in ascolto sulla porta **10000**
- L'interfaccia web è disponibile su `http://[IP_DEL_RASPBERRY]:5000`
- I dati OSC ricevuti vengono visualizzati in tempo reale nell'interfaccia web

## Customization

You can modify the `osc_receiver.py` script to:

-   Change the listening port.
-   Handle specific OSC addresses differently by adding more mappings to the `dispatcher`.