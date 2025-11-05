#!/usr/bin/env python3
"""
Client OSC per Raspberry Pi
Si connette a un server OSC remoto e visualizza i dati ricevuti
"""

import argparse
import socket
import struct
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_message import OscMessage
import time
from datetime import datetime

class OSCClient:
    def __init__(self, server_ip, server_port=10000):
        """Inizializza il client OSC"""
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        
        # Dati ricevuti
        self.last_message = None
        self.last_address = None
        self.last_timestamp = None
        self.message_count = 0
        
    def connect(self):
        """Stabilisce la connessione UDP al server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Timeout per non bloccare il programma
            self.socket.settimeout(1.0)
            print(f"Connesso al server OSC: {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"Errore nella connessione: {e}")
            return False
    
    def receive_messages(self):
        """Riceve messaggi OSC dal server"""
        if not self.socket:
            print("Socket non inizializzato. Chiama connect() prima.")
            return
        
        print(f"In ascolto su {self.server_ip}:{self.server_port}...")
        print("Premi Ctrl+C per interrompere")
        print("-" * 50)
        
        try:
            while True:
                try:
                    # Ricevi dati
                    data, addr = self.socket.recvfrom(4096)
                    
                    # Processa il messaggio OSC
                    message = self.parse_osc_message(data)
                    if message:
                        self.handle_message(message)
                        
                except socket.timeout:
                    # Timeout normale, continua il loop
                    continue
                    
                except KeyboardInterrupt:
                    print("\nInterruzione richiesta dall'utente")
                    break
                    
                except Exception as e:
                    print(f"Errore nella ricezione: {e}")
                    time.sleep(1)
                    
        finally:
            self.cleanup()
    
    def parse_osc_message(self, data):
        """Parsa i dati OSC grezzi"""
        try:
            # Estrai l'indirizzo OSC
            address_end = data.find(b'\0')
            if address_end == -1:
                return None
                
            address = data[:address_end].decode('utf-8')
            
            # Estrai i tipi di argomento
            type_tag_index = address_end + (4 - (address_end % 4))
            if type_tag_index >= len(data):
                return None
                
            type_tag = data[type_tag_index:type_tag_index+1].decode('utf-8')
            if type_tag != ',':
                return None
                
            # Estrai gli argomenti
            args = []
            arg_index = type_tag_index + 1
            
            for tag in data[type_tag_index+1:]:
                tag_char = chr(tag)
                
                if tag_char == '\0':
                    break
                    
                if tag_char == 'i':  # intero
                    if arg_index + 4 > len(data):
                        break
                    value = struct.unpack('>i', data[arg_index:arg_index+4])[0]
                    args.append(value)
                    arg_index += 4
                    
                elif tag_char == 'f':  # float
                    if arg_index + 4 > len(data):
                        break
                    value = struct.unpack('>f', data[arg_index:arg_index+4])[0]
                    args.append(value)
                    arg_index += 4
                    
                elif tag_char == 's':  # stringa
                    string_end = data.find(b'\0', arg_index)
                    if string_end == -1:
                        break
                    value = data[arg_index:string_end].decode('utf-8')
                    args.append(value)
                    arg_index = string_end + (4 - ((string_end - arg_index) % 4))
                    
                else:
                    # Tipo non supportato, salta
                    arg_index += 4
            
            return {'address': address, 'args': args}
            
        except Exception as e:
            print(f"Errore nel parsing OSC: {e}")
            return None
    
    def handle_message(self, message):
        """Gestisce un messaggio OSC ricevuto"""
        self.message_count += 1
        self.last_message = message['args']
        self.last_address = message['address']
        self.last_timestamp = datetime.now()
        
        # Visualizza il messaggio
        timestamp_str = self.last_timestamp.strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp_str}] {self.last_address} -> {self.format_args(self.last_message)}")
    
    def format_args(self, args):
        """Formatta gli argomenti per la visualizzazione"""
        if not args:
            return "Nessun argomento"
        
        formatted = []
        for arg in args:
            if isinstance(arg, float):
                formatted.append(f"{arg:.3f}")
            else:
                formatted.append(str(arg))
        
        return f"[{', '.join(formatted)}]"
    
    def cleanup(self):
        """Pulisce le risorse"""
        if self.socket:
            self.socket.close()
            print("Connessione chiusa")
    
    def get_stats(self):
        """Restituisce le statistiche"""
        return {
            'message_count': self.message_count,
            'last_address': self.last_address,
            'last_message': self.last_message,
            'last_timestamp': self.last_timestamp
        }

def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(description='Client OSC per Raspberry Pi')
    parser.add_argument('server_ip', help='Indirizzo IP del server OSC')
    parser.add_argument('-p', '--port', type=int, default=10000, 
                       help='Porta del server OSC (default: 10000)')
    
    args = parser.parse_args()
    
    # Crea e avvia il client
    client = OSCClient(args.server_ip, args.port)
    
    if client.connect():
        client.receive_messages()
    else:
        print("Impossibile connettersi al server")

if __name__ == "__main__":
    main()