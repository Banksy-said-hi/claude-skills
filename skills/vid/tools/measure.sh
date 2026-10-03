#!/usr/bin/env bash
# In plain words: Measures a rendered film against the bar. Near-frozen moments (frame-to-frame change below a
# threshold, sampled at 10 fps), loudness (integrated, true peak, range), and any second where the sound drops
# below -30 LUFS (momentary), which is dead air unless it is the final fade.
# Usage: bash measure.sh film.mp4 [freeze-threshold=0.35]    (needs ffmpeg)
set -euo pipefail
f="$1"; th="${2:-0.35}"
echo "== near-frozen samples (time in s) =="
ffmpeg -hide_banner -i "$f" -vf "fps=10,scale=320:-1,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG" -an -f null - 2>&1 \
  | grep -o "YAVG=[0-9.]*" | awk -F= -v th="$th" '{t=NR/10; if($2<th){n++; printf "%.1f ", t}} END{printf "\nnear-frozen: %d samples (~%.1fs)\n", n, n/10}'
echo "== loudness =="
ffmpeg -hide_banner -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|LRA:|Peak:)" | tail -3
echo "== quiet moments (momentary < -30 LUFS) =="
ffmpeg -hide_banner -i "$f" -af ebur128 -f null - 2>&1 | grep -oE "t: *[0-9.]+ .*M: *-?[0-9.]+" \
  | awk '{match($0,/t: *[0-9.]+/);t=substr($0,RSTART+3,RLENGTH-3)+0;match($0,/M: *-?[0-9.]+/);m=substr($0,RSTART+3,RLENGTH-3)+0; if(m<-30){printf "%.1f:%.0f ",t,m; q++}} END{if(!q) printf "none"; printf "\n"}'
