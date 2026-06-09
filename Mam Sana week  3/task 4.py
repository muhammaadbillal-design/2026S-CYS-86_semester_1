def factorial(a):
    fact = 1
    for i in range(1, a + 1):
        fact = fact * i
    return fact

num = int(input("Enter number: "))
f = factorial(num)
print(f"Factorial of {num} is {f}")