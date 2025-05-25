# File2prompt for Home Assistant

## Overview

This repository contains a custom integration for Home Assistant called "File2prompt." The integration connects Home Assistant with an Ollama language model server to analyze data. It allows users to choose a input data file and send it to an Ollama LLM for analysis via Home Assistant. 

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The system is built as a Home Assistant custom integration that communicates with an external Ollama server. The integration follows the standard Home Assistant integration structure with config flows for user configuration.

The architecture consists of:

1. **Home Assistant Integration Layer**: Manages configuration and interaction with Home Assistant
2. **Script Generation Component**: Creates a shell script to handle the communication with the Ollama server
3. **External Ollama Server**: Hosts the LLM model that performs the analysis (not part of this repository)

The integration uses a shell script to make API calls to both the Ollama server and back to Home Assistant, which is generated during setup rather than being a Python component.

## Key Components

### 1. Integration Initialization (`__init__.py`)
- Sets up the integration and stores configuration data
- Creates necessary directories for the script
- Handles lifecycle events like loading and unloading

### 2. Configuration Flow (`config_flow.py`)
- Implements the UI configuration flow for setup in Home Assistant
- Validates user input (IP addresses, URLs, entity selections)
- Creates the configuration entry in Home Assistant

### 3. Constants (`const.py`)
- Defines all constant values used throughout the integration
- Includes configuration keys, default values, and error messages

### 4. Manifest and Translations
- `manifest.json`: Declares integration metadata for Home Assistant
- `strings.json` and translations: Provide localized text for the UI

## Data Flow

1. User enters data into the configured input_text helper entity in Home Assistant
2. The generated script reads this data from the input_text entity
3. The script sends the data to the Ollama server for analysis using its API
4. The Ollama server processes the data with the configured LLM model
5. Results are sent back to Home Assistant and stored in the helper entity

## External Dependencies

1. **Home Assistant**: The platform this integration runs on
2. **Ollama Server**: External server running the LLM model (referenced by IP address)
3. **voluptuous**: Used for schema validation in the configuration flow

## Deployment Strategy

The integration is designed to be deployed in a standard Home Assistant environment:

1. The code should be placed in the `custom_components` directory of a Home Assistant installation
2. Configuration is done through the Home Assistant UI using the config flow
3. A shell script is generated at runtime and placed in the Home Assistant configuration directory
4. The integration requires network access to both the Home Assistant instance and the Ollama server

### Development Environment

The repository is configured to run in a Replit environment with:
- Python 3.11
- Home Assistant development server running with a local configuration directory
- Dependencies automatically installed via pip (homeassistant, voluptuous)

## Technical Notes

- The integration doesn't directly use any databases but relies on Home Assistant's state machine
- Authentication to Home Assistant is required for the script to function
- The script needs proper error handling for network issues and API failures
- Consider adding validation to check if the Ollama server is reachable during setup

## Documentation

- 
