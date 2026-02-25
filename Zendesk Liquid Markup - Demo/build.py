# build.py
import os
import requests
import json
from config_sandbox import SUBDOMAIN, EMAIL, API_TOKEN
from dynamic_contents import DCS  # Mapping of file paths -> DC names

TEMPLATE_DIR = r"Liquid"
auth = (f"{EMAIL}/token", API_TOKEN)
headers = {"Content-Type": "application/json"}

def load_template(filename):
    """
    Load a single Liquid template file (no recursion needed).
    """
    path = os.path.join(TEMPLATE_DIR, filename)
    if not os.path.isfile(path):
        print(f"Warning: File not found: {path}")
        return f"<!-- Missing file: {filename} -->"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def push_dc(dc_name, content):
    """
    Push a single Dynamic Content item to Zendesk.
    Updates variant content if item exists, creates item if not.
    """
    try:
        # Get existing DC items
        url_list = f"https://{SUBDOMAIN}.zendesk.com/api/v2/dynamic_content/items.json"
        response = requests.get(url_list, auth=auth)
        data = response.json()

        existing_item = None
        for item in data.get("items", []):
            if item["name"] == dc_name:
                existing_item = item
                break

        if existing_item:
            item_id = existing_item["id"]

            # Get variants for this item
            variant_url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/dynamic_content/items/{item_id}/variants.json"
            variant_response = requests.get(variant_url, auth=auth)
            variant_data = variant_response.json()

            # Find default variant (locale_id 1 in system)
            default_variant = None
            for variant in variant_data.get("variants", []):
                if variant.get("locale_id") == 1:
                    default_variant = variant
                    break

            if not default_variant:
                print(f"No default variant found for '{dc_name}'")
                return

            variant_id = default_variant["id"]

            # Update ONLY the content field
            update_payload = {
                "variant": {
                    "content": content
                }
            }

            update_url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/dynamic_content/items/{item_id}/variants/{variant_id}.json"
            r = requests.put(
                update_url,
                headers=headers,
                auth=auth,
                data=json.dumps(update_payload)
            )

            print(f"Updated DC '{dc_name}': {r.status_code}")
            if r.status_code != 200:
                print(r.text)

        else:
            # Create new item (this creates default variant automatically)
            create_payload = {
                "item": {
                    "name": dc_name,
                    "variants": [
                        {
                            "locale_id": 1,
                            "default": True,
                            "active": True,
                            "content": content
                        }
                    ]
                }
            }

            url_create = f"https://{SUBDOMAIN}.zendesk.com/api/v2/dynamic_content/items.json"
            r = requests.post(
                url_create,
                headers=headers,
                auth=auth,
                data=json.dumps(create_payload)
            )

            print(f"Created DC '{dc_name}': {r.status_code}")
            if r.status_code != 201:
                print(r.text)

    except Exception as e:
        print(f"Error pushing DC '{dc_name}': {e}")


if __name__ == "__main__":
    # Load lib once
    lib_content = load_template("library_sandbox.liquid")

    # Closed-loop per DC
    for file_path, dc_name in DCS.items():
        print(f"\nProcessing DC: {dc_name} ({file_path})")

        # Load the DC content
        dc_content = load_template(file_path)

        # Prepend lib content
        final_content = lib_content + "\n" + dc_content

        # Push to Zendesk
        push_dc(dc_name, final_content)

    print("\nAll DCs processed.")

