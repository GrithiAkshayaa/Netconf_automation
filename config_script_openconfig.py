import subprocess
import json
import os

CONFD_BIN = "/home/test/confd/bin/confd"
CONFD_ETC = "/home/test/confd/etc/confd"
YANG_PATH = "/home/test/confd/src/openconfig-platform.yang"
JSON_PATH = "/home/test/confd/src/openconfig-platform-config.json"
XML_PATH = "/home/test/confd/src/openconfig-platform-config.xml"
CLI_PATH = "/home/test/confd/bin/confd_cli"

def start_confd():
    subprocess.run([CONFD_BIN], check=True)
    print("Confd server started successfully")

def load_yang():
    subprocess.run([CONFD_BIN, "-c", YANG_PATH, "-o", f"{CONFD_ETC}/openconfig-platform.fxs"], check=True)
    print("YANG model compiled successfully")

def json_to_xml(json_data):
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <components xmlns="http://openconfig.net/yang/platform">
    """
    for component in json_data["components"]:
        xml_data += f"""
            <component>
                <name>{component["name"]}</name>
            </component>
        """
    xml_data += "</components></config>"

    with open(XML_PATH, 'w') as xml_file:
        xml_file.write(xml_data.strip())
    print(f"JSON data converted to XML format and saved to {XML_PATH}")

def load_data_commit():
    cli_commands = f"""
    config
    load merge {XML_PATH}
    show configuration
    commit
    exit
    """

    subprocess.run([CLI_PATH, "-u", "admin", "-g", "admin"], input=cli_commands.strip(), text=True, check=True)
    print("Data loaded and committed successfully into confd")

if __name__ == "__main__":
    with open(JSON_PATH, "r") as file:
        json_data = json.load(file)

    start_confd()
    load_yang()
    json_to_xml(json_data)
    load_data_commit()
