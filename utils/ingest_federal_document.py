import json
import psycopg
from dotenv import load_dotenv
import sys
import os
from .date import parse as parse_date


def insert_federal_document(conn, json_data):
    data = json.loads(json_data)

    agencies = data.get("agencies", [])
    agency_id = str(agencies[0].get("id")) if agencies else None
    agency_names = [a.get("raw_name") for a in agencies if a.get("raw_name")]

    cfr_references = data.get("cfr_references", [])
    cfr_title = str(cfr_references[0].get("title")) if cfr_references else None
    cfr_part = str(cfr_references[0].get("part")) if cfr_references else None

    values = (
        data.get("document_number"),
        data.get("document_id"),
        data.get("title"),
        data.get("type"),
        data.get("abstract"),
        parse_date(data.get("publication_date")),
        parse_date(data.get("effective_on")),
        data.get("docket_ids"),
        agency_id,
        agency_names,
        data.get("topics"),
        data.get("significant"),
        data.get("regulation_id_numbers"),
        data.get("html_url"),
        data.get("pdf_url"),
        data.get("json_url"),
        data.get("start_page"),
        cfr_title,
        cfr_part,
        data.get("end_page"),
    )

    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO federal_register_documents (
                document_number, document_id, document_title, document_type,
                abstract, publication_date, effective_on, docket_ids,
                agency_id, agency_names, topics, significant,
                regulation_id_numbers, html_url, pdf_url, json_url,
                start_page, title, cfrpart, end_page
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (document_number) DO UPDATE
            SET
                document_id = EXCLUDED.document_id,
                document_title = EXCLUDED.document_title,
                document_type = EXCLUDED.document_type,
                abstract = EXCLUDED.abstract,
                publication_date = EXCLUDED.publication_date,
                effective_on = EXCLUDED.effective_on,
                docket_ids = EXCLUDED.docket_ids,
                agency_id = EXCLUDED.agency_id,
                agency_names = EXCLUDED.agency_names,
                topics = EXCLUDED.topics,
                significant = EXCLUDED.significant,
                regulation_id_numbers = EXCLUDED.regulation_id_numbers,
                html_url = EXCLUDED.html_url,
                pdf_url = EXCLUDED.pdf_url,
                json_url = EXCLUDED.json_url,
                start_page = EXCLUDED.start_page,
                title = EXCLUDED.title,
                cfrpart = EXCLUDED.cfrpart,
                end_page = EXCLUDED.end_page;
            """
            cursor.execute(insert_query, values)
            print(f"Federal document {data.get('document_number')} inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python ingest_federal_document.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    load_dotenv()
    conn_params = {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
    }

    try:
        with open(json_file_path, "r") as json_file:
            json_data = json_file.read()
            with psycopg.connect(**conn_params) as conn:
                insert_federal_document(conn, json_data)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
