from app.error_handler import ErrorHandler
from app.configuration import Configuration, _mqtt_settings_from_yaml_data
import paho.mqtt.client as mqtt
from freezegun import freeze_time
from unittest.mock import MagicMock


def example_config_path():
    # Note that this assumes tests are being run from repo root level, not within `tests` directory
    return "tests/config/example_configuration.yaml"


def test_create_error_handler():
    mock_mqtt_client = MagicMock(spec=mqtt.Client)
    config = Configuration.from_file(example_config_path())
    error = ErrorHandler(config, mock_mqtt_client)
    assert error.active is True


def test_no_error_handler():
    mock_mqtt_client = MagicMock(spec=mqtt.Client)
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
    error = ErrorHandler(config, mock_mqtt_client)
    assert error.active is False
    error.publish(error.Category.UNKNOWN_COMMAND, "foo")


def test_error_payload():
    mock_mqtt_client = MagicMock(spec=mqtt.Client)
    config = Configuration.from_file(example_config_path())
    error = ErrorHandler(config, mock_mqtt_client)

    with freeze_time("2023-07-01 12:00:00"):
        error.publish(error.Category.UNKNOWN_COMMAND, "oops")
        call_args, _ = mock_mqtt_client.publish.call_args
        payload = call_args[1]
        assert '"timestamp": 1688212800.0' in payload
        assert '"message": "oops"' in payload
