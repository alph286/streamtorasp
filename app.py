from flask import Flask, render_template, jsonify
from pythonosc import dispatcher, osc_server
from threading import Thread
import time
from collections import deque

app = Flask(__name__)

# Variabile globale per memorizzare gli ultimi dati OSC ricevuti
osc_data = {
    'last_message': None,
    'last_address': None,
    'last_timestamp': None,
    'message_history': deque(maxlen=100)  # Mantiene gli ultimi 100 messaggi
}

# Funzione per gestire i messaggi OSC
def handle_osc_message(address, *args):
    """Gestisce i messaggi OSC in arrivo e aggiorna i dati globali."""
    current_time = time.time()
    
    osc_data['last_message'] = args
    osc_data['last_address'] = address
    osc_data['last_timestamp'] = current_time
    
    # Aggiunge il messaggio alla cronologia
    message_info = {
        'address': address,
        'args': args,
        'timestamp': current_time,
        'time_str': time.strftime('%H:%M:%S', time.localtime(current_time))
    }
    osc_data['message_history'].append(message_info)
    
    print(f"OSC Message received: {address} -> {args}")

# Configurazione del server OSC
def start_osc_server():
    """Avvia il server OSC in un thread separato."""
    osc_dispatcher = dispatcher.Dispatcher()
    
    # Mappa tutti gli indirizzi OSC alla funzione di gestione
    osc_dispatcher.map("/*", handle_osc_message)
    
    # Configura il server OSC per ricevere dalla rete locale (porta 10000)
    ip = "0.0.0.0"  # Ascolta su tutte le interfacce di rete
    port = 10000
    server = osc_server.ThreadingOSCUDPServer((ip, port), osc_dispatcher)
    
    print(f"OSC Server started on {ip}:{port}")
    print("Ready to receive OSC messages from TouchDesigner...")
    
    # Avvia il server
    server.serve_forever()

# Route principale - Interfaccia web
@app.route('/')
def index():
    """Pagina principale dell'interfaccia web."""
    return render_template('index.html')

# API endpoint per ottenere i dati OSC
@app.route('/api/osc-data')
def get_osc_data():
    """Restituisce i dati OSC più recenti in formato JSON."""
    return jsonify({
        'last_message': osc_data['last_message'],
        'last_address': osc_data['last_address'],
        'last_timestamp': osc_data['last_timestamp'],
        'message_count': len(osc_data['message_history']),
        'history': list(osc_data['message_history'])
    })

# Avvia l'applicazione
if __name__ == "__main__":
    # Avvia il server OSC in un thread separato
    osc_thread = Thread(target=start_osc_server, daemon=True)
    osc_thread.start()
    
    # Avvia il server web Flask
    print("Starting web server...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)