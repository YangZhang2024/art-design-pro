import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from database import init_db, get_session, User, Role, UserRole, MenuResource, RoleMenuResource, Customer

db = get_session()

def import_menus(items, parent_id=None, sort_offset=0):
    idx = 0
    for item in items:
        meta = {k: v for k, v in item.get("meta", {}).items()}
        menu = MenuResource(
            parentId=parent_id,
            name=item["name"],
            path=item.get("path", ""),
            component=item.get("component", ""),
            meta=json.dumps(meta, ensure_ascii=False),
            sort=sort_offset + idx,
            isFirstLevel=(parent_id is None)
        )
        db.add(menu)
        db.flush()
        if item.get("children"):
            import_menus(item["children"], parent_id=menu.id)
        idx += 1

def seed():
    init_db()
    # Clear
    for t in [RoleMenuResource, UserRole, MenuResource, Role, User, Customer]:
        db.query(t).delete()

    # 1. Menus
    menu_path = os.path.join(os.path.dirname(__file__), "menu.json")
    with open(menu_path, "r", encoding="utf-8") as f:
        import_menus(json.load(f))
    print("Menus imported")

    # 2. Roles
    role_map = {}
    for i, (rn, rc, desc) in enumerate([
        ("超级管理员", "R_SUPER", "拥有系统全部权限"),
        ("管理员", "R_ADMIN", "拥有系统管理权限"),
        ("普通用户", "R_USER", "拥有系统普通权限"),
    ]):
        r = Role(id=i+1, roleName=rn, roleCode=rc, description=desc, enabled=True, createTime="2025-05-15 12:30:45")
        db.add(r); db.flush(); role_map[rc] = r
    print("Roles created")

    # 3. Assign menus
    all_menus = db.query(MenuResource).all()
    for m in all_menus:
        meta_obj = json.loads(m.meta) if m.meta else {}
        marks = [a["authMark"] for a in meta_obj.get("authList", [])]
        db.add(RoleMenuResource(roleId=role_map["R_SUPER"].id, menuResourceId=m.id,
                                authMarks=json.dumps(marks, ensure_ascii=False)))
    for m in all_menus:
        db.add(RoleMenuResource(roleId=role_map["R_ADMIN"].id, menuResourceId=m.id, authMarks="[]"))
    public = {"Dashboard", "Console", "Template", "Cards", "Banners", "Charts",
              "Widgets", "Icon", "Exception", "404", "403", "500"}
    for m in all_menus:
        if m.name in public or m.isFirstLevel:
            db.add(RoleMenuResource(roleId=role_map["R_USER"].id, menuResourceId=m.id, authMarks="[]"))
    print("Menu-role assignments done")

    # 4. Users
    for un, nick, rcs in [("Super", "超级管理员", ["R_SUPER"]), ("Admin", "管理员", ["R_ADMIN"]), ("User", "普通用户", ["R_USER"])]:
        u = User(userName=un, password="123456", nickName=nick, userGender="男", status="1",
                 userPhone="13800000000", userEmail=un.lower()+"@company.com", createTime="2024-01-01 00:00:00")
        db.add(u); db.flush()
        for rc in rcs:
            db.add(UserRole(userId=u.id, roleId=role_map[rc].id))
    print("Users created")

    # 5. Customers
    for row in [
        (10001, "星河科技（上海）有限公司", "张伟", "13800000001", "zhangwei@startech.cn", "1", "上海市浦东新区张江高科技园区", "核心客户，季度采购量大"),
        (10002, "云帆贸易（深圳）有限公司", "李娜", "13800000002", "lina@yunfan.com", "1", "深圳市南山区科技园南区", "长期合作客户"),
        (10003, "青岚设计工作室", "王强", "13800000003", "wangqiang@qinglan.com", "2", "杭州市西湖区转塘街道", "已暂停合作"),
        (10004, "海盐智能制造有限公司", "赵敏", "13800000004", "zhaomin@haiyan.cn", "1", "宁波市北仑区大碶街道", "新开发客户，潜力大"),
        (10005, "光年网络科技有限公司", "陈杰", "13800000005", "chenjie@guangnian.dev", "2", "成都市高新区天府大道", "合同到期未续签"),
        (10006, "天穹数据技术有限公司", "刘洋", "13800000006", "liuyang@tianqiong.com", "1", "北京市海淀区上地信息产业基地", "重点客户，需要定期跟进"),
        (10007, "碧波生态农业集团", "周婷", "13800000007", "zhouting@bibo.agri", "1", "昆明市盘龙区北京路", "首次合作，试用阶段"),
        (10008, "墨白文化传媒有限公司", "黄磊", "13800000008", "em@mobai.cn", "2", "长沙市岳麓区梅溪湖", "业务调整中"),
    ]:
        cid, name, contact, phone, email, status, addr, remark = row
        db.add(Customer(id=cid, name=name, contactName=contact, phone=phone, email=email,
                        status=status, address=addr, remark=remark,
                        createdAt="2026-05-01 09:00:00", updatedAt="2026-05-30 12:00:00"))
    print("Customers seeded")

    db.commit()
    print("Seed complete!")

if __name__ == "__main__":
    seed()
