import psycopg2

DATABASE_URL = "postgresql://mercadolibre_user:6hAgdeOOJKhi08EzMwfp896oiGAq6jRc@dpg-d7ko499f9bms739kgtbg-a.virginia-postgres.render.com/mercadolibre_ln5u"

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    with open("schema.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()

    print("Tablas creadas correctamente.")

if __name__ == "__main__":
    main()