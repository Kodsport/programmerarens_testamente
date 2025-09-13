
def generateText(flag: str):
    import random
    l = [[i+1, char] for i, char in enumerate(flag)]
    random.shuffle(l)
    kod = f"""l = {l}
print(''.join([x[1] for x in sorted(l, key=lambda x: x[0])]))
"""
    return kod
    
if __name__ == '__main__':
    print(generateText('FL61'))
