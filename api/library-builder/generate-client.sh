#!/bin/bash

echo "Downloading GraphQL introspection schema..."

curl -X POST http://fastapi:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name } } }"}' \
  > /workspace/schema.json


echo "Downloading full introspection schema..."

curl -X POST http://fastapi:8000/graphql \
  -H "Content-Type: application/json" \
  -d @<(echo '{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name } } }"}') \
  > /workspace/schema.json

curl -X GET http://fastapi:8000/schema.graphql -o schema.graphql

echo "Generating Python client..."

ariadne-codegen client --config /workspace/library-builder/pyproject.toml

echo "Done."
