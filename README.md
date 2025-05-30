# File2prompt for Home Assistant - Custom integration

## Overview

This repository contains a custom integration with a user friendly UI for Home Assistant called "File2prompt." 

The integration connects Home Assistant with a local Ollama language model server to analyze data. It allows users to choose an input data file and send it to an Ollama LLM for analysis via Home Assistant. 

---

## Requirements

- Home Assistant with [HACS](https://hacs.xyz/docs/use/) installed  
- Access to [File Editor](https://www.home-assistant.io/common-tasks/supervised/) or a way to edit your `configuration.yaml`  
- Running [Ollama](https://github.com/ollama/ollama/blob/main/README.md) server or compatible LLM API with token-based authentication



## Installation

1. Open Home Assistant UI and go to **HACS** → **Integrations**.  
2. Click the three dots menu (top right), then **Custom repositories**.  
3. Add this repository URL: `https://github.com/Peacem4kr/file2prompt`
4. **Download** 
5. Restart Home Assistant


## Configuration

### Step 1: Create API Token

Create a token for your Ollama LLM server in Home Assistant:
1. Open your profile
2. Security - scroll down to Long-lived access tokens
3. Create Token
4. Give the token a descriptive name (e.g., `HomeAssistant File2prompt`)
5. Copy the token into memory  


### Step 2: Add the Integration

1. Go to **Settings** → **Devices & Services** → **Add Integration**.  
2. Search for **File2prompt** and select it.  
3. Fill in the following:  
   - **Ollama Server IP:** Your Ollama server IP address  
   - **Ollama Model Version:** Model name/version you want to use  
   - **Home Assistant URL:** Your Home Assistant base URL  
   - **Create New Text Helper:** Ccreate a helper to store AI responses (max length 1024)  
   - **Select Helper:** Choose the input_text helper for AI responses  
   - **Paste Token:** Paste the token created/copied earlier  
   - **Choose Data Input File:** Provide the filename + full path. (this file should contain your data to analyze), checking **"Create file if it doesn't exist?"** will create a file :)
4. Click **Submit**.
   

You can update these settings later under **Settings → Devices & Services → File2prompt → Configure**.

The prompt can be changed here aswell. (at the moment the prompt is not showing correctly what is setup, meaning that u can save a new prompt - it will work - but the interface will keep showing the default - use the **Reset prompt to default** to apply the default)


### Step 3: Add Shell Command to `configuration.yaml`

   Add the following to your `configuration.yaml`:
   ```
   shell_command:
     file2prompt: "/config/file2prompt.sh"
   ```
This [shell command](https://www.home-assistant.io/integrations/shell_command/) is used later in an Automation and triggers the file processing script.

Restart Home Assistant after saving the configuration.yaml file.


### Step 4: Create an Automation

The automation is required to trigger the integration to run once (sending the input file to the LLM and returning a respond)

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

Trigger this automation however you like — from a dashboard button (then u can leave the trigger part empty), or add an other trigger into this automation.


---

---


## Example Use Case: Grocery List Data Analysis with File2prompt

I use the File2prompt integration to analyze my grocery purchasing behavior by automatically logging the items i add to my shopping list, then processing that data with AI.
The idea is that my LLM can suggest products that i could have missed on my grocery list.

Let's continue the setup.

In a nutshell, i use the "File" integration as this allows me to save data with a timestamp into a file quite easy - an automation will be created that triggers when an new item is added to the shopping list, it then adds the item to a file (with timestamp).

### Step 1: Install the File Integration

1. First, install the standard [File](https://www.home-assistant.io/integrations/file/) Integration in Home Assistant to create a file where we will save the grocery items
2. Go to Settings → Integrations → + Add Integration
3. Search for and install **File**
4. During setup, create a new entry:
 - Select Set up a notification service
 - Set File path: /config/www/grocerylog.json
 - Enable Timestamp
 - (Optional) Change the entity name, e.g., to Grocerylog once saved

This JSON file will be used to save my grocery items in, including timestamps.


### Step 2: Install the "Shopping list" Integration

1. Install the standard [Shopping list](https://www.home-assistant.io/integrations/shopping_list) Integration in Home Assistant to create a shopping list (and start using it as main grocery list :D)
2. Go to Settings → Integrations → + Add Integration
3. Search for and install **Shopping list**

*In some shops with "client-cards" you can request your purchase history which u can manually add to grocerylog.json (mind the timeformat, ask any LLM to fix it otherwise)*

### Step 3: Automation to Save Grocery Items to File

Create an automation that automatically saves every new item added to your shopping list into the file created with the file intgeration:

```
alias: Grocery - Save todo to file
description: ""
triggers:
  - event_type: shopping_list_updated
    event_data:
      action: add
    trigger: event
conditions: []
actions:
  - data:
      message: "{{ trigger.event.data.item.name }}"
    action: notify.send_message
    enabled: true
    target:
      entity_id:
        - notify.file
mode: single

```

Make sure to check that your file/ entity is added correctly.
Via the visual reprentation remove/add the correct File/Entity (created by the **[File](https://www.home-assistant.io/integrations/file/) integration)**

### Dashboard
I have created A simple dashboard that 
- Shows the todo list
- Has a button to trigger the File2prompt integration (send my grocerylog.json to my LLM together with a prompt)
- Shows the respond from AI

**I use the [Mushroom](https://github.com/piitaya/lovelace-mushroom) addon from HACS if you just want to copy paste**



```
type: sections
max_columns: 4
title: Boodschappenlijst
path: boodschappenlijst
icon: mdi:cart
sections:
  - type: grid
    cards:
      - type: heading
        heading_style: title
      - display_order: alpha_asc
        type: todo-list
        entity: todo.shopping_list
        hide_create: false
        hide_completed: true
  - type: grid
    cards:
      - type: heading
        heading_style: title
      - type: custom:mushroom-entity-card
        entity: automation.file2prompt_send_file_to_llama_via_shell
        icon_color: green
        fill_container: false
        layout: horizontal
        name: Duw op mij en vraag AI voor suggesties
        primary_info: name
        secondary_info: none
        tap_action:
          action: perform-action
          perform_action: automation.trigger
          target:
            entity_id: automation.file2prompt_send_file_to_llama_via_shell
          data:
            skip_condition: true
        hold_action:
          action: none
        double_tap_action:
          action: none
      - type: markdown
        content: |
          **🛒 Voorgestelde artikels:**   
          {{ states('input_text.myhelper') }}
header: {}
theme: synthwave
cards: []
subview: false


```

### **Make sure that you modify the File2prompt integration to use the correct data input file!**

I use this prompt: Below is my purchase history, including dates. I do groceries weekly (once a week). Do not give any other sentence besides the list. Compare this week's groceries to my normal pattern. Identify purchase frequencies (like weekly or monthly recurring products). Give me a list of products that are missing this week but are normally expected, without showing this week's list. Only give the missing products, on one line, separated by a comma and space. Ignore products that were bought only once, unless that was recent

---
## Troubleshooting

The script is located in \\homeassistantIP\config and is called file2prompt.sh
Add this to that file if you want the AI reponse to be registered in a file:
```
# Save response to JSON file
echo "{\"response\": \"$SUMMARY\"}" > /config/www/ai_reponse.json`
```
There is a log file available where u can check what the AI is doing /config/www/grocerylog.log

---
---
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
