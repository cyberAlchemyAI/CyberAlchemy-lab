//! Fixed, statically linked Linux control custody. No authority is inferred from
//! possession of these Rust types: the host loader must independently select
//! root, authority domain, current writer fence and continuity confirmation.
//! Actual host bootstrap/confirmation is deliberately outside this crate.
pub mod codec;
pub mod custody;
pub mod ledger;

pub type Result<T> = std::result::Result<T, Error>;
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error(pub String);
impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { f.write_str(&self.0) }
}
impl std::error::Error for Error {}
impl From<std::io::Error> for Error {
    fn from(value: std::io::Error) -> Self { Self(format!("io: {}", value)) }
}
pub(crate) fn fail<T>(message: &str) -> Result<T> { Err(Error(message.into())) }
