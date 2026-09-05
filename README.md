# notes

Reference notes and scratch code, consolidated from 19 former `*-r` repositories.

| Folder | Was | Folder | Was |
|---|---|---|---|
| `3D-printing` | `3D-printing-r` | `learning-platforms` | `learning-platforms-r` |
| `AWS` | `AWS-r` | `mathematics` | `mathematics-r` |
| `chemistry` | `chemistry-r` | `physics` | `physics-r` |
| `cooking` | `cooking-r` | `pointers` | `pointers-r` |
| `cpp` | `cpp-r` | `probability` | `probability-r` |
| `font` | `font-r` | `python` | `python-r` |
| `gnuplot` | `gnuplot-r` | `sed-awk` | `sed-awk-r` |
| `javascript` | `javascript-r` | `shell` | `shell-r` |
| `kalman` | `kalman-r` | `WSL` | `WSL-r` |
| `latex` | `latex-r` | | |

## Loose files

- `ideas.md` — project backlog, from the former `active-proj` repo.
- `networking/` — router and OpenWrt config notes, from `GL-AR750S-Ext`.
- `chatgpt/` — saved answers, from `chat.openai-answers`.
- `shell/covid-bash.sh`, `shell/norske-tekster-count.sh` — from `covid-bash` and
  `Norske-tekster-med-enkel-formatering`.
- `python/count-char.py`, `python/norske-tekster-format.py`,
  `python/paintings-getlinks.py` — from `count-char`, the Norske-tekster repo
  and `paintings`.

## History

All original commits are preserved via `git subtree`. Note that
`git log -- <folder>` will **not** show them: in the source repositories those
files lived at the repository root, so path-limited log stops at the merge.
Walk the merge commit's second parent instead:

```sh
sha=$(git log --full-history --format=%H -- shell | tail -1)
git log $sha^2
```

`latex` is the exception — imported without history, because its original
carried large third-party template archives.

## Import notes

- Third-party archives (course tarballs, template zips) were excluded.
- Ten accidentally committed compiled binaries were removed.
