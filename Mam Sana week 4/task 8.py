def h(y):
    global x
    x += 1
    x = 5

x = 5
h(x)
print(x)