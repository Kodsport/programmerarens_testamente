def generateCode(room: str, unusedRooms: list[str]):
    import random
    l = [[i+1, char] for i, char in enumerate(room)]
    random.shuffle(l)
    kod = f"""l = {l}
print(''.join([x[1] for x in sorted(l, key=lambda x: x[0])]))
"""
    return kod


if __name__ == '__main__':
    print(generateCode('AB123', []))
