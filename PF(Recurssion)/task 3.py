# repeatetive addition using recurssion 
# like 1+2=3 further 3+3=6  and so on 

def fibonacci_series(n):
    
    if n <= 0:                                             
        return "Input should be a positive integer."                    #Input: n, a positive int Returns the nth Fibonacci number 
    elif n == 1:
        return 0                                                        
    elif n == 2:
        return 1
    else:
        return fibonacci_series(n-1) + fibonacci_series(n-2)

# Print results
Result = fibonacci_series(10)
print("The Fibonacci number at the given position 10 is=", Result)
