#!/bin/bash
set -euo pipefail

out=${OUT:-mkosi.output}
image=$(readlink -f "$out/avenoros_$(sed -n 's/^ImageVersion=//p' mkosi.conf).raw")
ram_budget=${RAM_BUDGET_MB:-500}
boot_budget=${BOOT_BUDGET_S:-15}
size_budget=${SIZE_BUDGET_MB:-2560}
settle=${SETTLE_S:-90}
ovmf=${OVMF:-/usr/share/OVMF}

work=$(mktemp -d)
qga=$work/qga.sock
cleanup() {
	[[ -n ${qemu_pid:-} ]] && kill "$qemu_pid" 2>/dev/null || true
	rm -rf "$work"
}
trap cleanup EXIT

cp --sparse=always "$image" "$work/disk.raw"
truncate -s +4G "$work/disk.raw"
cp "$ovmf/OVMF_VARS_4M.fd" "$work/vars.fd"

qemu-system-x86_64 \
	-machine q35,accel="${ACCEL:-kvm}" -cpu "${CPU:-host}" -smp 4 -m 4G \
	-drive if=pflash,format=raw,readonly=on,file="$ovmf/OVMF_CODE_4M.fd" \
	-drive if=pflash,format=raw,file="$work/vars.fd" \
	-drive if=virtio,format=raw,file="$work/disk.raw" \
	-device virtio-vga -display none \
	-nic user,model=virtio-net-pci \
	-chardev socket,id=qga,path="$qga",server=on,wait=off \
	-device virtio-serial -device virtserialport,chardev=qga,name=org.qemu.guest_agent.0 \
	-serial file:"${SERIAL_LOG:-$work/serial.log}" &
qemu_pid=$!

g() { python3 ci/qga.py "$qga" "${QGA_TIMEOUT:-300}" "$@"; }

g /usr/bin/systemctl is-system-running --wait >/dev/null || true
sleep "$settle"

boot=$(g /usr/bin/systemd-analyze)
used_kb=$(g /usr/bin/awk '/^MemTotal/ {t=$2} /^MemAvailable/ {a=$2} END {print t-a}' /proc/meminfo)
session=$(g /usr/bin/pgrep -c -x plasmashell || true)
ram=$((used_kb / 1024))
[[ $boot =~ =\ ((([0-9]+)min\ )?([0-9.]+)s) ]] && boot_s=$(awk -v m="${BASH_REMATCH[3]:-0}" -v s="${BASH_REMATCH[4]}" 'BEGIN { print m * 60 + s }')
size=$(( $(du -B1 "$image" | cut -f1) / 1048576 ))

echo "$boot" | head -n1
echo "plasmashell running: ${session:-0}"
printf 'idle ram  %5d MB  budget %d\n' "$ram" "$ram_budget"
printf 'boot      %5s s   budget %d\n' "$boot_s" "$boot_budget"
printf 'image     %5d MB  budget %d\n' "$size" "$size_budget"

fail=0
((ram <= ram_budget)) || fail=1
awk -v b="$boot_s" -v m="$boot_budget" 'BEGIN { exit !(b <= m) }' || fail=1
((size <= size_budget)) || fail=1
exit "$fail"
