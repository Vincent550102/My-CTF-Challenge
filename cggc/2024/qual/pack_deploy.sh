#!/bin/bash

skip_dirs=("sol" "deploy" "breakjail-archived" "shared")

should_skip() {
    local dir="$1"
    for skip_dir in "${skip_dirs[@]}"; do
        if [[ "$dir" == "$skip_dir/" ]]; then
            return 0
        fi
    done
    return 1
}

rm deploy/*.zip

for p in $(ls -d */); do
    if ! should_skip "$p"; then
        echo "Processing deploy $p"
        zip -r "deploy/${p%/}-deploy.zip" $p -x "*.DS_Store"
    fi
done

rm shared/*.zip

for p in $(ls -d */); do
    if ! should_skip "$p"; then
        echo "Processing shared $p"
        tmp_dir="shared_$p"
        cp -r "$p" "$tmp_dir"
        find $tmp_dir -type f -exec sed -i '' -e 's/CGGC{[^}]*}/CGGC{fakeflag}/g' {} \;
        zip -r "shared/${p%/}-shared.zip" "$tmp_dir" -x "*.DS_Store"
        rm -rf "$tmp_dir"
    fi
done
