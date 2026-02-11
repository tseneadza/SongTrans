# PRD: Synced Playback & Lyric Highlighting

## 1. Overview

**Goal:** Enable users to play a song in the app and have lyrics highlight in sync with playback, with the option to view lyrics with or without music.

**Outcomes:**
- Lyrics highlight line-by-line as the song plays (when music is on).
- Optional “lyrics only” mode: no audio, with optional simulated highlighting (auto-advance by time).
- Clear UI: “Play music” vs “Lyrics only” (and optional “Simulate” for lyrics-only).

---

## 2. User Stories

| ID | As a… | I want to… | So that… |
|----|--------|-------------|----------|
| US-1 | User | Play the selected song in the browser | I can listen while reading lyrics. |
| US-2 | User | See the current lyric line highlighted as the song plays | I can follow along easily. |
| US-3 | User | Choose to view lyrics without playing music | I can read/translate without audio. |
| US-4 | User | Optionally auto-advance lyric highlight without music (“simulate”) | I can still follow timing when I don’t want sound. |

---

## 3. Scope

**In scope**
- Synced (timestamped) lyrics: LRC/synced-lyrics API or duration-based estimation.
- Playback when user has Spotify Premium: Web Playback SDK, OAuth, play/pause/seek.
- Lyric highlight engine: map current time → line index, highlight + scroll.
- Toggle: “Play music” vs “Lyrics only”; optional “Simulate” for lyrics-only.
- Exposing Spotify track URI when we have it (album/singles flows); optional search for “All Songs”.

**Out of scope (for this PRD)**
- Offline playback.
- Non-Spotify players (e.g. YouTube) unless added in a later PRD.
- Editing or uploading custom LRC files (can be a follow-up).

---

## 4. Requirements

### 4.1 Synced lyrics

- **R1.1** System SHALL obtain per-line start times for the current song (LRC or equivalent).
- **R1.2** Preferred: integrate a synced-lyrics API (e.g. LRCLIB) by title + artist (+ duration when available).
- **R1.3** Fallback: estimate line start times from track duration (from Spotify) and line count when no LRC is available.
- **R1.4** API response SHALL expose lines as a list of `{ startTimeMs, text }` (or equivalent) for the frontend.

### 4.2 Playback (play with music)

- **R2.1** When “Play music” is on and a Spotify track URI is available, system SHALL use Spotify Web Playback SDK to play the track in the browser.
- **R2.2** Playback SHALL require user sign-in (Spotify OAuth) and SHALL only be enabled for Spotify Premium (or document limitation).
- **R2.3** Backend SHALL expose Spotify track `id` or `uri` for songs that come from Spotify (album/singles); for “All Songs” (Genius-only), SHALL support optional Spotify search by title/artist to resolve a URI when possible.
- **R2.4** Player SHALL support play, pause, and seek; UI SHALL show play/pause and optionally a progress bar.

### 4.3 Lyric highlighting

- **R3.1** When playback is active or “Simulate” is on, system SHALL highlight the lyric line whose start time is ≤ current time and (optionally) whose next line start is > current time.
- **R3.2** Highlight SHALL update at least every 200 ms (or on player state change).
- **R3.3** Highlighted line SHALL be scrolled into view (e.g. center) when it changes.
- **R3.4** Same highlight logic SHALL apply to both “original” and “translated” columns (sync scroll already exists; ensure highlight state is shared).

### 4.4 “Play music” vs “Lyrics only”

- **R4.1** UI SHALL provide a clear choice: “Play music” (audio + sync) vs “Lyrics only” (no audio).
- **R4.2** When “Lyrics only” is selected, system SHALL NOT start or require Spotify playback or Premium.
- **R4.3** When “Lyrics only” is selected, UI MAY offer “Simulate” (or “Auto-advance”) that runs a local timer and uses the same timestamp data to advance highlight as if the song were playing.
- **R4.4** If no Spotify URI is available, “Play music” SHALL be disabled or hidden, with a short explanation (e.g. “Playback available when song is selected from an album”).

### 4.5 Non-functional

- **R5.1** Lyric sync SHALL work for songs where LRC (or estimated) data exists; gracefully degrade to no highlight when no timestamps are available.
- **R5.2** No playback SHALL start without user action (e.g. click “Play” or enable “Play music” and play).

---

## 5. Technical approach (summary)

| Area | Approach |
|------|----------|
| **Synced lyrics** | Add backend (or frontend) call to LRCLIB (or similar) with title, artist, duration_ms; parse LRC into `[{ startTimeMs, text }]`. Fallback: divide `duration_ms` by line count. Cache by song (e.g. same TTL as lyrics). |
| **Spotify URI** | In `spotify_service.get_album_tracks()`, include `id` (and build `uri`). In `/api/album-songs` and any song-detail response, include `spotify_id` / `spotify_uri` when available. For “All Songs”, add optional Spotify search by title/artist to get URI. |
| **Web Playback SDK** | Load SDK, implement OAuth (Implicit or Auth Code + backend token exchange). On “Play”, create/use player, `play({ uris: [uri] })`. Subscribe to `player_state_changed` or poll `getCurrentState()` for `position`. |
| **Highlight engine** | Single source of “current time”: from player `position` (when “Play music”) or from local timer (when “Simulate”). Binary search or linear scan on line start times → index → set `.highlighted` and scroll into view. |
| **UI** | Results section: add “Play music” toggle and “Simulate” (when “Lyrics only”). Show Play/Pause and optional seek bar when playback is available. Disable/hide “Play music” when no Spotify URI. |

---

## 6. API / data changes

- **New or extended**
  - `GET /api/synced-lyrics?title=...&artist=...&duration_ms=...` (or include in existing translate/lyrics response): returns `{ lines: [{ startTimeMs, text }], source: "lrclib"|"estimated" }`.
  - `/api/album-songs` (and any song list/detail): add `spotify_uri` (and/or `spotify_id`) when track comes from Spotify.
  - Optional: `GET /api/spotify-search?q=...` or include in translate flow to resolve Spotify URI for Genius-only songs.

- **Existing**
  - `/api/translate` (or lyrics path): may optionally include `synced_lines` or a link to synced-lyrics endpoint; frontend needs track duration when using estimation (can come from Spotify track in album-songs or from a separate call).

---

## 7. Success criteria

- [ ] User can turn “Play music” on and hear the song while lyrics highlight in sync (when URI + LRC/estimated data exist).
- [ ] User can choose “Lyrics only” and read without any audio.
- [ ] When “Lyrics only” + “Simulate” is on, highlight advances over time without playback.
- [ ] When no Spotify URI is available, “Play music” is not offered (or is disabled with a clear reason).
- [ ] No autoplay; playback only after explicit user action.

---

## 8. Open decisions

- Use LRCLIB vs another LRC API (cost, rate limits, coverage).
- OAuth flow: Implicit Grant vs Authorization Code (with backend redirect/token exchange) for Web Playback SDK.
- Whether “Simulate” requires track duration (e.g. from Spotify) or can use a default duration when unknown.

---

## 9. Dependencies

- Spotify Web Playback SDK (script + OAuth).
- Spotify Premium for playback (document for users).
- Synced-lyrics API (e.g. LRCLIB) or commitment to estimation-only fallback.
- Backend: expose Spotify track `id`/`uri` from `spotify_service` and album-songs (and optionally search).

---

## 10. Phasing (suggested)

| Phase | Deliverable |
|-------|-------------|
| **1** | Synced lyrics: LRCLIB (or similar) + fallback estimation; API returning `lines[]` with `startTimeMs`; cache. |
| **2** | Backend: expose `spotify_uri` (and `spotify_id`) in album-songs and, if needed, search for Genius-only songs. |
| **3** | Frontend: highlight engine (time → line index, highlight + scroll); “Simulate” with timer when “Lyrics only”. |
| **4** | Frontend: Spotify OAuth + Web Playback SDK; “Play music” toggle; Play/Pause (and optional seek); wire current time from player to highlight engine. |
| **5** | Polish: disable “Play music” when no URI; copy/error states; docs and INDEX update. |
