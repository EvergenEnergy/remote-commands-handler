# Remote Commands Handler

Remote Commands Handler is a Python application that handles remote commands via MQTT and Modbus protocols. The application listens to commands from an MQTT broker and sends corresponding commands to a Modbus server.

[![Coverage Status](https://coveralls.io/repos/github/EvergenEnergy/remote-commands-handler/badge.svg?branch=main)](https://coveralls.io/github/EvergenEnergy/remote-commands-handler?branch=main)

## Features

- Listen to an MQTT broker for command messages.
- Send corresponding commands to a Modbus server.
- Can handle coil and holding register commands.
- Configuration of Modbus settings via a YAML configuration file.

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

## Running the Tests

This project uses pytest for unit testing.
To run the tests:

```bash
poetry install
```
## Usage
To run the application:

```bash
poetry run python main.py
```

or
```bash
docker run -e CONFIGURATION_PATH=config/configuration.yaml ghcr.io/evergenenergy/remote-comands-handler:latest
``````

## Configuration

Modify the config.yml file to match your MQTT and Modbus settings.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)