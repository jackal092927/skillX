from skillx.docker_image_names import build_harbor_task_pair_image_name, sanitize_harbor_image_name


def test_build_harbor_task_pair_image_name_preserves_task_schema_separator() -> None:
    assert (
        build_harbor_task_pair_image_name(
            task_name="Task-Alpha",
            schema_id="Artifact-Generation",
        )
        == "task-alpha__artifact-generation"
    )


def test_sanitize_harbor_image_name_replaces_invalid_characters() -> None:
    assert sanitize_harbor_image_name(" Demo Task / Schema A ") == "demo-task-schema-a"
