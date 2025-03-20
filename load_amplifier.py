import subprocess
import json
import os

# Paths
CONFD_BIN = "/home/confd/bin"
YANG_PATH = "/home/confd/src/openconfig-platform.yang"
JSON_PATH = "/home/confd/src/amplifier-data.json"
XML_PATH = "/home/confd/src/amplifier-data.xml"
CLI_PATH = "/home/confd/bin/confd_cli"

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

    # Save CLI commands to a file
    cli_cmd_path = "/home/confd/src/cli_commands.txt"
    with open(cli_cmd_path, 'w') as file:
        file.write(cli_commands.strip())

    # Run ConfD CLI with the generated commands
    subprocess.run(
        [CLI_PATH, "-u", "admin", "-g", "admin", "-C", "-f", cli_cmd_path],
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
    with open(JSON_PATH, 'r') as file:
        json_data = json.load(file)
    
    start_confd()
    load_yang()
    json_to_xml(json_data)
    load_data()
    commit_data()
