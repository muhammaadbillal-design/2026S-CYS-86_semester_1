def g(x):
    def h():
        x = 'abc'

        print('inside h: x =', x)
    h()
    print('g: x =', x)
    return x

x = 3
z = g(x)

print("z =", z)