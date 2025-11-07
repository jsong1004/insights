"""
Vite Asset Helper for Flask
Dynamically loads Vite asset paths from manifest.json
"""

import json
from pathlib import Path
from typing import Optional


class ViteAssetHelper:
    """Helper class to load Vite-generated assets in Flask templates."""

    def __init__(self, manifest_path: str = 'static/dist/.vite/manifest.json'):
        self.manifest_path = Path(manifest_path)
        self._manifest: Optional[dict] = None
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load the Vite manifest file."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    self._manifest = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Vite] Failed to load manifest: {e}")
                self._manifest = None
        else:
            # Development mode - no manifest yet
            self._manifest = None

    def get_asset(self, entry: str) -> str:
        """
        Get the hashed asset filename from Vite manifest.

        Args:
            entry: Source file path (e.g., 'ts/main.ts' or 'css/main.css')

        Returns:
            Hashed filename for production or source path for development
        """
        if self._manifest is None:
            # Development mode - return source path
            # This won't be used since Vite dev server serves directly
            return f'src/{entry}'

        if entry in self._manifest:
            return f"dist/{self._manifest[entry]['file']}"

        # Fallback to entry name if not in manifest
        print(f"[Vite] Warning: Entry '{entry}' not found in manifest")
        return f'dist/{entry}'

    def get_js_asset(self) -> str:
        """Get the main JavaScript bundle path."""
        return self.get_asset('ts/main.ts')

    def get_css_asset(self) -> str:
        """Get the main CSS bundle path."""
        return self.get_asset('css/main.css')

    def is_production(self) -> bool:
        """Check if running in production mode (manifest exists)."""
        return self._manifest is not None

    def reload_manifest(self) -> None:
        """Reload the manifest file (useful during development)."""
        self._load_manifest()


# Global instance
vite = ViteAssetHelper()


def get_vite_asset(entry: str) -> str:
    """
    Flask template helper function.

    Usage in templates:
        {{ url_for('static', filename=get_vite_asset('ts/main.ts')) }}
    """
    return vite.get_asset(entry)


def setup_vite_helper(app):
    """
    Setup Vite helper for Flask app.

    Usage in app.py:
        from vite_helper import setup_vite_helper
        setup_vite_helper(app)

    Then in templates:
        <script type="module" src="{{ url_for('static', filename=vite_js) }}"></script>
        <link rel="stylesheet" href="{{ url_for('static', filename=vite_css) }}">
    """
    @app.context_processor
    def inject_vite_assets():
        return {
            'vite_js': vite.get_js_asset(),
            'vite_css': vite.get_css_asset(),
            'vite_asset': get_vite_asset,
            'vite_is_production': vite.is_production(),
        }

    # Reload manifest on each request in development
    if app.debug:
        @app.before_request
        def reload_vite_manifest():
            vite.reload_manifest()

    return app


if __name__ == '__main__':
    # Test the helper
    print("Testing Vite Asset Helper...")
    print(f"Production mode: {vite.is_production()}")
    print(f"JS asset: {vite.get_js_asset()}")
    print(f"CSS asset: {vite.get_css_asset()}")
