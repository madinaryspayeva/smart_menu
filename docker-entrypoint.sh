#!/bin/sh
set -e

# Copy pre-built static files into the shared volume
# so nginx can serve them directly
if [ -d /code/staticfiles_build ]; then
    cp -r /code/staticfiles_build/* /code/staticfiles/ 2>/dev/null || true
fi

exec "$@"
