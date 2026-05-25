c=int(input("Enter the total Students numbers="))
for i in range(c):
    
    d=input("Enter the Student name=")
    b=int(input("Enter the total marks="))
    a=int(input("Enter the obtained marks="))
    g=0
    per=(a/b)*100
    print("Percentage",per)
    
    if(per>=90):
       g="A"
    elif(per>=85):
        g="A-"
    elif(per>=80):
        g="B+"
    elif(per>=75):
        g="B-"
    elif(per>=70):
        g="C"
    else :
        g="F"

    print("Student Name =",d)
    print("Grade =",g)
