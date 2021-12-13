import dataclasses
from dataclasses import dataclass
from io import StringIO
import enum
import sys
import unittest

Axes = enum.Enum('Axes', 'x y')

@dataclass(order=True)
class Point:
    x: int
    y: int

    def __getitem__(self, axis):
        return self.__getattribute__(axis.name)

    def __mul__(self, val):
        return Point(*[self[a] * val for a in Axes])

    def __add__(self, other):
        return Point(*[self[a] + other[a] for a in Axes])

    def __neg__(self):
        return self * -1

    def __hash__(self):
        return hash(tuple(self))

    def __iter__(self):
        return iter(self[a] for a in Axes)

@dataclass
class Fold:
    axis: Axes
    pos: int

class Paper:
    def __init__(self, dots):
        self.dots = set(dots)

    def fold(self, axis, pos):
        p1, p2 = self.split_at(axis, pos)
        p2 = p2.flip(axis)
        
        len2 = self.end[axis] - pos
        len1 = self.end[axis] - len2
        len_diff = len1 - len2
        offset = {a.name:0 for a in Axes}
        offset[axis.name] = len_diff
        offset = Point(**offset)
        if len_diff >= 1:
            p2 = p2.translate(offset)
        elif len_diff <= -1:
            p1 = p1.translate(-offset)

        return p1.overlay(p2)

    def split_at(self, axis, pos):
        d1 = [d for d in self.dots if d[axis] < pos]
        d2 = [d for d in self.dots if d[axis] > pos]
        p2 = Paper(d2)
        offset = {a.name:0 for a in Axes}
        offset[axis.name] = pos+1
        offset = Point(**offset)
        p2 = p2.translate(-offset)

        return Paper(d1), p2

    def flip(self, axis):
        end = self.end[axis]
        
        def flip_dots():
            for d in self.dots:
                d1 = dataclasses.replace(d, **{axis.name:end-d[axis]})
                yield d1
        return Paper(flip_dots())

    def overlay(self, other):
        return Paper(self.dots | other.dots)

    def translate(self, offset):
        return Paper(d + offset for d in self.dots)

    @property
    def end(self):
        end = Point(*[
            max(pt[a] for pt in self.dots) for a in Axes
        ])
        return end

    @property
    def size(self):
        return self.end + Point(1,1)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.dots))

    def __eq__(self, other):
        return self.dots == other.dots

    def __str__(self):
        x, y = self.size
        dots = set(tuple(d) for d in self.dots)
        s = StringIO()
        for j in range(y):
            for i in range(x):
                c = '#' if (i,j) in dots else '.'
                print(c, end='', file=s)
            print(file=s)
        return s.getvalue()

class TestPaper(unittest.TestCase):
    data = [
        [
            Paper([Point(6,10), Point(0,14)])
        ]
    ]

    def test_translate(self):
        pass

    def test_split_at(self):
        p = self.data[0][0]
        p1, p2 = p.split_at(Axes.y, 7)
        self.assertListEqual([p1, p2], [
            Paper([]),
            Paper([Point(6,2), Point(0,6)])
        ])

    def test_flip(self):
        p = self.data[0][0]
        p1 = p.flip(Axes.y)
        self.assertEqual(p1, Paper([Point(6,4), Point(0,0)]))
    
    def test_fold(self):
        p = self.data[0][0]
        p1 = p.fold(Axes.y, 7)
        self.assertEqual(p1, Paper([Point(6,4), Point(0,0)]))

class TestAoc13(unittest.TestCase):
    data = [
        [
            [Point(6,10), Point(0,14)],
            [Fold(Axes.y,7)],
            [Point(6,4), Point(0,0)]
        ],
        [
            [Point(6,10), Point(0,14), Point(9,10)],
            [Fold(Axes.y,7)],
            [Point(6,4), Point(0,0), Point(9, 4)]
        ]
    ]
    def test_read_input(self):
        test_input = StringIO('''
6,10
0,14

fold along y=7
'''.lstrip()
        )
        dots, folds = read_input(test_input)
        self.assertListEqual(dots, self.data[0][0])
        self.assertListEqual(folds, self.data[0][1])
    
    def test_run(self):
        for i, d in enumerate(self.data):
            with self.subTest(i=i):
                *_, p = run(d[0], d[1])
                self.assertEqual(p, Paper(d[2]))

def read_input(file):
    dots = []
    folds = []
    for line in file:
        line = line.strip()
        if not line: break
        x, y = list(map(int, line.split(',')))
        dots.append(Point(x,y))
    for line in file:
        line = line.strip()
        if not line: break
        s = 'fold along '
        axis, pos = line[len(s):].split('=')
        folds.append(Fold(Axes[axis], int(pos)))
    return dots, folds

def run(dots, folds):
    p = Paper(dots)
    for fold in folds:
        p = p.fold(fold.axis, fold.pos)
        yield p

if __name__ == '__main__':
    dots, folds = read_input(sys.stdin)
    papers = run(dots, folds)
    for i, p in enumerate(papers):
        print('Fold {}: {} dots'.format(i+1, len(p.dots)))
    print(p)