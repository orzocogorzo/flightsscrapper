from bson.json_util import loads
import sys


def decode(t):
    data = loads(open(t, 'r').read())

    with open(t, 'w') as out:
        out.write(data)


if __name__ == '__main__':
    f = sys.argv[1]
    decode(f)
