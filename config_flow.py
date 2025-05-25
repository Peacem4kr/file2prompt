"""Config flow for File2prompt integration."""
import os
import re
import logging
import ipaddress
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.template import Template


def ensure_single_line(prompt):
    """Ensure the prompt is on a single line with no line breaks."""
    if not prompt:
        return ""
    # Join all lines with spaces, removing any extra whitespace
    return " ".join(line.strip() for line in prompt.splitlines())


from .const import (
    DOMAIN,
    CONF_OLLAMA_IP,
    CONF_OLLAMA_VERSION,
    CONF_HA_URL,
    CONF_HELPER_ENTITY,
    CONF_HA_TOKEN,
    CONF_PROMPT,
    CONF_RESET_PROMPT,
    CONF_INPUT_FILE,
    CONF_CREATE_FILE,
    DEFAULT_OLLAMA_VERSION,
    DEFAULT_PROMPT,
    DEFAULT_INPUT_FILE,
    SCRIPT_FILENAME,
    SCRIPT_PATH,
    ERROR_INVALID_IP,
    ERROR_INVALID_URL,
    ERROR_INVALID_TOKEN,
    ERROR_INVALID_FILE,
)

_LOGGER = logging.getLogger(__name__)

class File2promptConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for File2prompt."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Get all input_text entities for dropdown selection
        input_text_entities = [
            entity_id
            for entity_id in self.hass.states.async_entity_ids("input_text")
        ]
        
        if not user_input:
            # Provide form with defaults and entity selector
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_OLLAMA_IP): str,
                        vol.Required(CONF_OLLAMA_VERSION, default=DEFAULT_OLLAMA_VERSION): str,
                        vol.Required(CONF_HA_URL): str,
                        vol.Required(CONF_HELPER_ENTITY): selector.EntitySelector(
                            selector.EntitySelectorConfig(
                                domain="input_text",
                                multiple=False,
                            ),
                        ),
                        vol.Required(CONF_HA_TOKEN): str,
                        vol.Required(CONF_INPUT_FILE, default=DEFAULT_INPUT_FILE): str,
                        vol.Optional(CONF_CREATE_FILE, default=False): bool,
                    }
                ),
                errors=errors,
            )
        
        # Validate inputs
        ollama_ip = user_input[CONF_OLLAMA_IP].strip()
        try:
            ipaddress.ip_address(ollama_ip)
        except ValueError:
            errors[CONF_OLLAMA_IP] = ERROR_INVALID_IP
        
        ha_url = user_input[CONF_HA_URL].strip()
        if not ha_url.startswith(("http://", "https://")):
            errors[CONF_HA_URL] = ERROR_INVALID_URL
            
        helper_entity = user_input[CONF_HELPER_ENTITY].strip()
        if not helper_entity.startswith("input_text."):
            errors[CONF_HELPER_ENTITY] = "invalid_entity"
            
        ha_token = user_input[CONF_HA_TOKEN].strip()
        if len(ha_token) < 5:  # Simple validation for token
            errors[CONF_HA_TOKEN] = ERROR_INVALID_TOKEN
            
        input_file = user_input[CONF_INPUT_FILE].strip()
        if not input_file.startswith("/config/"):
            errors[CONF_INPUT_FILE] = ERROR_INVALID_FILE
        
        if not errors:
            # All validation passed, set up integration
            ollama_version = user_input[CONF_OLLAMA_VERSION].strip()
            
            # Generate the script file
            try:
                # Use the default prompt initially
                script_content = self._generate_script(
                    ollama_ip,
                    ollama_version,
                    ha_url,
                    helper_entity,
                    ha_token,
                    DEFAULT_PROMPT,
                    input_file,
                )
                
                # Ensure the script directory exists
                os.makedirs(SCRIPT_PATH, exist_ok=True)
                
                # Write the script file
                script_path = os.path.join(SCRIPT_PATH, SCRIPT_FILENAME)
                with open(script_path, "w") as script_file:
                    script_file.write(script_content)
                
                # Make the script executable
                os.chmod(script_path, 0o755)
                
                # Create input file if it doesn't exist and option is selected
                if user_input.get(CONF_CREATE_FILE, False) and not os.path.exists(input_file):
                    # Create directory if needed
                    os.makedirs(os.path.dirname(input_file), exist_ok=True)
                    
                    # Create an empty file
                    with open(input_file, "w") as f:
                        f.write('{"data": "Sample data for File2prompt"}')
            
            except Exception as e:
                _LOGGER.error(f"Failed to set up integration: {e}")
                errors["base"] = "cannot_write"
            
            if not errors:
                # Store configuration (without the default prompt to keep proper UI in options)
                title = f"File2prompt ({ollama_ip})"
                return self.async_create_entry(title=title, data=user_input)
        
        # Show form with errors
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OLLAMA_IP, default=user_input.get(CONF_OLLAMA_IP, "")): str,
                    vol.Required(CONF_OLLAMA_VERSION, default=user_input.get(CONF_OLLAMA_VERSION, DEFAULT_OLLAMA_VERSION)): str,
                    vol.Required(CONF_HA_URL, default=user_input.get(CONF_HA_URL, "")): str,
                    vol.Required(CONF_HELPER_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="input_text",
                            multiple=False,
                        ),
                    ),
                    vol.Required(CONF_HA_TOKEN, default=user_input.get(CONF_HA_TOKEN, "")): str,
                    vol.Required(CONF_INPUT_FILE, default=user_input.get(CONF_INPUT_FILE, DEFAULT_INPUT_FILE)): str,
                    vol.Optional(CONF_CREATE_FILE, default=user_input.get(CONF_CREATE_FILE, False)): bool,
                }
            ),
            errors=errors,
        )

    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return File2promptOptionsFlow(config_entry)
        
    def _generate_script(self, ollama_ip, ollama_version, ha_url, helper_entity, ha_token, prompt=None, input_file=None):
        """Generate the shell script content."""
        if prompt is None:
            prompt = DEFAULT_PROMPT
            
        if input_file is None:
            input_file = DEFAULT_INPUT_FILE
            
        # Ensure prompt is on a single line (replace any newlines with spaces)
        single_line_prompt = ensure_single_line(prompt)
        
        # Prepare prompt for script - escape special characters and format for shell
        prompt_formatted = single_line_prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        # Create log filename based on input file
        log_filename = os.path.basename(input_file).split('.')[0] + ".log"
        
        return f"""#!/bin/bash
exec > /config/www/{log_filename} 2>&1
set -x

INPUT_FILE="{input_file}"
HA_URL="{ha_url}"
HA_TOKEN="{ha_token}"

# Read contents of input file and remove escape characters
FILE_CONTENT=$(cat "$INPUT_FILE" | tr -d '\\n' | sed 's/"/\\\\"/g')

# Create prompt
PROMPT="{prompt_formatted}\\n\\nHere is the content:\\n$FILE_CONTENT"

# Build JSON payload
JSON="{{\\\"model\\\":\\\"{ollama_version}\\\",\\\"prompt\\\":\\\"$PROMPT\\\",\\\"stream\\\":false}}"

# Send to Ollama
RESPONSE=$(curl -s -X POST "http://{ollama_ip}:11434/api/generate" \\
    -H "Content-Type: application/json" \\
    -d "$JSON")

# Extract response without jq
SUMMARY=$(echo "$RESPONSE" | grep -o '"response":"[^"]*' | cut -d'"' -f4)

# Fallback if no response
if [ -z "$SUMMARY" ]; then
  SUMMARY="No response received from Ollama."
fi
  
# Save to input_text helper (for dashboard display)
curl -X POST -H "Authorization: Bearer $HA_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d "{{\\\"state\\\": \\\"$SUMMARY\\\"}}" \\
     "$HA_URL/api/states/{helper_entity}"
"""


class File2promptOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for File2prompt."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        # Read the current prompt directly from the script file
        import re
        script_path = os.path.join(SCRIPT_PATH, SCRIPT_FILENAME)
        current_prompt_from_file = ""
        if os.path.exists(script_path):
            try:
                with open(script_path, "r") as script_file:
                    script_content = script_file.read()
                    # Simple approach to extract the raw PROMPT value from the script file
                    # Get the line containing PROMPT=
                    script_lines = script_content.split('\n')
                    for line in script_lines:
                        if line.strip().startswith('PROMPT='):
                            # Found the PROMPT line, now extract its value
                            prompt_line = line.strip()
                            
                            # Remove the 'PROMPT=' part and any quotes around it
                            if "'$PROMPT'" in prompt_line:  # It's a variable reference
                                # Try to find where the PROMPT variable is defined
                                for var_line in script_lines:
                                    if var_line.strip().startswith('PROMPT="') or var_line.strip().startswith("PROMPT='"):
                                        prompt_line = var_line.strip()
                                        break
                                        
                            # Now extract the value from something like: PROMPT="value" or PROMPT='value'
                            if prompt_line.startswith('PROMPT="'):
                                # Double-quoted value
                                prompt_value = prompt_line[8:-1]  # Remove PROMPT=" and the ending "
                                
                                # Clean up the prompt value - remove the "Here is the content" part
                                if "\\n\\nHere is the" in prompt_value:
                                    prompt_value = prompt_value.split("\\n\\nHere is the")[0]
                                elif "\\n\\nHere is the list" in prompt_value:
                                    prompt_value = prompt_value.split("\\n\\nHere is the list")[0]
                                elif "\\n\\nHere is" in prompt_value:
                                    prompt_value = prompt_value.split("\\n\\nHere is")[0]
                                    
                                # Convert to single line without breaks
                                current_prompt_from_file = prompt_value.replace('\\n', ' ').replace('\\"', '"')
                                break
                            elif prompt_line.startswith("PROMPT='"):
                                # Single-quoted value
                                prompt_value = prompt_line[8:-1]  # Remove PROMPT=' and the ending '
                                
                                # Clean up the prompt value - remove the "Here is the content" part
                                if "\\n\\nHere is the" in prompt_value:
                                    prompt_value = prompt_value.split("\\n\\nHere is the")[0]
                                elif "\\n\\nHere is the list" in prompt_value:
                                    prompt_value = prompt_value.split("\\n\\nHere is the list")[0]
                                elif "\\n\\nHere is" in prompt_value:
                                    prompt_value = prompt_value.split("\\n\\nHere is")[0]
                                    
                                # Convert to single line without breaks
                                current_prompt_from_file = prompt_value.replace('\\n', ' ').replace("\\'", "'")
                                break
                                
                            _LOGGER.info(f"Extracted raw PROMPT from script file")
                            _LOGGER.info(f"Read prompt from script file: {current_prompt_from_file[:20]}...")
            except Exception as e:
                _LOGGER.error(f"Error reading prompt from script file: {e}")
        
        if user_input is not None:
            # Validate IP address
            ollama_ip = user_input[CONF_OLLAMA_IP].strip()
            try:
                ipaddress.ip_address(ollama_ip)
            except ValueError:
                errors[CONF_OLLAMA_IP] = ERROR_INVALID_IP
            
            ha_url = user_input[CONF_HA_URL].strip()
            if not ha_url.startswith(("http://", "https://")):
                errors[CONF_HA_URL] = ERROR_INVALID_URL
                
            helper_entity = user_input[CONF_HELPER_ENTITY].strip()
            if not helper_entity.startswith("input_text."):
                errors[CONF_HELPER_ENTITY] = "invalid_entity"
                
            ha_token = user_input[CONF_HA_TOKEN].strip()
            if len(ha_token) < 5:  # Simple validation for token
                errors[CONF_HA_TOKEN] = ERROR_INVALID_TOKEN
                
            input_file = user_input[CONF_INPUT_FILE].strip()
            if not input_file.startswith("/config/"):
                errors[CONF_INPUT_FILE] = ERROR_INVALID_FILE
            
            # If validation passed, update script
            if not errors:
                ollama_version = user_input[CONF_OLLAMA_VERSION].strip()
                
                # Determine what prompt to use
                if user_input.get(CONF_RESET_PROMPT, False):
                    # Reset to default grocery analysis prompt
                    prompt = DEFAULT_PROMPT
                    # Update the user_input so the UI shows the default prompt
                    user_input[CONF_PROMPT] = prompt
                else:
                    # Use the user-provided prompt or the existing one
                    prompt = user_input.get(CONF_PROMPT, "").strip()
                    if not prompt:
                        prompt = DEFAULT_PROMPT
                
                # Update script with new values
                try:
                    script_content = self._generate_script(
                        ollama_ip,
                        ollama_version,
                        ha_url,
                        helper_entity,
                        ha_token,
                        prompt,
                        input_file,
                    )
                    
                    script_path = os.path.join(SCRIPT_PATH, SCRIPT_FILENAME)
                    
                    # Write file with error handling
                    with open(script_path, "w") as script_file:
                        script_file.write(script_content)
                    
                    # Make the script executable
                    os.chmod(script_path, 0o755)
                    
                    _LOGGER.info("Updated script successfully with new values")
                    
                    # Update config entry with new values
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data={
                            **self.config_entry.data,
                            CONF_OLLAMA_IP: ollama_ip,
                            CONF_OLLAMA_VERSION: ollama_version,
                            CONF_HA_URL: ha_url,
                            CONF_HELPER_ENTITY: helper_entity,
                            CONF_HA_TOKEN: ha_token,
                            CONF_INPUT_FILE: input_file,
                            CONF_PROMPT: prompt,
                        },
                    )
                    
                    # Return updated options
                    return self.async_create_entry(title="", data={})
                except Exception as e:
                    _LOGGER.error(f"Failed to update script: {e}")
                    errors["base"] = "cannot_write"
                    
        # Collect current data
        current_config = dict(self.config_entry.data)
        
        # Show form with current values
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_OLLAMA_IP, 
                        default=current_config.get(CONF_OLLAMA_IP, "")
                    ): str,
                    vol.Required(
                        CONF_OLLAMA_VERSION, 
                        default=current_config.get(CONF_OLLAMA_VERSION, DEFAULT_OLLAMA_VERSION)
                    ): str,
                    vol.Required(
                        CONF_HA_URL, 
                        default=current_config.get(CONF_HA_URL, "")
                    ): str,
                    vol.Required(
                        CONF_HELPER_ENTITY,
                        default=current_config.get(CONF_HELPER_ENTITY, "")
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="input_text",
                            multiple=False,
                        ),
                    ),
                    vol.Required(
                        CONF_HA_TOKEN, 
                        default=current_config.get(CONF_HA_TOKEN, "")
                    ): str,
                    vol.Required(
                        CONF_INPUT_FILE, 
                        default=current_config.get(CONF_INPUT_FILE, DEFAULT_INPUT_FILE)
                    ): str,
                    vol.Optional(
                        CONF_PROMPT, 
                        default=current_prompt_from_file or current_config.get(CONF_PROMPT, DEFAULT_PROMPT)
                    ): str,
                    vol.Optional(
                        CONF_RESET_PROMPT, 
                        default=False
                    ): bool,
                }
            ),
            errors=errors,
        )

    def _generate_script(self, ollama_ip, ollama_version, ha_url, helper_entity, ha_token, prompt=None, input_file=None):
        """Generate the shell script content."""
        if prompt is None:
            prompt = DEFAULT_PROMPT
            
        if input_file is None:
            input_file = DEFAULT_INPUT_FILE
            
        # Ensure prompt is on a single line (replace any newlines with spaces)
        single_line_prompt = ensure_single_line(prompt)
        
        # Prepare prompt for script - escape special characters and format for shell
        prompt_formatted = single_line_prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        # Create log filename based on input file
        log_filename = os.path.basename(input_file).split('.')[0] + ".log"
        
        return f"""#!/bin/bash
exec > /config/www/{log_filename} 2>&1
set -x

INPUT_FILE="{input_file}"
HA_URL="{ha_url}"
HA_TOKEN="{ha_token}"

# Read contents of input file and remove escape characters
FILE_CONTENT=$(cat "$INPUT_FILE" | tr -d '\\n' | sed 's/"/\\\\"/g')

# Create prompt
PROMPT="{prompt_formatted}\\n\\nHere is the content:\\n$FILE_CONTENT"

# Build JSON payload
JSON="{{\\\"model\\\":\\\"{ollama_version}\\\",\\\"prompt\\\":\\\"$PROMPT\\\",\\\"stream\\\":false}}"

# Send to Ollama
RESPONSE=$(curl -s -X POST "http://{ollama_ip}:11434/api/generate" \\
    -H "Content-Type: application/json" \\
    -d "$JSON")

# Extract response without jq
SUMMARY=$(echo "$RESPONSE" | grep -o '"response":"[^"]*' | cut -d'"' -f4)

# Fallback if no response
if [ -z "$SUMMARY" ]; then
  SUMMARY="No response received from Ollama."
fi
  
# Save to input_text helper (for dashboard display)
curl -X POST -H "Authorization: Bearer $HA_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d "{{\\\"state\\\": \\\"$SUMMARY\\\"}}" \\
     "$HA_URL/api/states/{helper_entity}"
"""
