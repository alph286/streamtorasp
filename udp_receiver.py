#!/usr/bin/env python3
"""
Simple UDP Receiver per Raspberry Pi
Ascolta sulla porta specificata e mostra tutti i dati ricevuti
"""

import socket
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='UDP Receiver per Raspberry Pi')
    parser.add_argument('-p', '--port', type=int, default=10000, 
                       help='Porta UDP in ascolto (default: 10000)')
    parser.add_argument('-i', '--interface', default='0.0.0.0',
                       help='Interfaccia di rete (default: 0.0.0.0 - tutte)')
    
    args = parser.parse_args()
    
    # Crea socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind alla porta
        sock.bind((args.interface, args.port))
        print(f"UDP Receiver avviato su {args.interface}:{args.port}")
        print("In attesa di dati UDP...")
        print("Premi Ctrl+C per fermare")
        print("-" * 60)
        
        while True:
            # Ricevi dati
            data, addr = sock.recvfrom(4096)  # Buffer di 4KB
            
            # Timestamp corrente
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Mostra informazioni
            print(f"[{timestamp}] Da {addr[0]}:{addr[1]} - {len(data)} bytes")
            
            # Prova a decodificare come testo
            try:
                text_data = data.decode('utf-8')
                print(f"   Testo: {text_data}")
            except UnicodeDecodeError:
                # Se non è testo, mostra esadecimale
                hex_data = data.hex()
                if len(hex_data) > 80:
                    hex_data = hex_data[:80] + "..."
                print(f"   Dati: {hex_data}")
            
            print("-" * 40)
            
    except KeyboardInterrupt:
        print("\nReceiver interrotto dall'utente")
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        sock.close()
        print("Socket chiuso")

if __name__ == "__main__":
    main()