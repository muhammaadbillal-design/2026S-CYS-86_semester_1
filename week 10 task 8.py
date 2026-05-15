i=1
while i<=4:
    j=0
    while j<(4-i):
        print(" ",end="")
        j=j+1
    j=0
    while j<(2*i-1):
        print("*",end="")
        j=j+1
    print()
    i=i+1