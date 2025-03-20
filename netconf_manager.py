import paramiko
from ncclient import manager
import xml.etree.ElementTree as ET

# ConfD NETCONF details
CONFD_HOST = "127.0.0.1"
CONFD_PORT = 2022
USERNAME = "admin"
PASSWORD = "admin"

# Function to establish NETCONF session
def netconf_connect():
    return manager.connect(
        host=CONFD_HOST,
        port=CONFD_PORT,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    )

# Function to create/update configuration
def configure_component(component_name, enabled):
    config_xml = f"""
    <config>
        <components xmlns="http://openconfig.net/yang/platform">
            <component>
                <name>{component_name}</name>
                <config>
                    <enabled>{str(enabled).lower()}</enabled>
                </config>
            </component>
        </components>
    </config>
    """
    with netconf_connect() as m:
        response = m.edit_config(target="candidate", config=config_xml)
        m.commit()
        print(response)

# Function to delete configuration
def delete_component(component_name):
    delete_xml = f"""
    <config>
        <components xmlns="http://openconfig.net/yang/platform">
            <component operation="delete">
                <name>{component_name}</name>
            </component>
        </components>
    </config>
    """
    with netconf_connect() as m:
        response = m.edit_config(target="candidate", config=delete_xml)
        m.commit()
        print(response)

# Function to fetch current configuration
def get_configuration():
    filter_xml = """
    <filter>
        <components xmlns="http://openconfig.net/yang/platform"/>
    </filter>
    """
    with netconf_connect() as m:
        response = m.get(filter=filter_xml)
        print(response.xml)

# Example usage
if __name__ == "__main__":
    configure_component("SLOT3", True)  # Add/update SLOT3
    get_configuration()  # Fetch current config
    delete_component("SLOT3")  # Delete SLOT3
