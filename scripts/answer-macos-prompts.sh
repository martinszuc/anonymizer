#!/usr/bin/env bash
# Click "Allow" on macOS permission prompts for a while, for unattended CI runs.
#
# Starting the review window makes macOS ask whether Python may find devices
# on the local network, and the page stays blank until that is answered. Each
# attempt is logged, including the error when UI scripting is not permitted,
# so a run that could not answer says why.
set -u
seconds="${1:-90}"

for _ in $(seq "$seconds"); do
  osascript <<'APPLESCRIPT' 2>&1 | grep -v '^$' || true
tell application "System Events"
  repeat with p in (every process)
    try
      if exists (button "Allow" of window 1 of p) then
        click button "Allow" of window 1 of p
        return "clicked Allow in " & (name of p)
      end if
    end try
  end repeat
end tell
APPLESCRIPT
  sleep 1
done
