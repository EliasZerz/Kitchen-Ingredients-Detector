"""Start the API. Run from project root: python serve.py

Then open http://127.0.0.1:8000/docs in your browser.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "kitchen_detector.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
