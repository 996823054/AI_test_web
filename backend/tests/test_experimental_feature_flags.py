import os
import unittest

from fastapi import FastAPI


class ExperimentalFeatureFlagTests(unittest.TestCase):
    def test_midscene_not_registered_by_default(self):
        from app.api import register_routers

        app = FastAPI()
        os.environ.pop("FEATURE_MIDSCENE_IOS", None)
        register_routers(app)
        paths = {getattr(route, "path", "") for route in app.routes}
        self.assertFalse(any(path.startswith("/api/midscene-ios") for path in paths))

    def test_midscene_registered_when_enabled(self):
        from importlib import reload
        import app.api as api_pkg

        os.environ["FEATURE_MIDSCENE_IOS"] = "1"
        try:
            reload(api_pkg)
            app = FastAPI()
            api_pkg.register_routers(app)
            paths = {getattr(route, "path", "") for route in app.routes}
            self.assertTrue(any(path.startswith("/api/midscene-ios") for path in paths))
        finally:
            os.environ.pop("FEATURE_MIDSCENE_IOS", None)
            reload(api_pkg)


if __name__ == "__main__":
    unittest.main()
