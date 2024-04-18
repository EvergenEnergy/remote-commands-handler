from pymodbus.constants import Endian
from app.exceptions import InvalidArgumentError


class MemoryOrder:
    """
    Describes the byte order and word order
    """

    def __init__(self, order: str) -> None:
        self._order = self._str_to_endian(order)

    def order(self):
        return self._order

    def _str_to_endian(self, order_string: str):
        match order_string:  # noqa
            case "AB":
                word_order = Endian.BIG
                byte_order = Endian.BIG
            case "ABCD":
                word_order = Endian.BIG
                byte_order = Endian.BIG
            case "BA":
                word_order = Endian.LITTLE
                byte_order = Endian.LITTLE
            case "CDAB":
                word_order = Endian.LITTLE
                byte_order = Endian.BIG
            case "BADC":
                word_order = Endian.BIG
                byte_order = Endian.LITTLE
            case _:
                raise InvalidArgumentError(
                    "Invalid memory order. Valid orders are 'AB', 'BA', 'ABCD', 'CDAB' and 'BADC'."
                )

        return (byte_order, word_order)
