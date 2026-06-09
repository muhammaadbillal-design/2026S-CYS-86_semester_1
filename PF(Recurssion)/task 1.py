def show(i):
 
  if (i==0):
      return        # reverse printing
  print(i)           # Using recursion
 
  show(i-1)
show(5)

