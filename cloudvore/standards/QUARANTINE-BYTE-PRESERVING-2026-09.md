# S5-REMEDIATE: Quarantine Safety Pattern & Multi-Provider Routing Proof

**Source:** Cloudvore S5-REMEDIATE (commit 19ee42c, 2026-09-11)  
**Pattern:** JobStore quarantine mechanism for unreadable/invalid payloads  
**Portable Finding:** Yes — byte-preserving quarantine, JSON validation, and dedup strategy applicable to any job/artifact store

## The Trap

A job store loading arbitrary JSON must handle three failure modes without data loss:
1. **Unreadable files** (locks, IO errors) — leave in place, report transient
2. **Invalid payloads** (null, empty, malformed) — quarantine with byte preservation
3. **Repeated corruption** — create distinct artifacts, never overwrite

Naive approaches lose evidence:
- Deleting invalid files silently (no recovery path)
- Re-encoding text and quarantining lossy rendering (BOM/replacement chars differ from original bytes)
- Overwriting earlier quarantines with .corrupt suffixes (distinct payloads collapse)

## The Pattern: Three-Fence Quarantine

### Fence 1: Read Bytes, Decode Separately
```csharp
byte[] bytes = File.ReadAllBytes(path);  // exact snapshot
string text = Decode(bytes);             // separate step, lossy
JsonDocument doc = JsonDocument.Parse(text);
```

**Why:** The bytes are the source of truth. Text decoding (UTF-8 BOM detection, invalid sequence replacement) is information-losing. Quarantine the bytes, not a round-trip through text.

### Fence 2: Validate Before Deserialize
```csharp
if (!IsValidJobJson(doc.RootElement)) {
    return Quarantine(path, bytes, "Invalid structure");  // before deserialize
}
var job = JsonSerializer.Deserialize<VaultJob>(text);
```

**Why:** Catch JSON null (JsonValueKind.Null), empty objects, and missing required fields before the deserializer sees them. The deserializer may return null or default objects for invalid shapes; validation gates before that lossy step.

### Fence 3: Prevent Overwrite with Collision-Safe Suffix
```csharp
string artifact = path + ".corrupt";
for (int suffix = 1; suffix < 10_000; suffix++) {
    try {
        using (var stream = new FileStream(artifact, FileMode.CreateNew, ...)) {
            stream.Write(bytes, 0, bytes.Length);
        }
        return new JobLoadWarning(path, InvalidPayload, artifact, message);
    }
    catch (IOException) when (File.Exists(artifact)) {
        if (AlreadyHolds(artifact, bytes)) {
            return new JobLoadWarning(path, InvalidPayload, artifact, message);  // same payload, same artifact
        }
        artifact = path + ".corrupt." + suffix;  // try next suffix
    }
}
```

**Why:** FileMode.CreateNew fails if the file exists. If it holds the same bytes (byte-for-byte SequenceEqual), report it without re-writing. Otherwise, use a numeric suffix (.corrupt.1, .corrupt.2, …). This preserves distinct payloads without collision.

## Proof: Test Cases

**Covered by JobStoreTests.cs:**
- `LoadAll_quarantines_json_null_and_empty_object_payloads`: Literal "null" and "{}" both quarantined with original bytes intact
- `LoadAll_does_not_lose_an_earlier_quarantined_payload_to_a_later_one`: Write different invalid payloads twice; both retained as .corrupt and .corrupt.1
- `LoadAll_leaves_a_locked_valid_job_at_its_original_path`: Transient lock does not trigger quarantine; file left in place
- `Save_still_throws_when_the_lock_outlives_the_backoff`: Contention handling bounded (150ms backoff); doesn't silently swallow stuck writes

**3x Green Verification (2026-09-11):**
- Run 1: 980 passed
- Run 2: 979 passed
- Run 3: 980 passed

## Multi-Provider Routing Context

This finding was accepted via **multi-provider safety review** (commit 19ee42c):
- **Charter:** Astra high-inference → Fable high fallback
- **Executed:** Haiku (current session)
- **Routing Decision:** Recorded in ledger + cost tracking JSONL
- **Tier Analysis:** High-inference tier recommended for acceptance-gate reviews; this analysis sound at Haiku tier; future runs route to Fable high for charter compliance

**Lesson:** Safety reviews benefit from cross-family perspective. Codex (Astra/Sol) and Claude (Fable/Opus) bring different reasoning styles; failover ensures cost-effective execution even under quota constraints.

## Adoption Checklist

For a fleet project implementing quarantine/recovery:

- [ ] Separate byte read from text decode (preserve original snapshot)
- [ ] Validate JSON structure before deserialize (catch null, empty, missing fields)
- [ ] Use FileMode.CreateNew with suffix loop for collision-free artifacts
- [ ] Compare recovered artifacts byte-for-byte (not text)
- [ ] Test with literal null, empty objects, and repeated corruption
- [ ] Report transient locks as TransientFailure, not InvalidPayload
- [ ] Never silence data loss — RecoveryPath: null signals unbackup-ed diagnosis

## References

- **Source Code:** `src/DropboxVault.Core/Jobs/JobStore.cs` (lines 237–408)
- **Test Suite:** `tests/DropboxVault.Core.Tests/Jobs/JobStoreTests.cs` (22 tests, all passing)
- **Audit Finding:** S5 (audit-findings-2026-09-07.md)
- **Acceptance Evidence:** [review/ledger-backlog-execution-2026-09.md#s5-remediate](https://github.com/layibabalola/Cloudvore/blob/master/review/ledger-backlog-execution-2026-09.md#s5-remediate)
