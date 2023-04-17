import psycopg2
from pprint import pprint


def create_db(cur):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Clients(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20),
            lastname VARCHAR(30),
            email VARCHAR(254)
            );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Phone(
        id SERIAL PRIMARY KEY,
        phone varchar(12),
        client_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES Clients (id)
    );

    """)
    return


def delete_db(cur):
    cur.execute("""
    DROP TABLE Clients, Phone CASCADE;
    """)


def add_client(cur, name, lastname, email, phone=None):
    cur.execute("""
    INSERT INTO Clients(name, lastname, email)
    VALUES (%s, %s, %s)
    """, (name, lastname, email))
    cur.execute("""
            SELECT id from clients
            ORDER BY id DESC
            LIMIT 1
            """)
    id = cur.fetchone()[0]
    if phone is None:
        return id
    else:
        add_phone(cur, id, phone)
        return id


def add_phone(cur, phone, client_id):
    cur.execute("""
    INSERT INTO Phone(phone, client_id)
    VALUES (%s, %s)
    """, (phone, client_id))
    return client_id


def change_client(cur, id, name=None, lastname=None, email=None):
    cur.execute("""
    SELECT * FROM Clients
    WHERE id = %s""", (id,))
    info = cur.fetchone()
    if info is not None:
        if name is None:
            name = info[1]
        if lastname is None:
            lastname = info[2]
        if email is None:
            email = info[3]
        cur.execute("""
        UPDATE Clients
        SET name = %s, lastname = %s, email = %s
        WHERE id = %s
        """, (name, lastname, email, id))
        return id
    else:
        return None


def delete_phone(cur, phone):
    cur.execute("""
    DELETE FROM Phone
    WHERE phone = %s
    """, (phone,))
    return phone


def delete_client(cur, id):
    cur.execute("""
    DELETE FROM Phone
    WHERE client_id = %s
    """, (id,))

    cur.execute("""
    DELETE FROM Clients
    WHERE id = %s
    """, (id,))
    return id


def find_client(cur, name=None, lastname=None, email=None, phone=None):
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if lastname is None:
        lastname = '%'
    else:
        lastname = '%' + lastname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'

    if phone is None:
        cur.execute("""
        SELECT clients.id, clients.name, clients.lastname, clients.email, phone.phone FROM Clients
        LEFT JOIN phone ON clients.id = phone.client_id
        WHERE clients.name LIKE %s AND clients.lastname LIKE %s AND clients.email LIKE %s 
        """, (name, lastname, email))

    else:
        cur.execute("""
        SELECT clients.id, clients.name, clients.lastname, clients.email, phone.phone FROM Clients
        LEFT JOIN phone ON clients.id = phone.client_id
        WHERE clients.name LIKE %s AND clients.lastname LIKE %s AND clients.email LIKE %s AND clients.phone LIKE %s
        """, (name, lastname, email, phone))
    return cur.fetchall()


if __name__ == '__main__':
    with psycopg2.connect(database='clients_db', user='postgres', password='') as conn:
        with conn.cursor() as curs:
            # удалить таблицы
            delete_db(curs)
            print('БД сброшена')

            # Создать таблицу
            create_db(curs)
            print('БД создана')

            # Добавить клиента
            print('Клиент создан, id', add_client(curs, 'Иван', 'Солдатов', 'soldatov@ya.ru'))
            curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.phone FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)
            pprint(curs.fetchall())

            # Добавить номер телефона
            add_phone(curs, '79161264578', 1)  # первый номер телефона
            print('Номер телефона добавлен')

            add_phone(curs, '79161234567', 1)  # второй номер телефона
            print('Номер телефона добавлен')
            curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.phone FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)
            pprint(curs.fetchall())

            # Изменить данные о клиенте
            change_client(curs, 1, 'Сергей')
            print('Данные о клиенте изменены')

            # Удалить телефон клиента
            delete_phone(curs, '79161234567')
            print('Номер телефона удален')
            curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.phone FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)
            pprint(curs.fetchall())

            # Удалить существующего клиента
            delete_client(curs, 1)
            print('Клиент удален')
            curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.phone FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)

            # Поиск клиента
            print('Клиент найден', find_client(curs, 'Иван'))
            curs.execute("""
                        SELECT c.id, c.name, c.lastname, c.email, p.phone FROM clients c
                        LEFT JOIN phone p ON c.id = p.client_id
                        ORDER by c.id
                        """)
