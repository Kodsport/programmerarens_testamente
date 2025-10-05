def generateCode(room: str, unusedRooms: list[str]):
    import random, string
    random.seed(__file__)
    n = len(room)
    L = 3 * n  # ensures (L-1) % 3 == 2, so s[::-3] grabs indices 2 mod 3
    chars = [random.choice(string.ascii_letters + string.digits) for _ in range(L)]

    # Place flag so that s[::-3] yields it in forward order
    for j, ch in enumerate(room):
        idx = L - 1 - 3*j   # L-1, L-4, L-7, ...
        chars[idx] = ch

    kod = f"""s = '{''.join(chars)}'
print(s[::-3])
"""
    return kod


if __name__ == '__main__':
    print(generateCode('AB123', []))
