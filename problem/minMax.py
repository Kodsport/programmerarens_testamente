
def generateText(flag: str):
    import random
    salar = ["FL64", "FL61", "FL62", "FL63", "KD2", "ML1", "ML2", "SB-M500", "SB-G311", "Pascal", "ML14", "ML16"]
    kod = f"""a = [-2, 3, 1]
b = [-5, -2, -3]
i = min(a)-max(b)
salar = [{flag}, {random.choice(salar)}, {random.choice(salar)}]
print(salar[i])
    """

    return kod

if __name__ == '__main__':
    print(generateText('FL61'))
