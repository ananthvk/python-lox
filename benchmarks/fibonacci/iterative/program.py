import time


def fib(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


n = int(input("Enter n: "))
start = time.time()
f = fib(n)
end = time.time()

print(f"fib({n}) is {f}")
print(f"Time taken: {end - start} seconds")
