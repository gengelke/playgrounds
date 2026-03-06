import json
from main import schema


# --------------------------
# Export schema.graphql
# --------------------------
with open("schema.graphql", "w") as f:
    f.write(schema.as_str())

print("schema.graphql created")


# --------------------------
# Export schema.json
# --------------------------
introspection = schema.introspect()

with open("schema.json", "w") as f:
    json.dump(introspection, f, indent=2)

print("schema.json created")
