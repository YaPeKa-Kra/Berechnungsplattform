list = [1, 2, 3]
lista = [4, 5, 6]

for i in list:
    print(i)

listb = []
for i in list:
    for j in lista:
        i*j
        listb.append(i * j)
print(listb)