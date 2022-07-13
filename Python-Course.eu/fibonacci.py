""" A module containing both a recursive and an iterative implementation of the Fibonacci function. 
The purpose of this module consists in showing the inefficiency of a purely recursive implementation of Fibonacci! """

def fib(n):
    """ recursive version of the Fibonacci function """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)
    
def fibi(n):
    """ iterative version of the Fibonacci function """
    old, new = 0, 1
    if n == 0:
        return 0
    for i in range(n-1):
        old, new = new, old + new
    return new

memo = {0:0, 1:1}
def fibm(n):
    """ recursive Fibonacci function which memoizes previously 
    calculated values with the help of a dictionary memo"""
    if not n in memo:
        memo[n] = fibm(n-1) + fibm(n-2)
    return memo[n]