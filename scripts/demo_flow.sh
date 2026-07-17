#!/bin/bash
set -e
BASE="http://127.0.0.1:8000"

echo "== 1. Ingest v1 =="
curl -s -X POST "$BASE/documents/1/ingest" -F "file=@data/ct200_manual.pdf" | tee v1.json
echo

echo "== 2. Look up real node IDs for 2.1.1.1 and 3.2 (from the version we just ingested) =="
curl -s "$BASE/documents/1/nodes" | tee nodes.json
echo

BATTERY_ID=$(py -c "import json; nodes=json.load(open('nodes.json')); print(next(n['id'] for n in nodes if n['stable_key']=='2.1.1.1'))")
INFLATION_ID=$(py -c "import json; nodes=json.load(open('nodes.json')); print(next(n['id'] for n in nodes if n['stable_key']=='3.2'))")
echo "Battery node id: $BATTERY_ID, Inflation node id: $INFLATION_ID"

echo "== 3. Create a selection using freshly-looked-up node IDs =="
curl -s -X POST "$BASE/selections" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"battery-and-inflation\", \"node_ids\": [$BATTERY_ID, $INFLATION_ID]}" | tee selection.json
echo

SEL_ID=$(py -c "import json; print(json.load(open('selection.json'))['selection_id'])")

echo "== 4. Generate test cases from that selection =="
curl -s -X POST "$BASE/generations/from-selection/$SEL_ID" | tee generation.json
echo

GEN_ID=$(py -c "import json; print(json.load(open('generation.json'))['generation_id'])")

echo "== 5. Confirm generation is fresh (not stale) right now =="
curl -s "$BASE/generations/$GEN_ID" | py -m json.tool

echo "== 6. Ingest v2 (battery/inflation numbers changed) =="
curl -s -X POST "$BASE/documents/1/ingest" -F "file=@data/ct200_manual_v2.pdf"
echo

echo "== 7. Re-fetch the SAME generation -- should now show stale: true =="
curl -s "$BASE/generations/$GEN_ID" | py -m json.tool