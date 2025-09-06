
def generateText(flag: str):
    import random
    salar = ["FL64", "FL61", "FL62", "FL63"]
    kod = f"""a = [-2, 3, 1]
b = [-5, -2, -3]
i = min(a)-max(b)
salar = [{flag}, {random.choice(salar)}, {random.choice(salar)}]
print(salar[i])
    """

    return kod

if __name__ == '__main__':
    print(generateText('FL61'))
