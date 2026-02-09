import sqlalchemy as sa

def sync_sequence(conn, table_name: str, id_col: str = "id"):
    conn.execute(sa.text(f"""
        SELECT setval(
            pg_get_serial_sequence('{table_name}', '{id_col}'),
            COALESCE((SELECT MAX({id_col}) FROM {table_name}), 1),
            true
        );
    """))
