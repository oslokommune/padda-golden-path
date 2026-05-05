# Use this script to read the JSON privilege backups and convert to SQL statements

import json
import os
import sys


def generate_sql_from_json(json_file, object_type, name_fn):
    with open(json_file) as f:
        for line in f:
            data = json.loads(line)
            if data.get("inherited_from", "NONE") == "NONE":
                object_name = name_fn(data)
                grant = (
                    f"GRANT {data['privilege_type']} ON {object_type}"
                    f" {object_name} TO `{data['grantee']}`;"
                )
                print(grant)


OBJECT_CONFIGS = [
    (
        "catalog_privileges.json",
        "CATALOG",
        lambda d: d["catalog_name"],
    ),
    (
        "schema_privileges.json",
        "SCHEMA",
        lambda d: f"{d['catalog_name']}.{d['schema_name']}",
    ),
    (
        "table_privileges.json",
        "TABLE",
        lambda d: f"{d['table_catalog']}.{d['table_schema']}.{d['table_name']}",
    ),
    (
        "volume_privileges.json",
        "VOLUME",
        lambda d: f"{d['volume_catalog']}.{d['volume_schema']}.{d['volume_name']}",
    ),
]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <json_dir>", file=sys.stderr)
        sys.exit(1)

    json_dir = sys.argv[1]
    files = os.listdir(json_dir)

    for filename, object_type, name_fn in OBJECT_CONFIGS:
        if filename not in files:
            print(f"{filename} not found in {json_dir}", file=sys.stderr)
            sys.exit(1)
        generate_sql_from_json(os.path.join(json_dir, filename), object_type, name_fn)
