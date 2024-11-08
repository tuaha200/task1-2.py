from netmiko import ConnectHandler
import difflib

# Device connection details
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.56.101',  # Ensure the correct IP address
    'username': 'prne',        # Username for SSH login
    'password': 'cisco123!',   # Password for SSH login
    'secret': 'cisco12345!',   # Enable password for privileged exec mode
    'verbose': True,           # Enable verbose output for debugging
}

# Connect to the device
try:
    connection = ConnectHandler(**device)
    print("Connection established successfully.")
    connection.enable()  # Enter enable mode (privileged exec mode)
except Exception as e:
    print(f"Error connecting to the device: {e}")
    exit(1)

# Retrieve the running and startup configurations
running_config = connection.send_command('show running-config')
startup_config = connection.send_command('show startup-config')

# Store the configurations in text files
with open('running_config.txt', 'w') as run_file:
    run_file.write(running_config)

with open('startup_config.txt', 'w') as start_file:
    start_file.write(startup_config)

# Disconnect after file operations
connection.disconnect()
print("Configs retrieved and stored successfully.")

# Compare running and startup configuration using difflib
diff = difflib.unified_diff(
    running_config.splitlines(),
    startup_config.splitlines(),
    fromfile='Running-config',
    tofile='Startup-config',
    lineterm=''
)

# Print the differences
print("\nDifferences between Running and Startup Configs:")
print('\n'.join(list(diff)))

# Define the hardening checks (instead of using a large string)
hardening_checks = {
    "SSH enabled": "ip ssh version 2",
    "Telnet disabled": "no service telnet",
    "Password encryption": "service password-encryption",
    "Logging enabled": "logging buffered",
    "NTP configured": "ntp server",
    "Enable secret password set": "enable secret cisco12345!",
    "VTY lines secured": "transport input ssh",
}

# Define commands for hardening configuration
hardening_commands = [
    "service password-encryption",  # Encrypt passwords
    "no ip http server",            # Disable HTTP server
    "no ip http secure-server",     # Disable HTTPS server
    "ip ssh version 2",             # Enable SSH version 2
    "no service telnet",            # Disable Telnet
    "logging buffered",             # Enable local logging
    "logging trap informational",  # Set logging level to informational
    "ntp server 192.168.1.100",    # Configure NTP server
    "banner motd # Unauthorized access is prohibited!",  # Example banner
    "enable secret cisco12345!",    # Secure enable password
    "line vty 0 4",                 # Configure VTY lines
    "login local",                  # Use local authentication
    "transport input ssh"           # Only allow SSH access
]

def check_hardening(running_config):
    # Loop through the hardening checks
    for check, rule in hardening_checks.items():
        if rule in running_config:
            print(f"[PASS] {check}")
        else:
            print(f"[FAIL] {check}")

# Perform hardening checks on the running config
check_hardening(running_config)

# Apply hardening commands to the device
connection = ConnectHandler(**device)
connection.enable()  # Enter enable mode

for command in hardening_commands:
    print(f"Applying command: {command}")
    connection.send_command(f"configure terminal\n{command}")

# Save the configuration
connection.send_command('write memory')

# Print confirmation
print("Hardening configuration applied successfully.")

# Configure syslog server (replace with your syslog server IP)
syslog_server = '192.168.1.100'  # Replace with your syslog server IP

# Send command to configure syslog
syslog_config_command = f"logging {syslog_server}"

# Apply the syslog configuration to the device
connection.send_command(syslog_config_command)
print(f"Syslog configured to send logs to {syslog_server}")

# Close the connection
connection.disconnect()