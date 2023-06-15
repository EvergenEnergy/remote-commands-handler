# Remote Commands Handler

Remote Commands Handler is a Python application that handles remote commands via MQTT and Modbus protocols. The application listens to commands from an MQTT broker and sends corresponding commands to a Modbus server.

[![Coverage Status](https://coveralls.io/repos/github/EvergenEnergy/remote-commands-handler/badge.svg?branch=main)](https://coveralls.io/github/EvergenEnergy/remote-commands-handler?branch=main)

## Features

- Listen to an MQTT broker for command messages.
- Send corresponding commands to a Modbus server.
- Can handle coil and holding register commands.
- Configuration of Modbus settings via a YAML configuration file.
- Optionally publish error messages to MQTT.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1. Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/remote-commands-handler.git
```

2. Navigate to the project directory:

```bash
cd remote-commands-handler
```

3. Install dependencies:

```bash
poetry install
```

## Running the Tests

This project uses pytest for unit testing.
To run the tests:

```bash
poetry install
poetry run pytest
```

## Usage
To run the application:

```bash
poetry run python main.py
```

or
```bash
docker run -e CONFIGURATION_PATH=config/configuration.yaml ghcr.io/evergenenergy/remote-commands-handler:latest
```

Once `main.py` is running, you can publish JSON payloads to your MQTT broker and these will be transformed into commands sent to Modbus. The expected JSON format is:

```
{
    "action": "firstCoilSlot",
    "value": 1
}
```

## Configuration

You will need to modify the `configuration.yaml` file to match your MQTT and Modbus settings.

- Provide the required host and port number for your MQTT broker in the `mqtt_settings` section, as well as the topic to subscribe to, and for your Modbus server in the `modbus_settings` section
- If you wish to receive error messages via MQTT, set the `error_topic` to an MQTT topic name. Allow for additional levels to be added to the topic when messages are published.
- The `modbus_mappings` section allows you to configure the coils and holding registers available on your Modbus server
- Each entry under `coils` and `holding_registers` refers to a space where Modbus will store data. The `name` for each entry will correspond to the `action` of your JSON payloads. The `address` for each entry identifies the relevant location within the Modbus server.
- For holding registers, you must also specify the `data_type` and `byte_order` for each register.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)