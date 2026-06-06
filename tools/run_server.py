import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import uvicorn


def main():
    uvicorn.run("src.server.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
