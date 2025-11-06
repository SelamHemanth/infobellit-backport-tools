#!/bin/bash

BASE_LINKS_FILE="$HOME/.gen_hyperlink_links"
touch "$BASE_LINKS_FILE"

# Add base link
if [[ "$1" == "--add" || "$1" == "-a" ]]; then
    if [[ -n "$2" ]]; then
        echo "$2" >> "$BASE_LINKS_FILE"
        index=$(wc -l < "$BASE_LINKS_FILE")
        echo "✅ Added as index $index: $2"
    else
        echo "❌ Missing link. Usage: ./gen_hyperlink.sh --add/-a <link>"
    fi
    exit 0
fi

# Remove base link
if [[ "$1" == "--remove" || "$1" == "-r" ]]; then
    if [[ "$2" =~ ^[0-9]+$ ]]; then
        index="$2"
        total=$(wc -l < "$BASE_LINKS_FILE")
        if (( index > 0 && index <= total )); then
            sed -i "${index}d" "$BASE_LINKS_FILE"
            echo "🗑️ Removed base link at index $index"
        else
            echo "❌ Invalid index: $index"
        fi
    else
        echo "❌ Missing or invalid index. Usage: ./gen_hyperlink.sh --remove/-r <index>"
    fi
    exit 0
fi

# List base links
if [[ "$1" == "--list" || "$1" == "-l" ]]; then
    echo "📌 Saved base links:"
    nl -w2 -s'. ' "$BASE_LINKS_FILE"
    exit 0
fi

# Use base link by index
if [[ "$1" =~ ^[0-9]+$ ]]; then
    index="$1"
    base_link=$(sed -n "${index}p" "$BASE_LINKS_FILE")
    if [[ -z "$base_link" ]]; then
        echo "❌ No base link found at index $index"
        exit 1
    fi
    echo "🔗 Using base link [$index]: $base_link"
    echo "Paste IDs (one per line). Type 'done' when finished:"

    output_file="links_file.html"
    cat > "$output_file" <<EOF
<!DOCTYPE html>
<html>
<head>
  <title>Links</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      padding: 20px;
    }
    h2 {
      color: #333;
    }
    ul {
      list-style-type: none;
      padding-left: 0;
    }
    li {
      margin: 8px 0;
    }
    a {
      color: #0077cc;
      text-decoration: none;
      font-weight: bold;
    }
    a:hover {
      text-decoration: underline;
      color: #005599;
    }
  </style>
</head>
<body>
  <h2>Output with Links (Base $index)</h2>
  <ul>
EOF

    while IFS= read -r commit_id; do
        [[ "$commit_id" == "done" ]] && break
        [[ -n "$commit_id" ]] && echo "    <li><a href=\"${base_link}${commit_id}\">${commit_id}</a></li>" >> "$output_file"
    done

    cat >> "$output_file" <<EOF
  </ul>
</body>
</html>
EOF

    echo "✅ HTML file generated: $output_file"
    exit 0
fi

# Help message
echo "Usage:"
echo "  ./gen_hyperlink.sh --add/-a <link>     # Add a new base link"
echo "  ./gen_hyperlink.sh --remove/-r <index> # Remove base link at index"
echo "  ./gen_hyperlink.sh --list/-l           # List saved base links"
echo "  ./gen_hyperlink.sh <index>             # Use base link at index"
exit 1
