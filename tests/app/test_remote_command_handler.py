import pytest

from app.remote_command_handler import RemoteCommandHandler


class TestRemoteCommandHandler:
    def test_parse_args(self):
        handler = RemoteCommandHandler()
        args = handler.parse_arguments([])
        assert args.configuration_path == "config/configuration.yaml"

        args = handler.parse_arguments(["--config=/tmp/nosuchfile"])
        assert args.configuration_path == "/tmp/nosuchfile"

        args = handler.parse_arguments(["--mqtt_port=999"])
        assert args.mqtt_port == 999

        with pytest.raises(SystemExit):
            args = handler.parse_arguments(["--mqtt_port=notanint"])

        args = handler.parse_arguments(["--modbus_port=80"])
        assert args.modbus_port == 80

        with pytest.raises(SystemExit):
            args = handler.parse_arguments(["--modbus_port='80'"])

        with pytest.raises(SystemExit):
            args = handler.parse_arguments(["modbus_port=80"])

        with pytest.raises(SystemExit):
            args = handler.parse_arguments(["non_existent_arg=80"])

    def test_config_with_overrides(self):
        handler = RemoteCommandHandler()

        args = handler.parse_arguments(["--mqtt_command_topic=mytopicname"])
        configuration = handler.get_configuration_with_overrides(args)
        assert configuration.get_mqtt_settings().command_topic == "mytopicname"

        args = handler.parse_arguments(["--modbus_host=modbus.server.localhost"])
        configuration = handler.get_configuration_with_overrides(args)
        assert configuration.get_modbus_settings().host == "modbus.server.localhost"

        # Having some args specified at the command line doesn't affect other config file settings
        args = handler.parse_arguments(
            [
                "--config=tests/config/example_configuration.yaml",
                "--mqtt_host=example.com",
            ]
        )
        configuration = handler.get_configuration_with_overrides(args)
        assert len(configuration.get_coils()) == 3
