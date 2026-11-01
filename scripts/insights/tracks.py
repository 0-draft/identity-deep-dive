"""The tracks this repository follows, in one place.

Imported by changes.py, stage.py and write.py, and read by the workflows.
Kept free of third-party imports so a job that installs nothing can use it.
"""
TRACKS = ("ietf-wimse", "oauth-wg", "openid")

if __name__ == "__main__":
    import json

    print(json.dumps(list(TRACKS)))
