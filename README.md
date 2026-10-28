# AvenorOS

Private, light Linux for laptops, built on Arch.

Website: https://avenor.chopstickshq.com
Download: [AvenorOS 1.0.0](https://github.com/ilikemacos/avenoros/releases/tag/v1.0.0)

## What it is

- Arch Linux packages, pinned to a dated Arch Linux Archive snapshot.
- KDE Plasma 6 with Avenor's own floating top bar and dock.
- No telemetry. Chromium ships with managed policies that turn its reporting
  off, and NetworkManager's connectivity check is disabled.
- Broad Wi-Fi, Ethernet and Bluetooth support: Intel, Realtek, MediaTek,
  Atheros, Broadcom (in-kernel drivers), Marvell and TI firmware, plus
  NetworkManager, bluez and the Plasma applets for both.
- An image-based system: `/usr` is a read-only erofs image checked by
  dm-verity, with A and B slots so updates land in the spare slot.

## Try it

1. Download `avenoros-1.0.0-x86_64.zip` from the
   [release page](https://github.com/ilikemacos/avenoros/releases/tag/v1.0.0).

2. Check the SHA-256. It should be:

       ee5bac793dfcec74b6b1a2007b8481d1425d48fe5b282eb81104d70ecae9470e

   Windows (PowerShell):

       Get-FileHash avenoros-1.0.0-x86_64.zip -Algorithm SHA256

   Windows (Command Prompt):

       certutil -hashfile avenoros-1.0.0-x86_64.zip SHA256

   macOS:

       shasum -a 256 avenoros-1.0.0-x86_64.zip

   Linux:

       sha256sum avenoros-1.0.0-x86_64.zip

3. Unzip it. You get one hybrid ISO, `avenoros-0.3.2-x86_64.iso` (about 4.5 GB).

4. Write the ISO to a USB stick. This erases the stick.
   - Rufus on Windows: pick the ISO, and choose DD Image mode when asked.
   - dd on Linux or macOS: `sudo dd if=avenoros-0.3.2-x86_64.iso of=/dev/sdX bs=4M status=progress oflag=sync`
     (replace `/dev/sdX` with the whole stick, not a partition).
   - balenaEtcher on any system.

5. Boot from the USB stick. You may need to pick it in your firmware's boot
   menu. In a VM (QEMU, VirtualBox, VMware), turn on UEFI and attach the ISO
   as a disc or as a USB drive.

AvenorOS runs live from the stick. Nothing is installed on your disk.


## Requirements

- A 64-bit x86 (x86_64) PC with UEFI boot. Legacy BIOS is not supported.
- A USB stick of 8 GB or more, since the ISO is about 4.5 GB.

  ## Tested Hardware:
  2021 ROG Zephryus G14
  -Ryzen 7 5800HS @ 2.8GHz
  -RTX 3060 Laptop GPU 6GB GDDR6 on a 192 bit bus (GA106) @ 1.38GHz
  -16GB DDR4 @ 3200MT/s
  -1TB M.2 NVme SSD PCIe 3.0
  -2560x1440 @ 120HZ 1600 Nits Peak prightness.
  ## Minimum Requirements
  -A 1ghz CPU with 2 cores or more (AMD Athlon K7 or faster)
-2GB of RAM DDR2-600 MHz
-20gb HDD for the OS and Updates (SATA SSD recommended)
-Any GPU faster than 800MHz
## Status and known limits

- Idle RAM is about 950 MB on a 2021 ROG Zephyrus G14. 
- Wi-Fi and Bluetooth have not been tested on real hardware.
- The Broadcom `wl` driver is not included, so some older Broadcom Wi-Fi cards
  will not work.
- The 1.0.0 release is the 0.3.2 build, so the version shown inside the
  image says 0.3.2.

## Gaming

In one test on an ASUS ROG G14 running BeamNG.drive at 1080p High on the Radeon integrated GPU, the 1% low was 27 fps on AvenorOS 1.1.0 gaming test 1, against 12 fps on Windows 11. That is one run on one machine, not a promise for every PC. See [bench/README.md](bench/README.md) to run the same test.

## Build from source

You need an Arch-based host with `mkosi`, plus `xorriso`, `mtools`,
`dosfstools`, `jq`, `cpio`, `binutils` and `systemd-ukify` for the ISO.

    mkosi genkey
    sudo mkosi -f build
    sudo ./iso/mkiso.sh

`mkosi genkey` makes the Secure Boot key and certificate (`mkosi.key`,
`mkosi.crt`). The build writes the disk image and its split parts to
`mkosi.output/`. `iso/mkiso.sh` turns those into the hybrid ISO
`mkosi.output/avenoros-<version>-x86_64.iso` and prints its SHA-256.

To boot-test the disk image under QEMU and OVMF:

    sudo ./ci/boot-test.sh

It fails when idle RAM, boot time or image size go over budget. Set
`RAM_BUDGET_MB`, `BOOT_BUDGET_S` and `SIZE_BUDGET_MB` to change them, and
`ACCEL=tcg CPU=max` on hosts without KVM.

## Layout

- `mkosi.conf`, `mkosi.repart/`: the image, its packages and partitions.
- `mkosi.extra/`: files copied into the image, including the B-slot
  partitions, sysupdate config and the Avenor theme.
- `iso/`: the live ISO script and its extra initrd files.
- `ci/`: the QEMU boot test.
- `tools/`: theme helpers.

## Contributing

Issues and pull requests are welcome. Keep changes small, and say what you
tested and on which hardware.

## Contributors
- [@ilikemacos](https://github.com/ilikemacos)
- [@duck-cl1](https://github.com/duck-cl1)
- [@mzxl-g](https://github.com/mzxl-g)
- [@forkie-gi](https://github.com/forkie-gi)
- [@chip-accident](https://github.com/chip-accident)
- [@b3st-b1y](https://github.com/b3st-b1y)


See [CONTRIBUTORS.md](CONTRIBUTORS.md).

## License

GPL-3.0. See [LICENSE](LICENSE).
