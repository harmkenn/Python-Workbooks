from timeit import Timer

t1 = Timer("fib(10)","from fibonacci import fib")

for i in range(1, 20):
    cmd = "fib(" + str(i) + ")"
    t1 = Timer(cmd, "from fibonacci import fib")
    time1 = t1.timeit(3)
    cmd = "fibi(" + str(i) + ")"
    t2 = Timer(cmd, "from fibonacci import fibi")
    time2 = t2.timeit(3)
    print(f"n={i:2d}, fib: {time1:9.7f}, fibi:  {time2:9.7f}, time1/time2: {time1/time2:10.2f}")