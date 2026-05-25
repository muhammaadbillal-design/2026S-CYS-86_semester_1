a=input("enter data")
if "." in a:
  a=float(a)
  print("type is :",type(a))
elif a.isdigit():
    a=int(a)
    print("type is :",type(a))
else:
    print("type is :",type(a))