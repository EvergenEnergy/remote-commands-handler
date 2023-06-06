"""Tests for the PayloadBuilder module."""

import pytest
from app.memory_order import MemoryOrder
from app.payload_builder import PayloadBuilder


def test_able_to_create_float32():
    builder = PayloadBuilder()

    builder.set_data_type("FLOAT32-IEEE")
    builder.set_value(20)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None


def test_able_to_create_float16():
    builder = PayloadBuilder()

    builder.set_data_type("FLOAT16-IEEE")
    builder.set_value(20)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None


def test_able_to_create_float64():
    builder = PayloadBuilder()

    builder.set_data_type("FLOAT64-IEEE")
    builder.set_value(20)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None


def test_able_to_create_unit64():
    builder = PayloadBuilder()

    builder.set_data_type("UINT64")
    builder.set_value(10)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 4
    assert payload == [0, 0, 0, 10]


def test_able_to_create_uint32():
    builder = PayloadBuilder()

    builder.set_data_type("UINT32")
    builder.set_value(10)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 2
    assert payload == [0, 10]


def test_able_to_create_uint8():
    builder = PayloadBuilder()

    builder.set_data_type("UINT8")
    builder.set_value(0)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 1
    assert payload == [0]


def test_able_to_create_uint16():
    builder = PayloadBuilder()

    builder.set_data_type("UINT16")
    builder.set_value(10)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 1
    assert payload == [10]


def test_able_to_create_int8():
    builder = PayloadBuilder()

    builder.set_data_type("INT8")
    builder.set_value(0)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 1
    assert payload == [0]


def test_able_to_create_int16():
    builder = PayloadBuilder()

    builder.set_data_type("INT16")
    builder.set_value(5)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 1
    assert payload == [5]


def test_able_to_create_int32():
    builder = PayloadBuilder()

    builder.set_data_type("INT32")
    builder.set_value(10)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 2
    assert payload == [0, 10]


def test_able_to_create_int64():
    builder = PayloadBuilder()

    builder.set_data_type("INT64")
    builder.set_value(10)
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None
    assert len(payload) == 4
    assert payload == [0, 0, 0, 10]


def test_able_to_create_string():
    builder = PayloadBuilder()

    builder.set_data_type("STRING")
    builder.set_value("testing")
    builder.set_memory_order(MemoryOrder("AB"))
    payload = builder.build()
    assert payload is not None


def test_if_no_memory_order_been_set():
    builder = PayloadBuilder()

    builder.set_data_type("FLOAT64-IEEE")
    builder.set_value(20)

    with pytest.raises(AttributeError):
        builder.build()


def test_if_no_data_type_has_been_set():
    builder = PayloadBuilder()

    builder.set_memory_order(MemoryOrder("AB"))
    builder.set_value(20)

    with pytest.raises(AttributeError):
        builder.build()


def test_if_no_value_has_been_set():
    builder = PayloadBuilder()

    builder.set_memory_order(MemoryOrder("AB"))
    builder.set_data_type("FLOAT64-IEEE")

    with pytest.raises(AttributeError):
        builder.build()


def test_if_unknown_data_type_is_given():
    builder = PayloadBuilder()

    builder.set_memory_order(MemoryOrder("AB"))
    builder.set_data_type("unknown data type")
    builder.set_value(1)

    with pytest.raises(RuntimeError):
        builder.build()
