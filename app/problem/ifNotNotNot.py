
def generateText(flag: str):
    import random
    salar = ["FL64", "FL61", "FL62", "FL63", ...]
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
