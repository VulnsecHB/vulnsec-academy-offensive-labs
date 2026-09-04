#!/usr/bin/env bash
set -Eeuo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$script_dir/.." && pwd)"
labs_dir="$repo_dir/labs"

expected_count=28
actual_count=0
failures=0

root_required_files=(
  LICENSE
  LICENSE-CONTENT.md
  NOTICE
)

for required_file in "${root_required_files[@]}"; do
  if [[ ! -f "$repo_dir/$required_file" ]]; then
    printf 'Missing repository licence file %s.\n' "$required_file" >&2
    ((failures += 1))
  fi
done

if [[ -f "$repo_dir/LICENSE" ]] && ! grep -Fqx 'Required Notice: Copyright © 2026 Vulnsec Academy.' "$repo_dir/LICENSE"; then
  printf 'The required pseudonymous copyright notice is missing from LICENSE.\n' >&2
  ((failures += 1))
fi

if [[ -e "$repo_dir/LICENSE-DECISION.md" ]]; then
  printf 'LICENSE-DECISION.md remains after the final licence was selected.\n' >&2
  ((failures += 1))
fi

required_files=(
  README.md
  docker-compose.yml
  scripts/start.sh
  scripts/stop.sh
  scripts/status.sh
  scripts/reset.sh
)

required_readme_sections=(
  '## Student scope'
  '## Environment architecture'
  '## Linux Docker setup'
)

while IFS= read -r -d '' package_dir; do
  ((actual_count += 1))
  for required_file in "${required_files[@]}"; do
    if [[ ! -f "$package_dir/$required_file" ]]; then
      printf 'Missing %s in %s\n' "$required_file" "${package_dir#"$repo_dir/"}" >&2
      ((failures += 1))
    fi
  done
  for required_section in "${required_readme_sections[@]}"; do
    if ! grep -Fqx "$required_section" "$package_dir/README.md"; then
      printf 'Missing README section %s in %s\n' "$required_section" "${package_dir#"$repo_dir/"}" >&2
      ((failures += 1))
    fi
  done
done < <(find "$labs_dir" -mindepth 2 -maxdepth 2 -type d -print0 | sort -z)

if [[ "$actual_count" -ne "$expected_count" ]]; then
  printf 'Expected %s packages but found %s.\n' "$expected_count" "$actual_count" >&2
  ((failures += 1))
fi

if find "$labs_dir" -type f -name '*.zip' -print -quit | grep -q .; then
  printf 'Nested ZIP files were found inside labs/. Release archives should be generated, not committed there.\n' >&2
  ((failures += 1))
fi

if find "$labs_dir" -type f \( -name '.DS_Store' -o -name '*.swp' -o -name '*.tmp' \) -print -quit | grep -q .; then
  printf 'Temporary or operating-system metadata files were found.\n' >&2
  ((failures += 1))
fi

if [[ "$failures" -ne 0 ]]; then
  printf 'Repository validation failed with %s problem(s).\n' "$failures" >&2
  exit 1
fi

printf 'Repository validation passed: %s packages.\n' "$actual_count"
