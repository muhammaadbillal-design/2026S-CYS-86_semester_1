a=int(input("Enter the obtained marks="))
b=int(input("Enter the total marks="))
per=(a/b)*100
print("Percentage",per)
if(per>=90):
    print("Grade A")
elif(per>=85):
    print("Grade A-")
elif(per>=80):
    print("Grade B+")
elif(per>=75):
    print("Grade B-")
elif(per>=70):
    print("Grade C")
else :
    print("Fail")
