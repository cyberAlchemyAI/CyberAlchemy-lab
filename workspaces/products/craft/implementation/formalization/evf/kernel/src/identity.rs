use std::fs;
use std::path::{Component, Path, PathBuf};

use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::execute::EvfError;
use crate::model::{ExactRef, RefLocation};

pub fn sha256_bytes(bytes: &[u8]) -> String {
    let digest = Sha256::digest(bytes);
    digest.iter().map(|byte| format!("{byte:02x}")).collect()
}

fn canonical_value(value: &Value) -> Value {
    match value {
        Value::Array(items) => Value::Array(items.iter().map(canonical_value).collect()),
        Value::Object(map) => {
            let mut keys: Vec<&String> = map.keys().collect();
            keys.sort();
            let mut result = serde_json::Map::new();
            for key in keys {
                result.insert(key.clone(), canonical_value(&map[key]));
            }
            Value::Object(result)
        }
        other => other.clone(),
    }
}

pub fn canonical_bytes<T: Serialize>(value: &T) -> Result<Vec<u8>, EvfError> {
    let value = serde_json::to_value(value)
        .map_err(|error| EvfError::new("SERIALIZATION_FAILED", error))?;
    serde_json::to_vec(&canonical_value(&value))
        .map_err(|error| EvfError::new("SERIALIZATION_FAILED", error))
}

pub fn canonical_digest<T: Serialize>(value: &T) -> Result<String, EvfError> {
    Ok(sha256_bytes(&canonical_bytes(value)?))
}

pub fn repository_root(start: &Path) -> Result<PathBuf, EvfError> {
    let mut cursor = fs::canonicalize(start)
        .map_err(|error| EvfError::new("REPOSITORY_ROOT_UNAVAILABLE", error))?;
    if cursor.is_file() {
        cursor.pop();
    }
    loop {
        if cursor.join(".git").exists() && cursor.join("projects/domainspec-v2").exists() {
            return Ok(cursor);
        }
        if !cursor.pop() {
            return Err(EvfError::message(
                "REPOSITORY_ROOT_UNAVAILABLE",
                "repository root not found",
            ));
        }
    }
}

fn safe_repository_path(root: &Path, text: &str) -> Result<PathBuf, EvfError> {
    let candidate = Path::new(text);
    if candidate.is_absolute()
        || candidate.components().any(|part| {
            matches!(
                part,
                Component::ParentDir | Component::RootDir | Component::Prefix(_)
            )
        })
    {
        return Err(EvfError::message(
            "UNSAFE_EXACT_REF",
            format!("unsafe repository path: {text}"),
        ));
    }
    let resolved = fs::canonicalize(root.join(candidate))
        .map_err(|error| EvfError::new("EXACT_REF_MISSING", error))?;
    if !resolved.starts_with(root) {
        return Err(EvfError::message(
            "UNSAFE_EXACT_REF",
            format!("reference escapes repository: {text}"),
        ));
    }
    Ok(resolved)
}

pub fn resolve_exact_ref(root: &Path, reference: &ExactRef) -> Result<PathBuf, EvfError> {
    match reference.location {
        RefLocation::Repository => safe_repository_path(root, &reference.path),
        RefLocation::Host => {
            let path = PathBuf::from(&reference.path);
            if !path.is_absolute() {
                return Err(EvfError::message(
                    "UNSAFE_EXACT_REF",
                    "host reference must be absolute",
                ));
            }
            fs::canonicalize(path).map_err(|error| EvfError::new("EXACT_REF_MISSING", error))
        }
    }
}

pub fn exact_ref(root: &Path, path: &Path) -> Result<ExactRef, EvfError> {
    let root = fs::canonicalize(root)
        .map_err(|error| EvfError::new("REPOSITORY_ROOT_UNAVAILABLE", error))?;
    let resolved =
        fs::canonicalize(path).map_err(|error| EvfError::new("EXACT_REF_MISSING", error))?;
    let bytes =
        fs::read(&resolved).map_err(|error| EvfError::new("EXACT_REF_UNREADABLE", error))?;
    let (path, location) = if let Ok(relative) = resolved.strip_prefix(&root) {
        (
            relative.to_string_lossy().replace('\\', "/"),
            RefLocation::Repository,
        )
    } else {
        (resolved.to_string_lossy().into_owned(), RefLocation::Host)
    };
    Ok(ExactRef {
        path,
        sha256: sha256_bytes(&bytes),
        size_bytes: bytes.len() as u64,
        location,
        current: true,
    })
}

pub fn verify_exact_ref(root: &Path, reference: &ExactRef) -> Result<PathBuf, EvfError> {
    if !reference.current {
        return Err(EvfError::message(
            "EXACT_REF_STALE",
            format!("{} is not current", reference.path),
        ));
    }
    let path = resolve_exact_ref(root, reference)?;
    let bytes = fs::read(&path).map_err(|error| EvfError::new("EXACT_REF_UNREADABLE", error))?;
    if bytes.len() as u64 != reference.size_bytes {
        return Err(EvfError::message(
            "EXACT_REF_SIZE_MISMATCH",
            reference.path.clone(),
        ));
    }
    if sha256_bytes(&bytes) != reference.sha256 {
        return Err(EvfError::message(
            "EXACT_REF_DIGEST_MISMATCH",
            reference.path.clone(),
        ));
    }
    Ok(path)
}
