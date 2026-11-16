import time
from hardware_entities import DMAChannel, ScatterGatherDMA


def run_dma_testbench() -> None:
    line_main = "=" * 90
    line_sub = "-" * 90

    print(line_main)
    print(f"{'ТЕСТОВИЙ СТЕНД МОДЕЛЮВАННЯ КОНТРОЛЕРА DMA ТА DUNDER-МЕТОДІВ':^90}")
    print(line_main)

    # Створюємо тестові екземпляри каналів
    dma1 = DMAChannel(
        channel_id="DMA-CH0",
        priority=5,
        transfer_buffer=[512, 1024, 256, 2048],
    )
    dma2 = DMAChannel(
        channel_id="DMA-CH1",
        priority=2,
        transfer_buffer=[128, 512, 1024],
    )
    sg_dma = ScatterGatherDMA(
        channel_id="SG-DMA-01",
        priority=6,
        descriptor_limit=4,
        transfer_buffer=[4096, 2048],
    )

    # 1. Перевірка __str__ та __repr__
    print(f"{'1. СТРОКОВЕ ВІДОБРАЖЕННЯ ОБ ЄКТІВ (__str__ та __repr__)':^90}")
    print(f"  print(dma1):   {dma1}")
    print(f"  print(dma2):   {dma2}")
    print(f"  print(sg_dma): {sg_dma}")
    print(f"  repr(sg_dma):  {repr(sg_dma)}")
    print(line_sub)

    # 2. Перевірка сетерів та валідації
    print(f"{'2. ІНКАПСУЛЯЦІЯ, ВАЛІДАЦІЯ (@property) ТА ДЕСКРИПТОРИ':^90}")
    print(f"  Початковий пріоритет dma1: {dma1.priority}")
    dma1.priority = 4
    print(f"  Оновлений пріоритет dma1:  {dma1.priority}")

    try:
        dma1.priority = 12  # поза межами 0..7
    except ValueError as err:
        print(f"  [ПЕРЕВІРКА СЕТЕРА]: {err}")

    # Тест реєстрації дескриптора в похідному класі
    sg_dma.register_descriptor("0x4A00", 1024)
    print(f"  Дескриптори sg_dma після додавання: {sg_dma.descriptors}")
    print(line_sub)

    # 3. Протокол послідовності (__len__, __getitem__)
    print(f"{'3. ПРОТОКОЛ ПОСЛІДОВНОСТЕЙ (__len__, __getitem__)':^90}")
    print(f"  Кількість блоків dma1 (len): {len(dma1)}")
    print(f"  Перший блок dma1[0]:         {dma1[0]} Б")
    print(f"  Останній блок dma1[-1]:      {dma1[-1]} Б")
    print(f"  Усі блоки через цикл:        {[dma1[i] for i in range(len(dma1))]}")
    print(line_sub)

    # 4. Перевантаження + (__add__)
    print(f"{'4. КОНКАТЕНАЦІЯ ЛАНЦЮЖКІВ ПЕРЕДАЧІ (__add__)':^90}")
    merged_dma = dma1 + dma2
    print(f"  Результат dma1 + dma2: {merged_dma}")
    print(f"  Об'єднаний ланцюжок:   {merged_dma.transfer_buffer}")
    print(line_sub)

    # 5. Оператори порівняння (__eq__, __lt__)
    print(f"{'5. ОПЕРАТОРИ ПОРІВНЯННЯ (__eq__, __lt__)':^90}")
    print(f"  Пріоритети -> dma1: {dma1.priority}, dma2: {dma2.priority}")
    print(f"  dma1 == dma2 ? {dma1 == dma2}")
    print(f"  dma2 < dma1  ? {dma2 < dma1} (порівняння за пріоритетом)")
    print(f"  dma1 < dma2  ? {dma1 < dma2}")
    print(line_sub)

    # 6. Поліморфне сортування різнорідної колекції
    print(f"{'6. ПОЛІМОРФНЕ СОРТУВАННЯ КАНАЛІВ (sorted за пріоритетом)':^90}")
    dma_cluster = [dma1, dma2, sg_dma, merged_dma]
    for rank, ch in enumerate(sorted(dma_cluster), start=1):
        print(f"  Ранг {rank}: {ch}")
    print(line_main + "\n")


def main() -> None:
    start_ts = time.perf_counter()
    run_dma_testbench()
    elapsed_ms = (time.perf_counter() - start_ts) * 1000
    print(f"Час виконання тестування: {elapsed_ms:.3f} мс\n")


if __name__ == "__main__":
    main()