# AvenorOS

Private, light, gaming-ready Linux for laptops. Image-based, built from Arch
packages pinned to a dated Arch Linux Archive snapshot.

## Layout

- `mkosi.conf`, `mkosi.repart/` build a UEFI x86-64 disk: ESP with a signed UKI
  and systemd-boot, `/usr` as erofs with dm-verity and a signed root hash, and a
  btrfs root with `/home` and `/var` subvolumes.
- `mkosi.extra/usr/lib/repart.d/` adds the empty B slots on first boot.
- `mkosi.extra/usr/lib/sysupdate.d/` pulls `avenoros_<ver>` artifact sets
  (UKI, usr, usr-verity, usr-verity-sig) into the inactive slot.
- `avenor-apply` verifies the new root hash signature, stages the new `/usr`
  under `/run/nextroot` and runs `systemctl soft-reboot` when the kernel is
  unchanged. A kernel change waits for consent (`avenor-apply --reboot`).
- New UKIs boot with three tries. `avenor-health` gates `boot-complete.target`,
  so a failing version falls back to the previous one.
- Plasma 6 is trimmed: Baloo, KDE Connect, Discover notifier and a few helpers
  are off. The `org.avenor.batterypill` applet draws the battery as a white
  pill with the percentage inside.

## Build

    mkosi genkey
    sudo mkosi -f build
    sudo ./ci/boot-test.sh

`ci/boot-test.sh` boots the image under QEMU and OVMF and fails when idle RAM,
boot time or image size go over budget (500 MB, 15 s, 2560 MB by default).
Set `ACCEL=tcg CPU=max` on hosts without working KVM.

## Status

Phase 0. Full-disk encryption is not wired yet: the root partition is plain
btrfs. The update server URL is a placeholder.

## License

GPL-3.0-or-later.
