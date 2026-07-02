# bracket26-data

Static results feed for the Bracket 26 app (FIFA World Cup 2026).
`results.json` is regenerated every ~15 minutes by GitHub Actions from
public fixture sources. Read-only; consumed by the app with ETag.

Primary source: [fixturedownload.com](https://fixturedownload.com/feed/json/fifa-world-cup-2026).

## Schema

`results[]` entries carry `matchNumber`, `home`/`away` (3-letter teamIDs),
`homeScore`/`awayScore`, `winner`, and `status` (`SCHEDULED` | `IN_PLAY` |
`FINISHED`). A finished **draw** is `status: "FINISHED"` with `winner: null`
and equal scores — consumers must treat null-winner FINISHED as a draw.

A knockout match with only one feeder resolved is emitted as a **partial**:
`status: "SCHEDULED"` with the unknown side as `null` (e.g. `home: null`,
`away: "ESP"`). Never both sides null; a partial never has scores or a winner.

## TODO: football-data.org arbiter (optional)

The pipeline can cross-check finished scores against
[football-data.org](https://www.football-data.org/) but the arbiter is
**disabled** until a token is provided. To enable it:

```
gh secret set FOOTBALL_DATA_TOKEN --repo che1404/bracket26-data
```

Without the secret the workflow runs fine and publishes from the primary
source alone.
