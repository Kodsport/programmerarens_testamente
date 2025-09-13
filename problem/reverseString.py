def generateText(flag: str):


    kod = f"""
s = {''.join(reversed(flag))}
print(''.join(reversed(s)))
"""
    return kod
if __name__ == '__main__':
    print(generateText('FL61'))
