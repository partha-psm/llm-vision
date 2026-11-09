def test_package_imports() -> None:
    import llm_vision

    assert llm_vision.__doc__ == "Llama 3.2 experimentation package."
