import json
import psycopg
from dotenv import load_dotenv
import sys
import os
from .date import parse as parse_date
from .dummy_docket import create as create_dummy_docket
from .ingest_docket import insert_docket


# Function to insert document into the database
def insert_document(conn, json_data):
    # Parse the JSON data
    data = json.loads(json_data)

    # Extract relevant fields
    attributes = data["data"]["attributes"]
    document_id = data["data"]["id"]
    document_api_link = data["data"]["links"]["self"]

    # if the docket is null, ingest a dummy docket
    if attributes.get("docketId") is None:
        docket = create_dummy_docket(attributes)
        insert_docket(conn, docket)

    attachments_links = (
        data["data"]
        .get("relationships", {})
        .get("attachments", {})
        .get("links", {})
    )

    # Prepare the values for insertion
    values = (
        document_id,
        document_api_link,
        attributes.get("address1"),
        attributes.get("address2"),
        attributes.get("agencyId"),
        attributes.get("allowLateComments"),
        parse_date(attributes.get("authorDate")),
        attributes.get("category"),
        attributes.get("city"),
        attributes.get("comment"),
        parse_date(attributes.get("commentEndDate")),
        parse_date(attributes.get("commentStartDate")),
        attributes.get("country"),
        attributes.get("docketId"),
        attributes.get("documentType"),
        parse_date(attributes.get("effectiveDate")),
        attributes.get("email"),
        attributes.get("fax"),
        attributes.get("field1"),
        attributes.get("field2"),
        attributes.get("firstName"),
        attributes.get("govAgency"),
        attributes.get("govAgencyType"),
        parse_date(attributes.get("implementationDate")),
        attributes.get("lastName"),
        parse_date(attributes.get("modifyDate")),
        attributes.get("openForComment"),
        attributes.get("organization"),
        attributes.get("phone"),
        parse_date(attributes.get("postedDate")),
        parse_date(attributes.get("postmarkDate")),
        attributes.get("reasonWithdrawn"),
        parse_date(attributes.get("receiveDate")),
        attributes.get("regWriterInstruction"),
        attributes.get("restrictReason"),
        attributes.get("restrictReasonType"),
        attributes.get("stateProvinceRegion"),
        attributes.get("subtype"),
        attributes.get("title"),
        attributes.get("topics"),
        attributes.get("withdrawn"),
        attributes.get("zip"),
        attributes.get("frDocNum"),
        attachments_links.get("self"),
        attachments_links.get("related"),
        json.dumps(attributes.get("fileFormats")) if attributes.get("fileFormats") is not None else None,
        json.dumps(attributes.get("displayProperties")) if attributes.get("displayProperties") is not None else None,
    )

    # Insert into the database
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO documents (
                document_id, document_api_link, address1, address2, agency_id,
                is_late_comment, author_date, comment_category, city, comment,
                comment_end_date, comment_start_date, country, docket_id,
                document_type, effective_date, email, fax, flex_field1,
                flex_field2, first_name, submitter_gov_agency, submitter_gov_agency_type,
                implementation_date, last_name, modify_date, is_open_for_comment,
                submitter_org, phone, posted_date, postmark_date, reason_withdrawn,
                receive_date, reg_writer_instruction, restriction_reason,
                restriction_reason_type, state_province_region, subtype,
                document_title, topics, is_withdrawn, postal_code,
                frdocnum, attachments_self_link, attachments_related_link,
                file_formats, display_properties
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (document_id) DO UPDATE
            SET
                document_api_link = EXCLUDED.document_api_link,
                address1 = EXCLUDED.address1,
                address2 = EXCLUDED.address2,
                agency_id = EXCLUDED.agency_id,
                is_late_comment = EXCLUDED.is_late_comment,
                author_date = EXCLUDED.author_date,
                comment_category = EXCLUDED.comment_category,
                city = EXCLUDED.city,
                comment = EXCLUDED.comment,
                comment_end_date = EXCLUDED.comment_end_date,
                comment_start_date = EXCLUDED.comment_start_date,
                country = EXCLUDED.country,
                docket_id = EXCLUDED.docket_id,
                document_type = EXCLUDED.document_type,
                effective_date = EXCLUDED.effective_date,
                email = EXCLUDED.email,
                fax = EXCLUDED.fax,
                flex_field1 = EXCLUDED.flex_field1,
                flex_field2 = EXCLUDED.flex_field2,
                first_name = EXCLUDED.first_name,
                submitter_gov_agency = EXCLUDED.submitter_gov_agency,
                submitter_gov_agency_type = EXCLUDED.submitter_gov_agency_type,
                implementation_date = EXCLUDED.implementation_date,
                last_name = EXCLUDED.last_name,
                modify_date = EXCLUDED.modify_date,
                is_open_for_comment = EXCLUDED.is_open_for_comment,
                submitter_org = EXCLUDED.submitter_org,
                phone = EXCLUDED.phone,
                posted_date = EXCLUDED.posted_date,
                postmark_date = EXCLUDED.postmark_date,
                reason_withdrawn = EXCLUDED.reason_withdrawn,
                receive_date = EXCLUDED.receive_date,
                reg_writer_instruction = EXCLUDED.reg_writer_instruction,
                restriction_reason = EXCLUDED.restriction_reason,
                restriction_reason_type = EXCLUDED.restriction_reason_type,
                state_province_region = EXCLUDED.state_province_region,
                subtype = EXCLUDED.subtype,
                document_title = EXCLUDED.document_title,
                topics = EXCLUDED.topics,
                is_withdrawn = EXCLUDED.is_withdrawn,
                postal_code = EXCLUDED.postal_code,
                frdocnum = EXCLUDED.frdocnum,
                attachments_self_link = EXCLUDED.attachments_self_link,
                attachments_related_link = EXCLUDED.attachments_related_link,
                file_formats = EXCLUDED.file_formats,
                display_properties = EXCLUDED.display_properties;
            """
            cursor.execute(insert_query, values)
            print(f"Document {document_id} inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Main function to read JSON from file and insert into the database
# Main function to read JSON from file and insert into the database
def main():
    if len(sys.argv) != 2:
        print("Usage: python IngestDocument.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    load_dotenv()
    dbname = os.getenv("POSTGRES_DB")
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")

    conn_params = {
        "dbname": dbname,
        "user": username,
        "password": password,
        "host": host,
        "port": port,
    }
    try:
        with open(json_file_path, "r") as json_file:
            json_data = json_file.read()
            with psycopg.connect(**conn_params) as conn:
                insert_document(conn, json_data)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
