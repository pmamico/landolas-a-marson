#!/usr/bin/env bash
set -euo pipefail

# Optional overrides
DO_SSH_USER="${DO_SSH_USER:-root}"
DO_DROPLET_PREFIX="${DO_DROPLET_PREFIX:-mars}"
DO_IMAGE_SLUG="${DO_IMAGE_SLUG:-docker-20-04}"
DO_GIT_REPO="${DO_GIT_REPO:-https://github.com/pmamico/landolas-a-marson}"
DO_GIT_DIR="${DO_GIT_DIR:-landolas-a-marson}"
DO_REGION="${DO_REGION:-fra1}"
DOCTL_CTX="${DOCTL_CTX:---context gui}"
DO_SSH_KEY_NAME="${DO_SSH_KEY_NAME:-m1}"
SSH_WAIT_SECONDS="${SSH_WAIT_SECONDS:-5}"

log() { printf "[%s] %s\n" "$(date '+%F %T')" "$*" >&2; }

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

usage() {
  cat >&2 <<'EOF'
Usage:
  ./do.sh             # create the next droplet
  ./do.sh N           # create the next N droplets
  ./do.sh list        # list droplets with IPv4
  ./do.sh reset       # delete all droplets with the configured prefix
  ./do.sh rm N        # delete droplet <prefix>-N
EOF
  exit 1
}

need doctl
need awk
need grep
need sort
REMOTE_SCRIPT="$(cat <<'EOS'
set -euo pipefail

REPO_URL="https://github.com/pmamico/landolas-a-marson"
REPO_DIR="landolas-a-marson"

if ! command -v git >/dev/null 2>&1; then
  apt-get update -y
  apt-get install -y git
fi

if [[ -d "${REPO_DIR}/.git" ]]; then
  cd "${REPO_DIR}"
  git fetch --all --prune
  git reset --hard origin/HEAD
else
  git clone "${REPO_URL}"
  cd "${REPO_DIR}"
fi

if [[ -d "notebooks" ]]; then
  chmod -R 777 "notebooks"
fi

NOTEBOOK_PATH="notebooks"
if [[ -d "${NOTEBOOK_PATH}" ]]; then
  # Ensure the Jupyter runtime dir is writable for the notebook UID/GID
  chown -R 1000:100 "${NOTEBOOK_PATH}"
  chmod -R u+rwX,g+rwX "${NOTEBOOK_PATH}"
fi

docker compose up -d
EOS
)"

lookup_ssh_key() {
  log "Looking up SSH key named '${DO_SSH_KEY_NAME}' in DigitalOcean account..."
  local ssh_key_id
  ssh_key_id="$(doctl ${DOCTL_CTX} compute ssh-key list --format ID,Name --no-header \
    | awk -v key="${DO_SSH_KEY_NAME}" '$2==key{print $1; exit}')"

  if [[ -z "${ssh_key_id}" ]]; then
    echo "ERROR: Could not find an SSH key with Name == '${DO_SSH_KEY_NAME}' via: doctl ${DOCTL_CTX} compute ssh-key list" >&2
    echo "Tip: run: doctl ${DOCTL_CTX} compute ssh-key list --format ID,Name,Fingerprint" >&2
    exit 1
  fi
  log "Using SSH key ID: ${ssh_key_id} (Name: ${DO_SSH_KEY_NAME})"
  printf '%s' "${ssh_key_id}"
}

determine_max_suffix() {
  local existing_names="$1"
  local max_n=0
  while IFS= read -r name; do
    [[ -z "${name}" ]] && continue
    if [[ "${name}" =~ ^${DO_DROPLET_PREFIX}-([0-9]+)$ ]]; then
      local n="${BASH_REMATCH[1]}"
      if (( n > max_n )); then
        max_n="$n"
      fi
    fi
  done <<< "${existing_names}"
  printf '%s' "${max_n}"
}

wait_for_ipv4() {
  local droplet_id="$1"
  local ipv4=""
  local status=""
  log "Waiting for droplet ${droplet_id} to become active and get a public IPv4..."
  for _ in {1..120}; do
    status="$(doctl ${DOCTL_CTX} compute droplet get "${droplet_id}" --format Status --no-header 2>/dev/null || true)"
    ipv4="$(doctl ${DOCTL_CTX} compute droplet get "${droplet_id}" --format PublicIPv4 --no-header 2>/dev/null || true)"
    if [[ "${status}" == "active" && -n "${ipv4}" && "${ipv4}" != "<nil>" ]]; then
      printf '%s' "${ipv4}"
      return
    fi
    sleep 5
  done
  echo ""  # Timed out
}

run_remote_setup() {
  local droplet_id="$1"
  local attempt=1
  while true; do
    log "Attempting remote deployment on droplet ${droplet_id} (ssh attempt ${attempt})..."
    if doctl ${DOCTL_CTX} compute ssh "${droplet_id}" --ssh-user "${DO_SSH_USER}" --ssh-command "bash -lc $(printf '%q' "${REMOTE_SCRIPT}")"; then
      log "Remote deployment finished on droplet ${droplet_id} (attempt ${attempt})."
      break
    fi
    log "SSH attempt ${attempt} failed, retrying in ${SSH_WAIT_SECONDS}s..."
    sleep "${SSH_WAIT_SECONDS}"
    attempt=$((attempt + 1))
  done
}

create_single_droplet() {
  local droplet_name="$1"
  local ssh_key_id="$2"
  log "Creating droplet '${droplet_name}' in region '${DO_REGION}' with image '${DO_IMAGE_SLUG}'..."
  local create_out
  create_out="$(
    doctl ${DOCTL_CTX} compute droplet create "${droplet_name}" \
      --region "${DO_REGION}" \
      --size "s-1vcpu-2gb" \
      --image "${DO_IMAGE_SLUG}" \
      --ssh-keys "${ssh_key_id}" \
      --enable-monitoring \
      --wait \
      --format ID,Name,Status,PublicIPv4 \
      --no-header
  )"

  local droplet_id
  droplet_id="$(awk '{print $1}' <<< "${create_out}")"
  if [[ -z "${droplet_id}" ]]; then
    echo "ERROR: Failed to parse droplet ID from doctl output:" >&2
    echo "${create_out}" >&2
    exit 1
  fi
  log "Created droplet ID: ${droplet_id}"

  local ipv4
  ipv4="$(wait_for_ipv4 "${droplet_id}")"
  if [[ -z "${ipv4}" ]]; then
    echo "ERROR: Droplet ${droplet_name} did not get a public IPv4 in time." >&2
    exit 1
  fi
  log "Droplet ${droplet_name} is active with IPv4: ${ipv4}"

  run_remote_setup "${droplet_id}"
  log "Done. Droplet: ${droplet_name} (${ipv4})"
  printf 'http://%s:8888\n' "${ipv4}"
}

create_droplets() {
  local count="$1"
  log "Determining next droplet name with prefix '${DO_DROPLET_PREFIX}-' ..."
  local existing_names
  existing_names="$({ doctl ${DOCTL_CTX} compute droplet list --format Name --no-header 2>/dev/null || true; } | sort)"
  local max_n
  max_n="$(determine_max_suffix "${existing_names}")"
  local ssh_key_id
  ssh_key_id="$(lookup_ssh_key)"
  local next_n=$((max_n + 1))
  for ((idx=0; idx<count; idx++)); do
    local droplet_name="${DO_DROPLET_PREFIX}-${next_n}"
    create_single_droplet "${droplet_name}" "${ssh_key_id}"
    next_n=$((next_n + 1))
  done
}

list_droplets() {
  local rows
  rows="$({ doctl ${DOCTL_CTX} compute droplet list --format Name,PublicIPv4 --no-header 2>/dev/null || true; } | sort)"
  local found=0
  printf "%-20s %s\n" "NAME" "IPV4"
  while read -r name ipv4; do
    [[ -z "${name}" ]] && continue
    if [[ "${name}" == ${DO_DROPLET_PREFIX}-* ]]; then
      [[ -z "${ipv4}" || "${ipv4}" == "<nil>" ]] && ipv4="-"
      printf "%-20s %s\n" "${name}" "${ipv4}"
      found=1
    fi
  done <<< "${rows}"
  if (( found == 0 )); then
    log "No droplets found with prefix '${DO_DROPLET_PREFIX}-'."
  fi
}

delete_droplet_by_name() {
  local droplet_name="$1"
  local droplet_id
  droplet_id="$(doctl ${DOCTL_CTX} compute droplet list --format ID,Name --no-header \
    | awk -v target="${droplet_name}" '$2==target{print $1; exit}')"
  if [[ -z "${droplet_id}" ]]; then
    echo "ERROR: Could not find droplet named '${droplet_name}'." >&2
    exit 1
  fi
  log "Deleting droplet ${droplet_name} (ID: ${droplet_id})"
  doctl ${DOCTL_CTX} compute droplet delete "${droplet_id}" --force >/dev/null
  log "Deleted ${droplet_name}"
}

reset_droplets() {
  local rows
  rows="$(doctl ${DOCTL_CTX} compute droplet list --format ID,Name --no-header 2>/dev/null || true)"
  local deleted=0
  while read -r droplet_id droplet_name; do
    [[ -z "${droplet_id}" ]] && continue
    if [[ "${droplet_name}" == ${DO_DROPLET_PREFIX}-* ]]; then
      log "Deleting droplet ${droplet_name} (ID: ${droplet_id})"
      doctl ${DOCTL_CTX} compute droplet delete "${droplet_id}" --force >/dev/null
      ((deleted++))
    fi
  done <<< "${rows}"
  if (( deleted == 0 )); then
    log "No droplets found with prefix '${DO_DROPLET_PREFIX}-'."
  else
    log "Deleted ${deleted} droplet(s)."
  fi
}

normalize_suffix() {
  local raw="$1"
  if [[ "${raw}" =~ ^[0-9]+$ ]]; then
    printf '%s' "${raw}"
  elif [[ "${raw}" =~ ^${DO_DROPLET_PREFIX}-([0-9]+)$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
  else
    echo "ERROR: Invalid droplet identifier '${raw}'. Use a numeric suffix." >&2
    exit 1
  fi
}

handle_delete() {
  local suffix
  suffix="$(normalize_suffix "$1")"
  delete_droplet_by_name "${DO_DROPLET_PREFIX}-${suffix}"
}

main() {
  local action="create"
  local count=1
  local rm_arg=""

  if [[ $# -eq 0 ]]; then
    action="create"
  else
    case "$1" in
      list)
        action="list"
        [[ $# -eq 1 ]] || usage
        ;;
      reset)
        action="reset"
        [[ $# -eq 1 ]] || usage
        ;;
      rm)
        action="rm"
        rm_arg="${2:-}"
        [[ $# -eq 2 && -n "${rm_arg}" ]] || usage
        ;;
      create)
        action="create"
        count="${2:-1}"
        [[ $# -le 2 ]] || usage
        ;;
      *)
        if [[ "$1" =~ ^[0-9]+$ ]]; then
          action="create"
          count="$1"
          [[ $# -eq 1 ]] || usage
        else
          usage
        fi
        ;;
    esac
  fi

  case "${action}" in
    create)
      if ! [[ "${count}" =~ ^[0-9]+$ ]] || (( count < 1 )); then
        echo "ERROR: Count must be a positive integer." >&2
        exit 1
      fi
      create_droplets "${count}"
      ;;
    list)
      list_droplets
      ;;
    reset)
      reset_droplets
      ;;
    rm)
      handle_delete "${rm_arg}"
      ;;
    *)
      usage
      ;;
  esac
}

main "$@"