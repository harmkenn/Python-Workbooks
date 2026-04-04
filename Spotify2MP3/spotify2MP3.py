"""
MusicBee ↔ Spotify Playlist Comparator
=======================================
Compare your playlists and find what's missing, extra, or mismatched.

Supported formats:
  MusicBee : .m3u / .m3u8  (File > Export Playlist)
             .mbl / .mbml  (MusicBee Library XML)
  Spotify  : .csv          (via Exportify: https://exportify.net)
             .json         (official Spotify data export)
"""

import streamlit as st
import pandas as pd
import re
import json
import io
from pathlib import Path
from difflib import SequenceMatcher


# ─────────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────────

def parse_m3u(content: str) -> pd.DataFrame:
    """Parse M3U / M3U8 playlist.  Returns df with title, artist, duration."""
    rows = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            # Format: #EXTINF:<seconds>,<Artist> - <Title>
            meta = line[8:]  # strip "#EXTINF:"
            comma = meta.find(",")
            duration = meta[:comma].strip() if comma != -1 else ""
            label = meta[comma + 1:].strip() if comma != -1 else meta.strip()
            # Try "Artist - Title" split
            if " - " in label:
                artist, title = label.split(" - ", 1)
            else:
                artist, title = "", label
            rows.append({"title": title.strip(), "artist": artist.strip(), "duration": duration})
            i += 1
        elif line and not line.startswith("#"):
            # Path line without preceding EXTINF
            stem = Path(line.replace("\\", "/")).stem
            if " - " in stem:
                artist, title = stem.split(" - ", 1)
            else:
                artist, title = "", stem
            rows.append({"title": title.strip(), "artist": artist.strip(), "duration": ""})
            i += 1
        else:
            i += 1
    return pd.DataFrame(rows, columns=["title", "artist", "duration"])


def parse_musicbee_xml(content: str) -> pd.DataFrame:
    """Parse MusicBee XML / MBML library export."""
    import xml.etree.ElementTree as ET
    rows = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        st.error(f"XML parse error: {e}")
        return pd.DataFrame(columns=["title", "artist", "duration"])

    # MusicBee uses a dict-like structure: <key>Artist</key><string>...</string>
    # Find all <dict> blocks inside <array>
    ns = {"": ""}  # no namespace

    def iter_track_dicts(node):
        for child in node:
            if child.tag == "dict":
                yield child
            else:
                yield from iter_track_dicts(child)

    for d in iter_track_dicts(root):
        keys = list(d)
        track = {}
        for j in range(0, len(keys) - 1, 2):
            k = keys[j].text or ""
            v = keys[j + 1].text or ""
            track[k] = v
        title = track.get("Name", track.get("Title", ""))
        artist = track.get("Artist", track.get("Album Artist", ""))
        duration = track.get("Total Time", "")
        if title:
            rows.append({"title": title, "artist": artist, "duration": duration})

    return pd.DataFrame(rows, columns=["title", "artist", "duration"]) if rows else pd.DataFrame(columns=["title", "artist", "duration"])


def parse_spotify_csv(content: str) -> pd.DataFrame:
    """Parse Exportify CSV.  Flexible column detection."""
    df = pd.read_csv(io.StringIO(content))
    df.columns = [c.strip().lower() for c in df.columns]

    title_col = next((c for c in df.columns if "track name" in c or c == "name" or c == "title"), None)
    artist_col = next((c for c in df.columns if "artist" in c), None)
    duration_col = next((c for c in df.columns if "duration" in c or "ms" in c), None)

    if title_col is None:
        st.error("Could not find a track name column in the CSV. Columns found: " + str(list(df.columns)))
        return pd.DataFrame(columns=["title", "artist", "duration"])

    result = pd.DataFrame()
    result["title"] = df[title_col].fillna("").astype(str)
    result["artist"] = df[artist_col].fillna("").astype(str) if artist_col else ""
    result["duration"] = df[duration_col].fillna("").astype(str) if duration_col else ""
    return result


def parse_spotify_json(content: str) -> pd.DataFrame:
    """Parse official Spotify data export JSON."""
    data = json.loads(content)
    rows = []

    # Format 1: {"items": [{"track": {...}}]}  (API / Exportify JSON)
    # Format 2: [{"trackName": ..., "artistName": ...}]  (playlist export)
    items = data if isinstance(data, list) else data.get("items", data.get("tracks", {}).get("items", []))

    for item in items:
        if isinstance(item, dict):
            track = item.get("track", item)
            title = track.get("name", track.get("trackName", ""))
            artists = track.get("artists", [])
            artist = ", ".join(a["name"] for a in artists) if artists else track.get("artistName", "")
            duration = str(track.get("duration_ms", track.get("msPlayed", "")))
            if title:
                rows.append({"title": title, "artist": artist, "duration": duration})

    return pd.DataFrame(rows, columns=["title", "artist", "duration"]) if rows else pd.DataFrame(columns=["title", "artist", "duration"])


def load_file(uploaded_file, source: str) -> pd.DataFrame:
    suffix = Path(uploaded_file.name).suffix.lower()
    content = uploaded_file.read()
    try:
        text = content.decode("utf-8-sig")  # handle BOM
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    if source == "musicbee":
        if suffix in (".m3u", ".m3u8"):
            return parse_m3u(text)
        elif suffix in (".xml", ".mbl", ".mbml"):
            return parse_musicbee_xml(text)
        else:
            st.error(f"Unsupported MusicBee format: {suffix}")
            return pd.DataFrame(columns=["title", "artist", "duration"])
    else:  # spotify
        if suffix == ".csv":
            return parse_spotify_csv(text)
        elif suffix == ".json":
            return parse_spotify_json(text)
        else:
            st.error(f"Unsupported Spotify format: {suffix}")
            return pd.DataFrame(columns=["title", "artist", "duration"])


# ─────────────────────────────────────────────────────────────────────────────
# Comparison logic
# ─────────────────────────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    """Lowercase, remove punctuation & common noise for fuzzy matching."""
    s = s.lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)          # remove parenthetical
    s = re.sub(r"feat\.?.*", "", s)                  # remove feat.
    s = re.sub(r"[^a-z0-9 ]", "", s)                 # strip punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s


def track_key(row) -> str:
    return normalize(row["title"]) + " ||| " + normalize(row["artist"])


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def compare_playlists(df_mb: pd.DataFrame, df_sp: pd.DataFrame, threshold: float = 0.82):
    """
    Returns three DataFrames:
      - matched      : tracks found in both (with match score)
      - only_musicbee: tracks only in MusicBee
      - only_spotify : tracks only in Spotify
    """
    mb_keys = {track_key(r): i for i, r in df_mb.iterrows()}
    sp_keys = {track_key(r): i for i, r in df_sp.iterrows()}

    matched_mb = set()
    matched_sp = set()
    match_rows = []

    # Exact key matches first
    for key, mb_idx in mb_keys.items():
        if key in sp_keys:
            sp_idx = sp_keys[key]
            match_rows.append({
                "title": df_mb.at[mb_idx, "title"],
                "artist": df_mb.at[mb_idx, "artist"],
                "match_score": 1.0,
                "match_type": "exact",
            })
            matched_mb.add(mb_idx)
            matched_sp.add(sp_idx)

    # Fuzzy match remaining
    unmatched_mb = [i for i in df_mb.index if i not in matched_mb]
    unmatched_sp = [i for i in df_sp.index if i not in matched_sp]

    for mb_idx in unmatched_mb:
        mb_key = track_key(df_mb.loc[mb_idx])
        best_score = 0
        best_sp_idx = None
        for sp_idx in unmatched_sp:
            if sp_idx in matched_sp:
                continue
            sp_key = track_key(df_sp.loc[sp_idx])
            score = similarity(mb_key, sp_key)
            if score > best_score:
                best_score = score
                best_sp_idx = sp_idx
        if best_score >= threshold and best_sp_idx is not None:
            match_rows.append({
                "title": df_mb.at[mb_idx, "title"],
                "artist": df_mb.at[mb_idx, "artist"],
                "match_score": round(best_score, 2),
                "match_type": "fuzzy",
            })
            matched_mb.add(mb_idx)
            matched_sp.add(best_sp_idx)

    df_matched = pd.DataFrame(match_rows) if match_rows else pd.DataFrame(columns=["title", "artist", "match_score", "match_type"])
    df_only_mb = df_mb.loc[[i for i in df_mb.index if i not in matched_mb]].reset_index(drop=True)
    df_only_sp = df_sp.loc[[i for i in df_sp.index if i not in matched_sp]].reset_index(drop=True)

    return df_matched, df_only_mb, df_only_sp


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Playlist Comparator",
    page_icon="🎵",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }

  .stApp { background: #0e0e14; color: #e8e4dd; }

  /* Header banner */
  .hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle, #e94560 0%, transparent 70%);
    opacity: 0.25;
  }
  .hero h1 { color: #fff; margin: 0 0 .4rem; font-size: 2.4rem; letter-spacing: -0.5px; }
  .hero p  { color: #8b8faa; margin: 0; font-size: 1rem; }

  /* Metric cards */
  .metric-card {
    background: #15151f;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
  }
  .metric-card .num { font-size: 2.5rem; font-weight: 700; font-family: 'DM Mono', monospace; }
  .metric-card .lbl { font-size: 0.8rem; color: #6b6f8a; text-transform: uppercase; letter-spacing: 1px; }

  .green { color: #4ade80; }
  .red   { color: #e94560; }
  .amber { color: #f59e0b; }
  .blue  { color: #60a5fa; }

  /* Tab panels */
  .stTabs [role="tab"] { font-family: 'DM Mono', monospace; font-size: 0.85rem; }

  /* Upload boxes */
  .uploader-box {
    background: #15151f;
    border: 1.5px dashed #2a2a4a;
    border-radius: 12px;
    padding: 1.5rem;
  }
  .uploader-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #6b6f8a;
    margin-bottom: .5rem;
  }

  /* Dataframe tweaks */
  .dataframe { font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }

  /* Footer note */
  .footnote { color: #4a4e6a; font-size: 0.78rem; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🎵 Playlist Comparator</h1>
  <p>Upload your MusicBee & Spotify exports — find what's missing, extra, or different.</p>
</div>
""", unsafe_allow_html=True)

# ── Upload columns ────────────────────────────────────────────────────────────
col_mb, col_sp = st.columns(2, gap="large")

with col_mb:
    st.markdown('<div class="uploader-label">MusicBee Playlist</div>', unsafe_allow_html=True)
    mb_file = st.file_uploader(
        "MusicBee file",
        type=["m3u", "m3u8", "xml", "mbl", "mbml"],
        help="Export from MusicBee: right-click playlist → Export → M3U",
        label_visibility="collapsed",
    )
    st.caption("Supported: `.m3u` `.m3u8` `.xml` `.mbl`")

with col_sp:
    st.markdown('<div class="uploader-label">Spotify Playlist</div>', unsafe_allow_html=True)
    sp_file = st.file_uploader(
        "Spotify file",
        type=["csv", "json"],
        help="Export via Exportify (exportify.net) → CSV, or Spotify data download → JSON",
        label_visibility="collapsed",
    )
    st.caption("Supported: `.csv` (Exportify) · `.json` (Spotify data export)")

# ── Settings expander ─────────────────────────────────────────────────────────
with st.expander("⚙️  Matching options", expanded=False):
    threshold = st.slider(
        "Fuzzy match threshold",
        min_value=0.5, max_value=1.0, value=0.82, step=0.01,
        help="Higher = stricter matching. 0.82 works well for most playlists.",
    )
    show_fuzzy_only = st.checkbox("Show only fuzzy (non-exact) matches in the Matched tab", value=False)

# ── Run comparison ────────────────────────────────────────────────────────────
if mb_file and sp_file:
    with st.spinner("Parsing & comparing…"):
        df_mb = load_file(mb_file, "musicbee")
        df_sp = load_file(sp_file, "spotify")

    if df_mb.empty or df_sp.empty:
        st.error("One or both playlists could not be parsed. Check the file format and try again.")
        st.stop()

    df_matched, df_only_mb, df_only_sp = compare_playlists(df_mb, df_sp, threshold)

    # ── Summary metrics ───────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, len(df_mb),       "MusicBee tracks",    "blue"),
        (c2, len(df_sp),       "Spotify tracks",     "blue"),
        (c3, len(df_matched),  "Matched",            "green"),
        (c4, len(df_only_mb),  "Only in MusicBee",   "amber"),
        (c5, len(df_only_sp),  "Only in Spotify",    "red"),
    ]
    for col, num, lbl, cls in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="num {cls}">{num}</div>
              <div class="lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("&nbsp;")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_miss_mb, tab_miss_sp, tab_matched, tab_raw = st.tabs([
        f"🟡  Only in MusicBee  ({len(df_only_mb)})",
        f"🔴  Only in Spotify  ({len(df_only_sp)})",
        f"✅  Matched  ({len(df_matched)})",
        "📋  Raw data",
    ])

    with tab_miss_mb:
        st.markdown("These tracks are in your **MusicBee** playlist but **not** found in Spotify.")
        if df_only_mb.empty:
            st.success("🎉 No missing tracks — everything is on Spotify too!")
        else:
            st.dataframe(
                df_only_mb[["title", "artist"]].reset_index(drop=True),
                use_container_width=True, height=min(40 * len(df_only_mb) + 50, 600),
            )
            csv = df_only_mb[["title", "artist"]].to_csv(index=False)
            st.download_button("⬇  Download as CSV", csv, "only_in_musicbee.csv", "text/csv")

    with tab_miss_sp:
        st.markdown("These tracks are on **Spotify** but **not** found in your MusicBee playlist.")
        if df_only_sp.empty:
            st.success("🎉 No extra tracks — everything on Spotify is in MusicBee too!")
        else:
            st.dataframe(
                df_only_sp[["title", "artist"]].reset_index(drop=True),
                use_container_width=True, height=min(40 * len(df_only_sp) + 50, 600),
            )
            csv = df_only_sp[["title", "artist"]].to_csv(index=False)
            st.download_button("⬇  Download as CSV", csv, "only_in_spotify.csv", "text/csv")

    with tab_matched:
        display_df = df_matched[df_matched["match_type"] == "fuzzy"] if show_fuzzy_only else df_matched
        st.markdown(f"**{len(display_df)}** tracks matched{' (fuzzy only)' if show_fuzzy_only else ''}.")
        if display_df.empty:
            st.info("No tracks to show with the current filter.")
        else:
            st.dataframe(
                display_df.reset_index(drop=True),
                use_container_width=True, height=min(40 * len(display_df) + 50, 600),
                column_config={
                    "match_score": st.column_config.ProgressColumn(
                        "Match score", min_value=0, max_value=1, format="%.2f"
                    ),
                    "match_type": st.column_config.TextColumn("Type"),
                },
            )

    with tab_raw:
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("**MusicBee — parsed tracks**")
            st.dataframe(df_mb, use_container_width=True, height=300)
        with r2:
            st.markdown("**Spotify — parsed tracks**")
            st.dataframe(df_sp, use_container_width=True, height=300)

else:
    st.info("👆  Upload both playlist files above to start the comparison.")
    # How-to guide
    with st.expander("📖  How to export your playlists", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
**MusicBee**
1. Open MusicBee
2. Right-click your playlist in the sidebar
3. **Send To → Export** (or **File → Export Library**)
4. Choose **M3U** format and save

> Alternatively use **File → Export Library** as XML for a full library export.
""")
        with c2:
            st.markdown("""
**Spotify**
1. Go to **[exportify.net](https://exportify.net)** in your browser
2. Log in with your Spotify account
3. Click **Export** next to the playlist you want
4. Download the `.csv` file

> Or use your official Spotify data: *Settings → Privacy → Download your data* (JSON, takes a few days).
""")

st.markdown('<p class="footnote">Matching uses normalized title+artist keys with fuzzy fallback. Adjust the threshold in ⚙️ settings if you get too many false positives/negatives.</p>', unsafe_allow_html=True)