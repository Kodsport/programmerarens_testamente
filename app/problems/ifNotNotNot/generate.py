def generateCode(room: str, unusedRooms: list[str]):
    import random
    random.seed(__file__)
    kod = f"""x=4
if not not not not (x^2==16):
    print('{random.choice(unusedRooms)}')
elif False**False < True**True:
    print('{random.choice(unusedRooms)}')
else:
    print('{room}')
"""

    return kod


if __name__ == '__main__':
    print(generateCode('AB123', ['CD456', 'EF789']))
