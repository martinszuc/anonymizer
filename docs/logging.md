# Logging

How the project logs, what a log may hold, and how to add a record. The code
is `packages/core/src/anonymizer/core/log.py`; the clients that switch it on
are `anonymize` and `anonymize-ui`.

## Using it

Both commands take the same three options; the records go to stderr.

```sh
uv run anonymize-ui cv.pdf --debug                       # every step and detection
uv run anonymize-ui cv.pdf --log-level info              # milestones only
uv run anonymize-ui cv.pdf --debug --log-file run.log    # also keep the log
uv run anonymize redact cv.pdf -o out.pdf --log-level info
ANONYMIZER_LOG_LEVEL=info uv run anonymize-ui
```

| Option | Effect |
| --- | --- |
| `--debug` | Level `debug`, and in the window the web inspector, available from the context menu (Inspect Element) or F12 where the platform has it; it does not open by itself |
| `--log-level {debug,info,warning,error}` | The level; beats `--debug` and the environment |
| `ANONYMIZER_LOG_LEVEL` | The level when no option names one |
| `--log-file PATH` | Also append to this file (UTF-8) |

The default is `warning`. **No file is written unless `--log-file` names one**,
`--debug` included. Anything the core logs is silent for a program that embeds
it until that program configures logging (`NullHandler` on the `anonymizer`
logger); `configure_logging` is called only by the two clients.

## Levels

| Level | What it holds | Example |
| --- | --- | --- |
| `DEBUG` | every step's start and end with timing, every detection and merge, every leak-check layer, the reviewer's decisions | `find_emails matched type=email page=0 span=[39,60) source=rule text=…` |
| `INFO` | milestones: a document read, detection done, a model loaded, a session saved, a copy exported, **every download** | `export: done document=df3c29bf written=True leak_check=passed elapsed=0.01s` |
| `WARNING` | work went on, degraded: a refused page call, a model or OCR engine that cannot load, a drop that is no PDF or image, exporting with unread scans | `session refused: it belongs to a different file` |
| `ERROR` | an operation failed: an unexpected exception in a page call, a leak found at export, a download that did not match its checksum | `export refused: leak check found 1 leak(s), nothing written` |

A debug log reads top to bottom as the run happened. For a word, it says which
function or model found it and what became of it:

```
find_urls matched type=url page=0 span=[88,131) source=rule text=https://example.org/u/jan.novak@example.com
find_emails matched type=email page=0 span=[110,131) source=rule text=jan.novak@example.com
merge: dropped type=email … text=jan.novak@example.com, inside type=url … text=https://example.org/…
gliner-multi-v2.1 predicted type=person page=0 span=[0,9) source=model score=0.90 text="Jan Novak" label=person
propagated further occurrence of a found text: type=person page=0 span=[40,49) source=propagated text="Jan Novak"
review: rejected decided type=person page=0 … text="Jan Novak"
```

## What a log may hold

- **INFO and above never hold document text, file names or paths.** They carry
  counts, entity types, page numbers, durations, resource ids and the first 8
  characters of a document's SHA-256 (`short_fingerprint`), enough to tell
  two documents apart in one log.
- **DEBUG holds the words detection found**, because following a detection to
  its rule needs them. `configure_logging` says so with a warning when DEBUG
  is on. A debug log is as sensitive as the document: do not attach it to a
  report, and do not run `--debug` on real documents you will share the log of.
  Even DEBUG never holds a file name or path.
- **Exception messages are never written, at any level.** `SafeFormatter`
  prints the frames and the exception's type, since pymupdf and `ValueError`
  messages can quote content. The window still shows the message to the reviewer.
- A value containing spaces, quotes or line breaks is quoted and escaped, and
  text is cut at 120 characters, so one record is one line and document text
  cannot forge another record (`fields`).

`tests/test_logging_flow.py` runs a whole review with a file name and document
text planted in it and asserts neither appears at INFO, and that the file name
and path appear at no level. Keep it passing when you add a record.

## Adding a record

1. `log = logging.getLogger(__name__)` at the top of the module. Never `print`
   in the core (ruff's `T20` enforces it) and never configure handlers.
2. Format lazily with `%`, not f-strings (ruff's `G`): `log.info("saved: entities=%d", n)`.
3. Pick the level by the table above. A step with a duration is
   `with step(log, "name", **context) as outcome:`: it writes `start` at DEBUG,
   `done` with the time and what the block put in `outcome` (at `done_level`),
   or `failed` with the exception's type.
4. Entity text goes through `detect.base.describe` and only into a DEBUG record.
   A new INFO record names counts and types.
5. Do not log a surface's id or `ref`, a path, or anything a caller passed that
   could be a file name.
6. A record that shows work being skipped or degraded (a missing model, an
   unread scan) is a `WARNING`; a user-facing message the client already
   prints (the CLI's own `warning:` lines) is not logged again at that level.

## Not done

- Browser-side errors are not forwarded to Python. `WindowApi`'s public surface
  must equal `ReviewBridge`, so a `log` method would widen what the page can
  call; with `--debug` the web inspector shows them.
- No JSON lines and no always-on log file: nothing consumes either, and even a
  log without content records when documents were processed.
