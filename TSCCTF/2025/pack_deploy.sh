#!/bin/bash

skip_dirs=("sol" "deploy" "shared" "_memo" "__pycache__")

should_skip() {
    local dir="$1"
    for skip_dir in "${skip_dirs[@]}"; do
        if [[ "$dir" == "$skip_dir/" ]]; then
            return 0
        fi
    done
    return 1
}

cleanup() {
    local dir="$1"
    find "$dir" -type d -name "__pycache__" -exec rm -rf {} +
    find "$dir" -type d -name ".ropeproject" -exec rm -rf {} +
    find "$dir" -type f -name "*.DS_Store" -exec rm -f {} +
    find "$dir" -type f -name "*.db" -exec rm -f {} +
    find "$dir" -type f -name "exploit.py" -exec rm -f {} +
    find "$dir" -type f -name "Readme.md" -exec rm -f {} +
}

rm deploy/*.zip

for p in $(ls -d */); do
    if ! should_skip "$p"; then
        echo "Processing deploy $p"
        tmp_dir="deploy_tmp_$p"
        cp -r "$p" "$tmp_dir"
        cleanup $tmp_dir
        zip -r "deploy/${p%/}-deploy.zip" $tmp_dir -x ".DS_Store" "exploit.py" "**/__pycache__" "**/.ropeproject" "Readmd.md"
        rm -rf $tmp_dir
    fi
done

rm shared/*.zip

for p in $(ls -d */); do
    if ! should_skip "$p"; then
        echo "Processing shared $p"
        tmp_dir="shared_tmp_$p"
        cp -r "$p" "$tmp_dir"
        cleanup $tmp_dir
        find $tmp_dir -type f -exec sed -i '' -e 's/TSC{[^}]*}/TSC{fakeflag}/g' {} \;
        zip -r "shared/${p%/}-shared.zip" "$tmp_dir" -x ".DS_Store" "exploit.py" "**/__pycache__" "**/.ropeproject" "Readmd.md"
        rm -rf "$tmp_dir"
    fi
done
