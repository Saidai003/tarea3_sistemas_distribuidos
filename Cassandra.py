from cassandra.cluster import Cluster

def save_to_cassandra(data):
    cluster = Cluster(['localhost'], port=9042)  # Cambia el host si no está en localhost
    session = cluster.connect()

    # Crear Keyspace y tabla
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS waze_keyspace
        WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 1 }
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS waze_keyspace.alerts (
            country TEXT,
            city TEXT,
            type TEXT,
            street TEXT,
            confidence INT,
            reliability INT,
            PRIMARY KEY (country, city, type)
        )
    """)

    # Insertar datos
    for row in data:
        session.execute("""
            INSERT INTO waze_keyspace.alerts (country, city, type, confidence, reliability, street)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (row['Country'], row['City'], row['Type'], row['Confidence'], row['Reliability'], row['Street']))

    cluster.shutdown()

