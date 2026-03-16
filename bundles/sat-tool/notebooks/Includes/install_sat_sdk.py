# Databricks notebook source
# MAGIC %md
# MAGIC **Notebook name:** install_sat_sdk
# MAGIC **Functionality:** Installs the necessary sat sdk (isolated VPC — wheels bundled via DAB)

# COMMAND ----------

RECOMMENDED_DBR_FOR_SAT = 14.3
import os

# Get databricks runtime configured to run SAT
dbr_version = os.environ.get("DATABRICKS_RUNTIME_VERSION", "0.0")
is_sat_compatible = False
is_serverless = False
# sanity check in case there is major and minor version
# strip minor version since we need to compare as number
if dbr_version.startswith("client"):
    is_sat_compatible = True
    is_serverless = True
else:
    dbrarray = dbr_version.split(".")
    dbr_version = f"{dbrarray[0]}.{dbrarray[1]}"
    dbr_version = float(dbr_version)
    is_sat_compatible = True if dbr_version >= RECOMMENDED_DBR_FOR_SAT else False

# test version

if is_sat_compatible == False:
    dbutils.notebook.exit(
        f"Detected DBR version {dbr_version} . Please use the DBR {RECOMMENDED_DBR_FOR_SAT} for SAT and try again , please refer to docs/setup.md"
    )

# COMMAND ----------

SDK_VERSION = "0.1.38"

# COMMAND ----------

# Wheels are synced to the workspace by the DAB deploy.
# Install from the bundle's wheels directory — no PyPI needed.
# Derive the wheels path relative to this notebook's location.
import subprocess
import sys

notebook_path = (
    dbutils.notebook.entry_point.getDbutils()
    .notebook()
    .getContext()
    .notebookPath()
    .get()
)
# notebook_path may or may not include the /Workspace prefix depending on
# the runtime (serverless vs classic) and deployment target (dev vs prod).
# Ensure it always starts with /Workspace so pip can resolve the local path.
bundle_root = notebook_path.rsplit("/notebooks/", 1)[0]
if not bundle_root.startswith("/Workspace"):
    bundle_root = f"/Workspace{bundle_root}"
wheels_path = f"{bundle_root}/wheels"

import glob

# Filter wheels to only those compatible with the running Python.
# We bundle wheels for multiple cpython versions (cp311–cp314); installing
# the wrong one causes pip to fail, so pick only matching or universal wheels.
py_ver = f"cp{sys.version_info.major}{sys.version_info.minor}"
print(f"Python: {sys.version} (tag: {py_ver})")

all_wheels = sorted(glob.glob(f"{wheels_path}/*.whl"))
compatible = []
for w in all_wheels:
    name = w.split("/")[-1]
    # Universal wheels (py3-none-any, py2.py3-none-any) always match.
    # cpXYZ wheels match only if they contain our version tag.
    # abi3 wheels (e.g. cryptography cp311-abi3) match if our version >= the tag.
    if "-py3-none-any" in name or "-py2.py3-none-any" in name:
        compatible.append(w)
    elif f"-{py_ver}-" in name:
        compatible.append(w)
    elif "-abi3-" in name:
        # abi3 wheels are forward-compatible: cp311-abi3 works on cp312+
        import re
        m = re.search(r"-cp(\d+)-abi3-", name)
        if m and int(m.group(1)) <= int(f"{sys.version_info.major}{sys.version_info.minor}"):
            compatible.append(w)

print(f"Installing {len(compatible)}/{len(all_wheels)} compatible wheels:")
for w in compatible:
    print(f"  {w.split('/')[-1]}")

if not compatible:
    msg = (
        f"No compatible wheels found in {wheels_path} "
        f"(found {len(all_wheels)} total, 0 match {py_ver}). "
        "Did you run download_wheels.sh before deploying?"
    )
    raise RuntimeError(msg)

subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "--force-reinstall", "--no-deps", "--quiet",
] + compatible)
