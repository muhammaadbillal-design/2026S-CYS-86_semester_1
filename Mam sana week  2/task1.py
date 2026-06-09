password="billaal"
max_attempts=3
attempts=0
while attempts<max_attempts:
    given_password=input("Enter the password:")
    attempts+=1
    if given_password==password:
        print("Access Granted")
        break
    else:
        print("Please try again.")
        if attempts==max_attempts:
            print("Max number of attempts reached . Access denied")
