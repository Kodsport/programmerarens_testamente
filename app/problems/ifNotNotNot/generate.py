def generateCode(room: str, unusedRooms: list[str]):
    import random
    kod = f"""x=4
if not not not not (x^2==16):
    print({random.choice(unusedRooms)})
elif False**False < True**True:
    print({random.choice(unusedRooms)})
else:
    print({room})
"""

    return kod

if __name__ == '__main__':
    print(generateCode('FL61', ["FL64", "FL61", "FL62", "FL63", "KD2", "ML1", "ML2", "SB-M500", "SB-G311", "Pascal", "ML14", "ML16"]))
