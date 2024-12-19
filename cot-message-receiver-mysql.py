import socket
import struct
import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime

def join_multicast_group(multicast_group, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def parse_cot_message(xml_string):
    root = ET.fromstring(xml_string)
    event_type = root.get('type')
    event_time = root.get('time')
    event_stale = root.get('stale')
    point = root.find('point')
    lat = point.get('lat')
    lon = point.get('lon')
    detail = root.find('detail')
    callsign = detail.find('callsign').text if detail is not None and detail.find('callsign') is not None else "N/A"
    return {
        'type': event_type,
        'time': event_time,
        'stale': event_stale,
        'lat': lat,
        'lon': lon,
        'callsign': callsign
    }

def init_database():
    conn = sqlite3.connect('cot_messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cot_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            event_time TEXT,
            stale_time TEXT,
            latitude REAL,
            longitude REAL,
            callsign TEXT,
            received_time TEXT
        )
    ''')
    # Create an index on type, event_time, and callsign for faster duplicate checking
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_type_time_callsign 
        ON cot_messages (type, event_time, callsign)
    ''')
    conn.commit()
    return conn

def is_duplicate(conn, message):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM cot_messages 
        WHERE type = ? AND event_time = ? AND callsign = ?
    ''', (message['type'], message['time'], message['callsign']))
    count = cursor.fetchone()[0]
    return count > 0

def insert_cot_message(conn, message):
    if is_duplicate(conn, message):
        print("Duplicate message detected. Skipping insertion.")
        return False

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cot_messages (type, event_time, stale_time, latitude, longitude, callsign, received_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        message['type'],
        message['time'],
        message['stale'],
        float(message['lat']),
        float(message['lon']),
        message['callsign'],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    return True

def receive_cot_messages(multicast_group, port):
    sock = join_multicast_group(multicast_group, port)
    conn = init_database()
    print(f"Listening for CoT messages on {multicast_group}:{port}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"Received message from {addr}")
            
            message = data.decode('utf-8')
            parsed_message = parse_cot_message(message)
            
            if insert_cot_message(conn, parsed_message):
                print("Parsed and stored new CoT Message:")
                print(f"Type: {parsed_message['type']}")
                print(f"Time: {parsed_message['time']}")
                print(f"Stale: {parsed_message['stale']}")
                print(f"Latitude: {parsed_message['lat']}")
                print(f"Longitude: {parsed_message['lon']}")
                print(f"Callsign: {parsed_message['callsign']}")
            else:
                print("Duplicate message received and skipped.")
            print("--------------------")
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    multicast_group = '239.2.3.1'
    port = 6969
    receive_cot_messages(multicast_group, port)
