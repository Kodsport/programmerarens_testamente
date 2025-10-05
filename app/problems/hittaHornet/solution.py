indata = [tuple(map(int, input().split())) for _ in range(3)]

# if indata[0][0] == indata[1][0]:
#     x = indata[2][0]
# elif indata[0][0] == indata[2][0]:
#     x = indata[1][0]
# else:
#     x = indata[0][0]

# if indata[0][1] == indata[1][1]:
#     y = indata[2][1]
# elif indata[0][1] == indata[2][1]:
#     y = indata[1][1]
# else:
#     y = indata[0][1]

def makeHist(l):
    d = {}
    for n in set(l):
        d[n] = len([a for a in l if a == n])
    return d

histX = makeHist(list(map(lambda t: t[0], indata)))
histY = makeHist(list(map(lambda t: t[1], indata)))

x = [a for a,n in histX.items() if n == 1][0]
y = [a for a,n in histY.items() if n == 1][0]

print(f'{x} {y}')
