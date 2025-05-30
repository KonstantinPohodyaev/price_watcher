def func():
    d = {
        'a': 1,
        'b': 2,
        'c': 3
    }
    d_2 = {}
    for field, value in d.items():
        d_2[field] = value * 10
    return d_2


print(func())
