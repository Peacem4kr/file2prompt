"""The File2prompt integration."""
import os
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_OLLAMA_IP,
    CONF_OLLAMA_VERSION,
    CONF_HA_URL,
    CONF_HELPER_ENTITY,
    CONF_HA_TOKEN,
    CONF_PROMPT,
    CONF_INPUT_FILE,
    SCRIPT_FILENAME,
    SCRIPT_PATH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up File2prompt from a config entry."""
    # Store the entry data in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Create the script path if it doesn't exist
    os.makedirs(SCRIPT_PATH, exist_ok=True)
    
    # Ensure the script is executable
    script_path = os.path.join(SCRIPT_PATH, SCRIPT_FILENAME)
    if os.path.exists(script_path):
        os.chmod(script_path, 0o755)
        _LOGGER.info("Made File2prompt script executable")
    else:
        _LOGGER.warning("Script file not found at %s", script_path)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the entry data from hass.data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # If this was the last entry, remove the domain data too
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    # Remove the generated script file when integration is removed
    script_path = os.path.join(SCRIPT_PATH, SCRIPT_FILENAME)
    if os.path.exists(script_path):
        try:
            os.remove(script_path)
            _LOGGER.info(f"Removed script file: {script_path}")
        except Exception as e:
            _LOGGER.error(f"Failed to remove script file: {e}")
            
    return True