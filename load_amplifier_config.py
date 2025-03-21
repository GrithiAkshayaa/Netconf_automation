import json

# Function to load amplifier configuration from JSON file
def load_amplifier_config(json_file):
    try:
        with open(json_file, "r") as file:
            config_data = json.load(file)

            # Validate if the essential structure is present
            if not isinstance(config_data, dict) or "components" not in config_data:
                raise ValueError("Invalid JSON format: Missing 'components' key.")

            return config_data
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file}.")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None

# Function to process amplifier configuration safely
def apply_amplifier_config(config_data):
    if not config_data:
        print("No valid configuration found.")
        return

    components = config_data.get("components", {}).get("component", [])
    
    for component in components:
        name = component.get("name", "Unknown")
        print(f"\nApplying configuration for amplifier: {name}")

        # Shelf and Slot Details
        shelf = component.get("shelf", {})
        shelf_name = shelf.get("name", "N/A")
        slot = shelf.get("slot", {})
        slot_name = slot.get("name", "N/A")
        print(f"  Shelf: {shelf_name}")
        print(f"  Slot: {slot_name}")

        # Port Configurations
        ports = slot.get("ports", {}).get("port", [])
        if not isinstance(ports, list):
            print("  Warning: Ports data structure is incorrect, skipping...")
        else:
            for port in ports:
                port_name = port.get("name", "Unknown")
                port_status = port.get("config", {}).get("status", "Unknown")
                print(f"  - Port: {port_name}, Status: {port_status}")

        # Processing Properties
        properties = component.get("properties", {}).get("property", [])
        if not isinstance(properties, list):
            print("  Warning: Properties data structure is incorrect, skipping...")
        else:
            for prop in properties:
                prop_name = prop.get("name", "Unknown")
                prop_value = prop.get("config", {}).get("value", "Unknown")
                print(f"  - Setting {prop_name}: {prop_value}")

        print("Configuration applied successfully!\n")

# Load and apply amplifier configuration
json_file = "amplifier_config.json"
config_data = load_amplifier_config(json_file)
apply_amplifier_config(config_data)
