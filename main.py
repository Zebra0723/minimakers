from datetime import datetime
import os

os.makedirs("reports", exist_ok=True)

ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
with open(f"reports/report_{ts}.md", "w") as f:
    f.write("# Daily Trend → MakerWorld Report\n\n")
    f.write("Entry point restored successfully.\n")
