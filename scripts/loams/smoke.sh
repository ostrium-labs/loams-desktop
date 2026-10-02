#!/usr/bin/env bash
# Smoke test for the Loams commands against the in-process mock (LOAMS_MOCK=1).
# Usage: scripts/loams/smoke.sh path/to/zeron
set -euo pipefail
zeron=${1:?usage: smoke.sh path/to/zeron}
export LOAMS_MOCK=1

echo "--- zeron loams status"
status=$("$zeron" loams status)
echo "$status"
grep -q "Loams (mock)" <<<"$status"
grep -q "loams.instance.v1" <<<"$status"

echo "--- zeron loams bot"
bot=$("$zeron" loams bot "file an issue for the checkout 500s")
echo "$bot"
grep -q "you said: file an issue" <<<"$bot"

echo "--- zeron loams bot-acp (initialize, session/new, prompt)"
out=$(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1}}' \
  '{"jsonrpc":"2.0","id":2,"method":"session/new","params":{"cwd":".","mcpServers":[]}}' \
  '{"jsonrpc":"2.0","id":3,"method":"session/prompt","params":{"sessionId":"loams-bot-1","prompt":[{"type":"text","text":"hello"}]}}' \
  | "$zeron" loams bot-acp)
echo "$out"
grep -q '"stopReason":"end_turn"' <<<"$out"
grep -q 'you said: hello' <<<"$out"
echo "smoke ok"
