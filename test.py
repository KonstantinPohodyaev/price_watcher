import threading
from time import sleep


def func1(time_for_sleep):
    print(f'Функция 1 засыпает на {time_for_sleep} секунд...')
    sleep(time_for_sleep)
    print('Функция 1 проснулась!')


def func2():
    print(f'Функция 2 засыпает на 1 раз')
    sleep(2)
    print(f'Функция 2 засыпает 2 раз')
    sleep(2)
    print(f'Функция 2 засыпает 3 раз')
    sleep(2)
    print('Функция 2 проснулась!')


if __name__ == '__main__':
    t1 = threading.Thread(target=func1, args=(3,))
    t2 = threading.Thread(target=func2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print('Окончание работы основного потока!')




