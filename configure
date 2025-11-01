#!/usr/bin/env bash
set -euo pipefail

# run.sh
# Modes:
#   --config   run interactive configure (exec ./configure if present)
#   --build    generate/modify/apply patches and build (applies one patch at a time)
#   --reset    reset linux repo to saved HEAD commit (no build)
#   --clean    remove patches/ and logs/

CONFIG_FILE=".configure"
MODE=""
WORKDIR="$(pwd)"
PATCHES_DIR="${WORKDIR}/patches"
BKP_DIR="${PATCHES_DIR}/.bkp"
LOGS_DIR="${WORKDIR}/logs"
HEAD_ID_FILE="${WORKDIR}/.head_commit_id"

# color helpers
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# parse args
while [ $# -gt 0 ]; do
  case "$1" in
    --config) MODE="config"; shift ;;
    --build)  MODE="build"; shift ;;
    --reset)  MODE="reset"; shift ;;
    --clean)  MODE="clean"; shift ;;
    -h|--help)
      cat <<EOF
Usage:
  ./run.sh --config             # run interactive configure (./configure)
  ./run.sh --build              # generate/modify/apply patches and build
  ./run.sh --reset              # reset linux repo to saved HEAD (no apply/build)
  ./run.sh --clean              # remove patches/ and logs/
EOF
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ -z "${MODE}" ]; then
  echo "No mode specified. Use --config, --build, --reset or --clean." >&2
  exit 1
fi

# mode handlers
if [ "${MODE}" = "config" ]; then
  if [ -x "./configure" ]; then
    exec ./configure "${CONFIG_FILE}"
  else
    echo "No ./configure script found or not executable." >&2
    exit 3
  fi
fi

if [ "${MODE}" = "clean" ]; then
  rm -rf "${PATCHES_DIR}" "${LOGS_DIR}" "${HEAD_ID_FILE}"
  echo -e "${GREEN}CLEAN: OK${NC}"
  exit 0
fi

if [ "${MODE}" = "reset" ]; then
  if [ ! -f "${CONFIG_FILE}" ]; then
    echo "Configuration file ${CONFIG_FILE} not found." >&2
    exit 4
  fi
  # load config for linux path
  # shellcheck disable=SC1090
  . "${CONFIG_FILE}"
  : "${LINUX_SRC_PATH:?missing in config}"
  if [ ! -f "${HEAD_ID_FILE}" ]; then
    echo "Head commit id file ${HEAD_ID_FILE} not found. Run --build once to record HEAD id." >&2
    exit 5
  fi
  HEAD_ID="$(cat "${HEAD_ID_FILE}")"
  if [ -z "${HEAD_ID}" ]; then
    echo "Saved HEAD id is empty." >&2
    exit 6
  fi
  if [ ! -d "${LINUX_SRC_PATH}/.git" ]; then
    echo "Linux source path is not a git repo: ${LINUX_SRC_PATH}" >&2
    exit 7
  fi
  git -C "${LINUX_SRC_PATH}" reset --hard "${HEAD_ID}"
  echo -e "${GREEN}RESET: OK -> ${HEAD_ID}${NC}"
  exit 0
fi

# MODE = build
if [ "${MODE}" != "build" ]; then
  echo "Unhandled mode: ${MODE}" >&2
  exit 8
fi

# check config
if [ ! -f "${CONFIG_FILE}" ]; then
  echo "Configuration file not found: ${CONFIG_FILE}. Run --config first." >&2
  exit 9
fi
# shellcheck disable=SC1090
. "${CONFIG_FILE}"
: "${LINUX_SRC_PATH:?missing in config}"
: "${SIGNER_NAME:?missing in config}"
: "${SIGNER_EMAIL:?missing in config}"
: "${ANBZ_ID:?missing in config}"
: "${NUM_PATCHES:?missing in config}"

mkdir -p "${PATCHES_DIR}" "${BKP_DIR}" "${LOGS_DIR}"

# validate repo
if [ ! -d "${LINUX_SRC_PATH}/.git" ]; then
  echo "Linux source path is not a git repo: ${LINUX_SRC_PATH}" >&2
  exit 10
fi

cd "${LINUX_SRC_PATH}"
TOTAL_COMMITS="$(git rev-list --count HEAD 2>/dev/null || true)"
if [ -z "${TOTAL_COMMITS}" ] || [ "${TOTAL_COMMITS}" -lt "${NUM_PATCHES}" ]; then
  echo "Repo has insufficient commits (${TOTAL_COMMITS}) for NUM_PATCHES=${NUM_PATCHES}" >&2
  exit 11
fi

# Save current HEAD id for later reset (full SHA)
HEAD_ID="$(git rev-parse --verify HEAD)"
printf "%s\n" "${HEAD_ID}" > "${HEAD_ID_FILE}"

TMP_FORMAT_DIR="$(mktemp -d "${WORKDIR}/formatpatches.XXXX")"
# generate patches quietly
git -c core.quiet=true format-patch -${NUM_PATCHES} -o "${TMP_FORMAT_DIR}" "HEAD~${NUM_PATCHES}..HEAD" >/dev/null 2>&1 || {
  git format-patch -${NUM_PATCHES} -o "${TMP_FORMAT_DIR}" "HEAD~${NUM_PATCHES}..HEAD"
}

# backup existing patches and move new ones
mkdir -p "${BKP_DIR}"
for ex in "${PATCHES_DIR}"/*.patch; do
  [ -f "${ex}" ] || continue
  cp -f "${ex}" "${BKP_DIR}/$(basename "${ex}").bak-$(date +%s)"
done
rm -f "${PATCHES_DIR}"/*.patch || true
mv "${TMP_FORMAT_DIR}"/*.patch "${PATCHES_DIR}/" 2>/dev/null || true
rm -rf "${TMP_FORMAT_DIR}"

# reset repo back by NUM_PATCHES commits so we can re-apply
git reset --hard "HEAD~${NUM_PATCHES}" >/dev/null 2>&1 || true
# print HEAD line
echo "HEAD is now at $(git rev-parse --short HEAD) $(git log -1 --pretty=%s)"

# modify patches in-place with required formatting
for p in "${PATCHES_DIR}"/*.patch; do
  [ -f "${p}" ] || continue
  cp -f "${p}" "${BKP_DIR}/$(basename "${p}")"
  # ensure exactly one blank line between Subject block and ANBZ, and one blank line after ANBZ
  awk -v ANBZ="ANBZ: #${ANBZ_ID}" '
    BEGIN { in_sub=0; printed_anbz=0 }
    {
      if (!in_sub) {
        print $0
        if ($0 ~ /^Subject:/) { in_sub=1; next }
      } else if (in_sub && !printed_anbz) {
        if ($0 ~ /^$/) {
          print ""           # ensure single blank line
          print ANBZ
          print ""           # blank line after ANBZ
          printed_anbz=1
          next
        } else {
          print $0
          next
        }
      } else {
        print $0
      }
    }
    END {
      if (in_sub && !printed_anbz) {
        print ""
        print ANBZ
        print ""
      }
    }' "${p}" > "${p}.tmp" && mv "${p}.tmp" "${p}"
  # insert Signed-off-by before first '---' or append if not found
  awk -v SOB="Signed-off-by: ${SIGNER_NAME} <${SIGNER_EMAIL}>" '
    BEGIN { inserted=0 }
    {
      if (!inserted && $0 ~ /^---$/) {
        print SOB
        inserted=1
      }
      print $0
    }
    END {
      if (!inserted) {
        print ""
        print SOB
      }
    }' "${p}" > "${p}.tmp" && mv "${p}.tmp" "${p}"
done

# ensure repo clean
if [ -n "$(git status --porcelain)" ]; then
  echo "Linux source tree is not clean. Commit or stash changes before running." >&2
  exit 12
fi

git config user.name "${SIGNER_NAME}"
git config user.email "${SIGNER_EMAIL}"

# helper: build and log
run_build_capture() {
  local repo_dir="$1"
  local logpath="$2"
  local cpus
  cpus="$(nproc 2>/dev/null || echo 1)"
  echo "Build log for ${logpath}" > "${logpath}"
  ( cd "${repo_dir}" && bash -lc "make clean && make anolis_defconfig && make -j${cpus} -s && make modules -j${cpus} -s" ) >> "${logpath}" 2>&1
  return $?
}

# collect patch filenames in lexical order (guaranteed 0001-....patch)
mapfile -t PATCH_LIST < <(ls -1 "${PATCHES_DIR}"/*.patch 2>/dev/null || true)
TOTAL_SELECTED="${#PATCH_LIST[@]}"
if [ "${TOTAL_SELECTED}" -eq 0 ]; then
  echo "No patches found in ${PATCHES_DIR}" >&2
  exit 13
fi

# Apply and build one patch at a time: apply single patch file path with git am "<path>"
summary=()
idx=0

for pf in "${PATCH_LIST[@]}"; do
  idx=$((idx+1))
  name="$(basename "${pf}")"

  # Apply exactly this patch file (one-by-one)
  if git -C "${LINUX_SRC_PATH}" am --3way "${pf}" >/dev/null 2>&1; then
    echo -e "Configuring: ${name} : ${GREEN}PASS${NC}"
  else
    git -C "${LINUX_SRC_PATH}" am --abort >/dev/null 2>&1 || true
    echo -e "Configuring: ${name} : ${RED}FAIL${NC}"
    echo ""
    echo -e "${RED}Note:${NC} git am failed for ${name}; no build was attempted"
    exit 20
  fi

  # Build this patch
  logfile="${LOGS_DIR}/${name}.log"
  if run_build_capture "${LINUX_SRC_PATH}" "${logfile}"; then
    echo -e "Building   : ${name} : ${GREEN}PASS${NC}"
    summary+=( "${name}:PASS" )
  else
    echo -e "Building   : ${name} : ${RED}FAIL${NC}"
    summary+=( "${name}:FAIL" )
    echo ""
    echo -e "Note: Refer the log in ${logfile}"
    exit 21
  fi
done

# final summary
echo ""
echo "== Summary =="
echo "Total Patches: ${TOTAL_SELECTED}"
for i in "${!summary[@]}"; do
  n=$((i+1))
  status="${summary[i]#*:}"
  color="${GREEN}"
  [ "${status}" != "PASS" ] && color="${RED}"
  printf "Patch-%d : %b%s%b\n" "${n}" "${color}" "${status}" "${NC}"
done
echo ""
echo -e "Note: Refer the logs in ${LOGS_DIR}"
exit 0

