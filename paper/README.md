# Example papers

Two write-ups of the same results (`results/results.json`).

| File | Written by | Numbers |
| --- | --- | --- |
| [`example_report.md`](example_report.md) | `04_paper/make_paper.py`, a fixed template | All computed by the script |
| [`openscience_report.md`](openscience_report.md) | OpenScience 2.0.151 with `openai/gpt-4.1-mini`, one run of about 40 seconds, saved unedited | Copied by the agent |

## Audit of the OpenScience report

Checked by hand against `results/results.json` and `literature/README.md`.

**Correct:** the model comparison table (errors, AIC, BIC), both exponent
intervals, both tests for `x2`, the estimate of G, and the conclusion that the
group-resampling interval is the one to trust.

**Wrong or unsupported:**

1. It says the row-resampling interval for G, [6.90e-11, 7.63e-11], contains
   the accepted value 6.674e-11. It does not. This is the main statistical
   point of the analysis, and the agent got it backwards.
2. The exponent table gives separate estimates for group resampling
   (p = 1.511, q = −0.516). Those numbers are not in the results; there is one
   estimate, p = 1.506 and q = −0.507.
3. H1 is labelled "Galileo's claim", and the discussion rejects "Galileo's
   simpler linear relation". Galileo gave no formula. H1 is a naive baseline.
4. The Kepler "quotation" is our paraphrase from `literature/README.md` set in
   quotation marks, and the Newton "quotation" splices a real quotation with
   our paraphrase.
5. It says the estimate of G "matches the accepted value well". It is 8.7% off.
6. The file lost its non-ASCII characters: apostrophes are missing
   ("Keplers"), and the units of G and the Latin title are garbled. The
   exponent table also has more cells than headers.

A fluent, well-organized paper with correct tables still carried six errors,
one of them in the headline result. That is why every claim needs checking.
