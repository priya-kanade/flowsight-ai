import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

def merge_jsonl_files(input_folder, output_filename):
    output_file = os.path.join(DATA_DIR, output_filename)

    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in os.listdir(input_folder):
            if filename.endswith(".jsonl"):
                path = os.path.join(input_folder, filename)

                with open(path, "r", encoding="utf-8") as infile:
                    for line in infile:
                        outfile.write(line)

    print(f"✅ Merged into {output_file}")

# -------- RUN FOR EACH DATASET --------
base_path = "C:/Users/priya/Downloads/sap-order-to-cash-dataset/sap-o2c-data"
merge_jsonl_files(
    os.path.join(base_path, "sales_order_headers"),
    "sales_order_headers.jsonl"
)


merge_jsonl_files(
    os.path.join(base_path, "sales_order_items"),
    "sales_order_items.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "outbound_delivery_headers"),
    "deliveries.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "outbound_delivery_items"),
    "delivery_items.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "billing_document_headers"),
    "billing.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "billing_document_items"),
    "billing_items.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "business_partners"),
    "customers.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "business_partner_addresses"),
    "addresses.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "products"),
    "products.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "product_descriptions"),
    "product_descriptions.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "journal_entry_items_accounts_receivable"),
    "accounting.jsonl"
)

merge_jsonl_files(
    os.path.join(base_path, "payments_accounts_receivable"),
    "payments.jsonl"
)