import random
import string


length = int(input("Enter password length: "))
use_upper = input("Include uppercase letters? (yes/no): ")
use_digits = input("Include numbers? (yes/no): ")
use_special = input("Include special characters? (yes/no): ")

characters = string.ascii_lowercase

if use_upper == "yes":
    characters += string.ascii_uppercase
if use_digits == "yes":
    characters += string.digits
if use_special == "yes":
    characters += string.punctuation
    
password = ""
for i in range(length):
    password += random.choice(characters)

print("Generated Password:", password)