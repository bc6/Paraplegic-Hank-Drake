#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\sqlite3\dump.py


def _iterdump(connection):
    cu = connection.cursor()
    yield 'BEGIN TRANSACTION;'
    q = "\n        SELECT name, type, sql\n        FROM sqlite_master\n            WHERE sql NOT NULL AND\n            type == 'table'\n        "
    schema_res = cu.execute(q)
    for table_name, type, sql in schema_res.fetchall():
        if table_name == 'sqlite_sequence':
            yield 'DELETE FROM sqlite_sequence;'
        elif table_name == 'sqlite_stat1':
            yield 'ANALYZE sqlite_master;'
        elif table_name.startswith('sqlite_'):
            continue
        else:
            yield '%s;' % sql
        res = cu.execute("PRAGMA table_info('%s')" % table_name)
        column_names = [ str(table_info[1]) for table_info in res.fetchall() ]
        q = 'SELECT \'INSERT INTO "%(tbl_name)s" VALUES('
        q += ','.join([ "'||quote(" + col + ")||'" for col in column_names ])
        q += ")' FROM '%(tbl_name)s'"
        query_res = cu.execute(q % {'tbl_name': table_name})
        for row in query_res:
            yield '%s;' % row[0]

    q = "\n        SELECT name, type, sql\n        FROM sqlite_master\n            WHERE sql NOT NULL AND\n            type IN ('index', 'trigger', 'view')\n        "
    schema_res = cu.execute(q)
    for name, type, sql in schema_res.fetchall():
        yield '%s;' % sql

    yield 'COMMIT;'