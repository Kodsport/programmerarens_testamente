def generateText(flag: str):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'
    key = 20

    flag = flag.upper()\
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
    caesar = ''.join(map(lambda c: alpha[(alpha.index(c) - key) % len(alpha)], flag))

    return f'''Julius Caesar hade 20 nycklar. Eller var det nyckeln som var 20??
{caesar}'''

if __name__ == '__main__':
    print(generateText('AB123'))
