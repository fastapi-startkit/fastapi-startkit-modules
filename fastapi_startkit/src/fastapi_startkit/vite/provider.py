import os

from fastapi_startkit.providers import Provider

from .vite import Vite


class ViteProvider(Provider):
    """Register and configure the Vite asset helper.

    Configuration keys (pass as a dict when registering the provider):

    - ``public_path``       Directory that is served as the web root.
                            Defaults to ``{base_path}/public``.
    - ``build_directory``   Sub-directory inside *public_path* that holds
                            the Vite build output.  Defaults to ``"build"``.
    - ``hot_file``          Path to the HMR sentinel file written by the Vite
                            dev server.  Defaults to ``{public_path}/hot``.
    - ``manifest_filename`` Name of the Vite manifest file.
                            Defaults to ``"manifest.json"``.
    - ``asset_url``         Optional base URL prefix prepended to all generated
                            asset URLs (e.g. a CDN origin).  Defaults to ``""``.
    - ``static_url``        URL path at which the build directory is mounted
                            for static file serving.  Defaults to
                            ``"/{build_directory}"``.
    - ``mount_static``      Set to ``False`` to skip mounting a StaticFiles
                            app (e.g. when assets are served by a CDN or a
                            dedicated web server).  Defaults to ``True``.

    Example::

        app = Application(
            base_path=str(Path.cwd()),
            providers=[
                (ViteProvider, {
                    "build_directory": "build",
                    "asset_url": "",          # or "https://cdn.example.com"
                }),
            ],
        )

    Jinja2 integration
    ------------------
    If a ``"templates"`` binding exists in the container (a
    ``starlette.templating.Jinja2Templates`` instance), the provider
    automatically injects three globals into the Jinja2 environment:

    - ``vite(entrypoint)``        → HTML tags for an entry point
    - ``vite_asset(path)``        → URL for a non-entry-point asset
    - ``vite_react_refresh()``    → React Fast Refresh preamble (HMR only)
    """

    provider_key = "vite"

    def register(self) -> None:
        cfg = self.config if isinstance(self.config, dict) else {}

        public_path = cfg.get(
            "public_path", os.path.join(self.app.base_path, "public")
        )
        build_directory = cfg.get("build_directory", "build")
        hot_file = cfg.get("hot_file", os.path.join(public_path, "hot"))
        manifest_filename = cfg.get("manifest_filename", "manifest.json")
        asset_url = cfg.get("asset_url", "")

        vite = Vite(
            public_path=public_path,
            build_directory=build_directory,
            hot_file=hot_file,
            manifest_filename=manifest_filename,
            asset_url=asset_url,
        )

        self.app.bind("vite", vite)

    def boot(self) -> None:
        vite: Vite = self.app.make("vite")
        cfg = self.config if isinstance(self.config, dict) else {}

        public_path = cfg.get(
            "public_path", os.path.join(self.app.base_path, "public")
        )
        build_directory = cfg.get("build_directory", "build")
        static_url = cfg.get("static_url", f"/{build_directory}")
        mount_static = cfg.get("mount_static", True)

        # Mount a StaticFiles handler so FastAPI serves the built assets.
        if mount_static:
            build_path = os.path.join(public_path, build_directory)
            if os.path.isdir(build_path):
                try:
                    from fastapi.staticfiles import StaticFiles

                    self.app.mount(
                        static_url,
                        StaticFiles(directory=build_path),
                        name="vite_assets",
                    )
                except ImportError:
                    pass  # fastapi optional dependency not installed

        # Wire up Jinja2 globals when a template object is registered.
        # Wrap HTML-returning helpers in Markup so Jinja2 does not escape the tags.
        if self.app.has("templates"):
            templates = self.app.make("templates")
            if hasattr(templates, "env"):
                try:
                    from markupsafe import Markup
                except ImportError:
                    Markup = str  # type: ignore[assignment,misc]

                templates.env.globals["vite"] = lambda *a, **kw: Markup(vite(*a, **kw))
                templates.env.globals["vite_asset"] = vite.asset
                templates.env.globals["vite_react_refresh"] = lambda: Markup(vite.react_refresh())
