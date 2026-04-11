"""Download the dataset from Roboflow. Run from repo root: python -m kitchen_detector.download_dataset

Set ROBOFLOW_API_KEY in the environment (never commit keys).
"""

import os
import sys

from roboflow import Roboflow


def main() -> None:
    key = os.environ.get("ROBOFLOW_API_KEY")
    if not key:
        print("Set ROBOFLOW_API_KEY, then re-run.", file=sys.stderr)
        sys.exit(1)
    rf = Roboflow(api_key=key)
    project = rf.workspace("school-qmdcx").project("fruit-detection-aubry")
    version = project.version(24)
    version.download("yolov8")


if __name__ == "__main__":
    main()
