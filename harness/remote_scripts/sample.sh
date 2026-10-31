#!/usr/bin/env bash
# Usage: sample.sh <out.csv> <interval_s>
# Appends one resource/thermal row per interval until killed. Bash builtins only
# in the loop (no subprocess per field); missing sources become empty fields.
set -u

if [ "$#" -ne 2 ]; then
    echo "usage: $0 <out.csv> <interval_s>" >&2
    exit 2
fi
out=$1 interval=$2

drm=/sys/class/drm/card0/device
k10="" amd=""
# hwmon numbering is not stable: find devices by name.
for h in /sys/class/hwmon/hwmon*; do
    [ -r "$h/name" ] || continue
    read -r name < "$h/name"
    case $name in
        k10temp) k10=$h ;;
        amdgpu) amd=$h ;;
    esac
done

# temp <var> <hwmon dir>: set var to temp1 in degrees (one decimal), else "".
temp() {
    local m
    printf -v "$1" ''
    [ -n "$2" ] && [ -r "$2/temp1_input" ] && read -r m < "$2/temp1_input" || return 0
    printf -v "$1" '%d.%d' $((m / 1000)) $((m % 1000 / 100))
}

# mib <var> <file>: set var to a byte-count sysfs file in MiB, else "".
mib() {
    local b
    printf -v "$1" ''
    [ -r "$2" ] && read -r b < "$2" || return 0
    printf -v "$1" '%d' $((b / 1048576))
}

echo "ts,mem_used_mib,vram_used_mib,gtt_used_mib,tctl_c,edge_c,sclk_mhz,cpu_mhz_avg" > "$out"

while :; do
    ts=$EPOCHSECONDS
    total="" avail="" mem=""
    while read -r key val _; do
        case $key in
            MemTotal:) total=$val ;;
            MemAvailable:) avail=$val; break ;;
        esac
    done < /proc/meminfo
    [ -n "$total" ] && [ -n "$avail" ] && mem=$(((total - avail) / 1024))

    sclk=""
    if [ -r "$drm/pp_dpm_sclk" ]; then
        while read -r _ f star; do
            if [ "$star" = "*" ]; then sclk=${f%[Mm][Hh][Zz]}; break; fi
        done < "$drm/pp_dpm_sclk"
    fi

    sum=0 n=0
    while IFS= read -r line; do
        case $line in
            "cpu MHz"*) v=${line##*: }; sum=$((sum + ${v%.*})); n=$((n + 1)) ;;
        esac
    done < /proc/cpuinfo
    cpu=""
    [ "$n" -gt 0 ] && cpu=$((sum / n))

    mib vram "$drm/mem_info_vram_used"
    mib gtt "$drm/mem_info_gtt_used"
    temp tctl "$k10"
    temp edge "$amd"
    echo "$ts,$mem,$vram,$gtt,$tctl,$edge,$sclk,$cpu" >> "$out"
    sleep "$interval"
done
