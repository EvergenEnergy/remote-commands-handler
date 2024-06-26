"""Tests for the MemoryOrder class."""

import pytest
from pymodbus.constants import Endian

from app.memory_order import MemoryOrder
from app.exceptions import InvalidArgumentError


def test_get_AB_order():
    order = MemoryOrder("AB")

    byte_order, word_order = order.order()

    assert word_order == Endian.BIG
    assert byte_order == Endian.BIG


def test_get_BA_order():
    order = MemoryOrder("BA")

    byte_order, word_order = order.order()

    assert word_order == Endian.LITTLE
    assert byte_order == Endian.LITTLE


def test_get_ABCD_order():
    order = MemoryOrder("ABCD")

    byte_order, word_order = order.order()

    assert word_order == Endian.BIG
    assert byte_order == Endian.BIG


def test_get_CDAB_order():
    order = MemoryOrder("CDAB")

    byte_order, word_order = order.order()

    assert word_order == Endian.LITTLE
    assert byte_order == Endian.BIG


def test_get_BADC():
    order = MemoryOrder("BADC")

    byte_order, word_order = order.order()

    assert word_order == Endian.BIG
    assert byte_order == Endian.LITTLE


def test_get_unknown_order():
    with pytest.raises(InvalidArgumentError) as ex:
        _ = MemoryOrder("FOO")
    assert "Invalid memory order" in str(ex.value)
