import os
import sys

# Ensure project root is on sys.path so `src` is importable when running the script directly.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.provider_manager.manager import ProviderManager


def main():
    pm = ProviderManager.from_config()
    if not pm.list_providers():
        print("No providers configured in config/providers.json.")
        return

    print("Configured providers:")
    for name in pm.list_providers():
        p = pm.get(name)
        print(f" - {name}: {p.model_info() if hasattr(p, 'model_info') else str(p)}")
        try:
            ok = p.health_check()
            print(f"   health: {ok}")
        except Exception as e:
            print(f"   health-check failed: {e}")


if __name__ == "__main__":
    main()
