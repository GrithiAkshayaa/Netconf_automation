import subprocess
import json
import os

# Define paths
CONFD_BIN = "/home/test/confd/bin"
CONFD_ETC = "/home/test/confd/etc/confd"
YANG_PATH = "/home/test/confd/src/openconfig-platform.yang"
JSON_PATH = "/home/test/confd/src/platform-data.json"
XML_PATH = "/home/test/confd/src/platform-data.xml"
CLI_PATH = "/home/test/confd/bin/confd_cli"

# Start ConfD server
def start_confd():
    subprocess.run([f"{CONFD_BIN}/confd"], check=True)
    print("Confd server started successfully")

# Load YANG model
def load_yang():
    subprocess.run([f"{CONFD_BIN}/confdc", "-c", YANG_PATH, "-o", f"{CONFD_ETC}/openconfig-platform.fxs"], check=True)
    print("YANG model compiled successfully")

# Function to filter only read-write (rw) config data
def filter_rw_data(data):
    """Filters only rw (config) sections from JSON data."""
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if key == "config":  # Keep only 'config' sections
                new_data[key] = value
            elif isinstance(value, (dict, list)):
                filtered_value = filter_rw_data(value)
                if filtered_value:  # Keep non-empty sections
                    new_data[key] = filtered_value
        return new_data
    elif isinstance(data, list):
        return [filter_rw_data(item) for item in data if filter_rw_data(item)]
    return data

# Convert JSON data to XML format
def json_to_xml(json_data):
    xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_data += '<components xmlns="http://openconfig.net/yang/platform">\n'
    
    for component in json_data.get('components', {}).get('component', []):
        xml_data += '  <component>\n'
        xml_data += f'    <name>{component["name"]}</name>\n'
        
        # Check if 'config' exists inside 'component'
        if "config" in component:
            xml_data += '    <config>\n'
            for key, value in component["config"].items():
                xml_data += f'      <{key}>{value}</{key}>\n'
            xml_data += '    </config>\n'
        
        xml_data += '  </component>\n'
    
    xml_data += '</components>\n'

    with open(XML_PATH, "w") as xml_file:
        xml_file.write(xml_data.strip())
    
    print(f"JSON data converted to XML format and saved to {XML_PATH}")

# Load data into ConfD
def load_data():
    cli_commands = f"""
    config
    load merge {XML_PATH}
    commit
    exit
    """
    subprocess.run([CLI_PATH, "-u", "admin", "-g", "admin"], input=cli_commands.strip(), text=True, check=True)
    print("Data loaded successfully into ConfD")

# Commit configuration
def commit_data():
    cli_commands = """
    config
    show configuration
    exit
    """
    subprocess.run([CLI_PATH, "-u", "admin", "-g", "admin"], input=cli_commands.strip(), text=True, check=True)
    print("Configuration committed successfully")

# Main execution
if __name__ == "__main__":
    with open(JSON_PATH, "r") as file:
        json_data = json.load(file)

    # Filter JSON to only include rw (config) sections
    filtered_json_data = filter_rw_data(json_data)

    start_confd()
    load_yang()
    json_to_xml(filtered_json_data)
    load_data()
    commit_data()
