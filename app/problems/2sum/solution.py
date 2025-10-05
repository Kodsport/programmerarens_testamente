target = int(input())
n = int(input())
ls = [int(input()) for _ in range(n)]
lp = 0
rp = len(ls)-1
while (lp <= rp):
    if ls[lp] + ls[rp] > target:
        rp -= 1
    elif ls[lp] + ls[rp] < target:
        lp += 1
    elif ls[lp] + ls[rp] == target:
        break

print(ls[lp])
print(ls[rp])
