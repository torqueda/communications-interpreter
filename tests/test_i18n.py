import json
import shutil
import subprocess
from pathlib import Path

import pytest

I18N = Path(__file__).resolve().parent.parent / "static" / "i18n.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_es_and_en_have_identical_keys():
    script = f"const fs=require('fs');eval(fs.readFileSync({json.dumps(str(I18N))},'utf8')+';globalThis.S=STRINGS;');console.log(JSON.stringify({{es:Object.keys(S.es),en:Object.keys(S.en)}}))"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
    keys = json.loads(out)
    assert set(keys["es"]) == set(keys["en"])
    assert len(keys["es"]) == len(set(keys["es"]))  # no duplicate keys
