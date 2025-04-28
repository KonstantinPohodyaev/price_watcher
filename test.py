def func_1():
    """Поиск самого длинного палиндрома в списке."""
    count_of_zones = int(input('Введите кол-во записей: '))
    zones = list(map(int, input(f'Введите {count_of_zones} чисел: ').split()))
    max_route = 0
    for i in range(count_of_zones):
        left, right = i, i
        while left >= 0 and right < count_of_zones and zones[left] == zones[right]:
            if right - left + 1 > max_route:
                max_route = right - left + 1
            left -= 1
            right += 1
        left, right = i, i + 1
        while left >= 0 and right < count_of_zones and zones[left] == zones[right]:
            if right - left + 1 > max_route:
                max_route = right - left + 1
            left -= 1
            right += 1
    print(max_route if max_route > 1 else 0)


def func_2():
    expression = input().strip()
    stack = []
    num = 0
    result = 0
    sign = 1
    current_index = 0
    n = len(expression)
    while current_index < n:
        char = expression[current_index]
        if char == ' ':
            current_index += 1
            continue
        elif char.isdigit():
            num = 0
            while current_index < n and expression[current_index].isdigit():
                num = num * 10 + int(expression[current_index])
                current_index += 1
            result += sign * num
            continue
        elif char in '+-':
            if current_index == 0 or expression[current_index - 1] == '(':
                count_minus = 0
                while current_index < n and expression[current_index] in '+-':
                    if expression[current_index] == '-':
                        count_minus += 1
                    current_index += 1
                sign = -1 if count_minus % 2 else 1
            else:
                sign = 1 if char == '+' else -1
                current_index += 1
        elif char == '(':
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
            current_index += 1
        elif char == ')':
            result *= stack.pop()
            result += stack.pop()
            current_index += 1
        else:
            current_index += 1
    
    print(result)

func_2()