import time


def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 2) + fib(n - 1)


n = int(input("Enter n: "))
start = time.time()
f = fib(n)
end = time.time()

print(f"fib({n}) is {f}")
print(f"Time taken: {end - start} seconds")
