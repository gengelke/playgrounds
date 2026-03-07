#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_URL="${API_URL:-http://127.0.0.1:8000}"

echo "Downloading full introspection schema from ${API_URL}..."

curl -sS -X POST "${API_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d @<(echo '{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name } } }"}') \
  > "${ROOT_DIR}/schema.json"

curl -sS -X GET "${API_URL}/schema.graphql" -o "${ROOT_DIR}/schema.graphql"

echo "Generating Python client..."
(
  cd "${ROOT_DIR}"
  ariadne-codegen client --config library-builder/pyproject.toml
)

echo "Done."
