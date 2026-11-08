//! Fixed Linux containment. No host enrollment, delegated root or process authority is supplied here.
pub mod state;
pub mod containment;
pub mod spawn;
pub(crate) mod evidence;
pub(crate) mod records;
pub(crate) mod attempt_journal;
pub(crate) mod adapters;
use serde::Serialize;
pub type Result<T> = std::result::Result<T, Error>;
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize)]
pub struct Error(pub &'static str);
impl From<std::io::Error> for Error { fn from(_:std::io::Error)->Self{Self("IO_REFUSAL")} }
impl From<lab_control_store::Error> for Error {fn from(_:lab_control_store::Error)->Self{Self("CONTROL_REFUSAL")}}
pub(crate) fn need(ok:bool,code:&'static str)->Result<()>{if ok{Ok(())}else{Err(Error(code))}}
