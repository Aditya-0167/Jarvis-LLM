def test_gradio_ui_imports():
    from jarvis.gradio_app import launch
    assert callable(launch)
