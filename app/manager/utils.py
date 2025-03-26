import xml.etree.ElementTree as ET

class MessageUtilities:
    XMLDefTag = '<?xml version="1.0" encoding="UTF-8" ?>'
    ParcoV1Tag = '<parco version="1.0">'
    ParcoEndTag = '</parco>'

# Constants
FASTAPI_BASE_URL = "http://192.168.210.231:8000"
MQTT_BROKER = "localhost"