import psycopg2

DATABASE_URL = "postgresql://mercadolibre_user:6hAgdeOOJKhi08EzMwfp896oiGAq6jRc@dpg-d7ko499f9bms739kgtbg-a.virginia-postgres.render.com/mercadolibre_ln5u"

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    tables = cur.fetchall()

    print("Tablas encontradas:")
    for table in tables:
        print("-", table[0])

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()