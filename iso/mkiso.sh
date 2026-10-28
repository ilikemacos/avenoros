#!/bin/bash
set -euo pipefail

version=$(sed -n 's/^ImageVersion=//p' mkosi.conf)
out=${OUT:-mkosi.output}
iso=${ISO:-$out/avenoros-$version-x86_64.iso}
key=${KEY:-mkosi.key}
crt=${CRT:-mkosi.crt}
raw=$out/avenoros_$version.raw

work=$(mktemp -d)
mnt=$work/usr
cleanup() {
	mountpoint -q "$mnt" && umount "$mnt"
	rm -rf "$work"
}
trap cleanup EXIT

part() {
	sfdisk -J "$raw" | jq -r --arg t "$1" '.partitiontable.partitions[] | select(.type == $t) | "\(.start) \(.size) \(.uuid)"'
}

read -r usr_start usr_size usr_uuid < <(part 8484680C-9521-48C6-9C11-B0720656F69E)
read -r ver_start ver_size ver_uuid < <(part 77FF5F63-E7B6-4633-ACF4-1565B864C0E6)
read -r sig_start sig_size sig_uuid < <(part E7BB33FB-06CF-4E81-8273-E543B413E2E2)
read -r root_start root_size root_uuid < <(part 4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709)

for p in usr:$usr_start:$usr_size ver:$ver_start:$ver_size sig:$sig_start:$sig_size root:$root_start:$root_size; do
	IFS=: read -r name start size <<< "$p"
	dd if="$raw" of="$work/$name.img" bs=512 skip="$start" count="$size" conv=sparse status=none
done

uki=$out/avenoros_$version.efi
for s in linux initrd osrel cmdline; do
	objcopy -O binary --only-section=".$s" "$uki" "$work/$s"
done
hash=$(grep -ao 'usrhash=[0-9a-f]*' "$work/cmdline")

mkdir "$mnt"
mount -o ro "$work/usr.img" "$mnt"
kver=$(ls "$mnt/lib/modules")
tree=$work/tree
cp -a iso/initrd "$tree"
src=$mnt/lib/modules/$kver
mods=$tree/usr/lib/modules/$kver
for m in sr_mod ata_piix ata_generic pata_acpi; do
	modprobe -d "$mnt" -S "$kver" --show-depends "$m" | awk '$1 == "insmod" { print $2 }'
done | sort -u | while read -r ko; do
	rel=${ko#"$src"/}
	mkdir -p "$mods/$(dirname "$rel")"
	cp "$ko" "$mods/$rel"
done
cp "$src"/modules.* "$mods/"
umount "$mnt"
(cd "$tree" && find . -mindepth 1 | sed 's|^\./||' | LC_ALL=C sort | cpio -o -H newc -R 0:0 --quiet) > "$work/live.cpio"

lower() { tr '[:upper:]' '[:lower:]' <<< "$1"; }
cmdline="$hash systemd.verity_usr_data=PARTUUID=$(lower "$usr_uuid") systemd.verity_usr_hash=PARTUUID=$(lower "$ver_uuid")"
cmdline+=" mount.usr=/dev/mapper/usr mount.usrfstype=erofs mount.usrflags=ro"
cmdline+=" root=PARTUUID=$(lower "$root_uuid") rootfstype=btrfs rootflags=ro ro"
cmdline+=" systemd.mask=systemd-repart.service systemd.mask=systemd-boot-random-seed.service console=ttyS0 quiet loglevel=3"

ukify build \
	--linux="$work/linux" \
	--initrd="$work/initrd" \
	--initrd="$work/live.cpio" \
	--os-release="@$work/osrel" \
	--cmdline="$cmdline" \
	--secureboot-private-key="$key" \
	--secureboot-certificate="$crt" \
	--output="$work/live.efi"

esp_mb=$(( $(stat -c %s "$work/live.efi") / 1048576 + 16 ))
mkdir "$work/iso"
truncate -s "${esp_mb}M" "$work/iso/esp.img"
mkfs.vfat -n AVENOR "$work/iso/esp.img" >/dev/null
mmd -i "$work/iso/esp.img" ::/EFI ::/EFI/BOOT
mcopy -i "$work/iso/esp.img" "$work/live.efi" ::/EFI/BOOT/BOOTX64.EFI

cp "$work/osrel" "$work/iso/os-release"

rm -f "$iso"
xorriso -as mkisofs \
	-iso-level 3 -R -J -V "AVENOROS_${version//./_}" \
	-appended_part_as_gpt \
	-append_partition 1 8484680C-9521-48C6-9C11-B0720656F69E "$work/usr.img" \
	-append_partition 2 77FF5F63-E7B6-4633-ACF4-1565B864C0E6 "$work/ver.img" \
	-append_partition 3 E7BB33FB-06CF-4E81-8273-E543B413E2E2 "$work/sig.img" \
	-append_partition 4 4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709 "$work/root.img" \
	-e esp.img -no-emul-boot -boot-load-size 1 -efi-boot-part --efi-boot-image \
	-o "$iso" "$work/iso"

slot() {
	sfdisk -J "$iso" | jq -r --arg t "$1" '.partitiontable.partitions[] | select(.type == $t) | .node' | grep -o '[0-9]*$'
}

for p in C12A7328-F81F-11D2-BA4B-00A0C93EC93B:esp: \
	8484680C-9521-48C6-9C11-B0720656F69E:avenoros_$version:$usr_uuid \
	77FF5F63-E7B6-4633-ACF4-1565B864C0E6:avenoros_$version:$ver_uuid \
	E7BB33FB-06CF-4E81-8273-E543B413E2E2:avenoros_$version:$sig_uuid \
	4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709:root-x86-64:$root_uuid; do
	IFS=: read -r type label uuid <<< "$p"
	n=$(slot "$type")
	sfdisk -q --part-label "$iso" "$n" "$label"
	[[ -z $uuid ]] || sfdisk -q --part-uuid "$iso" "$n" "$uuid"
done

sha256sum "$iso"
