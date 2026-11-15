# Shared by tools/Get-FleetPathHealthStatus.ps1 (the reader) and tools/Repair-MachinePath.ps1 (the
# publisher), so both judge an ack by ONE rule: a record the reader would call UNEVALUABLE can never
# be "unchanged, already published" to the publisher. Functions only, no param block: safe to
# dot-source from either script.

<#
Validate one ack at its TOP level: schema, machine equal to the file name, verdict, UTC stamp.
Anything else throws, so a malformed or misfiled ack is UNEVALUABLE, never a pass.
#>
function Test-AckRecord([string]$Raw, [string]$FileMachine, [Nullable[datetime]]$NowUtc = $null) {
    # System.Text.Json keeps JSON types and raw strings. ConvertFrom-Json would unwrap a
    # one-element root array and turn a stamp with any offset into a [datetime], so it cannot tell
    # "2026-11-14T23:00:00Z" from "2026-11-14T23:00:00+02:00" or a scalar from an array.
    $id = "path-health/$FileMachine.json"
    try { $doc = [System.Text.Json.JsonDocument]::Parse([string]$Raw) } catch { throw "${id}: not valid JSON" }
    try {
        $root = $doc.RootElement
        if ($root.ValueKind -ne [System.Text.Json.JsonValueKind]::Object) { throw "${id}: root is not a JSON object" }
        # A repeated top-level key is refused: which copy "wins" differs between parsers (and between
        # a regex and a parser), so a record with one is never anybody's verdict.
        $names = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        foreach ($p in $root.EnumerateObject()) { if (-not $names.Add($p.Name)) { throw "${id}: top-level key '$($p.Name)' is repeated" } }
        $str = {
            param($name)
            $el = [System.Text.Json.JsonElement]::new()
            if (-not $root.TryGetProperty($name, [ref]$el)) { throw "${id}: no top-level $name" }
            if ($el.ValueKind -ne [System.Text.Json.JsonValueKind]::String) { throw "${id}: $name is not a string" }
            $el.GetString()
        }
        if ((& $str 'schema') -cne 'fleet-path-health.v1') { throw "${id}: schema is not fleet-path-health.v1" }
        if ((& $str 'machine').ToUpperInvariant() -ne $FileMachine.ToUpperInvariant()) { throw "${id}: machine field does not match the file name" }
        $verdict = & $str 'verdict'
        if ($verdict -cnotin @('HEALTHY', 'UNHEALTHY')) { throw "${id}: verdict is not HEALTHY or UNHEALTHY" }
        $stamp = & $str 'published_utc'
        # Case-sensitive, anchored with \z: `$` would accept a trailing newline, -notmatch a lower-case z.
        if ($stamp -cnotmatch '^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\z') { throw "${id}: published_utc is not a yyyy-MM-ddTHH:mm:ssZ UTC stamp" }
        $utc = try { [datetime]::ParseExact($stamp, "yyyy-MM-dd'T'HH:mm:ss'Z'", [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]'AdjustToUniversal,AssumeUniversal') } catch { throw "${id}: published_utc is not a valid date" }
        if ($null -ne $NowUtc -and $utc -gt ([datetime]$NowUtc).AddMinutes(10)) { throw "${id}: published_utc is in the future" }
        $fe = [System.Text.Json.JsonElement]::new()
        if (-not $root.TryGetProperty('findings', [ref]$fe) -or $fe.ValueKind -ne [System.Text.Json.JsonValueKind]::Array) { throw "${id}: findings is not an array" }
        $findings = [System.Collections.Generic.List[string]]::new()
        foreach ($x in $fe.EnumerateArray()) {
            if ($x.ValueKind -ne [System.Text.Json.JsonValueKind]::String) { throw "${id}: a finding is not a string" }
            $findings.Add($x.GetString())
        }
        if (($verdict -eq 'HEALTHY') -ne ($findings.Count -eq 0)) { throw "${id}: verdict $verdict contradicts its $($findings.Count) findings" }
        return [pscustomobject]@{ PublishedUtc = $utc; Verdict = $verdict; Findings = $findings.ToArray() }
    } finally { $doc.Dispose() }
}
