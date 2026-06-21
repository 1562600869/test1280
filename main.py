import argparse
import sys
import json

from models import ValidationError
import commands


def cmd_add_stage(args):
    result = commands.add_stage(
        args.stage_id, args.name, args.capacity, args.type, args.status
    )
    print(f"场地已添加: {result['id']} - {result['name']}")


def cmd_apply(args):
    result = commands.apply(
        args.stage_id, args.org, args.contact,
        args.date, args.start, args.end, args.type,
    )
    print(f"申请已提交: {result['id']}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_approve(args):
    result = commands.approve(args.apply_id)
    print(f"申请已通过: {result['id']}")


def cmd_reject(args):
    result = commands.reject(args.apply_id, args.reason)
    print(f"申请已拒绝: {result['id']}，原因: {result['reason']}")


def cmd_monthly(args):
    stats = commands.monthly(args.month)
    if not stats:
        print(f"{args.month} 无演出申请记录")
        return
    print(f"{args.month} 月度统计:")
    print(f"{'演出类型':<10}{'申请次数':<10}{'通过次数':<10}")
    print("-" * 30)
    for show_type, counts in stats.items():
        print(f"{show_type:<10}{counts['apply']:<10}{counts['approved']:<10}")


def main():
    parser = argparse.ArgumentParser(description="社区舞台场地档案与演出申请管理")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add-stage", help="添加场地")
    p_add.add_argument("stage_id", help="场地编号")
    p_add.add_argument("name", help="场地名称")
    p_add.add_argument("--capacity", type=int, required=True, help="容纳人数")
    p_add.add_argument("--type", required=True, help="场地类型: 镜框式/黑匣子/露天/多功能")
    p_add.add_argument("--status", required=True, help="场地状态: 开放/维修")
    p_add.set_defaults(func=cmd_add_stage)

    p_apply = sub.add_parser("apply", help="申请演出")
    p_apply.add_argument("stage_id", help="场地编号")
    p_apply.add_argument("--org", required=True, help="申请团体")
    p_apply.add_argument("--contact", required=True, help="联系方式")
    p_apply.add_argument("--date", required=True, help="演出日期 YYYY-MM-DD")
    p_apply.add_argument("--start", required=True, help="开始时间 HH:MM")
    p_apply.add_argument("--end", required=True, help="结束时间 HH:MM")
    p_apply.add_argument("--type", required=True, help="演出类型: 音乐会/话剧/舞蹈/综艺/其他")
    p_apply.set_defaults(func=cmd_apply)

    p_approve = sub.add_parser("approve", help="审批通过")
    p_approve.add_argument("apply_id", help="申请编号")
    p_approve.set_defaults(func=cmd_approve)

    p_reject = sub.add_parser("reject", help="拒绝申请")
    p_reject.add_argument("apply_id", help="申请编号")
    p_reject.add_argument("--reason", required=True, help="拒绝原因")
    p_reject.set_defaults(func=cmd_reject)

    p_monthly = sub.add_parser("monthly", help="月度统计")
    p_monthly.add_argument("--month", required=True, help="月份 YYYY-MM")
    p_monthly.set_defaults(func=cmd_monthly)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except ValidationError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
