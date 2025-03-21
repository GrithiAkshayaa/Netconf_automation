import subprocess
import json
import os

# Define paths
CONFD_BIN = "/home/test/confd/bin/confd"
CONFD_ETC = "/home/test/confd/etc/confd"
YANG_PATH = "/home/test/confd/src/openconfig-platform.yang"
JSON_PATH = "/home/test/confd/src/openconfig-platform-config.json"
XML_PATH = "/home/test/confd/src/openconfig-platform-config.xml"
CLI_PATH = "/home/test/confd/bin/confd_cli"

def start_confd():
    """Start the ConfD server."""
    try:
        subprocess.run([CONFD_BIN], check=True, stderr=subprocess.PIPE)
        print("✅ ConfD server started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting ConfD: {e.stderr.decode()}")
        exit(1)

def load_yang():
    """Load the YANG model into ConfD."""
    try:
        subprocess.run([CONFD_BIN, "-c", YANG_PATH, "-o", f"{CONFD_ETC}/openconfig-platform.fxs"], check=True)
        print("✅ YANG model compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error compiling YANG model: {e.stderr.decode()}")
        exit(1)

def json_to_xml(json_data):
    """
    Converts JSON data to XML format compatible with ConfD.
    """
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <components xmlns="http://openconfig.net/yang/platform">
    """

    components_list = json_data.get("components", {}).get("component", [])
    
    if not isinstance(components_list, list):
        print("❌ Error: 'components.component' should be a list.")
        exit(1)

    for component in components_list:
        xml_data += f"""
            <component>
                <name>{component.get("name", "")}</name>
                <config>
                    <name>{component.get("config", {}).get("name", "")}</name>
                </config>
        """

        # Handle properties
        properties = component.get("properties", {}).get("property", [])
        if properties:
            xml_data += "<properties>"
            for prop in properties:
                xml_data += f"""
                <property>
                    <name>{prop.get("name", "")}</name>
                    <config>
                        <name>{prop.get("config", {}).get("name", "")}</name>
                        <value>{prop.get("config", {}).get("value", "")}</value>
                    </config>
                </property>
                """
            xml_data += "</properties>"

        # Handle subcomponents
        subcomponents = component.get("subcomponents", {}).get("subcomponent", [])
        if subcomponents:
            xml_data += "<subcomponents>"
            for subcomponent in subcomponents:
                xml_data += f"""
                <subcomponent>
                    <name>{subcomponent.get("name", "")}</name>
                    <config>
                        <name>{subcomponent.get("config", {}).get("name", "")}</name>
                    </config>
                </subcomponent>
                """
            xml_data += "</subcomponents>"

        xml_data += "</component>"

    xml_data += "</components></config>"

    with open(XML_PATH, 'w') as xml_file:
        xml_file.write(xml_data.strip())
    
    print(f"✅ JSON data converted to XML and saved to {XML_PATH}")

def load_data_commit():
    """Load the generated XML into ConfD and commit the configuration."""
    cli_commands = f"""
    config
    load merge {XML_PATH}
    show configuration
    commit
    exit
    """

    try:
        subprocess.run([CLI_PATH, "-u", "admin", "-g", "admin"], input=cli_commands.strip(), text=True, check=True)
        print("✅ Data loaded and committed successfully into ConfD.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error loading data into ConfD: {e.stderr.decode()}")
        exit(1)

if __name__ == "__main__":
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: JSON file {JSON_PATH} not found.")
        exit(1)

    # Load JSON data
    with open(JSON_PATH, "r") as file:
        json_data = json.load(file)

    start_confd()
    load_yang()
    json_to_xml(json_data)
    load_data_commit()
