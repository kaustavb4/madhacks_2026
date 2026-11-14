"""Fixed tool set the LLM may call. The LLM never writes CadQuery code or
states a measurement directly -- it only invokes these, per the design doc.
"""

TOOLS = [
    {
        "name": "ask_intent",
        "description": "Ask the user a clarifying question about what the part is for.",
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
        },
    },
    {
        "name": "create_model",
        "description": "Build a new model from a template and named parameters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "template": {"type": "string", "enum": ["plate_with_hole", "box"]},
                "params": {"type": "object"},
                "braille_text": {"type": "string"},
            },
            "required": ["template", "params"],
        },
    },
    {
        "name": "edit_model",
        "description": "Change one or more named parameters of the current model.",
        "input_schema": {
            "type": "object",
            "properties": {"params": {"type": "object"}},
            "required": ["params"],
        },
    },
    {
        "name": "measure",
        "description": "Measure the current model: size, hole info, or wall thickness.",
        "input_schema": {
            "type": "object",
            "properties": {"what": {"type": "string", "enum": ["size", "hole", "wall_thickness"]}},
            "required": ["what"],
        },
    },
    {
        "name": "check_printable",
        "description": "Check bed fit, overhangs, and brim need for the current model.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "set_print_settings",
        "description": "Map a plain-language request (stronger/faster/finer) to slicer settings.",
        "input_schema": {
            "type": "object",
            "properties": {"request": {"type": "string"}},
            "required": ["request"],
        },
    },
    {"name": "print", "description": "Slice and start printing the confirmed model.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "pause", "description": "Pause the current print.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "cancel", "description": "Cancel the current print.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "undo", "description": "Revert the model to its previous version.",
     "input_schema": {"type": "object", "properties": {}}},
]
