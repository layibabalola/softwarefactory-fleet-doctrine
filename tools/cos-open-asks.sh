#!/usr/bin/env bash
# cos-open-asks.sh - list open Chief of Staff (CoS) asks on this repo's GitHub threads.
# Canonical copy: layibabalola/softwarefactory-fleet-doctrine tools/cos-open-asks.sh (CoS response duty r3).
# Needs only bash + gh (uses gh's built-in --jq; no jq binary, no GNU date).
#
# Source of truth is the PR / commit thread itself (not the doctrine bus).
#   Ask   : a PR conversation comment, PR review, inline review comment, or commit comment that
#           has a line `CoS-ASK: <id>`, or (legacy) starts with `**Chief of Staff` / `**CoS`,
#           contains `ACK`, and does not say no reply is needed in its closing
#           400 characters (so a review that merely quotes that phrase is still an ask). `CoS-CONCERN:` comments are never asks.
#           Legacy ask id = the comment's numeric id. A comment may carry both `CLOSED:` and `CoS-ASK:`.
#   Closed: (legacy asks: any later valid ACK:/DISTINGUISH: on the thread, the pre-r3 rule)
#           a later comment on the same thread that starts with
#             `ACK:` + quotes the ask id or comment URL + gives a plan and a real ETA (date or time), or
#             `DISTINGUISH:` + quotes the ask id or URL + gives a reason;
#           or a comment with a line `CLOSED: <id>` (CoS only).
# Cost is bounded: 2 list calls + 3 paginated calls per candidate PR + 1 paginated call for commit
# comments. Candidates = all open PRs + the COS_CLOSED_LIMIT (default 30) most recently updated of the
# 200 newest closed PRs.
# NOTE: on a shared GitHub account nothing here proves a comment came from CoS. See the doctrine text.
# Usage: tools/cos-open-asks.sh [owner/repo]  |  tools/cos-open-asks.sh --classify fixture.json     Output: one `OPEN ...` line per open ask; exit 1 if any.
set -euo pipefail
CLOSED_LIMIT=${COS_CLOSED_LIMIT:-30}
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# Per comment emit TSV: kind  key  created  url  thread  then the body as JSON.
# kind: ASK (key=ask id) | REPLY (key=-) | CLOSE (key=closed id)
JQ='def classify($thread):
  (.body // "") as $b | (.created_at // .submitted_at // "") as $t | (.html_url // "") as $u |
  if ($b | test("(^|\n)\\s*CoS-CONCERN:")) then empty
  elif ($b | test("^\\s*(ACK|DISTINGUISH):")) then ["REPLY","-",$t,$u,$thread,($b|@json)] | @tsv
  else
    ( ($b | [match("(?:^|\n)\\s*CLOSED:\\s*(\\S+)"; "g").captures[0].string][]) as $k
        | ["CLOSE",$k,$t,$u,$thread,($b|@json)] | @tsv ),
    ( if ($b | test("(^|\n)\\s*CoS-ASK:\\s*\\S")) then
        ($b | [match("(?:^|\n)\\s*CoS-ASK:\\s*(\\S+)"; "g").captures[0].string][]) as $k
          | ["ASK",$k,$t,$u,$thread,($b|@json)] | @tsv
      elif ($b | test("(^|\n)\\s*CLOSED:")) then empty
      elif ($b | test("^\\s*\\*\\*(Chief of Staff|CoS)")) and ($b | test("ACK"))
           and (($b | test("ACK: <plan|within 24 hours"))
                or ($b | .[-400:] | test("no (reply|response|ACK|action)( is)? (needed|required)|does not need (a )?(reply|an ACK)|no ACK (is )?(needed|required)"; "i") | not))
      then ["LEGACY",(.id|tostring),$t,$u,$thread,($b|@json)] | @tsv
      else empty end )
  end;'

# Offline fixture mode (needs a jq binary; production path uses only gh --jq):
#   tools/cos-open-asks.sh --classify fixture.json   -> prints classified rows
if [ "${1:-}" = --classify ]; then jq -r "$JQ .[] | classify(\"fixture\")" "$2"; exit; fi
REPO=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}

prs=$( { gh pr list -R "$REPO" --state open --limit 1000 --json number --jq '.[].number'
         gh pr list -R "$REPO" --state closed --limit 200 --json number,updatedAt \
           --jq "sort_by(.updatedAt) | reverse | .[0:$CLOSED_LIMIT] | .[].number"; } | sort -un)
for n in $prs; do
  gh api --paginate "repos/$REPO/issues/$n/comments?per_page=100" --jq "$JQ .[] | classify(\"pr#$n\")"
  gh api --paginate "repos/$REPO/pulls/$n/comments?per_page=100"  --jq "$JQ .[] | classify(\"pr#$n\")"
  gh api --paginate "repos/$REPO/pulls/$n/reviews?per_page=100"   --jq "$JQ .[] | classify(\"pr#$n\")"
done >"$tmp/rows"
gh api --paginate "repos/$REPO/comments?per_page=100" \
  --jq "$JQ .[] | classify(\"commit:\" + (.commit_id[0:12]))" >>"$tmp/rows" || true

# Real ETA = a date or a clock time (not just the letters "eta").
eta_re='[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}:[0-9]{2}|[0-9]{1,2} ?([AaPp][Mm])|\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)(day|sday|nesday|rsday|urday)?\b|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* [0-9]{1,2}|\b([Tt]omorrow|[Tt]onight|[Tt]oday)\b'
open=0
while IFS=$'\t' read -r kind key t url thread body; do
  [ "$kind" = ASK ] || [ "$kind" = LEGACY ] || continue
  closed=0
  while IFS=$'\t' read -r k2 key2 t2 url2 th2 b2; do
    [ "$th2" = "$thread" ] || continue
    if [ "$k2" = CLOSE ] && [ "$key2" = "$key" ]; then closed=1; break; fi
    [ "$k2" = REPLY ] || continue
    [[ "$t2" > "$t" ]] || continue
    # CoS-ASK asks need the reply to cite the id or URL; legacy asks accept any later valid reply.
    if [ "$kind" = ASK ]; then case "$b2" in *"$key"*|*"$url"*) ;; *) continue ;; esac; fi
    if [[ "$b2" =~ ^\"[[:space:]]*ACK: ]]; then
      echo "$b2" | grep -Eq "$eta_re" && { closed=1; break; }
    elif [[ "$b2" =~ ^\"[[:space:]]*DISTINGUISH:[[:space:]]*.{20,} ]]; then closed=1; break
    fi
  done <"$tmp/rows"
  [ "$kind" = LEGACY ] && kind_l=" (legacy)" || kind_l=""
  if [ $closed = 0 ]; then echo "OPEN CoS ask$kind_l $key on $REPO $thread (asked $t): $url"; open=$((open+1)); fi
done <"$tmp/rows"
echo "# $REPO: $open open CoS ask(s); scanned PRs: $(echo $prs | wc -w)"
[ $open = 0 ]
