def show(n):
    if n==0 or n==1:
        return 1                   # factorial finding 
    else:                          #by recursion
        return n*show(n-1)
print(show(6))