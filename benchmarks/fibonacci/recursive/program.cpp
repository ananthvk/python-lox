#include <chrono>
#include <iostream>

int fib(int n)
{
    if (n <= 1)
    {
        return n;
    }
    return fib(n - 2) + fib(n - 1);
}

int main()
{
    int n;
    std::cout << "Enter n: ";
    std::cin >> n;

    auto start = std::chrono::high_resolution_clock::now();
    int f = fib(n);
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> elapsed = end - start;

    std::cout << "fib(" << n << ") is " << f << std::endl;
    std::cout << "Time taken: " << elapsed.count() << " seconds" << std::endl;

    return 0;
}