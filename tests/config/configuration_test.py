""" ignore """

from app.configuration import Configuration


def test_get_coil():
    configuration = Configuration.from_file("./tests/config/example_configuration.yml")

    evg_battery_mode_coil_address = configuration.get_coil("evgBatteryModeCoil")
    target_watt_coil = configuration.get_coil("evgBatteryTargetPowerWattsCoil")

    assert evg_battery_mode_coil_address.address == [3]
    assert target_watt_coil.address == [4]

def test_get_holding_registers():
    configuration = Configuration.from_file("./tests/config/example_configuration.yml")

    evg_battery_mode = configuration.get_holding_register("evgBatteryMode")

    assert evg_battery_mode.name == "evgBatteryMode"
    assert evg_battery_mode.byte_order == "AB"
    assert evg_battery_mode.data_type == "INT16"
    assert evg_battery_mode.scale == 1.0
    assert evg_battery_mode.address == [0]

    evg_battery_target_soc_percent = configuration.get_holding_register("evgBatteryTargetSOCPercent")

    assert evg_battery_target_soc_percent.name == "evgBatteryTargetSOCPercent"
    assert evg_battery_target_soc_percent.byte_order == "AB"
    assert evg_battery_target_soc_percent.data_type == "INT16"
    assert evg_battery_target_soc_percent.scale == 1.0
    assert evg_battery_target_soc_percent.address == [2]

def test_able_to_get_mqtt_settings():
    configuration = Configuration.from_file("./tests/config/example_configuration.yml")

    mqtt_settings = configuration.get_mqtt_settings()
    
    assert mqtt_settings.port == 9000
    assert mqtt_settings.host == "localhost"
    assert mqtt_settings.command_topic == "commands/*"

def test_able_to_get_modbus_settings():
    configuration = Configuration.from_file("./tests/config/example_configuration.yml")

    modbus_settings = configuration.get_modbus_settings()

    assert modbus_settings.port == 8080
    assert modbus_settings.host == "localhost"
