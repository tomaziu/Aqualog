#!/usr/bin/env bash
# Build script for frontend: concatenates all JS files in the correct order.

set -e

FRONTEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JS_DIR="$FRONTEND_DIR/js"
OUTPUT_DIR="$FRONTEND_DIR/dist"
OUTPUT_FILE="$OUTPUT_DIR/bundle.js"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Define the order of files as they appear in index.html
FILES=(
  "api.js"
  "utils.js"
  "login.js"
  "dashboard.js"
  "clientes.js"
  "entregadores.js"
  "produtos.js"
  "pedidos.js"
  "suporte.js"
  "relatorio.js"
  "app.js"
)

# Concatenate
echo "Building frontend bundle..."
> "$OUTPUT_FILE"
for file in "${FILES[@]}"; do
  if [[ -f "$JS_DIR/$file" ]]; then
    echo "Adding $file"
    cat "$JS_DIR/$file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE" # Add a newline between files for readability
  else
    echo "Warning: $JS_DIR/$file not found!" >&2
  fi
done

echo "Bundle created at $OUTPUT_FILE"