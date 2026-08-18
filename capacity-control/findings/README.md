# Project findings packet

Each project publishes findings through its own `specs/<project>.md` writer after local review. The
live broker database, raw quota-domain fingerprint, balance, account identity, prompts, transcripts,
and native session ids never enter Git.

A finding reports only:

- candidate version or pinned SHA-256;
- project and machine class, not account identity;
- observation interval and provider family;
- admitted, held, and refused counts by reason;
- aggregate input, cached-input, output, reasoning, peak-context, turns, and wall time when native
  structured evidence exposes them;
- useful terminal outcome counts and quality comparison against the unchanged project gates;
- bypasses, false holds, false admissions, and the exact local evidence pointer used to correct the
  adapter;
- whether the project `ADOPT`, `DISTINGUISH`, or `REJECT` decision was locally ratified.

The first enforcement report must include shadow-mode counterfactuals and the unchanged pre-existing
test/review/landing/release results. Token reduction without the same quality outcome is not an
adoption proof. Metrics remain diagnostic and never become launch or acceptance authority.
