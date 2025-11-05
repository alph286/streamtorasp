#!/usr/bin/env python3
"""
Server WebSocket + UDP Bridge
Riceve dati UDP e li invia al browser via WebSocket
"""

import asyncio
import websockets
import socket
import json
from datetime import datetime
import threading

# Dati condivisi
udp_messages = []
clients = set()

async def handle_websocket(websocket, path):
    """Gestisce le connessioni WebSocket"""
    clients.add(websocket)
    print(f"Client WebSocket connesso: {websocket.remote_address}")
    
    try:
        # Invia la cronologia iniziale
        if udp_messages:
            history_msg = {
                'type': 'history',
                'messages': udp_messages[-20:]  # Ultimi 20 messaggi
            }
            await websocket.send(json.dumps(history_msg))
        
        # Mantieni la connessione aperta
        async for message in websocket:
            # Il client può inviare comandi, ma per ora ignoriamo
            pass
            
    except websockets.exceptions.ConnectionClosed:
        print("Client WebSocket disconnesso")
    finally:
        clients.remove(websocket)

async def broadcast_message(message):
    """Invia un messaggio a tutti i client WebSocket connessi"""
    if clients:
        message_json = json.dumps(message)
        await asyncio.gather(*[
            client.send(message_json) for client in clients
        ])

def udp_receiver_thread(udp_port=10000, interface='0.0.0.0'):
    """Thread che riceve dati UDP e li invia via WebSocket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((interface, udp_port))
        print(f"UDP Receiver avviato su {interface}:{udp_port}")
        print("In attesa di dati UDP...")
        
        while True:
            data, addr = sock.recvfrom(4096)
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Prova a decodificare come testo
            try:
                text_data = data.decode('utf-8')
                data_type = 'text'
                content = text_data
            except UnicodeDecodeError:
                # Se non è testo, mostra esadecimale
                data_type = 'binary'
                hex_data = data.hex()
                if len(hex_data) > 100:
                    content = hex_data[:100] + "..."
                else:
                    content = hex_data
            
            # Crea il messaggio
            udp_message = {
                'timestamp': timestamp,
                'source_ip': addr[0],
                'source_port': addr[1],
                'data_type': data_type,
                'content': content,
                'size': len(data)
            }
            
            # Aggiungi alla cronologia
            udp_messages.append(udp_message)
            if len(udp_messages) > 100:  # Limita a 100 messaggi
                udp_messages.pop(0)
            
            # Invia via WebSocket
            websocket_msg = {
                'type': 'udp_message',
                'message': udp_message
            }
            
            # Usa asyncio per inviare nel thread principale
            asyncio.run_coroutine_threadsafe(
                broadcast_message(websocket_msg), 
                asyncio.get_event_loop()
            )
            
            # Log sulla console
            print(f"[{timestamp}] UDP da {addr[0]}:{addr[1]} - {len(data)} bytes")
            
    except Exception as e:
        print(f"Errore UDP receiver: {e}")
    finally:
        sock.close()

async def main():
    """Avvia server WebSocket e UDP"""
    # Avvia thread UDP
    udp_thread = threading.Thread(
        target=udp_receiver_thread, 
        args=(10000, '0.0.0.0'),
        daemon=True
    )
    udp_thread.start()
    
    # Avvia server WebSocket
    server = await websockets.serve(
        handle_websocket, 
        '0.0.0.0', 
        8765
    )
    
    print("Server WebSocket avviato su ws://0.0.0.0:8765")
    print("Interfaccia web disponibile su http://localhost:8000")
    print("-" * 50)
    
    # Mantieni il server attivo
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())