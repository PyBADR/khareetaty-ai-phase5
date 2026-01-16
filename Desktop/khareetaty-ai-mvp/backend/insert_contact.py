import psycopg2

conn = psycopg2.connect('dbname=khareetaty_ai user=bdr.ai')
cur = conn.cursor()

try:
    cur.execute("""
        INSERT INTO contacts (name, phone, role) 
        VALUES ('Bader Admin', '+96655663338736', 'Admin')
        ON CONFLICT DO NOTHING
    """)
    conn.commit()
    print('✅ Contact inserted successfully')
    
    cur.execute("SELECT * FROM contacts")
    contacts = cur.fetchall()
    print(f'Total contacts: {len(contacts)}')
    for contact in contacts:
        print(f'  - {contact}')
except Exception as e:
    print(f'❌ Error: {e}')
finally:
    cur.close()
    conn.close()
