from pymodbus.constants import Endian

from app.memory_order import MemoryOrder


def test_get_AB_order():
    order = MemoryOrder("AB")

    byte_order, word_order = order.order()

    assert word_order == Endian.Big
    assert byte_order == Endian.Big


def test_get_BA_order():
    order = MemoryOrder("BA")

    byte_order, word_order = order.order()

    assert word_order == Endian.Little
    assert byte_order == Endian.Little


def test_get_ABCD_order():
    order = MemoryOrder("ABCD")

    byte_order, word_order = order.order()

    assert word_order == Endian.Big
    assert byte_order == Endian.Big


def test_get_CDAB_order():
    order = MemoryOrder("CDAB")

    byte_order, word_order = order.order()

    assert word_order == Endian.Little
    assert byte_order == Endian.Big


def test_get_BADC():
    order = MemoryOrder("BADC")

    byte_order, word_order = order.order()

    assert word_order == Endian.Big
    assert byte_order == Endian.Little
