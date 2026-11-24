use super::*;

#[test]
fn test_drop_env() {
    let mut args = vec![
        "FOO=bar".to_string(),
        "BAZ=qux".to_string(),
        "actual".to_string(),
        "command".to_string(),
    ];
    drop_env(&mut args);
    assert_eq!(args, vec!["actual", "command"]);
}

#[test]
fn test_drop_env_no_env_vars() {
    let mut args = vec!["actual".to_string(), "command".to_string()];
    let original = args.clone();
    drop_env(&mut args);
    assert_eq!(args, original);
}

#[test]
fn test_drop_env_empty() {
    let mut args = vec![];
    drop_env(&mut args);
    assert!(args.is_empty());
}

#[test]
fn test_drop_env_only_env_vars() {
    let mut args = vec!["FOO=bar".to_string(), "BAZ=qux".to_string()];
    drop_env(&mut args);
    assert!(args.is_empty());
}

#[test]
fn test_drop_env_with_equals_in_arg() {
    let mut args = vec![
        "FOO=bar".to_string(),
        "command".to_string(),
        "--option=value".to_string(),
    ];
    drop_env(&mut args);
    assert_eq!(args, vec!["command", "--option=value"]);
}

#[test]
fn test_add_codemod_result() {
    let mut vs = serde_json::json!({"role": "main"});
    add_codemod_result(&mut vs, &serde_json::json!({"applied": 3}));
    assert_eq!(
        vs,
        serde_json::json!({"role": "main", "applied": 3, "codemod": {"applied": 3}})
    );
}

#[test]
fn test_add_codemod_result_without_result() {
    let mut vs = serde_json::json!({"role": "main"});
    add_codemod_result(&mut vs, &serde_json::Value::Null);
    assert_eq!(vs, serde_json::json!({"role": "main"}));
}
