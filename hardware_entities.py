from typing import List, Optional, Union


class DMAChannel:
    """Модель каналу контролера DMA з буфером блоків пам'яті та пріоритетом."""

    def __init__(
        self,
        channel_id: str,
        priority: int,
        transfer_buffer: Optional[List[int]] = None,
    ):
        clean_id = str(channel_id).strip()
        if not clean_id:
            raise ValueError("Ідентифікатор каналу не може бути порожнім.")

        self.__channel_id: str = clean_id
        self.__priority: int = 0
        # Проганяємо через сетер, щоб одразу спрацювала перевірка
        self.priority = priority

        self.__transfer_buffer: List[int] = []
        if transfer_buffer is not None:
            for block in transfer_buffer:
                self.add_block(block)

    @property
    def channel_id(self) -> str:
        return self.__channel_id

    @property
    def priority(self) -> int:
        return self.__priority

    @priority.setter
    def priority(self, value: int) -> None:
        # В Python bool наслідує int, тому відсіюємо True/False окремо
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("Пріоритет каналу має бути цілим числом.")
        if not (0 <= value <= 7):
            raise ValueError(f"Пріоритет {value} виходить за допустимі межі (0..7).")
        self.__priority = value

    @property
    def transfer_buffer(self) -> List[int]:
        # Повертаємо копію списку, щоб ззовні випадково не змінили внутрішній буфер
        return self.__transfer_buffer.copy()

    @property
    def total_bytes(self) -> int:
        return sum(self.__transfer_buffer)

    def add_block(self, block_bytes: int) -> None:
        if not isinstance(block_bytes, int) or isinstance(block_bytes, bool):
            raise TypeError("Розмір блоку пам'яті має бути цілим числом.")
        if block_bytes <= 0:
            raise ValueError("Розмір блоку повинен бути більшим за 0 байт.")
        self.__transfer_buffer.append(block_bytes)

    # Протокол послідовності: довжина та доступ за індексом
    def __len__(self) -> int:
        return len(self.__transfer_buffer)

    def __getitem__(self, index: Union[int, slice]) -> Union[int, List[int]]:
        return self.__transfer_buffer[index]

    def __repr__(self) -> str:
        return (
            f"DMAChannel(channel_id='{self.__channel_id}', "
            f"priority={self.__priority}, blocks={len(self)})"
        )

    def __str__(self) -> str:
        return (
            f"DMA [{self.__channel_id}] | Пріоритет: {self.__priority} | "
            f"Блоків: {len(self)} | Всього: {self.total_bytes} Б"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DMAChannel):
            return False
        return (
            self.__channel_id == other.channel_id
            and self.__priority == other.priority
        )

    def __lt__(self, other: object) -> bool:
        # Порівняння за пріоритетом для роботи оператора < та sorted()
        if not isinstance(other, DMAChannel):
            return NotImplemented
        return self.__priority < other.priority

    def __add__(self, other: object) -> "DMAChannel":
        # Конкатенація двох ланцюжків передачі в один новий канал
        if not isinstance(other, DMAChannel):
            return NotImplemented

        new_id = f"{self.__channel_id}+{other.channel_id}"
        max_prio = max(self.__priority, other.priority)
        merged_chain = self.__transfer_buffer + other.transfer_buffer

        return DMAChannel(
            channel_id=new_id,
            priority=max_prio,
            transfer_buffer=merged_chain,
        )


class ScatterGatherDMA(DMAChannel):
    """Багатоканальний DMA-вузол з підтримкою таблиці дескрипторів."""

    def __init__(
        self,
        channel_id: str,
        priority: int,
        descriptor_limit: int,
        transfer_buffer: Optional[List[int]] = None,
    ):
        super().__init__(channel_id, priority, transfer_buffer)

        if not isinstance(descriptor_limit, int) or isinstance(descriptor_limit, bool):
            raise TypeError("Ліміт дескрипторів має бути цілим числом.")
        if descriptor_limit <= 0:
            raise ValueError("Ліміт дескрипторів повинен бути додатним.")
        if len(self) > descriptor_limit:
            raise ValueError("Початковий буфер перевищує розмір таблиці дескрипторів.")

        self.__descriptor_limit: int = descriptor_limit
        # Формуємо базові записи дескрипторів під вже передані блоки
        self.__descriptors: List[str] = [
            f"0x{0x1000 + i * 0x100:04X} ({size}B)"
            for i, size in enumerate(self.transfer_buffer)
        ]

    @property
    def descriptor_limit(self) -> int:
        return self.__descriptor_limit

    @property
    def descriptors(self) -> List[str]:
        return self.__descriptors.copy()

    def register_descriptor(self, mem_addr: str, block_bytes: int) -> None:
        """Реєструє новий дескриптор сегмента пам'яті та додає блок у чергу."""
        if len(self.__descriptors) >= self.__descriptor_limit:
            raise ValueError(
                f"Таблиця дескрипторів заповнена (максимум {self.__descriptor_limit})."
            )
        addr = str(mem_addr).strip()
        if not addr:
            raise ValueError("Адреса пам'яті не може бути порожньою.")

        self.add_block(block_bytes)
        self.__descriptors.append(f"{addr} ({block_bytes}B)")

    def __repr__(self) -> str:
        return (
            f"ScatterGatherDMA(channel_id='{self.channel_id}', "
            f"priority={self.priority}, "
            f"descriptors={len(self.__descriptors)}/{self.__descriptor_limit})"
        )

    def __str__(self) -> str:
        base_str = super().__str__()
        return (
            f"{base_str} | Дескриптори: "
            f"{len(self.__descriptors)}/{self.__descriptor_limit}"
        )