import dataclasses
from fastapi_startkit.environment import env
from fastapi_startkit.helpers.app import storage_path, public_path

@dataclasses.dataclass
class StorageConfig:
    default: str = dataclasses.field(
        default_factory=lambda: env("FILESYSTEM_DISK", "local")
    )

    disks: dict = dataclasses.field(
        default_factory=lambda: {
            "local": {
                "driver": "local",
                "root": storage_path("app/private"),
                "serve": True,
                "throw": False,
                "report": False,
            },
            "public": {
                "driver": "local",
                "root": storage_path("app/public"),
                "url": env("APP_URL", "http://localhost").rstrip("/") + "/storage",
                "visibility": "public",
                "throw": False,
                "report": False,
            },
            "s3": {
                "driver": "s3",
                "key": env("AWS_ACCESS_KEY_ID"),
                "secret": env("AWS_SECRET_ACCESS_KEY"),
                "region": env("AWS_DEFAULT_REGION", "us-east-1"),
                "bucket": env("AWS_BUCKET"),
                "url": env("AWS_URL"),
                "endpoint": env("AWS_ENDPOINT"),
                "use_path_style_endpoint": env("AWS_USE_PATH_STYLE_ENDPOINT", False),
                "throw": False,
                "report": False,
            },
        }
    )
