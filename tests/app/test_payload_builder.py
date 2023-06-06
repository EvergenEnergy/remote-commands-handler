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
