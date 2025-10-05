def generateCode(room: str, unusedRooms: list[str]):
    import random
    buff = [[i+1, char] for i, char in enumerate(room)]
    random.shuffle(buff)
    kod = f"""l = {buff}
print(''.join([x[1] for x in sorted(l, key=lambda x: x[0])]))
"""
    return kod


if __name__ == '__main__':
    print(generateCode('AB123', []))
