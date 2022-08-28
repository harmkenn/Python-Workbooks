from timeit import Timer
from fibonacci import fib

t1 = Timer("fib(10)","from fibonacci import fib")

for i in range(1, 20):
    s = "fibm(" + str(i) + ")"
    t1 = Timer(s,"from fibonacci import fibm")
    time1 = t1.timeit(3)
    s = "fibi(" + str(i) + ")"
    t2 = Timer(s,"from fibonacci import fibi")
    time2 = t2.timeit(3)
    print(f"n={i:2d}, fibm: {time1:8.6f}, fibi:  {time2:7.6f}, time1/time2: {time1/time2:10.2f}")