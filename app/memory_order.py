from pymodbus.constants import Endian


class MemoryOrder:
    """
    Describes the byte order and word order
    """

    def __init__(self, order: str) -> None:
        self._order = self._str_to_endian(order)

    def order(self):
        return self._order

    def _str_to_endian(self, order_string: str):
        word_order = Endian.Big
        byte_order = Endian.Big

        if order_string is None:
            return (byte_order, word_order)

        match order_string:  # noqa
            case "AB":
                word_order = Endian.Big
                byte_order = Endian.Big
            case "BA":
                word_order = Endian.Little
                byte_order = Endian.Little
            case "CDAB":
                word_order = Endian.Little
                byte_order = Endian.Big
            case "BADC":
                word_order = Endian.Big
                byte_order = Endian.Little

        return (byte_order, word_order)
