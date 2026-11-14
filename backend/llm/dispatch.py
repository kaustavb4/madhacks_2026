"""Executes one tool call against the current Session. Every number spoken
back comes from here (measure/checks), never invented by the LLM, per the
design doc's "AI makes up numbers" guard.
"""
from backend.measure.checks import fits_bed, needs_brim, overhangs
from backend.measure.measure import bounding_box, hole_info, min_wall_thickness
from backend.slicer.slice import map_settings, slice_stl


def execute_tool(name: str, args: dict, session) -> dict:
    if name == "ask_intent":
        return {"question": args["question"]}

    if name == "create_model":
        version = session.model.create(
            args["template"], args.get("params", {}), args.get("braille_text")
        )
        session.design_log.record("template", args["template"], "ai")
        for k, v in version.params.items():
            session.design_log.record(k, v, "ai")
        paths = session.model.export("part")
        return {"params": version.params, **paths}

    if name == "edit_model":
        version = session.model.edit(args["params"])
        for k, v in args["params"].items():
            session.design_log.record(k, v, "user")
        paths = session.model.export("part")
        return {"params": version.params, **paths}

    if name == "undo":
        version = session.model.undo()
        return {"params": version.params if version else None}

    if name == "measure":
        bb = bounding_box(session.model._solid)
        if args["what"] == "size":
            return bb
        if args["what"] == "hole":
            return hole_info(session.model.current.params) or {"error": "no hole on this model"}
        if args["what"] == "wall_thickness":
            paths = session.model.export("part")
            return {"min_wall_thickness": min_wall_thickness(paths["stl"])}

    if name == "check_printable":
        bb = bounding_box(session.model._solid)
        bed_ok, bed_msg = fits_bed(bb)
        brim, brim_msg = needs_brim(bb)
        return {"fits_bed": bed_ok, "bed_message": bed_msg, "needs_brim": brim, "brim_message": brim_msg}

    if name == "set_print_settings":
        settings = map_settings(args["request"])
        session.print_settings.update(settings)
        return settings

    if name == "print":
        paths = session.model.export("part")
        result = slice_stl(paths["stl"], None, "exports/part.gcode")
        session.print_job_id = session.printer.upload_and_print(result["gcode"])
        return {"job_id": session.print_job_id, **result}

    if name == "pause":
        session.printer.pause(session.print_job_id)
        return {"status": "paused"}

    if name == "cancel":
        session.printer.cancel(session.print_job_id)
        return {"status": "cancelled"}

    raise ValueError(f"Unknown tool: {name}")
