#!/usr/bin/env bash
set -Eeuo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$script_dir/.." && pwd)"
version="${1:-$(tr -d '[:space:]' < "$repo_dir/VERSION")}"

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  printf 'Version must use MAJOR.MINOR.PATCH, for example 1.0.0.\n' >&2
  exit 1
fi

if ! command -v zip >/dev/null 2>&1; then
  printf 'The zip command is required.\n' >&2
  exit 1
fi

if ! command -v sha256sum >/dev/null 2>&1; then
  printf 'sha256sum is required.\n' >&2
  exit 1
fi

"$script_dir/validate-repository.sh"

output_dir="$repo_dir/_release-assets/v$version"
mkdir -p -- "$output_dir"

license_files=(LICENSE LICENSE-CONTENT.md NOTICE)
staging_dir="$(mktemp -d "${TMPDIR:-/tmp}/vulnsec-release.XXXXXX")"
cleanup() {
  rm -rf -- "$staging_dir"
}
trap cleanup EXIT

while IFS= read -r -d '' package_dir; do
  package_name="$(basename "$package_dir")"
  archive_path="$output_dir/${package_name}-Student-Kit-v${version}.zip"
  package_stage="$staging_dir/$package_name"
  cp -a -- "$package_dir" "$package_stage"
  for license_file in "${license_files[@]}"; do
    cp -- "$repo_dir/$license_file" "$package_stage/$license_file"
  done
  rm -f -- "$archive_path"
  (
    cd -- "$staging_dir"
    zip -qr "$archive_path" "$package_name"
  )
  printf 'Built %s\n' "$(basename "$archive_path")"
done < <(find "$repo_dir/labs" -mindepth 2 -maxdepth 2 -type d -print0 | sort -z)

complete_archive="$output_dir/Vulnsec-Academy-Complete-Lab-Range-v${version}.zip"
rm -f -- "$complete_archive"
(
  cd -- "$repo_dir"
  zip -qr "$complete_archive" \
    README.md LAB-CATALOG.md QUICKSTART.md REQUIREMENTS.md TROUBLESHOOTING.md \
    ETHICAL-USE.md SECURITY.md CHANGELOG.md VERSION \
    LICENSE LICENSE-CONTENT.md NOTICE labs
)

(
  cd -- "$output_dir"
  sha256sum -- *.zip > SHA256SUMS.txt
)

printf 'Release assets are ready in %s\n' "$output_dir"
