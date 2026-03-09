#!/bin/bash
# Professional Manylinux Build Pipeline for quadrosdesaude
set -e -x

PROJECT_ROOT="/app"
DIST_DIR="$PROJECT_ROOT/dist"
WHEELHOUSE="/tmp/wheelhouse"

echo ">>> Initializing build environment..."
cd "$PROJECT_ROOT"

# Ensure clean workspace
rm -rf "$DIST_DIR" "$WHEELHOUSE" build/
mkdir -p "$DIST_DIR" "$WHEELHOUSE"

# Supported Python versions (3.10 to 3.13)
PY_VERSIONS=("cp310-cp310" "cp311-cp311" "cp312-cp312" "cp313-cp313")

for VERSION in "${PY_VERSIONS[@]}"; do
    PYBIN="/opt/python/$VERSION/bin"
    
    if [ ! -d "$PYBIN" ]; then
        echo ">>> Warning: Python $VERSION bin directory not found. Skipping..."
        continue
    fi

    echo ">>> Building wheel for $VERSION..."
    
    # Update build toolchain
    "$PYBIN/pip" install --upgrade pip
    "$PYBIN/pip" install poetry-core setuptools

    # Build the distribution using the backend specified in pyproject.toml
    # This triggers build.py to compile C extensions
    "$PYBIN/pip" wheel "$PROJECT_ROOT" --no-deps -w "$WHEELHOUSE"
done

echo ">>> Repairing wheels to ensure Manylinux compliance..."
for whl in "$WHEELHOUSE"/quadrosdesaude-*.whl; do
    auditwheel repair "$whl" --plat "$PLAT" -w "$DIST_DIR"
done

# Final cleanup of raw artifacts
rm -rf "$WHEELHOUSE" build/

echo ">>> Build process completed successfully. Artifacts located in: $DIST_DIR"


# docker run --rm -e PLAT=manylinux_2_28_x86_64 -v "${PWD}:/app" -w /app quay.io/pypa/manylinux_2_28_x86_64 bash scripts/unix/build_manylinux.sh