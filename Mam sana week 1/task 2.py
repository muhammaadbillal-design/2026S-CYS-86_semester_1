sentence=input("Enter a sentence:")
vowels=0
consonants=0
for ch in sentence:
    if ch.lower() in "aeiou":
        vowels+=1
    elif ch.isalpha():
        consonants+=1

print("vowels:",vowels)
print("Consonants",consonants)