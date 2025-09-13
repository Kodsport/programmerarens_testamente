
def generateText(flag: str):
    import random
    salar = ["FL64", "FL61", "FL62", "FL63", "KD2", "ML1", "ML2", "SB-M500", "SB-G311", "Pascal", "ML14", "ML16"]
    kod = f"""x=4
if not not not not (x^2==16):
    print({random.choice(salar)})
elif False**False < True**True:
    print({random.choice(salar)})
else: 
    print({flag})
    """

    return kod

if __name__ == '__main__':
    print(generateText('FL61'))
