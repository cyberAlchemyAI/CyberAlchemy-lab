use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::os::fd::AsRawFd;
use std::path::{Path, PathBuf};

use serde_json::json;

use crate::execute::EvfError;

fn safe_attempt_id(attempt_id: &str) -> bool {
    !attempt_id.is_empty()
        && attempt_id.len() <= 120
        && attempt_id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.'))
}

fn try_attempt_lease(store: &Path, attempt_id: &str) -> Result<Option<File>, EvfError> {
    let leases = store.join("leases");
    fs::create_dir_all(&leases)
        .map_err(|error| EvfError::new("RUN_STORE_LEASE_CREATE_FAILED", error))?;
    let lease = OpenOptions::new()
        .create(true)
        .read(true)
        .write(true)
        .open(leases.join(format!("{attempt_id}.lock")))
        .map_err(|error| EvfError::new("RUN_STORE_LEASE_OPEN_FAILED", error))?;
    // SAFETY: the lock applies to this owned descriptor, which remains alive for
    // the entire staging lifetime and releases the lease on drop or process exit.
    let result = unsafe { libc::flock(lease.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) };
    if result == 0 {
        return Ok(Some(lease));
    }
    let error = std::io::Error::last_os_error();
    if error.raw_os_error() == Some(libc::EWOULDBLOCK) {
        return Ok(None);
    }
    Err(EvfError::new("RUN_STORE_LEASE_FAILED", error))
}

pub fn recover_partials(store: &Path) -> Result<Vec<PathBuf>, EvfError> {
    fs::create_dir_all(store).map_err(|error| EvfError::new("RUN_STORE_CREATE_FAILED", error))?;
    let interrupted = store.join("interrupted");
    fs::create_dir_all(&interrupted)
        .map_err(|error| EvfError::new("RUN_STORE_CREATE_FAILED", error))?;
    let mut recovered = Vec::new();
    for entry in
        fs::read_dir(store).map_err(|error| EvfError::new("RUN_STORE_READ_FAILED", error))?
    {
        let entry = entry.map_err(|error| EvfError::new("RUN_STORE_READ_FAILED", error))?;
        let name = entry.file_name().to_string_lossy().into_owned();
        if !name.starts_with(".partial-") || !entry.path().is_dir() {
            continue;
        }
        let attempt_id = name.trim_start_matches(".partial-");
        if !safe_attempt_id(attempt_id) {
            return Err(EvfError::message("INVALID_PARTIAL_ATTEMPT_ID", attempt_id));
        }
        let Some(_recovery_lease) = try_attempt_lease(store, attempt_id)? else {
            continue;
        };
        let destination = interrupted.join(attempt_id);
        if destination.exists() {
            return Err(EvfError::message(
                "RUN_STORE_RECOVERY_COLLISION",
                destination.display().to_string(),
            ));
        }
        let receipt = json!({
            "schema_version": "evf.interrupted-run-recovery/v1",
            "state": "interrupted",
            "reason_code": "UNFINALIZED_PARTIAL_RECOVERED",
            "authority_effect": "none"
        });
        fs::write(
            entry.path().join("RECOVERY.json"),
            serde_json::to_vec_pretty(&receipt).unwrap(),
        )
        .map_err(|error| EvfError::new("RUN_STORE_RECOVERY_FAILED", error))?;
        fs::rename(entry.path(), &destination)
            .map_err(|error| EvfError::new("RUN_STORE_RECOVERY_FAILED", error))?;
        recovered.push(destination);
    }
    Ok(recovered)
}

pub struct StagingRun {
    pub path: PathBuf,
    store: PathBuf,
    attempt_id: String,
    _lease: File,
}

impl StagingRun {
    pub fn create(store: &Path, attempt_id: &str) -> Result<Self, EvfError> {
        if !safe_attempt_id(attempt_id) {
            return Err(EvfError::message("INVALID_ATTEMPT_ID", attempt_id));
        }
        recover_partials(store)?;
        let lease = try_attempt_lease(store, attempt_id)?
            .ok_or_else(|| EvfError::message("RUN_STORE_ATTEMPT_ACTIVE", attempt_id))?;
        let path = store.join(format!(".partial-{attempt_id}"));
        if path.exists() {
            return Err(EvfError::message(
                "RUN_STORE_ATTEMPT_EXISTS",
                path.display().to_string(),
            ));
        }
        fs::create_dir_all(&path)
            .map_err(|error| EvfError::new("RUN_STORE_CREATE_FAILED", error))?;
        Ok(Self {
            path,
            store: store.to_path_buf(),
            attempt_id: attempt_id.to_owned(),
            _lease: lease,
        })
    }

    pub fn write_json<T: serde::Serialize>(
        &self,
        name: &str,
        value: &T,
    ) -> Result<PathBuf, EvfError> {
        if name.contains('/') || name.contains("..") {
            return Err(EvfError::message("UNSAFE_RUN_ARTIFACT", name));
        }
        let path = self.path.join(name);
        let mut bytes = serde_json::to_vec_pretty(value)
            .map_err(|error| EvfError::new("SERIALIZATION_FAILED", error))?;
        bytes.push(b'\n');
        let mut file =
            File::create(&path).map_err(|error| EvfError::new("RUN_STORE_WRITE_FAILED", error))?;
        file.write_all(&bytes)
            .map_err(|error| EvfError::new("RUN_STORE_WRITE_FAILED", error))?;
        file.sync_all()
            .map_err(|error| EvfError::new("RUN_STORE_SYNC_FAILED", error))?;
        Ok(path)
    }

    pub fn finalize(self, payload_digest: &str) -> Result<PathBuf, EvfError> {
        if payload_digest.len() != 64
            || !payload_digest
                .bytes()
                .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
        {
            return Err(EvfError::message("INVALID_PAYLOAD_DIGEST", payload_digest));
        }
        let parent = self.store.join("sha256").join(payload_digest);
        fs::create_dir_all(&parent)
            .map_err(|error| EvfError::new("RUN_STORE_CREATE_FAILED", error))?;
        let final_path = parent.join(&self.attempt_id);
        if final_path.exists() {
            return Err(EvfError::message(
                "RUN_STORE_FINAL_EXISTS",
                final_path.display().to_string(),
            ));
        }
        fs::rename(&self.path, &final_path)
            .map_err(|error| EvfError::new("RUN_STORE_FINALIZE_FAILED", error))?;
        File::open(&parent)
            .and_then(|file| file.sync_all())
            .map_err(|error| EvfError::new("RUN_STORE_SYNC_FAILED", error))?;
        Ok(final_path)
    }
}
