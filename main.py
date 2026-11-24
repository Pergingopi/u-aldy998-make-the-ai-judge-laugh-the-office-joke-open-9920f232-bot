#!/usr/bin/env python3
"""Make the AI Judge Laugh: the Office Joke Open.

Pure Python 3.13 standard library. The program writes one single-line
office joke to /output/entry.txt. No network, no model call, fully
deterministic: the same code always writes the same bytes.

The joke (94 characters, no trailing newline):
    The office plant got promoted before I did — turns out photosynthesizing counts as visibility.

Format decisions (from the gate in the rules: entry.txt must be UTF-8
text of 1 to 200 characters, not only white space, a single line):
- No trailing newline: the file is exactly the joke, one line, 94
  characters. Nothing extra for the gate to count.
- The em dash in the joke is UTF-8; the gate counts characters, and
  the file is valid UTF-8.

Why this joke (judge brief, criteria in their stated priority order):
1. About office life, and a joke, not a complaint: a promotion race
   between the narrator and the office plant.
2. The laugh is earned in the last few words: "photosynthesizing
   counts as visibility" is the turn -- the plant's literal biology
   re-read as performance-review jargon, landing at the very end.
3. The office detail is specific: the office plant, the promotion,
   and "visibility", the exact word performance reviews use for
   being seen doing the work.
4. Fresh: it avoids the saturated templates already flooding this
   competition's early submissions -- the meeting that should have
   been an email, the broken printer, "per my last email". A plant
   out-promoting its owner is a setup the judge has not met before.
5. Tight: every word carries the joke; cut "office" and the setting
   is gone, cut "photosynthesizing" and the punchline is gone.

Candidate comparison (fresh alternatives weighed against the draft):
1. Printer: "The office printer got Employee of the Month. It jams
   less than I do and never takes a sick day." Already the title of
   an early submission in this competition -- saturated, and the
   printer is the brief's own example of a specific detail, so it
   reads as the obvious pick.
2. Reply-all: "I hit reply-all to say 'please remove me'. Now 400
   people know my name and none of them can remove me." Two beats,
   and reply-all is another of the brief's own examples.
3. Calendar: "My calendar is so full it asked me for a 1:1 about my
   availability." Cute, but the turn lands mid-line and the joke is
   about the calendar, not a recognisable office moment.
4. Out-of-office: "My out-of-office reply got promoted. It answers
   emails faster than I do and never asks for a raise." Two clauses
   after the turn dilute the punchline (criterion 5).
5. Plant (CHOSEN): one setup, one turn, the punchline in the last
   three words, and the freshest angle of the set.

Revision round, 24 Nov 2026 (batch-5 reviser): six fresh angles were
written and scored against the finisher on the judge's axes -- (a)
about office life, (b) earned turn in the last few words, (c)
specific office detail, (d) fresh, (e) tight, (f) originality vs
the saturated templates, (g) gate 1-200 characters. Verdict: KEEP
the finisher; every alternative loses on at least one axis.
1. Lift: "I pressed the lift button so many times it filed a
   harassment complaint with HR." (80 chars) Turn lands at the end
   and HR is specific, but the setup is a familiar trope and the
   punchline is personification, not a conceptual twist -- loses
   (b) and (d) to the plant.
2. Pantry milk: "Someone labelled the pantry milk 'DO NOT TOUCH --
   Dave'. Dave left in 2019. The milk outlasted him." (98 chars)
   Very specific, and "outlasted him" is a real end-turn, but three
   sentences make it two beats and the fridge-milk shape is a known
   office joke -- loses (d) and (e).
3. Badge: "My access badge works everywhere except the room where
   they decide my salary." (77 chars) Tightest of the set and a
   clean end-turn, but the laugh is recognition of a grumble rather
   than a twist, and it leans complaint (criterion 1) -- loses (b).
4. AC: "HR said the AC can't go below 18 degrees. Apparently
   freezing is only allowed in performance reviews." (101 chars)
   The freezing double meaning is a genuine end-turn, but the setup
   is the common too-cold-AC grumble and the punchline needs a beat
   of parsing ("a joke that needs explaining has already lost") --
   loses (d) and (b).
5. Ergonomic chair: "My ergonomic chair has lumbar support,
   armrests and a tilt function -- it still can't support my
   career." (103 chars) Specific list, one-word pun on "support",
   but setup-heavy and complaint-flavoured -- loses (b) and (e).
6. Judge-addressed meta: "Dear judge: if this joke doesn't make
   you laugh, blame the office plant -- it got promoted for less."
   (99 chars) Freshest angle -- almost no entry addresses the
   judge, and the brief allows it -- but it is a remark/plea, not a
   joke, and its payoff depends on the judge enjoying the meta-game
   rather than laughing at an office joke; high variance and a
   criterion-1 risk -- rejected on risk, not on length.
The plant stays: the only candidate whose punchline is a conceptual
re-read (biology as performance-review jargon) landing in the last
three words, with no complaint flavour and no saturated setup.

Gate validation: validate_joke() below enforces the gate before
anything is written, so a bad JOKE can never reach the file: the
text must be one non-blank line, 1 to 200 characters, with no
newline or carriage return inside it, and no leading or trailing
whitespace. The check runs on every invocation, not just in tests.

Output handling: the program never removes the output directory
itself (the grader mounts it); it only clears the directory's
contents, then writes entry.txt atomically: the bytes go to a
temporary file created by mkstemp in the same directory, flushed
with a _write_all loop (no partial writes), fsynced, and renamed
over entry.txt with os.replace. A stale temporary file is unlinked
in a finally block, and the write is retried once if the temporary
file went stale.

Usage: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import tempfile

JOKE = "The office plant got promoted before I did \u2014 turns out photosynthesizing counts as visibility."

MAX_CHARS = 200


def validate_joke(text):
    """Enforce the competition gate on the joke text before writing.

    Raises AssertionError on any violation, so a bad JOKE fails loudly
    instead of producing an invalid entry.txt.
    """
    assert isinstance(text, str), "joke must be a string"
    assert text == text.strip(), "joke must have no leading/trailing whitespace"
    assert text, "joke must not be blank"
    assert len(text) <= MAX_CHARS, (
        f"joke is {len(text)} characters, over the {MAX_CHARS} cap"
    )
    assert "\n" not in text and "\r" not in text, (
        "joke must be a single line with no newline inside it"
    )


def _write_all(f, data):
    """Write every byte of data to f, looping until none remain."""
    view = memoryview(data)
    while view:
        written = f.write(view)
        if written is None:
            raise IOError("write returned None; cannot confirm bytes written")
        view = view[written:]


def _clear_output_dir(out_dir):
    """Remove the output directory's contents, never the directory."""
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                os.unlink(path)
            except OSError:
                pass


def main():
    validate_joke(JOKE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    _clear_output_dir(out_dir)
    data = JOKE.encode("utf-8")
    final = os.path.join(out_dir, "entry.txt")
    tmp_fd = None
    tmp_path = None
    for _attempt in range(2):
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(
                prefix=".entry.txt.", dir=out_dir
            )
            with os.fdopen(tmp_fd, "wb") as f:
                tmp_fd = None
                _write_all(f, data)
                f.flush()
                os.fsync(f.fileno())
            os.chmod(tmp_path, 0o644)
            os.replace(tmp_path, final)
            tmp_path = None
            os.chmod(final, 0o644)
            return
        except FileNotFoundError:
            # Temporary file went stale (e.g. directory recreated);
            # retry once with a fresh mkstemp.
            continue
        finally:
            if tmp_fd is not None:
                try:
                    os.close(tmp_fd)
                except OSError:
                    pass
                tmp_fd = None
            if tmp_path is not None:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                tmp_path = None
    raise IOError("failed to write entry.txt after retry")


if __name__ == "__main__":
    main()
