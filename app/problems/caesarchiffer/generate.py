def generateCode(room: str, unusedRooms: list[str]):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'
    key = 20

    room = room.upper()\
        .replace('0', 'NOLL')\
        .replace('1', 'ETT')\
        .replace('2', 'TVÅ')\
        .replace('3', 'TRE')\
        .replace('4', 'FYRA')\
        .replace('5', 'FEM')\
        .replace('6', 'SEX')\
        .replace('7', 'SJU')\
        .replace('8', 'ÅTTA')\
        .replace('9', 'NIO')
    caesar = ''.join(map(lambda c: alpha[(alpha.index(c) - key) % len(alpha)], room))

    return caesar

if __name__ == '__main__':
    print(generateCode('AB123', []))
