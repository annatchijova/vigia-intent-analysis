#!/usr/bin/env python3
"""Assemble the VIGÍA demo video from image slides and video clips using ffmpeg."""

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

DEMO_DIR = Path("~/Desktop/vigia_demo_readme").expanduser()
LAMINAS = DEMO_DIR / "laminas_logo"
VIDEOS = DEMO_DIR / "videos"
OUTPUT = DEMO_DIR / "vigia_demo_final.mp4"
TEMP = DEMO_DIR / "tmp_clips"

SCALE_VF = (
    "scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1"
)

# (type, source_relative_to_DEMO_DIR, start, end, duration)
SEGMENTS = [
    ("IMAGE", "laminas_logo/logo.png",               None, None, 3),
    ("IMAGE", "laminas_logo/0.png",                   None, None, 2),
    ("IMAGE", "laminas_logo/1.png",                   None, None, 3),
    ("IMAGE", "laminas_logo/2.png",                   None, None, 3),
    ("IMAGE", "videos/caso31.png",                    None, None, 2),
    ("VIDEO", "videos/2.mkv",                         5,    14,   None),
    ("IMAGE", "laminas_logo/3.png",                   None, None, 2),
    ("IMAGE", "laminas_logo/4.png",                   None, None, 3),
    ("IMAGE", "videos/caso38.png",                    None, None, 2),
    ("VIDEO", "videos/3.mkv",                         15,   21,   None),
    ("IMAGE", "laminas_logo/5.png",                   None, None, 2),
    ("IMAGE", "laminas_logo/6.png",                   None, None, 3),
    ("IMAGE", "videos/caso18.png",                    None, None, 2),
    ("VIDEO", "videos/4.mkv",                         24,   32,   None),
    ("IMAGE", "laminas_logo/7.png",                   None, None, 2),
    ("IMAGE", "laminas_logo/8.png",                   None, None, 3),
    ("IMAGE", "videos/casoreal7.png",                None, None, 2),
    ("VIDEO", "videos/5.mkv",                         6,    12,   None),
    ("IMAGE", "laminas_logo/9.png",                   None, None, 2),
    ("IMAGE", "laminas_logo/10.png",                  None, None, 3),
    ("IMAGE", "laminas_logo/11.png",                  None, None, 3),
    ("IMAGE", "videos/casorealsrl.png",               None, None, 2),
    ("VIDEO", "videos/6.mkv",                         3,    9,    None),
    ("VIDEO", "videos/7.mkv",                         25,   35,   None),
    ("VIDEO", "videos/8.mkv",                         5,    15,   None),
    ("VIDEO", "videos/8.mkv",                         63,   67,   None),
    ("IMAGE", "videos/selfcorection.png",             None, None, 2),
    ("IMAGE", "videos/selfcorectionresaltado.png",    None, None, 4),
    ("VIDEO", "videos/8.mkv",                         136,  153,  None),
    ("VIDEO", "videos/8.mkv",                         579,  603,  None),
    ("VIDEO", "videos/10.mkv",                        3,    6,    None),
    ("IMAGE", "laminas_logo/12.png",                  None, None, 3),
    ("IMAGE", "laminas_logo/13.png",                  None, None, 3),
    ("IMAGE", "laminas_logo/14.png",                  None, None, 3),
    ("VIDEO", "videos/11.mkv",                        2,    22,   None),
    ("VIDEO", "videos/1.mkv",                         2,    16,   None),
    ("IMAGE", "laminas_logo/15.png",                  None, None, 5),
    ("IMAGE", "laminas_logo/logo.png",                None, None, 3),
]


def run_ffmpeg(cmd: list[str]) -> None:
    """Run an ffmpeg command, exiting on failure."""
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: ffmpeg command failed:\n  {' '.join(cmd)}", file=sys.stderr)
        if e.stderr:
            print(e.stderr[-2000:], file=sys.stderr)
        sys.exit(1)


def generate_clip(idx: int, seg: tuple, out_path: Path) -> None:
    """Generate a single clip from an image or video segment."""
    kind, source_rel, start, end, duration = seg
    source = DEMO_DIR / source_rel

    if not source.exists():
        print(f"  ERROR: source not found: {source}", file=sys.stderr)
        sys.exit(1)

    if kind == "IMAGE":
        cmd = [
            "ffmpeg", "-y", "-loop", "1",
            "-i", str(source),
            "-t", str(duration),
            "-vf", SCALE_VF,
            "-r", "25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", str(source),
            "-vf", SCALE_VF,
            "-r", "25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            str(out_path),
        ]

    run_ffmpeg(cmd)


def get_duration(path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def sha256(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build VIGÍA demo video")
    parser.add_argument("--clean", action="store_true", help="Delete tmp_clips and start fresh")
    parser.add_argument("--from-clip", type=int, default=0, metavar="N",
                        help="Resume from clip N (skip earlier clips)")
    args = parser.parse_args()

    if args.clean and TEMP.exists():
        print(f"Cleaning {TEMP}")
        shutil.rmtree(TEMP)

    TEMP.mkdir(parents=True, exist_ok=True)

    total = len(SEGMENTS)

    # Step 1: Generate clips
    print(f"=== Step 1: Generating {total} clips ===")
    for idx, seg in enumerate(SEGMENTS):
        clip_path = TEMP / f"clip_{idx:02d}.mp4"
        source_rel = seg[1]

        if idx < args.from_clip:
            print(f"  Skipping clip {idx:02d}/{total - 1} (--from-clip {args.from_clip})")
            continue

        if clip_path.exists():
            print(f"  Clip {idx:02d}/{total - 1} exists, skipping: {source_rel}")
            continue

        print(f"  Generating clip {idx:02d}/{total - 1}: {source_rel}")
        generate_clip(idx, seg, clip_path)

    # Step 2: Concat list
    print("\n=== Step 2: Writing concat list ===")
    concat_list = TEMP / "concat_list.txt"
    with open(concat_list, "w") as f:
        for idx in range(total):
            f.write(f"file 'clip_{idx:02d}.mp4'\n")
    print(f"  Written: {concat_list}")

    # Step 3: Concatenate video (no audio)
    print("\n=== Step 3: Concatenating clips (video only) ===")
    video_only = TEMP / "video_only.mp4"
    run_ffmpeg([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(video_only),
    ])
    print(f"  Created: {video_only}")

    # Step 4: Add background music
    print("\n=== Step 4: Mixing background audio ===")
    music_source = VIDEOS / "vigia.mpeg"
    if not music_source.exists():
        print(f"  ERROR: music file not found: {music_source}", file=sys.stderr)
        sys.exit(1)

    total_duration = get_duration(video_only)
    fade_start = max(0, total_duration - 3)

    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_only),
        "-stream_loop", "-1",
        "-i", str(music_source),
        "-filter_complex",
        f"[1:a]afade=t=out:st={fade_start}:d=3[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(OUTPUT),
    ])
    print(f"  Created: {OUTPUT}")

    # Step 5: Summary
    print("\n=== Final Summary ===")
    print(f"  Duration : {total_duration:.1f} seconds")
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"  File size: {size_mb:.1f} MB")
    print(f"  SHA-256  : {sha256(OUTPUT)}")
    print(f"  Output   : {OUTPUT}")


if __name__ == "__main__":
    main()
