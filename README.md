# File2prompt for Home Assistant Custom integration

## Overview

This repository contains a custom integration for Home Assistant called "File2prompt." The integration connects Home Assistant with an Ollama language model server to analyze data. It allows users to choose an input data file and send it to an Ollama LLM for analysis via Home Assistant. 

---

## Requirements

- Home Assistant with [HACS](https://hacs.xyz/docs/use/) installed  
- Access to File Editor or a way to edit your `configuration.yaml`  
- Running Ollama server or compatible LLM API with token-based authentication  

---

## Installation

1. Open Home Assistant UI and go to **HACS** → **Integrations**.  
2. Click the three dots menu (top right), then **Custom repositories**.  
3. Add this repository URL: `https://github.com/Peacem4kr/file2prompt`  
4. Choose **Integration** as the category and click **Add**.  
5. Back in HACS, search for **File2prompt** and click **Install**.  
6. Restart Home Assistant to complete installation.  

---

## Configuration

### Step 1: Create API Token

Create a token in your Ollama or LLM server interface:

- Give the token a descriptive name (e.g., `HomeAssistant File2prompt`)  
- Copy the token and save it securely  

### Step 2: Add the Integration

1. Go to **Settings** → **Devices & Services** → **Add Integration**.  
2. Search for **File2prompt** and select it.  
3. Fill in the following:  
   - **Ollama Server IP:** Your Ollama server IP address  
   - **Ollama Model Version:** Model name/version you want to use  
   - **Home Assistant URL:** Your Home Assistant base URL  
   - **Create New Text Helper:** Check this to create a helper to store AI responses (max length 1024)  
   - **Select Helper:** Choose the input_text helper for AI responses  
   - **Paste Token:** Paste the token created earlier  
   - **Choose Data Input File:** Select or create an empty input file  
4. Click **Submit**.

You can update these settings later under **Settings → Devices & Services → File2prompt → Configure**.


### Step 3: Add Shell Command to `configuration.yaml`

Add the following to your `configuration.yaml`:
```
shell_command:
  file2prompt: "/config/file2prompt.sh"
```
This shell command is used later in an Automation and triggers the file processing script.
Restart Home Assistant after saving the file.


### Step 4: Create an Automation

```
alias: File2prompt - Send file to Llama (via shell)
description: Trigger sending file contents to the LLM
trigger:
  # Add your trigger here (time, event, button, etc.)
condition: []
action:
  - service: shell_command.file2prompt
mode: single
```

Trigger this automation however you like — from a dashboard button or other event.

---

#Example Use Case: Grocery List Data Analysis with File2prompt

I use this integration to analyze my grocery and to-do behavior by automatically logging items added to my shopping list and then processing that data with AI via File2prompt.

Step 1: Install the File Integration
First, install the standard File Integration in Home Assistant to create a file where the grocery items will be saved:

Go to Settings → Integrations → + Add Integration

Search for and install File

During setup, create a new entry:

Select Set up a notification service

Set File path: /config/www/grocerylog.json

Enable Timestamp

(Optional) Change the entity name, e.g., to Grocerylog

This file service saves grocery items in a JSON file, including timestamps.

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
