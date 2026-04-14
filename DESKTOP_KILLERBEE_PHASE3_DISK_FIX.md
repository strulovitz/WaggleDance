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

They are useless to us now. They point at the template as a backing file, they live on the small root partition, and the work that has been done inside `giantqueen-b` (hostname, machine-id) is cheap to redo in the new VM.

```bash
# First, make sure they are NOT running (see §4.1).
# Then undefine the libvirt domains:
for vm in giantqueen-b dwarfqueen-b1 dwarfqueen-b2 worker-b1 worker-b2 worker-b3 worker-b4; do
  virsh destroy $vm 2>/dev/null
  virsh undefine $vm --remove-all-storage 2>/dev/null
done
```

If `--remove-all-storage` complains or does not remove the overlay qcow2 files, remove them by hand from wherever they were created. **You may ALSO delete `desktop-template.qcow2` once you have confirmed the autoinstall cloud-init config (§4.6) is preserved in git — we are NOT going to clone from the template anymore, so it is no longer load-bearing.** If unsure, leave it alone for now.

### 4.6 Autoinstall 7 fresh Ubuntu VMs from scratch

**This is the key change from the original briefing.** We are NOT going to clone the template. We are going to build 7 fresh Ubuntu installs, the exact same way the template itself was built. Yes, this takes longer — probably 10–30 minutes per VM depending on autoinstall config and CPU. We are trading execution time for zero risk of clever-tool footguns. Nir's explicit direction: when the executor is unreliable, pick the long simple path over the short clever path.

**Why this is safer than any form of copy/convert/clone:**
- Each VM goes through the exact same autoinstall pipeline that built `desktop-template.qcow2` in the first place. That pipeline is already proven to work on this machine.
- There is no qcow2 manipulation, no sparse-file handling, no `cp` flags, no backing-file indirection, no shared state between VMs.
- If an autoinstall fails, you redo that one autoinstall. You do not debug "why did the copy produce a broken image." Fewer failure modes.
- The result is 7 genuinely independent Ubuntu systems. Each one was installed by Ubuntu's own installer. There is no shared history, no fingerprint overlap, no risk of hidden coupling.

**Prerequisites.** Desktop, you MUST have the autoinstall config that built `desktop-template.qcow2`. Typically this is a cloud-init `user-data` + `meta-data` pair, or an Ubuntu autoinstall YAML seed. Find it:

```bash
# Wherever you ran the template autoinstall from — likely under your home dir
find ~/ -name "user-data" -o -name "autoinstall*.yaml" -o -name "meta-data" 2>/dev/null
# Or check the KillerBee repo — it may already be committed there
grep -r "autoinstall" ~/Projects/KillerBee/ 2>/dev/null
```

**If you cannot find the autoinstall config**, STOP and report to Nir via ICQ. Do not improvise. Do not re-download the ISO and walk through the installer GUI — that is not reproducible. The config must exist somewhere; it was used to produce the template earlier today.

**Once you have the config**, write a small shell script that loops over the 7 VM names and for each one:
1. Copies the autoinstall config into a fresh working directory.
2. Edits ONLY the hostname in the config so the new VM gets the right name (e.g. `giantqueen-b`, `dwarfqueen-b1`, etc.). Leave everything else alone.
3. Calls `virt-install` with the correct RAM, the correct disk path on the big volume, and the autoinstall seed.
4. Waits for the autoinstall to complete (libvirt + autoinstall handles this — the VM shuts down when the install finishes, typically).
5. Moves to the next VM.

RAM tiers (unchanged from before):

- `giantqueen-b`: 12288 MB
- `dwarfqueen-b1`, `dwarfqueen-b2`: 8192 MB each
- `worker-b1`, `worker-b2`, `worker-b3`, `worker-b4`: 4096 MB each

Disk size: pick whatever the template used (probably 20–40 GB virtual, which will be sparse on disk, starting at ~8.6 GB real). **Do NOT increase the disk size just because you have room.** Matching the template keeps behavior predictable.

Example `virt-install` invocation for one VM (adapt names and RAM per tier):

```bash
virt-install \
  --name giantqueen-b \
  --memory 12288 \
  --vcpus 2 \
  --disk path=$BIG/libvirt-images/giantqueen-b.qcow2,format=qcow2,bus=virtio,size=20 \
  --os-variant ubuntu24.04 \
  --network network=default,model=virtio \
  --graphics none \
  --location 'http://releases.ubuntu.com/24.04/,kernel=casper/vmlinuz,initrd=casper/initrd' \
  --extra-args 'autoinstall ds=nocloud-net;s=http://_gateway:3003/' \
  --noautoconsole
```

Exact flags depend on how the template autoinstall was configured. The point is: **reuse the same method that built the template.** Do not invent a new one.

**Run them one at a time, not in parallel.** Seven autoinstalls running concurrently on a CPU-only host will thrash each other. Finish one, verify it boots, then start the next. Total wall-clock time: probably 2–4 hours. That is fine. You are trading time for safety.

### 4.7 After each VM completes autoinstall

1. Boot the VM (`virsh start <name>`) — if the autoinstall shut it down automatically, this will boot it into the finished Ubuntu.
2. From inside, verify hostname is correct.
3. Verify `machine-id` is unique (Ubuntu autoinstall generates a fresh one at install time — you should not need the `systemd-machine-id-setup` trick, but verify with `cat /etc/machine-id`).
4. Verify SSH host keys are unique (again, fresh install = fresh keys by default).
5. Install Ollama if the template did not already include it: follow the exact same install steps used for the template.
6. Bind Ollama to `0.0.0.0:11434` (same as template).
7. From the host, `curl http://<vm-ip>:11434/api/version` should return JSON.
8. Only then move on to the next VM.

If any step fails, STOP that VM, destroy + undefine it, redo the autoinstall for only that VM, and try again. Do not keep going on top of a broken VM.

### 4.8 Only then pull models

Once all 7 are standalone, cleanly hostnamed, and reachable over SSH, *then* go VM by VM and `ollama pull` whatever model each one needs. Not before. Do not try to parallelize the model pulls across all 7 VMs at the same time on a CPU-only machine — it will thrash.

---

## 5. Sanity checks before you declare Phase 3 done

1. `qemu-img info` for each VM shows **no backing file line**. Each VM is fully standalone.
2. `df -h $BIG` shows reasonable free space (plenty, since you have 1.9 TB).
3. `df -h /` is nowhere near 100 %.
4. All 7 VMs boot independently of each other.
5. Each VM has a unique hostname, a unique `/etc/machine-id`, and unique SSH host keys. (With fresh autoinstalls this should be automatic. Verify anyway.)
6. Ollama on each VM responds to `curl http://<vm-ip>:11434/api/version` from the host.
7. `ollama pull` on one VM does not affect the others (disk usage on one qcow2 grows, the others do not).

---

## 6. Things to NOT do

- Do **NOT** use `sudo cp` on qcow2 files. Ever. Not in this session, not later. It is the thing that filled the disk the first time. We are not copying qcow2 files at all anymore — we are autoinstalling fresh ones.
- Do **NOT** use `qemu-img create -b` (backing-file overlays). We are explicitly moving away from that pattern.
- Do **NOT** use `qemu-img convert` either. Nir's direction: the simple long path, not the clever short path. We are autoinstalling 7 fresh Ubuntu systems. That is the whole method.
- Do **NOT** run multiple autoinstalls in parallel on this CPU-only host. One at a time.
- Do **NOT** repartition or resize the root filesystem. That is destructive and far beyond the scope of this fix.
- Do **NOT** invent a new autoinstall method. Reuse whatever autoinstall config already built `desktop-template.qcow2` earlier today. If you cannot find it, STOP and ask Nir — do not improvise.
- Do **NOT** boot `desktop-template.qcow2` itself ever again. If you need to inspect the autoinstall config, read the config files, do not boot the template.
- Do **NOT** increase disk size "just because there is room." Match whatever the template used.
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
