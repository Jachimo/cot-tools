import uuid
from datetime import datetime
import xml.etree.ElementTree as ET
import socket
import struct

def generate_cot_message(event_type, lat, lon, callsign):
    # Create the root element
    event = ET.Element("event")
    event.set("version", "2.0")
    event.set("uid", str(uuid.uuid4()))
    event.set("type", event_type)
    event.set("time", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    event.set("start", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    event.set("stale", (datetime.utcnow().replace(hour=datetime.utcnow().hour+1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    event.set("how", "m-g")

    # Add point information
    point = ET.SubElement(event, "point")
    point.set("lat", str(lat))
    point.set("lon", str(lon))
    point.set("hae", "0")
    point.set("ce", "9999999.0")
    point.set("le", "9999999.0")

    # Add detail information
    detail = ET.SubElement(event, "detail")
    ET.SubElement(detail, "callsign").text = callsign

    # Convert to XML string
    return ET.tostring(event, encoding="unicode")

def transmit_cot_message(message, multicast_group, port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the time-to-live for the message
    ttl = struct.pack('b', 1)  # Restrict to the same subnet
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        # Send the message
        print(f"Sending CoT message to {multicast_group}:{port}")
        sock.sendto(message.encode('utf-8'), (multicast_group, port))
        print("Message sent successfully")
    finally:
        print("Closing socket")
        sock.close()

# Example usage
if __name__ == "__main__":
    # Generate a CoT message
    cot_message = generate_cot_message("a-f-G-U-C", 40.7128, -74.0060, "EXAMPLE_UNIT")
    print("Generated CoT message:")
    print(cot_message)

    # Transmit the CoT message
    multicast_group = '239.2.3.1'  # This is an example multicast address
    port = 6969  # This is an example port number
    transmit_cot_message(cot_message, multicast_group, port)
