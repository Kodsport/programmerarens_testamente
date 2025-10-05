def generateCode(room: str, unusedRooms: list[str]):
    import random
    random.seed(__file__)
    kod = f"""a = [-2, 3, 1]
b = [-5, -2, -3]
i = min(a)-max(b)
salar = ['{room}', '{random.choice(unusedRooms)}', '{random.choice(unusedRooms)}']
print(salar[i])
"""
    return kod


if __name__ == '__main__':
    print(generateCode('AB123', ['CD456', 'EF789']))
