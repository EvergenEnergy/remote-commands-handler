from app.remote_command_handler import RemoteCommandHandler


class TestRemoteCommandHandler:
    def test_parse_args(self):
        handler = RemoteCommandHandler()
        args = handler.parse_arguments(["--config=/tmp/nosuchfile"])
        print(args)
        assert args.configuration_path == "/tmp/nosuchfile"

    def test_config_with_overrides(self):
        handler = RemoteCommandHandler()

        args = handler.parse_arguments(["--mqtt_command_topic=mytopicname"])
        configuration = handler.get_configuration_with_overrides(args)
        assert configuration.get_mqtt_settings().command_topic == "mytopicname"

        args = handler.parse_arguments(["--modbus_host=modbus.server.localhost"])
        configuration = handler.get_configuration_with_overrides(args)
        assert configuration.get_modbus_settings().host == "modbus.server.localhost"

        # Having some args specified at the command line doesn't affect other config file settings
        assert len(configuration.get_coils()) == 3
