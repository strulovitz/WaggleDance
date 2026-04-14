# Desktop Claude — KillerBee Phase 3 Disk Fix Briefing

**From:** Laptop Claude (after Nir caught the mistake)
**To:** Desktop Claude (KillerBee Phase 3 executor)
**Date:** 2026-04-14
**Priority:** READ THIS BEFORE YOU TOUCH ANYTHING ELSE ON KILLERBEE PHASE 3.
**Tone:** You and I are both Opus 4.6. This is a peer-to-peer correction, not a scolding. I made the same mistake in how I framed it to Nir earlier and I had to walk it back too. Read it carefully, do not skim, do not pattern-match past the details.

---

## 0. The one-sentence summary

**You built the 7 VMs as qcow2 backing-file overlays to save disk space on a 92 GB partition, but the physical disk is 2 TB. The overlay approach is solving a problem that does not exist, and it is the wrong architecture for Nir's use case. You need to throw away the overlays and rebuild the 7 VMs as independent full copies on the big volume.**

If you only remember one thing from this document: remember that. Then keep reading.

---

## 1. What you did (no blame, just facts)

Earlier today on Desktop (Linux Mint, mint-desktop) you executed KillerBee Phase 3 and did the following:

1. Autoinstalled a `desktop-template` Ubuntu VM via qemu-kvm + virt-manager.
2. Installed Ollama 0.20.7 CPU-only inside it, bound to `0.0.0.0:11434`.
3. Verified from the host: `curl http://10.0.0.9:11434/api/version` returned JSON.
4. Committed + pushed the template work (commit `1fd0dda`).
5. Inferred a host split: Desktop gets GiantQueen-B, DwarfQueen-B1, DwarfQueen-B2, Worker-B1..B4 (7 VMs, 44 GB RAM total).
6. Attempted to clone the 7 VMs by running `sudo cp` on `desktop-template.qcow2`.
7. That attempt filled the root filesystem (`/`) to 100 %, because the template qcow2 is almost certainly **sparse** — the `du` number was ~8.6 GB of real data but the *virtual* disk size is much larger, and naive `cp` without `--sparse=always` expands sparse files to their full allocated size. Five such expanded copies blew past the free space on `/`.
8. You recovered by truncating the stray qcow2 files with `sudo tee` (freed the disk — nothing was corrupted, this was a safe recovery).
9. Second attempt: you used `qemu-img create -b desktop-template.qcow2 -f qcow2 <clone>.qcow2` to create thin **backing-file overlays**, each ~200 KB. All 7 clones currently exist as overlays on top of the same template.
10. You booted `giantqueen-b`, set its hostname, regenerated its machine-id, and rebooted it.
11. You asked Nir whether to proceed autonomously with the remaining 6 VMs + model pulls.

Everything up through step 4 is fine. Steps 5–11 are where we start having problems.

---

## 2. What is actually wrong

### 2.1 The disk is not 92 GB. It is 2 TB.

The 92 GB number you saw was a **partition size**, specifically `/` — the root filesystem Ubuntu's installer carved out of the physical disk when Mint was installed. The rest of the 2 TB disk is on the same physical drive, just mounted elsewhere or in a separate volume. Almost certainly it is:

- mounted at `/home` (default Ubuntu/Mint behavior when a user chose "separate /home partition"), or
- an entirely separate partition or LVM volume that is mounted somewhere like `/mnt/data` or `/storage`, or
- unpartitioned free space at the end of the disk that was never claimed at install time.

**Run these commands to see what the real situation is:**

```bash
lsblk -f
df -h
sudo fdisk -l /dev/sda   # or whatever the main disk is; check lsblk output
sudo vgs                 # in case LVM is in use
sudo lvs                 # ditto
```

You are looking for: where the other ~1.9 TB lives, and whether it is already mounted somewhere writable.

### 2.2 libvirt stores VM images on the root filesystem by default

The default libvirt storage pool `default` lives at `/var/lib/libvirt/images/`, which is on `/`. That is why when you ran `sudo cp` to make 5 copies, they landed on the 92 GB partition and filled it. libvirt has no idea the big volume exists — you never told it. You squeezed seven Ubuntu VMs into a 92 GB closet while a 1.9 TB warehouse sat next door.

### 2.3 The qcow2 backing-file overlay approach is the wrong architecture for this use case

Backing-file overlays are a production-standard KVM pattern. I am not saying they are bad or broken. I am saying they are **wrong for what Nir is doing here**, for three reasons:

1. **The pattern exists to save disk when disk is scarce.** Nir has 2 TB. Disk is not scarce. The whole justification for overlays evaporates.
2. **Backing-file overlays add a small but real block-layer indirection on every uncached read** (VM → qcow2 driver → check overlay L2 table → miss → check backing file L2 table → physical read). On CPU-only VMs running LLM inference, where compute is already painful, every avoidable cycle matters. The overhead is small after page cache warms up, but it is nonzero, and the correct trade when disk is free is "pay disk, not CPU."
3. **The template file becomes load-bearing for every clone.** If anyone ever deletes, moves, renames, or — worst — *boots* the template qcow2 (which would modify it), **all 7 clones break simultaneously**. Full independent copies have no such coupling. Each VM is its own universe.

### 2.4 Nir's actual mental model

Nir thinks of each VM as a real, standalone Ubuntu system sitting in his living room doing real work. Not a clever filesystem optimization. When he said "I don't understand how accessing an actual disk that physically saves your status is worse than some diff mechanism," he was right. On his hardware, with his disk, the full-copy approach is strictly simpler, strictly faster, and strictly more robust. There is no trade-off in his favor here — the overlay approach is pure cost for zero benefit.

---

## 3. What the correct architecture looks like

- **One** libvirt storage pool, pointed at a directory on the big 2 TB volume (e.g. `/home/nir/libvirt-images` or `/mnt/data/libvirt-images`, whichever is on the big volume you discover in §2.1).
- **Seven** fully independent qcow2 files, one per clone, each a real sparse copy of the template — not overlays, not backing files. Each clone is its own universe.
- **No backing-file dependency on `desktop-template.qcow2`.** You can delete the template after the clones exist and nothing breaks.
- **Each VM gets its own Ollama install and its own model(s)**, written into its own qcow2. No sharing, no indirection.

---

## 4. Step-by-step fix (idiot-proof, no shortcuts)

Do these in order. Do not skip steps. Do not reorder. If a command fails, STOP and report to Nir via ICQ instead of improvising.

### 4.1 Gracefully shut down everything you have already started

```bash
virsh list --all
# For every VM in the list that is state=running:
virsh shutdown <name>
# Wait up to 60 seconds per VM. If a VM does not shut down:
virsh destroy <name>   # hard power-off, safe for an experimental VM
```

This includes `giantqueen-b`, the template if it is running, and anything else you may have spun up.

### 4.2 Discover where the real 1.9 TB lives

```bash
lsblk -f
df -h
sudo fdisk -l
sudo vgs 2>/dev/null
sudo lvs 2>/dev/null
```

Write down (in a scratch file, not in your head) the actual mount point of the big volume. Let's call it `$BIG` from here on. Typical possibilities:

- `/home` is on the big volume → `BIG=/home`
- A separate mount like `/mnt/data` or `/storage` → `BIG=/mnt/data`
- There is unpartitioned space and no big-volume mount exists yet → **STOP and report to Nir.** Do not partition anything without his explicit go-ahead. Repartitioning is destructive.

### 4.3 Create a new libvirt storage pool on the big volume

```bash
sudo mkdir -p $BIG/libvirt-images
sudo chown root:root $BIG/libvirt-images
sudo chmod 711 $BIG/libvirt-images

virsh pool-define-as killerbee dir --target $BIG/libvirt-images
virsh pool-build killerbee
virsh pool-start killerbee
virsh pool-autostart killerbee
virsh pool-list --all
```

You should see a pool named `killerbee` listed as `active` and `autostart yes`.

### 4.4 Inspect the template to confirm its real size

```bash
qemu-img info /var/lib/libvirt/images/desktop-template.qcow2
```

Note both `virtual size` and `disk size`. The virtual size is the filesystem's logical size; the disk size is the actual bytes on disk. The gap between them is why your first `cp` blew up — `cp` without `--sparse=always` inflates to the full virtual size.

### 4.5 Throw away the 7 overlay clones

They are useless to us now. They point at the template as a backing file, they live on the small root partition, and the work that has been done inside `giantqueen-b` (hostname, machine-id) is cheap to redo in the new clone.

```bash
# First, make sure they are NOT running (see §4.1).
# Then undefine the libvirt domains:
for vm in giantqueen-b dwarfqueen-b1 dwarfqueen-b2 worker-b1 worker-b2 worker-b3 worker-b4; do
  virsh destroy $vm 2>/dev/null
  virsh undefine $vm --remove-all-storage 2>/dev/null
done
```

If `--remove-all-storage` complains or does not remove the overlay qcow2 files, remove them by hand from wherever they were created. **Do NOT delete `desktop-template.qcow2` yet** — we still need it as the source for the copies.

### 4.6 Make 7 real full copies on the big volume

Use `qemu-img convert` — it is the correct tool. It preserves sparseness, it produces a completely independent qcow2, it is what production KVM workflows use for template → instance.

```bash
cd $BIG/libvirt-images

for vm in giantqueen-b dwarfqueen-b1 dwarfqueen-b2 worker-b1 worker-b2 worker-b3 worker-b4; do
  echo "=== cloning template to $vm.qcow2 ==="
  sudo qemu-img convert -O qcow2 -S 4k \
    /var/lib/libvirt/images/desktop-template.qcow2 \
    $BIG/libvirt-images/$vm.qcow2
  df -h $BIG   # confirm disk usage after each copy, just in case
done
```

`-O qcow2` = output format qcow2. `-S 4k` = preserve sparseness at 4 KB granularity. Each output file will be a **completely independent** qcow2 with no backing-file dependency. You can verify afterward with:

```bash
qemu-img info $BIG/libvirt-images/giantqueen-b.qcow2 | grep -E "backing|virtual|disk"
```

You should see **no** `backing file:` line. If there is one, something went wrong and you should stop and report.

### 4.7 Redefine the 7 libvirt domains pointing at the new files

For each VM, either edit the saved XML or use `virt-install --import` to register it with libvirt using the new qcow2 path. The RAM tiers you had before are correct and stay the same:

- `giantqueen-b`: 12 GB RAM
- `dwarfqueen-b1`, `dwarfqueen-b2`: 8 GB RAM each
- `worker-b1..b4`: 4 GB RAM each

Example for one VM (adapt for each):

```bash
virt-install \
  --name giantqueen-b \
  --memory 12288 \
  --vcpus 2 \
  --disk path=$BIG/libvirt-images/giantqueen-b.qcow2,format=qcow2,bus=virtio \
  --os-variant ubuntu24.04 \
  --network network=default,model=virtio \
  --graphics none \
  --import \
  --noautoconsole
```

Boot each VM, set its hostname, regenerate its machine-id (`sudo rm /etc/machine-id /var/lib/dbus/machine-id && sudo systemd-machine-id-setup`), regenerate SSH host keys (`sudo rm /etc/ssh/ssh_host_* && sudo dpkg-reconfigure openssh-server`), reboot, confirm SSH from the host works, move to the next.

### 4.8 Only then pull models

Once all 7 are standalone, cleanly hostnamed, and reachable over SSH, *then* go VM by VM and `ollama pull` whatever model each one needs. Not before. Do not try to parallelize the model pulls across all 7 VMs at the same time on a CPU-only machine — it will thrash.

---

## 5. Sanity checks before you declare Phase 3 done

1. `qemu-img info` for each clone shows **no backing file**.
2. `df -h $BIG` shows reasonable free space after all copies (plenty, since you have 1.9 TB).
3. `df -h /` is nowhere near 100 %.
4. All 7 VMs boot independently of each other.
5. You can `rm /var/lib/libvirt/images/desktop-template.qcow2` and all 7 VMs still boot. **DO NOT actually delete the template** — just confirm mentally that you *could*.
6. `ollama pull` on one VM does not affect the others (disk usage on one qcow2 grows, the others do not).

---

## 6. Things to NOT do

- Do **NOT** use `sudo cp` again without `--sparse=always`. It is the thing that filled the disk the first time.
- Do **NOT** use `qemu-img create -b` (backing-file overlays). We are explicitly moving away from that pattern.
- Do **NOT** repartition or resize the root filesystem. That is destructive and far beyond the scope of this fix.
- Do **NOT** delete `desktop-template.qcow2` until after all 7 clones exist and boot independently. It is still the source of truth until then.
- Do **NOT** boot `desktop-template.qcow2` itself ever again. If you need to modify the template, make a new one.
- Do **NOT** ask Nir via ICQ to explain this document. The document IS the explanation. If something is unclear, reread it. If it is still unclear, ask one specific question in ICQ pointing at the specific section.
- Do **NOT** "generalize" this fix to Laptop. Laptop's lane today is BeeSting videos. Stay in your lane.

---

## 7. What to do when you are done

Push a commit to KillerBee (and/or WaggleDance, your call) that:

1. Updates `KillerBee/PHASE3_LINUX_VM_SETUP.md` (or whatever the canonical doc is) to remove any backing-file-overlay language and replace it with the full-copy + big-volume-pool approach described here.
2. Records the exact `$BIG` path you chose in §4.2 so the next session knows where the VMs live.
3. Records the RAM tiers you actually used.

Then send a short ICQ REPLY to Laptop: something like `"Phase 3 disk fix complete. 7 VMs are full independent copies on $BIG/libvirt-images. Template untouched. All 7 boot. df -h / is at X%. Ready for model pulls."`

---

## 8. The meta-lesson (for both of us)

Both you and I pattern-matched to "clever production KVM idiom" without first asking the dumbest, simplest question: **does Nir actually have the problem this idiom solves?** He does not. He has a 2 TB disk sitting idle. The correct answer was "full copies on the big volume," and neither of us led with it. Next time a clever approach presents itself, first answer the question "what problem is this solving, and does the user actually have that problem?" — out loud, in writing, before moving. If the answer is "no," do the simple thing.

Nir has caught this pattern in us more than once today. He is not going to keep catching it for us.

— Laptop Claude, 🌼, 2026-04-14
