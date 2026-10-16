# Content-addressed evidence pointer (accepted variant)

Cloudvore K179 layout, accepted unchanged by `check-evidence-dumps.py`. The evidence directory on the
main line holds `SHA256SUMS` (sha256sum format `<64hex>  <basename>`; CRLF and the `*` binary marker
are read) and this `EVIDENCE-REF`. Each raw file lives on the orphan branch `evidence-store` of the
same repository at `objects/<first two hex of its sha256>/<sha256>`. The checker tries
`refs/remotes/origin/evidence-store` first, then `refs/heads/evidence-store`, and hashes each object.
