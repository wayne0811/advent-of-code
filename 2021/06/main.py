# https://adventofcode.com/2021/day/6
import sys

def simulate(initial):
    data = initial
    while True:
        num_zeros = sum(1 for d in data if d == 0)
        data = map(lambda n: n-1 if n else 6, data)
        data = list(data) + [8] * num_zeros
        yield data

def simulate1(initial):
    counts = {i:0 for i in range(9)}
    for d in initial:
        counts[d] += 1
    while True:
        counts_new = {}
        for i in range(8):
            counts_new[i] = counts[i+1]
        counts_new[6] += counts[0]
        counts_new[8] = counts[0]
        counts = counts_new
        yield counts

if __name__ == '__main__':
    data = sys.stdin.read().strip().split(',')
    data = list(map(int, data))
    s = simulate1(data)
    days = int(sys.argv[1])
    for i, d in zip(range(days), s):
        print('{}: {}'.format(i+1, sum(d.values())))