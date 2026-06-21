VALID_STAGE_TYPES = ("镜框式", "黑匣子", "露天", "多功能")
VALID_STAGE_STATUSES = ("开放", "维修")
VALID_SHOW_TYPES = ("音乐会", "话剧", "舞蹈", "综艺", "其他")
VALID_APPLY_STATUSES = ("待审批", "已通过", "已拒绝")


class ValidationError(Exception):
    pass


def validate_stage_type(stage_type):
    if stage_type not in VALID_STAGE_TYPES:
        raise ValidationError(
            f"场地类型无效: {stage_type}，可选值: {'/'.join(VALID_STAGE_TYPES)}"
        )


def validate_stage_status(status):
    if status not in VALID_STAGE_STATUSES:
        raise ValidationError(
            f"场地状态无效: {status}，可选值: {'/'.join(VALID_STAGE_STATUSES)}"
        )


def validate_show_type(show_type):
    if show_type not in VALID_SHOW_TYPES:
        raise ValidationError(
            f"演出类型无效: {show_type}，可选值: {'/'.join(VALID_SHOW_TYPES)}"
        )


def validate_time_order(start, end):
    if start >= end:
        raise ValidationError(
            f"结束时间({end})必须晚于开始时间({start})"
        )


def check_stage_exists(data, stage_id):
    if stage_id not in data["stages"]:
        raise ValidationError(f"场地不存在: {stage_id}")


def check_stage_not_under_repair(data, stage_id):
    stage = data["stages"][stage_id]
    if stage["status"] == "维修":
        raise ValidationError(f"场地 {stage_id} 正在维修，无法申请")


def check_no_overlap(data, stage_id, date, start, end, exclude_apply_id=None):
    for aid, app in data["applications"].items():
        if aid == exclude_apply_id:
            continue
        if app["stage_id"] != stage_id:
            continue
        if app["date"] != date:
            continue
        if app["status"] == "已拒绝":
            continue
        if start < app["end"] and end > app["start"]:
            raise ValidationError(
                f"时段冲突: 场地 {stage_id} 在 {date} {app['start']}-{app['end']} "
                f"已被占用(申请号 {aid})"
            )


def check_apply_status(data, apply_id, expected_status="待审批"):
    if apply_id not in data["applications"]:
        raise ValidationError(f"申请不存在: {apply_id}")
    app = data["applications"][apply_id]
    if app["status"] != expected_status:
        raise ValidationError(
            f"申请 {apply_id} 当前状态为'{app['status']}'，无法操作(需'{expected_status}')"
        )
