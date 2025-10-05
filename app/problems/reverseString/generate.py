def generateCode(room: str, unusedRooms: list[str]):
    kod = f"""s = '{''.join(reversed(room))}'
print(''.join(reversed(s)))
"""
    return kod


if __name__ == '__main__':
    print(generateCode('AB123', []))
