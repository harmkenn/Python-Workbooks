"""
Spotify -> MP3 Downloader
Upload your Exportify CSV, pick a track, download as MP3 via yt-dlp.
"""

import streamlit as st
import pandas as pd
import io
import re
import glob
import shutil
import subprocess
import tempfile
from pathlib import Path

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

YTDLP_AVAILABLE  = shutil.which("yt-dlp")  is not None
FFMPEG_AVAILABLE = shutil.which("ffmpeg")  is not None


def parse_exportify_csv(content: bytes) -> pd.DataFrame:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    df = pd.read_csv(io.StringIO(text))
    df.columns = [c.strip().lower() for c in df.columns]

    title_col  = next((c for c in df.columns if "track name" in c or c in ("name", "title")), None)
    artist_col = next((c for c in df.columns if "artist" in c), None)
    album_col  = next((c for c in df.columns if "album" in c), None)
    dur_col    = next((c for c in df.columns if "duration" in c or "ms" in c), None)

    if title_col is None:
        return pd.DataFrame()

    result = pd.DataFrame()
    result["title"]       = df[title_col].fillna("").astype(str)
    result["artist"]      = df[artist_col].fillna("").astype(str) if artist_col else ""
    result["album"]       = df[album_col].fillna("").astype(str)  if album_col  else ""
    result["duration_ms"] = pd.to_numeric(df[dur_col], errors="coerce") if dur_col else None
    return result


def fmt_ms(ms) -> str:
    try:
        ms = int(ms)
        s  = ms // 1000
        return f"{s // 60}:{s % 60:02d}"
    except Exception:
        return "--"


def ytdlp_download(title: str, artist: str) -> tuple[bytes, str] | None:
    """
    Search YouTube Music for 'Artist - Title' and download best quality MP3.
    Falls back to regular YouTube search if YouTube Music returns nothing.
    """
    queries = []
    if artist:
        queries.append(f"ytmsearch1:{artist} - {title}")
        queries.append(f"ytsearch1:{artist} - {title}")
    else:
        queries.append(f"ytmsearch1:{title}")
        queries.append(f"ytsearch1:{title}")

    with tempfile.TemporaryDirectory() as tmpdir:
        for query in queries:
            out_tmpl = str(Path(tmpdir) / "%(title)s.%(ext)s")
            cmd = [
                "yt-dlp",
                query,
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--output", out_tmpl,
                "--no-playlist",
                "--quiet",
                "--no-warnings",
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue

            mp3_files = glob.glob(f"{tmpdir}/*.mp3")
            if mp3_files:
                fpath = mp3_files[0]
                with open(fpath, "rb") as f:
                    return f.read(), Path(fpath).name

    return None


# -----------------------------------------------------------------------------
# Page config & CSS
# -----------------------------------------------------------------------------

st.set_page_config(page_title="SP->MP3", page_icon="🎵", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: #0a0a0a;
    color: #e0d8cc;
  }

  h1, h2 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 2px; }

  .hero {
    border-left: 4px solid #c8a84b;
    padding: .6rem 0 .6rem 1.2rem;
    margin-bottom: 2rem;
  }
  .hero h1 { font-size: 3rem; color: #f5f0e8; margin: 0; line-height: 1; }
  .hero p  { font-family: 'IBM Plex Mono', monospace; font-size: .75rem;
              color: #6b6355; margin: .3rem 0 0; letter-spacing: 1px; }

  .track-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: .5rem;
    display: flex; align-items: center; gap: 1rem;
  }
  .track-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .7rem; color: #444; min-width: 2rem; text-align: right;
  }
  .track-info { flex: 1; min-width: 0; }
  .track-title {
    font-weight: 500; font-size: .95rem; color: #f0ebe2;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .track-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .7rem; color: #5a5248; margin-top: .15rem;
  }
  .track-dur {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .75rem; color: #3d3830;
  }

  .selected-panel {
    background: linear-gradient(135deg, #151208 0%, #1a140a 100%);
    border: 1px solid #c8a84b44;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1.5rem 0;
  }
  .selected-panel .s-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem; color: #c8a84b; letter-spacing: 1px; line-height: 1.1;
  }
  .selected-panel .s-artist {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .8rem; color: #8a7e6e; margin-top: .3rem;
  }
  .selected-panel .s-query {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .65rem; color: #3a3530; margin-top: .5rem;
  }

  .install-box {
    background: #1a0f0f; border: 1px solid #5a2020;
    border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0;
  }

  .stTextInput input {
    background: #111 !important; border-color: #333 !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: .85rem;
  }
  .stButton button[kind="primary"] {
    background: #c8a84b !important; color: #0a0a0a !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important; letter-spacing: 2px !important;
    border: none !important; border-radius: 4px !important;
    padding: .5rem 2rem !important;
  }
  .stButton button[kind="primary"]:hover { background: #d4b862 !important; }

  .footnote { color: #2e2a25; font-family: 'IBM Plex Mono', monospace;
               font-size: .65rem; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------

st.markdown("""
<div class="hero">
  <h1>SP -> MP3</h1>
  <p>SPOTIFY PLAYLIST DOWNLOADER  &middot;  POWERED BY YT-DLP</p>
</div>
""", unsafe_allow_html=True)

if not YTDLP_AVAILABLE:
    st.markdown("""
<div class="install-box">
  <strong>yt-dlp not found.</strong> Install it first, then restart the app.<br><br>
  <code>pip install yt-dlp</code>
</div>
""", unsafe_allow_html=True)
    st.stop()

if not FFMPEG_AVAILABLE:
    st.markdown("""
<div class="install-box">
  <strong>FFmpeg not found.</strong> yt-dlp needs FFmpeg to convert audio to MP3.<br><br>
  <code>winget install ffmpeg</code> &nbsp; (Windows)<br>
  <code>brew install ffmpeg</code> &nbsp;&nbsp;&nbsp;&nbsp; (Mac)<br>
  <code>sudo apt install ffmpeg</code> &nbsp; (Linux)
</div>
""", unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# Upload
# -----------------------------------------------------------------------------

uploaded = st.file_uploader(
    "Drop your Exportify CSV here",
    type=["csv"],
    label_visibility="collapsed",
)
st.caption("Export your playlist at [exportify.net](https://exportify.net) -> .csv")

if uploaded is not None:
    st.session_state["csv_bytes"] = uploaded.read()

if "csv_bytes" not in st.session_state:
    st.stop()

df = parse_exportify_csv(st.session_state["csv_bytes"])

if df.empty:
    st.error("Could not parse the CSV. Make sure it is an Exportify export.")
    st.stop()

# -----------------------------------------------------------------------------
# Two-column layout: track list left, selection + download right
# -----------------------------------------------------------------------------

col_list, col_dl = st.columns([3, 2], gap="large")

with col_list:
    st.markdown(f"**{len(df)} tracks** &mdash; search or scroll to pick one.")
    search = st.text_input("Filter", placeholder="Filter by title or artist...", label_visibility="collapsed")

    mask = pd.Series([True] * len(df))
    if search.strip():
        q = search.strip().lower()
        mask = (df["title"].str.lower().str.contains(q, na=False) |
                df["artist"].str.lower().str.contains(q, na=False))

    filtered = df[mask].reset_index(drop=True)

    if filtered.empty:
        st.info("No tracks match your search.")
        st.stop()

    # Styled cards (cap at 300 to keep DOM fast)
    preview = filtered.head(300)
    cards_html = ""
    for i, row in preview.iterrows():
        dur    = fmt_ms(row["duration_ms"]) if pd.notna(row.get("duration_ms")) else "--"
        title  = str(row["title"]).replace("<", "&lt;").replace(">", "&gt;")
        artist = str(row["artist"]).replace("<", "&lt;").replace(">", "&gt;")
        album  = str(row["album"]).replace("<", "&lt;").replace(">", "&gt;") if row["album"] else ""
        meta   = artist + ("  &middot;  " + album if album else "")
        cards_html += f"""
        <div class="track-card">
          <div class="track-num">{i+1:02d}</div>
          <div class="track-info">
            <div class="track-title">{title}</div>
            <div class="track-meta">{meta}</div>
          </div>
          <div class="track-dur">{dur}</div>
        </div>"""

    if len(filtered) > 300:
        cards_html += f'<div class="track-meta" style="padding:.5rem 0 0;color:#444">{len(filtered)-300} more tracks &mdash; refine your search to see them</div>'

    st.markdown(cards_html, unsafe_allow_html=True)

with col_dl:
    st.markdown("**Select a track**")

    labels = [
        f"{row['title']}  -  {row['artist']}" if row["artist"] else row["title"]
        for _, row in filtered.iterrows()
    ]

    chosen_label = st.selectbox("Track", labels, label_visibility="collapsed")
    chosen_idx   = labels.index(chosen_label)
    chosen_row   = filtered.iloc[chosen_idx]

    title  = chosen_row["title"]
    artist = chosen_row["artist"]
    album  = chosen_row["album"] if chosen_row["album"] else ""
    dur    = fmt_ms(chosen_row["duration_ms"]) if pd.notna(chosen_row.get("duration_ms")) else "--"
    search_query = f"{artist} - {title}" if artist else title

    st.markdown(f"""
<div class="selected-panel">
  <div class="s-title">{title}</div>
  <div class="s-artist">{artist}{"  &middot;  " + album if album else ""}
    <span style="color:#4a4440;margin-left:1rem">{dur}</span>
  </div>
  <div class="s-query">YouTube Music search: {search_query}</div>
</div>
""", unsafe_allow_html=True)

    if st.button("DOWNLOAD MP3", type="primary"):
        with st.spinner(f"Searching YouTube Music for '{title}'... (~30-60 s)"):
            result = ytdlp_download(title, artist)

        if result:
            mp3_bytes, filename = result
            st.success(f"Ready: {filename}")
            st.download_button(
                label="SAVE FILE",
                data=mp3_bytes,
                file_name=filename,
                mime="audio/mpeg",
                type="primary",
            )
        else:
            st.error(
                "Download failed. yt-dlp could not find or fetch this track. "
                "Try checking your internet connection or whether the video is available in your region."
            )

st.markdown('<p class="footnote">yt-dlp sources audio from YouTube Music then YouTube. For personal use only.</p>', unsafe_allow_html=True)