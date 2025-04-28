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


def dz():
    for X1 in range(0, 2):
        for X2 in range(0, 2):
            for X3 in range(0, 2):
                for X4 in range(0, 2):
                    for X5 in range(0, 2):
                        term1 = (not X1) and X2 and X3
                        term2 = X2 and X3 and (not X4)
                        term3 = (not X1) and X2 and (not X3) and X4
                        term4 = X1 and (not X3) and (not X4) and X5
                        term5 = (not X2) and X3 and X5
                        
                        print(X1, X2, X3, X4, X5, f'Y = {int(term1 or term2 or term3 or term4 or term5)}')


dz()