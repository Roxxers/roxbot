from pony.orm import Database, db_session, TransactionIntegrityError

db = Database()
db.bind(provider='postgres', user='roxie', password='', host='localhost', database='roxbot')
db.generate_mapping(create_tables=True)