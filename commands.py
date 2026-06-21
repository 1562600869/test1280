import uuid
from collections import defaultdict

from models import (
    ValidationError,
    validate_stage_type,
    validate_stage_status,
    validate_show_type,
    validate_time_order,
    check_stage_exists,
    check_stage_not_under_repair,
    check_no_overlap,
    check_apply_status,
)
from storage import transaction


@transaction
def add_stage(data, stage_id, name, capacity, stage_type, status):
    if stage_id in data["stages"]:
        raise ValidationError(f"场地已存在: {stage_id}")
    validate_stage_type(stage_type)
    validate_stage_status(status)
    data["stages"][stage_id] = {
        "id": stage_id,
        "name": name,
        "capacity": capacity,
        "type": stage_type,
        "status": status,
    }
    return data["stages"][stage_id]


@transaction
def apply(data, stage_id, org, contact, date, start, end, show_type):
    check_stage_exists(data, stage_id)
    check_stage_not_under_repair(data, stage_id)
    validate_show_type(show_type)
    validate_time_order(start, end)
    check_no_overlap(data, stage_id, date, start, end)
    apply_id = "APPLY_" + uuid.uuid4().hex[:8].upper()
    data["applications"][apply_id] = {
        "id": apply_id,
        "stage_id": stage_id,
        "org": org,
        "contact": contact,
        "date": date,
        "start": start,
        "end": end,
        "type": show_type,
        "status": "待审批",
        "reason": None,
    }
    return data["applications"][apply_id]


@transaction
def approve(data, apply_id):
    check_apply_status(data, apply_id, "待审批")
    app = data["applications"][apply_id]
    check_no_overlap(
        data, app["stage_id"], app["date"], app["start"], app["end"],
        exclude_apply_id=apply_id,
    )
    app["status"] = "已通过"
    return app


@transaction
def reject(data, apply_id, reason):
    check_apply_status(data, apply_id, "待审批")
    app = data["applications"][apply_id]
    app["status"] = "已拒绝"
    app["reason"] = reason
    return app


@transaction
def monthly(data, month):
    stats = defaultdict(lambda: {"apply": 0, "approved": 0})
    for app in data["applications"].values():
        if not app["date"].startswith(month):
            continue
        show_type = app["type"]
        stats[show_type]["apply"] += 1
        if app["status"] == "已通过":
            stats[show_type]["approved"] += 1
    return dict(stats)
