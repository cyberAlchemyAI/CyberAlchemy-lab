use hmac::{Hmac, KeyInit, Mac};
use r13_commerce_candidate::providers::reference::{
    application::RuntimeHttpResult,
    inbound_http::{webhook_router, LifecycleHealth, WebhookFuture},
};
use serde_json::json;
use sha2::Sha256;
use std::error::Error;
use std::sync::{Arc, atomic::{AtomicUsize, Ordering}};

fn sign(body: &[u8], secret: &str) -> String {
    let mut mac = Hmac::<Sha256>::new_from_slice(secret.as_bytes()).expect("HMAC accepts every key length");
    mac.update(body);
    mac.finalize().into_bytes().iter().map(|byte| format!("{byte:02x}")).collect()
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let route = std::env::args().nth(1).unwrap_or_else(|| "/webhook".to_owned());
    assert!(route.starts_with('/') && route.len() > 1 && !route.contains("//")
        && route.bytes().skip(1).all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'/' | b'_' | b'-')));
    let body = b"domainspec-installed-webhook";
    let secret = "installed-reference-secret";
    let invocations = Arc::new(AtomicUsize::new(0));
    let observed = Arc::clone(&invocations);
    let health = LifecycleHealth::default();
    health.ready();
    let router = webhook_router(secret.to_owned(), health, move |received| {
        let observed = Arc::clone(&observed);
        Box::pin(async move {
            assert_eq!(received, body);
            observed.fetch_add(1, Ordering::SeqCst);
            Ok(RuntimeHttpResult { status_code: 202, body: json!(null) })
        }) as WebhookFuture
    });
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await?;
    let address = listener.local_addr()?;
    let task = tokio::spawn(async move { axum::serve(listener, router).await });
    let client = reqwest::Client::new();
    let url = format!("http://{address}{route}");
    let invalid_status = client.post(&url).header("x-domainspec-signature", "0".repeat(64)).body(body.to_vec()).send().await?.status();
    assert_eq!(invalid_status.as_u16(), 401);
    assert_eq!(invocations.load(Ordering::SeqCst), 0);
    let valid_status = client.post(&url).header("x-domainspec-signature", sign(body, secret)).body(body.to_vec()).send().await?.status();
    assert_eq!(valid_status.as_u16(), 202);
    assert_eq!(invocations.load(Ordering::SeqCst), 1);
    println!("{{\"language\":\"rust\",\"startup\":\"axum-http-listener\",\"invalid_status\":{},\"valid_status\":{},\"handler_invocations\":{},\"result\":\"pass\"}}", invalid_status.as_u16(), valid_status.as_u16(), invocations.load(Ordering::SeqCst));
    task.abort();
    let _ = task.await;
    Ok(())
}
