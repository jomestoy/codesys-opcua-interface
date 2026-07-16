from codesys_opcua_interface.profile import build_profile, validate_profile


def test_profile_is_safe_by_default():
    profile = build_profile()
    assert profile["real_io_enabled"] is False
    assert profile["write_authority"] == "Bloqueada"
    assert profile["endpoint_url"].startswith("opc.tcp://")
    assert any(node["key"] == "input_weight" for node in profile["nodes"])
    assert any(node["direction"] == "write_guarded" for node in profile["nodes"])


def test_profile_rejects_insecure_mode():
    profile = build_profile()
    profile["security_mode"] = "None"
    errors = validate_profile(profile)
    assert any("SignAndEncrypt" in error for error in errors)
