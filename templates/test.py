import psycopg2


# Configure CS50 Library to use Postgres database
conn = psycopg2.connect("postgres://czznryphemnxjs:4a6625d3983a3befabf184350cfc1d43b1d285b396838bb7255421f1f32c3267@ec2-184-73-206-155.compute-1.amazonaws.com:5432/d36i73dhm3jssb")

def db_execute(*args, **kwargs):
    try:
        cur = conn.cursor()
        cur.execute(*args, **kwargs)
        conn.commit()
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        print('ignoring error:', e)
        conn.rollback()
row = db_execute("SELECT * from users")
print(row)

row = db_execute("INSERT into airports (aportid) VALUES (1)")
print(row)

row = db_execute("SELECT * from airports")
print(row)