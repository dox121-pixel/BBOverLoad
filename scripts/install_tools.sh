#!/usr/bin/env bash
# install_tools.sh
# Downloads and installs apktool and jadx into ~/.bboverload/tools/
# and creates wrapper scripts in ~/.local/bin/ (Linux/macOS).
#
# Usage:
#   bash scripts/install_tools.sh

set -euo pipefail

TOOLS_DIR="${HOME}/.bboverload/tools"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "${TOOLS_DIR}" "${BIN_DIR}"

# ---------------------------------------------------------------------------
# Helper: download a URL to a file (curl preferred, wget fallback)
# ---------------------------------------------------------------------------
download() {
  local url="$1" dest="$2"
  if command -v curl &>/dev/null; then
    curl -fsSL -o "${dest}" "${url}"
  elif command -v wget &>/dev/null; then
    wget -q -O "${dest}" "${url}"
  else
    echo "ERROR: neither curl nor wget found. Please install one and retry." >&2
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Check for Java
# ---------------------------------------------------------------------------
if ! command -v java &>/dev/null; then
  echo "ERROR: Java is not installed or not on PATH." >&2
  echo "Install a JDK (>= 11) and retry." >&2
  exit 1
fi
JAVA_VERSION=$(java -version 2>&1 | head -1)
echo "Found Java: ${JAVA_VERSION}"

# ---------------------------------------------------------------------------
# apktool
# ---------------------------------------------------------------------------
APKTOOL_VERSION="2.9.3"
APKTOOL_JAR="${TOOLS_DIR}/apktool-${APKTOOL_VERSION}.jar"
APKTOOL_WRAPPER="${BIN_DIR}/apktool"

if [ ! -f "${APKTOOL_JAR}" ]; then
  echo "Downloading apktool ${APKTOOL_VERSION}..."
  download \
    "https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar" \
    "${APKTOOL_JAR}"
  echo "apktool downloaded → ${APKTOOL_JAR}"
else
  echo "apktool already present: ${APKTOOL_JAR}"
fi

cat > "${APKTOOL_WRAPPER}" <<EOF
#!/usr/bin/env bash
exec java -jar "${APKTOOL_JAR}" "\$@"
EOF
chmod +x "${APKTOOL_WRAPPER}"
echo "apktool wrapper → ${APKTOOL_WRAPPER}"

# ---------------------------------------------------------------------------
# jadx
# ---------------------------------------------------------------------------
JADX_VERSION="1.4.7"
JADX_ZIP="${TOOLS_DIR}/jadx-${JADX_VERSION}.zip"
JADX_DIR="${TOOLS_DIR}/jadx-${JADX_VERSION}"
JADX_WRAPPER="${BIN_DIR}/jadx"

if [ ! -d "${JADX_DIR}" ]; then
  echo "Downloading jadx ${JADX_VERSION}..."
  download \
    "https://github.com/skylot/jadx/releases/download/v${JADX_VERSION}/jadx-${JADX_VERSION}.zip" \
    "${JADX_ZIP}"
  unzip -q "${JADX_ZIP}" -d "${JADX_DIR}"
  rm -f "${JADX_ZIP}"
  echo "jadx extracted → ${JADX_DIR}"
else
  echo "jadx already present: ${JADX_DIR}"
fi

cat > "${JADX_WRAPPER}" <<EOF
#!/usr/bin/env bash
exec "${JADX_DIR}/bin/jadx" "\$@"
EOF
chmod +x "${JADX_WRAPPER}"
echo "jadx wrapper → ${JADX_WRAPPER}"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "All tools installed!"
echo ""
echo "Make sure ${BIN_DIR} is on your PATH:"
echo "  export PATH=\"\${PATH}:${BIN_DIR}\""
echo ""
echo "Add the above line to your shell rc file (~/.bashrc, ~/.zshrc, etc.)."
