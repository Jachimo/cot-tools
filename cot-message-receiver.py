import socket
import struct
import xml.etree.ElementTree as ET

def join_multicast_group(multicast_group, port):
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Allow reuse of the socket address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to the port
    sock.bind(('', port))
    
    # Join the multicast group
    mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    return sock

def parse_cot_message(xml_string):
    root = ET.fromstring(xml_string)
    
    # Extract basic event information
    event_type = root.get('type')
    event_time = root.get('time')
    event_stale = root.get('stale')
    
    # Extract point information
    point = root.find('point')
    lat = point.get('lat')
    lon = point.get('lon')
    
    # Extract detail information
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

def receive_cot_messages(multicast_group, port):
    sock = join_multicast_group(multicast_group, port)
    print(f"Listening for CoT messages on {multicast_group}:{port}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received message from {addr}")
            
            message = data.decode('utf-8')
            parsed_message = parse_cot_message(message)
            
            print("Parsed CoT Message:")
            print(f"Type: {parsed_message['type']}")
            print(f"Time: {parsed_message['time']}")
            print(f"Stale: {parsed_message['stale']}")
            print(f"Latitude: {parsed_message['lat']}")
            print(f"Longitude: {parsed_message['lon']}")
            print(f"Callsign: {parsed_message['callsign']}")
            print("--------------------")
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    multicast_group = '239.2.3.1'  # This should match the sender's multicast group
    port = 6969  # This should match the sender's port
    
    receive_cot_messages(multicast_group, port)
