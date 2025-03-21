import subprocess
import json
import os

# Paths - Update according to your system setup
CONFD_BIN = "/home/test/confd/bin/confd"
CONFD_CLI = "/home/test/confd/bin/confd_cli"
YANG_MODEL = "/home/test/confd/src/openconfig-platform.yang"
JSON_CONFIG = "/home/test/confd/src/amplifier-config.json"
XML_CONFIG = "/home/test/confd/src/amplifier-config.xml"

def start_confd():
    """Start the ConfD server."""
    try:
        subprocess.run([CONFD_BIN], check=True)
        print("✅ ConfD server started successfully")
    except subprocess.CalledProcessError:
        print("❌ Error starting ConfD")

def validate_yang():
    """Validate the YANG model using pyang."""
    try:
        subprocess.run(["pyang", "-f", "tree", YANG_MODEL], check=True)
        print("✅ YANG model validated successfully")
    except subprocess.CalledProcessError:
        print("❌ YANG model validation failed")

def json_to_xml(json_file, xml_file):
    """Convert JSON configuration to XML format for ConfD."""
    try:
        with open(json_file, "r") as file:
            config_data = json.load(file)

        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <components xmlns="http://openconfig.net/yang/platform">
        """

        for component in config_data.get("components", []):
            xml_data += f"""
            <component>
                <name>{component["name"]}</name>
                <properties>
                    <property>
                        <name>{component["property"]["name"]}</name>
                        <value>{component["property"]["value"]}</value>
                    </property>
                </properties>
            </component>
            """

        xml_data += "</components></config>"

        with open(xml_file, "w") as file:
            file.write(xml_data)

        print(f"✅ JSON converted to XML and saved to {xml_file}")

    except Exception as e:
        print(f"❌ Error converting JSON to XML: {e}")

def load_config():
    """Load the XML configuration into ConfD."""
    cli_commands = f"""
    config
    load merge {XML_CONFIG}
    commit
    exit
    """

    try:
        subprocess.run([CONFD_CLI, "-u", "admin", "-g", "admin"],
                       input=cli_commands.strip(), text=True, check=True)
        print("✅ Configuration loaded and committed successfully into ConfD")
    except subprocess.CalledProcessError:
        print("❌ Error loading configuration into ConfD")

def check_config():
    """Check if the configuration is applied correctly."""
    try:
        result = subprocess.run([CONFD_CLI, "-u", "admin", "-g", "admin", "-c", "show configuration"],
                                text=True, capture_output=True, check=True)
        print("🔍 Current Configuration:\n", result.stdout)
    except subprocess.CalledProcessError:
        print("❌ Error retrieving configuration")

if __name__ == "__main__":
    start_confd()
    validate_yang()
    json_to_xml(JSON_CONFIG, XML_CONFIG)
    load_config()
    check_config()
