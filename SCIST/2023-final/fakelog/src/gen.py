#!/usr/local/bin/python3
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("no argument")
        sys.exit()

    magic_num = int(sys.argv[1]) if sys.argv[1].isdigit() else sys.argv[1]
    if magic_num == 0:
        print("0 is not allowed")
        sys.exit()
    while magic_num != 1:
        with open(f"fakelog/{magic_num % 6 if isinstance(magic_num, int) else magic_num}", "r", encoding="utf-8") as fd:
            print(fd.read())
        magic_num = 3 * magic_num + 1 if magic_num % 2 else magic_num // 2
