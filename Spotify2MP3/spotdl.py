"""
Spotify -> MP3 Downloader
Upload your Exportify CSV, pick a track, download as MP3 via yt-dlp.
"""

import streamlit as st
import pandas as pd
import io
import json
import re
import glob
import shutil
import subprocess
import tempfile
from pathlib import Path
import zipfile

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

YTDLP_AVAILABLE  = shutil.which("yt-dlp")  is not None
FFMPEG_AVAILABLE = shutil.which("ffmpeg")  is not None

def build_zip(downloads: dict) -> bytes:
    """
    Build an in-memory ZIP file from the downloaded MP3s.
    downloads = { label: (mp3_bytes, filename), ... }
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for lbl, (mp3_bytes, filename) in downloads.items():
            z.writestr(filename, mp3_bytes)
    return buf.getvalue()


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


def fetch_playlist_from_url(url: str) -> pd.DataFrame:
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--flat-playlist",
        "--no-warnings",
        url
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
        data = json.loads(proc.stdout)
        rows = []
        for entry in data.get("entries", []):
            rows.append({
                "title": entry.get("title", "Unknown"),
                "artist": entry.get("uploader", "Unknown"),
                "album": "",
                "duration_ms": (entry.get("duration") * 1000) if entry.get("duration") else None
            })
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error fetching playlist metadata: {e}")
        return pd.DataFrame()


def fmt_ms(ms) -> str:
    try:
        ms = int(ms)
        s  = ms // 1000
        return f"{s // 60}:{s % 60:02d}"
    except Exception:
        return "--"


def ytdlp_download(title: str, artist: str, album: str):
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

                # Reliable metadata injection
                "--add-metadata",
                "--parse-metadata", f"title:{title}",
                "--parse-metadata", f"artist:{artist}",
                "--parse-metadata", f"album:{album}",

                "--output", out_tmpl,
                "--no-playlist",
                "--quiet",
                "--no-warnings",
            ]

            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=True)
            except Exception:
                continue

            mp3_files = glob.glob(f"{tmpdir}/*.mp3")
            if mp3_files:
                fpath = mp3_files[0]
                with open(fpath, "rb") as f:
                    return f.read(), Path(fpath).name

    return None

# ---------------------------------------------------------------------
# Page config & CSS
# ---------------------------------------------------------------------

st.set_page_config(page_title="SP->MP3", page_icon="🎵", layout="wide")

st.markdown("""
<style>
  /* your CSS unchanged */
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.markdown("""
<div class="hero">
  <h1>SP -> MP3</h1>
  <p>SPOTIFY PLAYLIST DOWNLOADER  ·  POWERED BY YT-DLP</p>
</div>
""", unsafe_allow_html=True)

if not YTDLP_AVAILABLE:
    st.error("yt-dlp not found. Install it first.")
    st.stop()

if not FFMPEG_AVAILABLE:
    st.error("FFmpeg not found. Install it first.")
    st.stop()

# ---------------------------------------------------------------------
# Upload / URL Tabs
# ---------------------------------------------------------------------

tab_csv, tab_url = st.tabs(["📁 Upload Exportify CSV", "🔗 Paste Spotify Link"])

with tab_csv:
    uploaded = st.file_uploader("Drop your Exportify CSV here", type=["csv"], label_visibility="collapsed")
    st.caption("Export your playlist at exportify.net → .csv")
    if uploaded:
        st.session_state["df"] = parse_exportify_csv(uploaded.read())

with tab_url:
    url_input = st.text_input("Spotify Playlist URL", placeholder="https://open.spotify.com/playlist/...")
    if url_input and st.button("Fetch Playlist Tracks"):
        with st.spinner("Fetching metadata..."):
            st.session_state["df"] = fetch_playlist_from_url(url_input)

if "df" not in st.session_state:
    st.stop()

df = st.session_state["df"]

if df.empty:
    st.error("Could not parse playlist.")
    st.stop()

# ---------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------

col_list, col_dl = st.columns([3, 2], gap="large")

# ---------------- LEFT COLUMN ----------------
with col_list:
    st.markdown(f"**{len(df)} tracks** — search or scroll to pick one.")
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

    preview = filtered.head(100)
    for i, row in preview.iterrows():
        dur    = fmt_ms(row["duration_ms"]) if pd.notna(row.get("duration_ms")) else "--"
        title  = str(row["title"])
        artist = str(row["artist"])
        album  = str(row["album"])

        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"""
            <div class="track-card" style="margin-bottom:0">
              <div class="track-num">{i+1:02d}</div>
              <div class="track-info">
                <div class="track-title">{title}</div>
                <div class="track-meta">{artist} · {album}</div>
              </div>
              <div class="track-dur">{dur}</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown('<div style="padding-top:12px"></div>', unsafe_allow_html=True)
            if st.button("⬇️", key=f"qdl_{i}", help=f"Quick download {row['title']}", use_container_width=True):
                with st.spinner("Downloading..."):
                    result = ytdlp_download(row["title"], row["artist"], row["album"])
                    if result:
                        mp3_bytes, filename = result
                        st.download_button("SAVE", mp3_bytes, filename, "audio/mpeg", key=f"qs_{i}")

    if len(filtered) > 100:
        st.markdown(
            f'<div class="track-meta" style="padding:.5rem 0 0;color:#444">'
            f'{len(filtered)-100} more tracks — refine your search to see them</div>',
            unsafe_allow_html=True
        )

# ---------------- RIGHT COLUMN ----------------
with col_dl:
    st.markdown("**Select tracks to download**")

    labels = [
        f"{row['title']}  -  {row['artist']}" if row["artist"] else row["title"]
        for _, row in filtered.iterrows()
    ]

    sel_col, clr_col = st.columns([1, 1])
    with sel_col:
        if st.button("Select all filtered", use_container_width=True):
            st.session_state["selected_labels"] = labels
    with clr_col:
        if st.button("Clear selection", use_container_width=True):
            st.session_state["selected_labels"] = []
            st.session_state.pop("downloads", None)

    chosen_labels = st.multiselect(
        "Tracks",
        options=labels,
        default=st.session_state.get("selected_labels", []),
        label_visibility="collapsed",
        placeholder="Pick one or more tracks...",
    )
    st.session_state["selected_labels"] = chosen_labels

    n = len(chosen_labels)
    if n == 0:
        st.stop()

    btn_label = f"DOWNLOAD {n} TRACKS" if n > 1 else "DOWNLOAD MP3"

    if st.button(btn_label, type="primary"):
        st.session_state["downloads"] = {}

        progress_bar = st.progress(0)
        status_text  = st.empty()

        for i, lbl in enumerate(chosen_labels):
            idx = labels.index(lbl)
            row = filtered.iloc[idx]

            status_text.markdown(
                f'<div class="track-meta" style="color:#c8a84b;font-size:.8rem">'
                f'Downloading {i+1}/{n}: {row["title"]}</div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress(i / n)

            result = ytdlp_download(row["title"], row["artist"], row["album"])
            if result:
                mp3_bytes, filename = result
                st.session_state["downloads"][lbl] = (mp3_bytes, filename)
            else:
                st.session_state["downloads"][lbl] = None

        progress_bar.progress(1.0)
        status_text.empty()

    downloads = st.session_state.get("downloads", {})
    if downloads:
        st.markdown("---")
        succeeded = [(lbl, v) for lbl, v in downloads.items() if v is not None]
        failed    = [lbl for lbl, v in downloads.items() if v is None]
        # SAVE ALL button
        if succeeded:
            zip_bytes = build_zip({lbl: v for lbl, v in succeeded})
            st.download_button(
                label="💾 SAVE ALL AS ZIP",
                data=zip_bytes,
                file_name="playlist_downloads.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )

        if succeeded:
            st.markdown(f"**{len(succeeded)} ready** — save individually below:")
            for lbl, (mp3_bytes, filename) in succeeded:
                row_l, row_r = st.columns([3, 2])
                with row_l:
                    lbl_safe = lbl.replace("<", "&lt;").replace(">", "&gt;")
                    st.markdown(
                        f'<div class="track-card" style="padding:.5rem 1rem;margin:0">'
                        f'<div class="track-title" style="font-size:.82rem">{lbl_safe}</div></div>',
                        unsafe_allow_html=True,
                    )
                with row_r:
                    st.download_button(
                        label="SAVE MP3",
                        data=mp3_bytes,
                        file_name=filename,
                        mime="audio/mpeg",
                        key=f"dl_{filename}",
                    )

        if failed:
            st.warning("Could not download:\n" + "\n".join(f"- {t}" for t in failed))

st.markdown('<p class="footnote">yt-dlp sources audio from YouTube Music then YouTube. For personal use only.</p>', unsafe_allow_html=True)
