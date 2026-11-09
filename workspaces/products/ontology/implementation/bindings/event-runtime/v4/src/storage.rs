use crate::*;
use std::{
    fs::{self, File, OpenOptions},
    io::Write,
    path::{Path, PathBuf},
};
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Frame {
    pub sequence: u64,
    pub previous: String,
    pub digest: String,
    pub manifest: Option<Manifest>,
    pub pairs: Vec<Pair>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Head {
    sequence: u64,
    digest: String,
}
fn seal(f: &Frame) -> Result<String> {
    let mut c = f.clone();
    c.digest = kernel::ZERO_DIGEST.into();
    Ok(sha(kernel::canonical_json(&c)?.as_bytes()))
}
fn write(path: &Path, v: &impl Serialize) -> Result<()> {
    let mut f = OpenOptions::new().write(true).create_new(true).open(path)?;
    f.write_all(kernel::canonical_json(v)?.as_bytes())?;
    f.sync_all()?;
    Ok(())
}
fn safe(root: &Path) -> Result<()> {
    for a in root.ancestors() {
        need(!a.is_symlink(), "symlink store path")?;
    }
    Ok(())
}
fn name(n: u64) -> String {
    format!("transaction-{n:08}.json")
}
struct Lock {
    path: PathBuf,
}
impl Lock {
    fn take(root: &Path) -> Result<Self> {
        safe(root)?;
        let path = root.join("WRITER-LOCK");
        let mut f = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)
            .map_err(|_| "writer lock held; do not steal")?;
        writeln!(f, "{}", std::process::id())?;
        f.sync_all()?;
        Ok(Self { path })
    }
}
impl Drop for Lock {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.path);
    }
}
#[derive(Debug)]
pub struct Loaded {
    pub manifest: Manifest,
    pub pairs: Vec<Pair>,
    pub sequence: u64,
    pub digest: String,
}
pub fn load(root: &Path) -> Result<Loaded> {
    safe(root)?;
    let hp = root.join("HEAD.json");
    need(!hp.is_symlink(), "symlink HEAD")?;
    let head: Head = serde_json::from_slice(&fs::read(hp)?)?;
    need(
        head.sequence > 0 && head.sequence <= 1_000_000,
        "invalid transaction head",
    )?;
    let mut previous = kernel::ZERO_DIGEST.to_string();
    let mut pairs = Vec::new();
    let mut manifest = None;
    for seq in 1..=head.sequence {
        let path = root.join(name(seq));
        need(!path.is_symlink(), "symlink transaction")?;
        let f: Frame = serde_json::from_slice(&fs::read(path)?)?;
        need(
            f.sequence == seq && f.previous == previous && f.digest == seal(&f)?,
            "transaction chain mismatch",
        )?;
        need(!f.pairs.is_empty(), "empty transaction")?;
        if seq == 1 {
            manifest = f.manifest;
        } else {
            need(f.manifest.is_none(), "manifest replacement refused")?;
        }
        pairs.extend(f.pairs);
        previous = f.digest;
    }
    need(previous == head.digest, "HEAD digest mismatch")?;
    kernel::validate_import_history(&pairs)?;
    Ok(Loaded {
        manifest: manifest.ok_or("missing genesis manifest")?,
        pairs,
        sequence: head.sequence,
        digest: previous,
    })
}
fn commit(root: &Path, mut f: Frame) -> Result<()> {
    need(
        !root.join("PENDING.json").exists() && !root.join("HEAD.pending").exists(),
        "pending write; recover before retry",
    )?;
    let next = root.join(name(f.sequence));
    need(
        !next.exists(),
        "uncommitted transaction; recover before retry",
    )?;
    f.digest = seal(&f)?;
    write(&root.join("PENDING.json"), &f)?;
    // Hard-link publication refuses any overwrite; HEAD is the atomic visibility point.
    fs::hard_link(root.join("PENDING.json"), &next)?;
    File::open(root)?.sync_all()?;
    write(
        &root.join("HEAD.pending"),
        &Head {
            sequence: f.sequence,
            digest: f.digest,
        },
    )?;
    fs::rename(root.join("HEAD.pending"), root.join("HEAD.json"))?;
    File::open(root)?.sync_all()?;
    fs::remove_file(root.join("PENDING.json"))?;
    Ok(())
}
pub fn import(path: &Path, root: &Path) -> Result<Value> {
    safe(root)?;
    need(!root.exists(), "target exists")?;
    let m: Manifest = serde_json::from_slice(&fs::read(path)?)?;
    let pairs = plan(&m)?;
    fs::create_dir(root)?;
    let _lock = Lock::take(root)?;
    commit(
        root,
        Frame {
            sequence: 1,
            previous: kernel::ZERO_DIGEST.into(),
            digest: kernel::ZERO_DIGEST.into(),
            manifest: Some(m),
            pairs,
        },
    )?;
    let state = load(root)?;
    project(&state.pairs, None, false)
}
pub fn apply(root: &Path, cmd: &Command) -> Result<Value> {
    let _lock = Lock::take(root)?;
    let loaded = load(root)?;
    let pairs = command_pairs(&loaded.manifest, &loaded.pairs, cmd)?;
    commit(
        root,
        Frame {
            sequence: loaded.sequence + 1,
            previous: loaded.digest,
            digest: kernel::ZERO_DIGEST.into(),
            manifest: None,
            pairs,
        },
    )?;
    let state = load(root)?;
    project(&state.pairs, Some(&cmd.package_key), false)
}
pub fn recover(root: &Path, expected_head: &str) -> Result<Value> {
    let _lock = Lock::take(root)?;
    let state = load(root)?;
    need(state.digest == expected_head, "recovery head mismatch")?;
    let mut removed = Vec::new();
    // Only uncommitted, explicitly named residue is eligible; committed frames are never removed.
    for n in [
        "PENDING.json".to_string(),
        "HEAD.pending".to_string(),
        name(state.sequence + 1),
    ] {
        let p = root.join(&n);
        need(!p.is_symlink(), "symlink recovery residue")?;
        if p.exists() {
            need(p.is_file(), "recovery residue not a file")?;
            fs::remove_file(p)?;
            removed.push(n);
        }
    }
    File::open(root)?.sync_all()?;
    Ok(
        json!({"result":"PASS","removed_uncommitted_files":removed,"committed_head":state.digest,"authority_effect":"none"}),
    )
}
