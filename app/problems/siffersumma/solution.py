n = list(input())
for i in range(len(n)):
    n[i] = int(n[i])
buff = sum(n)
while buff > 9:
    n = list(str(buff))
    for i in range(len(n)):
        n[i] = int(n[i])
    buff = sum(n)
print(buff)
