"""
MusicBee ↔ Spotify Playlist Comparator
=======================================
Supported formats:
  MusicBee : .m3u / .m3u8  (right-click playlist → Export → M3U)
             .xml / .mbl / .mbml  (File → Export Library)
  Spotify  : .csv  (via Exportify: https://exportify.net)
             .json (official Spotify data export)
"""

import streamlit as st
import pandas as pd
import re
import json
import io
from pathlib import Path
from difflib import SequenceMatcher

# ─────────────────────────────────────────────────────────────────────────────
# Duration helpers
# ─────────────────────────────────────────────────────────────────────────────

def to_seconds(raw: str) -> float | None:
    """
    Normalise any duration representation to seconds (float).
    Handles:
      - plain integer seconds  e.g. "213"       → M3U EXTINF
      - milliseconds           e.g. "213000"    → Spotify CSV / MusicBee XML
      - mm:ss or h:mm:ss       e.g. "3:33"
    Returns None when the value is missing or unparseable.
    """
    if not raw or raw.strip() in ("", "nan", "None", "-1"):
        return None
    raw = raw.strip()
    # mm:ss or h:mm:ss
    if ":" in raw:
        parts = raw.split(":")
        try:
            secs = sum(int(p) * 60 ** (len(parts) - 1 - i) for i, p in enumerate(parts))
            return float(secs)
        except ValueError:
            return None
    try:
        val = float(raw)
        # Heuristic: Spotify/XML store ms; values ≥ 10 000 are almost certainly ms
        return val / 1000.0 if val >= 10_000 else val
    except ValueError:
        return None


def fmt_seconds(s: float | None) -> str:
    """Format seconds as m:ss, or '—' if unknown."""
    if s is None:
        return "—"
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


# ─────────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────────

def parse_m3u(text: str) -> pd.DataFrame:
    rows = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            meta = line[8:]
            comma = meta.find(",")
            label = meta[comma + 1:].strip() if comma != -1 else meta.strip()
            duration = meta[:comma].strip() if comma != -1 else ""
            if " - " in label:
                artist, title = label.split(" - ", 1)
            else:
                artist, title = "", label
            rows.append({"title": title.strip(), "artist": artist.strip(), "duration": duration})
        elif line and not line.startswith("#"):
            stem = Path(line.replace("\\", "/")).stem
            if " - " in stem:
                artist, title = stem.split(" - ", 1)
            else:
                artist, title = "", stem
            rows.append({"title": title.strip(), "artist": artist.strip(), "duration": ""})
        i += 1
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["title", "artist", "duration"])


def parse_musicbee_xml(text: str) -> pd.DataFrame:
    import xml.etree.ElementTree as ET
    rows = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        st.error(f"XML parse error: {e}")
        return pd.DataFrame(columns=["title", "artist", "duration"])

    def iter_dicts(node):
        for child in node:
            if child.tag == "dict":
                yield child
            else:
                yield from iter_dicts(child)

    for d in iter_dicts(root):
        keys = list(d)
        track = {}
        for j in range(0, len(keys) - 1, 2):
            track[keys[j].text or ""] = keys[j + 1].text or ""
        title = track.get("Name", track.get("Title", ""))
        artist = track.get("Artist", track.get("Album Artist", ""))
        duration = track.get("Total Time", "")
        if title:
            rows.append({"title": title, "artist": artist, "duration": duration})

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["title", "artist", "duration"])


def parse_spotify_csv(text: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(text))
    df.columns = [c.strip().lower() for c in df.columns]
    title_col  = next((c for c in df.columns if "track name" in c or c in ("name", "title")), None)
    artist_col = next((c for c in df.columns if "artist" in c), None)
    dur_col    = next((c for c in df.columns if "duration" in c or "ms" in c), None)
    if title_col is None:
        st.error("Could not detect a track-name column. Columns found: " + str(list(df.columns)))
        return pd.DataFrame(columns=["title", "artist", "duration"])
    result = pd.DataFrame()
    result["title"]    = df[title_col].fillna("").astype(str)
    result["artist"]   = df[artist_col].fillna("").astype(str) if artist_col else ""
    result["duration"] = df[dur_col].fillna("").astype(str)    if dur_col    else ""
    return result


def parse_spotify_json(text: str) -> pd.DataFrame:
    data = json.loads(text)
    rows = []
    items = data if isinstance(data, list) else data.get("items", data.get("tracks", {}).get("items", []))
    for item in items:
        if isinstance(item, dict):
            track   = item.get("track", item)
            title   = track.get("name", track.get("trackName", ""))
            artists = track.get("artists", [])
            artist  = ", ".join(a["name"] for a in artists) if artists else track.get("artistName", "")
            dur     = str(track.get("duration_ms", track.get("msPlayed", "")))
            if title:
                rows.append({"title": title, "artist": artist, "duration": dur})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["title", "artist", "duration"])


def parse_file(name: str, content: bytes, source: str) -> pd.DataFrame:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")
    suffix = Path(name).suffix.lower()
    if source == "musicbee":
        if suffix in (".m3u", ".m3u8"):
            return parse_m3u(text)
        elif suffix in (".xml", ".mbl", ".mbml"):
            return parse_musicbee_xml(text)
        else:
            st.error(f"Unsupported MusicBee format: {suffix}")
    else:
        if suffix == ".csv":
            return parse_spotify_csv(text)
        elif suffix == ".json":
            return parse_spotify_json(text)
        else:
            st.error(f"Unsupported Spotify format: {suffix}")
    return pd.DataFrame(columns=["title", "artist", "duration"])


# ─────────────────────────────────────────────────────────────────────────────
# Comparison (cached so settings changes don't re-run the whole thing)
# ─────────────────────────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    s = re.sub(r"feat\.?.*", "", s)
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()

def track_key(title: str, artist: str) -> str:
    return normalize(title) + " ||| " + normalize(artist)

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

@st.cache_data(show_spinner=False)
def compare_playlists(mb_records: tuple, sp_records: tuple,
                      threshold: float, dur_tolerance: int):
    """
    mb_records / sp_records: tuples of (title, artist, duration_str)
    dur_tolerance: max allowed difference in seconds before flagging a mismatch
    """
    mb_list = list(mb_records)
    sp_list = list(sp_records)
    mb_keys = {track_key(t, a): i for i, (t, a, _) in enumerate(mb_list)}
    sp_keys = {track_key(t, a): i for i, (t, a, _) in enumerate(sp_list)}

    matched_mb, matched_sp = set(), set()
    match_rows = []

    def dur_diff(mb_dur: str, sp_dur: str) -> float | None:
        """Return absolute difference in seconds, or None if either is unknown."""
        a, b = to_seconds(mb_dur), to_seconds(sp_dur)
        return abs(a - b) if (a is not None and b is not None) else None

    def make_match(mb_idx, sp_idx, score, mtype):
        t, a, mb_dur = mb_list[mb_idx]
        _,  _, sp_dur = sp_list[sp_idx]
        diff = dur_diff(mb_dur, sp_dur)
        return {
            "title":        t,
            "artist":       a,
            "mb_duration":  fmt_seconds(to_seconds(mb_dur)),
            "sp_duration":  fmt_seconds(to_seconds(sp_dur)),
            "dur_diff_s":   round(diff, 1) if diff is not None else None,
            "dur_ok":       (diff is None or diff <= dur_tolerance),
            "match_score":  score,
            "match_type":   mtype,
        }

    # Exact matches
    for key, mb_idx in mb_keys.items():
        if key in sp_keys:
            sp_idx = sp_keys[key]
            match_rows.append(make_match(mb_idx, sp_idx, 1.0, "exact"))
            matched_mb.add(mb_idx)
            matched_sp.add(sp_idx)

    # Fuzzy matches on remainders only
    unmatched_mb = [i for i in range(len(mb_list)) if i not in matched_mb]
    unmatched_sp = [i for i in range(len(sp_list)) if i not in matched_sp]
    sp_remainder  = [(i, track_key(sp_list[i][0], sp_list[i][1])) for i in unmatched_sp]
    fuzzy_matched_sp = set()

    for mb_idx in unmatched_mb:
        mb_key = track_key(mb_list[mb_idx][0], mb_list[mb_idx][1])
        best_score, best_sp_idx = 0.0, None
        for sp_idx, sp_key in sp_remainder:
            if sp_idx in fuzzy_matched_sp:
                continue
            score = similarity(mb_key, sp_key)
            if score > best_score:
                best_score, best_sp_idx = score, sp_idx
        if best_score >= threshold and best_sp_idx is not None:
            match_rows.append(make_match(mb_idx, best_sp_idx, round(best_score, 2), "fuzzy"))
            matched_mb.add(mb_idx)
            fuzzy_matched_sp.add(best_sp_idx)
            matched_sp.add(best_sp_idx)

    def only_row(lst, i):
        t, a, dur = lst[i]
        return {"title": t, "artist": a, "duration": fmt_seconds(to_seconds(dur))}

    only_mb = [only_row(mb_list, i) for i in range(len(mb_list)) if i not in matched_mb]
    only_sp = [only_row(sp_list, i) for i in range(len(sp_list)) if i not in matched_sp]
    return match_rows, only_mb, only_sp


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Playlist Comparator", page_icon="🎵", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
  .stApp { background: #0e0e14; color: #e8e4dd; }
  .hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2a2a4a; border-radius: 16px;
    padding: 2.5rem 3rem; margin-bottom: 2rem; position: relative; overflow: hidden;
  }
  .hero::before {
    content:""; position:absolute; top:-60px; right:-60px;
    width:200px; height:200px; border-radius:50%;
    background:radial-gradient(circle,#e94560 0%,transparent 70%); opacity:0.25;
  }
  .hero h1 { color:#fff; margin:0 0 .4rem; font-size:2.4rem; letter-spacing:-0.5px; }
  .hero p  { color:#8b8faa; margin:0; font-size:1rem; }
  .metric-card {
    background:#15151f; border:1px solid #2a2a4a; border-radius:12px;
    padding:1.2rem 1.5rem; text-align:center;
  }
  .metric-card .num { font-size:2.5rem; font-weight:700; font-family:'DM Mono',monospace; }
  .metric-card .lbl { font-size:0.8rem; color:#6b6f8a; text-transform:uppercase; letter-spacing:1px; }
  .green{color:#4ade80;} .red{color:#e94560;} .amber{color:#f59e0b;} .blue{color:#60a5fa;}
  .uploader-label {
    font-family:'DM Mono',monospace; font-size:0.75rem;
    text-transform:uppercase; letter-spacing:1.5px; color:#6b6f8a; margin-bottom:.5rem;
  }
  .footnote { color:#4a4e6a; font-size:0.78rem; margin-top:2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🎵 Playlist Comparator</h1>
  <p>Upload your MusicBee &amp; Spotify exports — find what's missing, extra, or different.</p>
</div>
""", unsafe_allow_html=True)

# ── Upload widgets ─────────────────────────────────────────────────────────────
col_mb, col_sp = st.columns(2, gap="large")
with col_mb:
    st.markdown('<div class="uploader-label">MusicBee Playlist</div>', unsafe_allow_html=True)
    mb_file = st.file_uploader("MusicBee", type=["m3u","m3u8","xml","mbl","mbml"],
                                label_visibility="collapsed")
    st.caption("`.m3u` `.m3u8` `.xml` `.mbl`")
with col_sp:
    st.markdown('<div class="uploader-label">Spotify Playlist</div>', unsafe_allow_html=True)
    sp_file = st.file_uploader("Spotify", type=["csv","json"],
                                label_visibility="collapsed")
    st.caption("`.csv` via [Exportify](https://exportify.net)  ·  `.json` Spotify data export")

# ── Immediately read bytes into session_state (survives reruns) ───────────────
if mb_file is not None:
    st.session_state["mb_bytes"] = (mb_file.name, mb_file.read())
if sp_file is not None:
    st.session_state["sp_bytes"] = (sp_file.name, sp_file.read())

mb_ready = "mb_bytes" in st.session_state
sp_ready = "sp_bytes" in st.session_state

# ── Options ───────────────────────────────────────────────────────────────────
with st.expander("⚙️  Matching options", expanded=False):
    threshold = st.slider("Fuzzy match threshold", 0.5, 1.0, 0.82, 0.01)
    dur_tolerance = st.slider(
        "Duration mismatch tolerance (seconds)", 1, 30, 5, 1,
        help="Matched tracks whose lengths differ by more than this are flagged as duration mismatches."
    )
    show_fuzzy_only   = st.checkbox("Show only fuzzy matches in the Matched tab", value=False)
    show_dur_mismatch = st.checkbox("Show only duration mismatches in the Matched tab", value=False)

# ── Action buttons ────────────────────────────────────────────────────────────
btn_col, clr_col = st.columns([3, 1])
with btn_col:
    run = st.button("🔍  Compare playlists", type="primary",
                    disabled=not (mb_ready and sp_ready))
with clr_col:
    if st.button("🗑  Clear"):
        for k in ("mb_bytes", "sp_bytes", "results"):
            st.session_state.pop(k, None)
        st.rerun()

# ── Guide when files not yet ready ───────────────────────────────────────────
if not (mb_ready and sp_ready):
    st.info("👆  Upload both playlist files above, then click **Compare playlists**.")
    with st.expander("📖  How to export your playlists", expanded=True):
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("""
**MusicBee**
1. Right-click your playlist in the sidebar
2. **Send To → Export**
3. Choose **M3U** format and save
""")
        with g2:
            st.markdown("""
**Spotify**
1. Visit **[exportify.net](https://exportify.net)**
2. Log in with Spotify
3. Click **Export** next to your playlist → `.csv`
""")
    st.stop()

# ── Parse & compare on button press ──────────────────────────────────────────
if run:
    mb_name, mb_bytes = st.session_state["mb_bytes"]
    sp_name, sp_bytes = st.session_state["sp_bytes"]

    with st.spinner("Parsing files…"):
        df_mb = parse_file(mb_name, mb_bytes, "musicbee")
        df_sp = parse_file(sp_name, sp_bytes, "spotify")

    if df_mb.empty:
        st.error("MusicBee playlist appears empty after parsing. Check the file.")
        st.stop()
    if df_sp.empty:
        st.error("Spotify playlist appears empty after parsing. Check the file.")
        st.stop()

    mb_records = tuple((str(r.title), str(r.artist), str(r.duration)) for r in df_mb.itertuples())
    sp_records = tuple((str(r.title), str(r.artist), str(r.duration)) for r in df_sp.itertuples())

    with st.spinner(f"Comparing {len(mb_records)} × {len(sp_records)} tracks…"):
        match_rows, only_mb, only_sp = compare_playlists(mb_records, sp_records, threshold, dur_tolerance)

    st.session_state["results"] = {
        "match_rows": match_rows, "only_mb": only_mb, "only_sp": only_sp,
        "total_mb": len(mb_records), "total_sp": len(sp_records),
    }

# ── Show results ──────────────────────────────────────────────────────────────
if "results" in st.session_state:
    res = st.session_state["results"]
    df_matched = pd.DataFrame(res["match_rows"]) if res["match_rows"] else pd.DataFrame(columns=["title","artist","match_score","match_type"])
    df_only_mb = pd.DataFrame(res["only_mb"])    if res["only_mb"]    else pd.DataFrame(columns=["title","artist"])
    df_only_sp = pd.DataFrame(res["only_sp"])    if res["only_sp"]    else pd.DataFrame(columns=["title","artist"])

    st.markdown("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, num, lbl, cls in [
        (c1, res["total_mb"],   "MusicBee tracks",  "blue"),
        (c2, res["total_sp"],   "Spotify tracks",   "blue"),
        (c3, len(df_matched),   "Matched",          "green"),
        (c4, len(df_only_mb),   "Only in MusicBee", "amber"),
        (c5, len(df_only_sp),   "Only in Spotify",  "red"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="num {cls}">{num}</div>'
                        f'<div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("&nbsp;")

    tab1, tab2, tab3, tab4 = st.tabs([
        f"🟡 Only in MusicBee ({len(df_only_mb)})",
        f"🔴 Only in Spotify ({len(df_only_sp)})",
        f"✅ Matched ({len(df_matched)})",
        "📋 Raw data",
    ])

    with tab1:
        st.caption("In MusicBee but not found on Spotify.")
        if df_only_mb.empty:
            st.success("🎉 Everything is on Spotify too!")
        else:
            st.dataframe(df_only_mb, width='stretch',
                         height=min(40*len(df_only_mb)+50, 600))
            st.download_button("⬇ Download CSV", df_only_mb.to_csv(index=False),
                               "only_in_musicbee.csv", "text/csv")

    with tab2:
        st.caption("On Spotify but not in your MusicBee playlist.")
        if df_only_sp.empty:
            st.success("🎉 Everything on Spotify is in MusicBee too!")
        else:
            st.dataframe(df_only_sp, width='stretch',
                         height=min(40*len(df_only_sp)+50, 600))
            st.download_button("⬇ Download CSV", df_only_sp.to_csv(index=False),
                               "only_in_spotify.csv", "text/csv")

    with tab3:
        disp = df_matched[df_matched["match_type"] == "fuzzy"] if show_fuzzy_only else df_matched
        st.caption(f"{len(disp)} tracks shown{' (fuzzy only)' if show_fuzzy_only else ''}.")
        if not disp.empty:
            st.dataframe(disp.reset_index(drop=True), width='stretch',
                         height=min(40*len(disp)+50, 600),
                         column_config={"match_score": st.column_config.ProgressColumn(
                             "Score", min_value=0, max_value=1, format="%.2f")})

    with tab4:
        r1, r2 = st.columns(2)
        mb_name, mb_bytes = st.session_state["mb_bytes"]
        sp_name, sp_bytes = st.session_state["sp_bytes"]
        with r1:
            st.markdown("**MusicBee — parsed**")
            st.dataframe(parse_file(mb_name, mb_bytes, "musicbee"),
                         width='stretch', height=300)
        with r2:
            st.markdown("**Spotify — parsed**")
            st.dataframe(parse_file(sp_name, sp_bytes, "spotify"),
                         width='stretch', height=300)

st.markdown('<p class="footnote">Matching: normalized title+artist keys, exact first, then fuzzy fallback. Adjust threshold in ⚙️ if needed.</p>', unsafe_allow_html=True)