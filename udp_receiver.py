#!/usr/bin/env python3
"""
Simple UDP Receiver per Raspberry Pi
Ascolta sulla porta specificata e mostra tutti i dati ricevuti
"""

import socket
import argparse
import threading
import queue
from datetime import datetime

def start_websocket_server(port=8765, udp_port=10000, interface='0.0.0.0'):
    import asyncio
    import websockets
    import json
    from datetime import datetime

    clients = set()
    message_queue = queue.Queue()

    async def handle_websocket(websocket, path):
        clients.add(websocket)
        try:
            async for message in websocket:
                pass
        finally:
            clients.remove(websocket)

    async def broadcast_message(message):
        if clients:
            message_json = json.dumps(message)
            await asyncio.gather(*[
                client.send(message_json) for client in clients
            ])

    def udp_receiver_thread():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((interface, udp_port))
        while True:
            data, addr = sock.recvfrom(4096)
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            # Conversione avanzata
            try:
                text_data = data.decode('utf-8')
                data_type = 'text'
                content = text_data
            except UnicodeDecodeError:
                # Prova conversione numerica
                if len(data) == 4:
                    try:
                        import struct
                        num = struct.unpack('!f', data)[0]
                        data_type = 'float'
                        content = str(num)
                    except Exception:
                        num = struct.unpack('!i', data)[0]
                        data_type = 'int'
                        content = str(num)
                elif len(data) == 8:
                    try:
                        import struct
                        num = struct.unpack('!d', data)[0]
                        data_type = 'double'
                        content = str(num)
                    except Exception:
                        content = data.hex()
                        data_type = 'binary'
                else:
                    content = data.hex()
                    data_type = 'binary'
            udp_message = {
                'timestamp': timestamp,
                'source_ip': addr[0],
                'source_port': addr[1],
                'data_type': data_type,
                'content': content,
                'size': len(data)
            }
            websocket_msg = {
                'type': 'udp_message',
                'message': udp_message
            }
            message_queue.put(websocket_msg)
            print(f"[{timestamp}] Da {addr[0]}:{addr[1]} - {len(data)} bytes | {data_type}: {content}")

    async def process_message_queue():
        while True:
            try:
                message = message_queue.get_nowait()
                await broadcast_message(message)
                message_queue.task_done()
            except queue.Empty:
                await asyncio.sleep(0.1)

    async def main_async():
        udp_thread = threading.Thread(target=udp_receiver_thread, daemon=True)
        udp_thread.start()
        server = await websockets.serve(handle_websocket, interface, port)
        print(f"Server WebSocket avviato su ws://{interface}:{port}")
        print("Interfaccia web disponibile su http://localhost:8000")
        await asyncio.gather(server.wait_closed(), process_message_queue())

    threading.Thread(target=lambda: __import__('asyncio').run(__import__('asyncio').new_event_loop().run_until_complete(main_async())), daemon=True).start()

def main():
    parser = argparse.ArgumentParser(description='UDP Receiver per Raspberry Pi')
    parser.add_argument('-p', '--port', type=int, default=10000, 
                       help='Porta UDP in ascolto (default: 10000)')
    parser.add_argument('-i', '--interface', default='0.0.0.0',
                       help='Interfaccia di rete (default: 0.0.0.0 - tutte)')
    args = parser.parse_args()
    # Avvia anche il server WebSocket
    start_websocket_server(port=8765, udp_port=args.port, interface=args.interface)
    # Crea socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((args.interface, args.port))
        print(f"UDP Receiver avviato su {args.interface}:{args.port}")
        print("In attesa di dati UDP...")
        print("Premi Ctrl+C per fermare")
        print("-" * 60)
        while True:
            data, addr = sock.recvfrom(4096)
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f"[{timestamp}] Da {addr[0]}:{addr[1]} - {len(data)} bytes")
            try:
                text_data = data.decode('utf-8')
                print(f"   Testo: {text_data}")
            except UnicodeDecodeError:
                # Conversione numerica
                if len(data) == 4:
                    try:
                        import struct
                        num = struct.unpack('!f', data)[0]
                        print(f"   Float: {num}")
                    except Exception:
                        num = struct.unpack('!i', data)[0]
                        print(f"   Int: {num}")
                elif len(data) == 8:
                    try:
                        import struct
                        num = struct.unpack('!d', data)[0]
                        print(f"   Double: {num}")
                    except Exception:
                        hex_data = data.hex()
                        print(f"   Dati: {hex_data}")
                else:
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