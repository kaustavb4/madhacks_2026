from backend.llm.tools import TOOLS

EXPECTED = {
    "ask_intent", "create_model", "edit_model", "measure",
    "check_printable", "set_print_settings", "print", "pause", "cancel", "undo",
}


def test_all_spec_tools_present():
    assert {t["name"] for t in TOOLS} == EXPECTED
