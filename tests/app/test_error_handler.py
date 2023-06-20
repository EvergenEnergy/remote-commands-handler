from app.error_handler import ErrorHandler
from app.configuration import Configuration, _mqtt_settings_from_yaml_data
import paho.mqtt.client as mqtt
from unittest.mock import MagicMock


def example_config_path():
    # Note that this assumes tests are being run from repo root level, not within `tests` directory
    return "tests/config/example_configuration.yaml"


def test_create_error_handler():
    config = Configuration.from_file(example_config_path())
    error = ErrorHandler.from_config(config)
    assert error.active is True


def test_no_error_handler():
    config = Configuration.from_file(example_config_path())
    config.mqtt_settings = _mqtt_settings_from_yaml_data(
        {
            "mqtt_settings": {
                "host": "",
                "port": "",
                "command_topic": "",
                "error_topic": "",
            }
        }
    )
    error = ErrorHandler.from_config(config)
    assert error.active is False
    error.publish(error.Category.UNKNOWN_COMMAND, "foo")


def test_publish_error():
    mock_mqtt_client = MagicMock(spec=mqtt.Client)
    config = Configuration.from_file(example_config_path())
    error = ErrorHandler.from_config(config, mock_mqtt_client)
    error.publish(error.Category.UNKNOWN_COMMAND, "oops")
