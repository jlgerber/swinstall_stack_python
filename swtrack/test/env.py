import os
import sys

path = \
os.path.dirname(
    os.path.dirname(
        os.path.abspath(
            __file__
        )
    )
)

print path
sys.path.append(path)