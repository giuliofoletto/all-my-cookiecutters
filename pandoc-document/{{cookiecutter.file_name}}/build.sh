#!/bin/bash


# Get the current directory
currentFolderPath=$(pwd)

# Find all markdown files in the directory
markdownFiles=("$currentFolderPath"/*.md)

# Loop through each markdown file and run the command
for file in "${markdownFiles[@]}"; do
  if [ -f "$file" ]; then
    name=$(basename "$file")
    echo "Building PDF from $name"
    pandoc "$name" -o "${name%.*}.pdf" --from markdown --template pandoc_latex_template --listings


# Find and remove subfolders starting with "tex2pdf"
found=false
for dir in "$currentFolderPath"/tex2pdf*/; do
  if [ -d "$dir" ]; then
    found=true
    echo "Deleting folder: $dir"
    rm -rf "$dir"
  fi
done

if ! $found; then
  echo "No subfolders starting with 'tex2pdf' found."
fi
