from pony.orm import *

def define_tables(db):
    class Users(db.Entity):
        id = PrimaryKey(int, size=64)
        pronouns = Optional(str)