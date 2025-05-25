"""Constants for the File2prompt integration."""

DOMAIN = "file2prompt"

# Configuration keys
CONF_OLLAMA_IP = "ollama_ip"
CONF_OLLAMA_VERSION = "ollama_version"
CONF_HA_URL = "ha_url"
CONF_HELPER_ENTITY = "helper_entity"
CONF_HA_TOKEN = "ha_token"
CONF_PROMPT = "prompt"
CONF_RESET_PROMPT = "reset_prompt"
CONF_INPUT_FILE = "input_file"
CONF_CREATE_FILE = "create_file"

# Default values
DEFAULT_OLLAMA_VERSION = "llama3.2"
DEFAULT_PROMPT = """Below is my purchase history, including dates. I do groceries weekly (once a week). Do not give any other sentence besides the list. Compare this week's groceries to my normal pattern. Identify purchase frequencies (like weekly or monthly recurring products). Give me a list of products that are missing this week but are normally expected, without showing this week's list. Only give the missing products, on one line, separated by a comma and space. Ignore products that were bought only once, unless that was recent."""
DEFAULT_INPUT_FILE = "/config/www/input_data.json"

# Script related
SCRIPT_FILENAME = "file2prompt.sh"
SCRIPT_PATH = "/config/"

# Error messages
ERROR_INVALID_IP = "Invalid IP address format"
ERROR_INVALID_URL = "Invalid URL format"
ERROR_INVALID_TOKEN = "Invalid token format"
ERROR_INVALID_FILE = "Invalid file path"