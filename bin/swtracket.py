#!/usr/bin/env python

def add_src_to_syspath():
    """helper function to update syspath"""
    import sys
    from os.path import realpath as real
    from os.path import dirname as cdu
    from os.path import join as joinpath
    pdir = cdu(cdu(real(__file__)))
    api_dir = joinpath(pdir, "src")
    sys.path.append(api_dir)

from datetime import datetime
add_src_to_syspath()
from swtrack.base import SchemaBase
from swtrack.schema2 import Schema2

# Register schemas
SchemaBase.register(Schema2)

def gen_random_hash():
    import random
    hash = random.getrandbits(128)
    return "%032x" % hash

usage = "usage: swtracket.py <install|rollback>"
def parse(action):
    schema2 = SchemaBase.parse('/Users/jonathangerber/src/python/swinstall_proposal/examples/bak/packages.xml/packages.xml_swinstall_stack')
    if action == "install":
        schema2.insert_element(gen_random_hash())
    elif action == "rollback":
        schema2.rollback_element()
    else:
        print usage


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print usage
    else:
        parse(sys.argv[1])
