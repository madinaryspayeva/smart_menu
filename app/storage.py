from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class SafeManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Skip @import resolution — Tailwind's @import "tailwindcss" is not a real static file."""

    patterns = (
        (
            "*.css",
            (r"""(?P<matched>url\(['"]{0,1}\s*(?P<url>.*?)["']{0,1}\))""",),
        ),
    )
