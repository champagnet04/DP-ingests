import json
import psycopg
from dotenv import load_dotenv


def insert_cfr_part(conn, json_data):
    data = json.loads(json_data)

    frdocnum = data.get("document_number")
    cfr_references = data.get("cfr_references", [])

    try:
        with conn.cursor() as cursor:
            for ref in cfr_references:
                title = str(ref.get("title")) if ref.get("title") is not None else None
                cfrpart = str(ref.get("part")) if ref.get("part") is not None else None

                insert_query = """
                INSERT INTO cfrparts (frdocnum, title, cfrpart)
                VALUES (%s, %s, %s)
                ON CONFLICT (frdocnum, title, cfrpart) DO NOTHING;
                """
                cursor.execute(insert_query, (frdocnum, title, cfrpart))
            print(f"CFR parts for {frdocnum} inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

