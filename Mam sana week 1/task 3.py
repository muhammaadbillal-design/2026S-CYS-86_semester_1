start=int(input("Enter start of range:"))
end=int(input("Enter end of range:"))
Sum=0
for num in range(start, end + 1 ):
     if num>1:
          prime=True
          for i in range(2,num):
               if num % i ==0:
                    prime=False
                    break
               if prime:
                    print(num)
                    Sum+= num
print("Sum of prime numbers:",Sum)
