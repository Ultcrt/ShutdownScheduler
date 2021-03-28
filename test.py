import winsound
from time import time_ns

if __name__ == "__main__":
    winsound.Beep(500,100)
    t = time_ns()
    while True:
        