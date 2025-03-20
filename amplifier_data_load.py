import subprocess
import json
import os

# Base Paths (Updated according to your structure)
BASE_DIR = "/home/test/confd"
CONFD_BIN = f"{BASE_DIR}/bin"
SRC_DIR = f"{BASE_DIR}/src"
SCRIPT_DIR = f"{BASE_DIR}/scripts"
PUBLIC_DIR = f"{BASE_DIR}/public-5.0.0/release/models/platform"

# YANG Model Path
YANG_PATH = f"{PUBLIC_DIR}/openconfig-platform.yang"

# Data Paths
JSON_PATH = f"{SRC_DIR}/amplifier_data.json"
XML_PATH = f"{SRC_DIR}/amplifier_data.xml"
CLI_PATH = f"{CONFD_BIN}/confd_cli"
CLI_CMD_PATH = f"{SRC_DIR}/cli_commands.txt"

# Step 1: Start ConfD
def start_confd():
    subprocess.run([f"{CONFD_BIN}/confd"], check=True)
    print("✅ ConfD server started successfully.")

# Step 2: Load YANG Model
def load_yang():
    cmd = [
        f"{CONFD_BIN}/confdc",
        "-c", YANG_PATH,
        "-o", f"{CONFD_BIN}/openconfig-platform.fxs"
    ]
    subprocess.run(cmd, check=True)
    print("✅ YANG model compiled successfully.")

# Step 3: Convert JSON Data to XML Format
def json_to_xml(json_data):
    xml_data = '<components>'
    for amp in json_data['components']['component']:
        xml_data += f"""
        <component>
            <name>{amp['name']}</name>
            <config>
                <name>{amp['config']['name']}</name>
            </config>
        </component>"""
    xml_data += '</components>'

    with open(XML_PATH, 'w') as xml_file:
        xml_file.write(xml_data)
    print(f"✅ JSON data converted to XML format and saved to {XML_PATH}")

# Step 4: Load Data Using ConfD CLI
def load_data():
    cli_commands = f"""
    config
    load merge {XML_PATH}
    commit
    exit
    """

    with open(CLI_CMD_PATH, 'w') as file:
        file.write(cli_commands.strip())

    subprocess.run(
        [CLI_PATH, "-u", "admin", "-g", "admin", "-C", "-f", CLI_CMD_PATH],
        check=True
    )
    print("✅ Data loaded successfully using ConfD CLI.")

# Step 5: Commit Data Using ConfD CLI
def commit_data():
    cmd = [
        CLI_PATH,
        "-u", "admin",
        "-g", "admin",
        "-C",
        "-c", "show running-config"
    ]
    subprocess.run(cmd, check=True)
    print("✅ Configuration committed successfully using ConfD CLI.")

# Step 6: Main Execution Flow
if __name__ == "__main__":
    json_file_path = JSON_PATH
    if not os.path.exists(json_file_path):
        print(f"❌ Error: JSON file not found at {json_file_path}")
        exit(1)

    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
    
    start_confd()
    load_yang()
    json_to_xml(json_data)
    load_data()
    commit_data()
