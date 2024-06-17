# Generated by Django 4.2.13 on 2024-06-01 15:20

import apps.account.models.user
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Users",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("username", models.CharField(db_index=True, max_length=64, unique=True, verbose_name="用户账号")),
                ("email", models.EmailField(blank=True, max_length=255, null=True, verbose_name="邮箱")),
                ("mobile", models.CharField(blank=True, max_length=255, null=True, verbose_name="电话")),
                ("avatar", models.CharField(blank=True, max_length=255, null=True, verbose_name="头像")),
                ("name", models.CharField(max_length=64, verbose_name="姓名")),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("UNKNOWN", "未知"), ("MALE", "男"), ("FEMALE", "女")],
                        default="UNKNOWN",
                        max_length=32,
                        null=True,
                        verbose_name="性别",
                    ),
                ),
                (
                    "user_type",
                    models.CharField(
                        blank=True,
                        choices=[("BACKEND", "后台用户"), ("FRONTEND", "前台用户")],
                        default="BACKEND",
                        max_length=32,
                        null=True,
                        verbose_name="用户类型",
                    ),
                ),
            ],
            options={
                "verbose_name": "用户表",
                "verbose_name_plural": "用户表",
            },
            managers=[
                ("objects", apps.account.models.user.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Dept",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("name", models.CharField(max_length=64, verbose_name="部门名称")),
                ("key", models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name="关联字符")),
                ("sort", models.IntegerField(default=1, verbose_name="显示排序")),
                ("owner", models.CharField(blank=True, max_length=64, null=True, verbose_name="负责人")),
                ("phone", models.CharField(blank=True, max_length=32, null=True, verbose_name="联系电话")),
                ("email", models.EmailField(blank=True, max_length=32, null=True, verbose_name="邮箱")),
                ("status", models.BooleanField(blank=True, default=True, null=True, verbose_name="部门状态")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.dept",
                        verbose_name="上级部门",
                    ),
                ),
            ],
            options={
                "verbose_name": "部门表",
                "verbose_name_plural": "部门表",
            },
        ),
        migrations.CreateModel(
            name="LoginLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("username", models.CharField(blank=True, max_length=32, null=True, verbose_name="登录用户名")),
                ("ip", models.CharField(blank=True, max_length=32, null=True, verbose_name="登录ip")),
                ("agent", models.TextField(blank=True, null=True, verbose_name="agent信息")),
                ("browser", models.CharField(blank=True, max_length=255, null=True, verbose_name="浏览器名")),
                (
                    "os",
                    models.CharField(
                        blank=True, help_text="操作系统", max_length=255, null=True, verbose_name="操作系统"
                    ),
                ),
                ("continent", models.CharField(blank=True, max_length=64, null=True, verbose_name="州")),
                ("country", models.CharField(blank=True, max_length=64, null=True, verbose_name="国家")),
                ("province", models.CharField(blank=True, max_length=64, null=True, verbose_name="省份")),
                ("city", models.CharField(blank=True, max_length=64, null=True, verbose_name="城市")),
                ("district", models.CharField(blank=True, max_length=64, null=True, verbose_name="县区")),
                ("isp", models.CharField(blank=True, max_length=64, null=True, verbose_name="运营商")),
                ("area_code", models.CharField(blank=True, max_length=64, null=True, verbose_name="区域代码")),
                ("country_english", models.CharField(blank=True, max_length=64, null=True, verbose_name="英文全称")),
                ("country_code", models.CharField(blank=True, max_length=64, null=True, verbose_name="简称")),
                ("longitude", models.CharField(blank=True, max_length=64, null=True, verbose_name="经度")),
                ("latitude", models.CharField(blank=True, max_length=64, null=True, verbose_name="纬度")),
                (
                    "login_type",
                    models.CharField(
                        choices=[("NORMAL", "普通登录"), ("WECHAT_SCAN_CODE", "微信扫码登录")],
                        default="NORMAL",
                        max_length=32,
                        verbose_name="登录类型",
                    ),
                ),
            ],
            options={
                "verbose_name": "登录日志",
                "verbose_name_plural": "登录日志",
            },
        ),
        migrations.CreateModel(
            name="Menu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("icon", models.CharField(blank=True, max_length=64, null=True, verbose_name="菜单图标")),
                ("name", models.CharField(max_length=64, verbose_name="菜单名称")),
                ("sort", models.IntegerField(blank=True, default=1, null=True, verbose_name="显示排序")),
                ("is_link", models.BooleanField(default=False, verbose_name="是否外链")),
                ("link_url", models.CharField(blank=True, max_length=255, null=True, verbose_name="链接地址")),
                ("is_catalog", models.BooleanField(default=False, verbose_name="是否目录")),
                ("web_path", models.CharField(blank=True, max_length=128, null=True, verbose_name="路由地址")),
                ("component", models.CharField(blank=True, max_length=128, null=True, verbose_name="组件地址")),
                ("component_name", models.CharField(blank=True, max_length=64, null=True, verbose_name="组件名称")),
                ("status", models.BooleanField(blank=True, default=True, verbose_name="菜单状态")),
                ("cache", models.BooleanField(blank=True, default=False, verbose_name="是否页面缓存")),
                ("visible", models.BooleanField(blank=True, default=True, verbose_name="侧边栏中是否显示")),
                ("is_iframe", models.BooleanField(blank=True, default=False, verbose_name="框架外显示")),
                ("is_affix", models.BooleanField(blank=True, default=False, verbose_name="是否固定")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.menu",
                        verbose_name="上级菜单",
                    ),
                ),
            ],
            options={
                "verbose_name": "菜单表",
                "verbose_name_plural": "菜单表",
            },
        ),
        migrations.CreateModel(
            name="MenuButton",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("name", models.CharField(max_length=64, verbose_name="名称")),
                ("value", models.CharField(max_length=64, unique=True, verbose_name="权限值")),
                ("api", models.CharField(max_length=255, verbose_name="接口地址")),
                (
                    "method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("GET", "GET"),
                            ("POST", "POST"),
                            ("PUT", "PUT"),
                            ("PATCH", "PATCH"),
                            ("DELETE", "DELETE"),
                        ],
                        max_length=32,
                        null=True,
                        verbose_name="接口请求方法",
                    ),
                ),
                (
                    "menu",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="menuPermission",
                        to="account.menu",
                        verbose_name="关联菜单",
                    ),
                ),
            ],
            options={
                "verbose_name": "菜单按钮表",
                "verbose_name_plural": "菜单按钮表",
            },
        ),
        migrations.CreateModel(
            name="MessageCenter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("title", models.CharField(max_length=128, verbose_name="标题")),
                ("content", models.TextField(verbose_name="内容")),
                ("target_type", models.IntegerField(default=0, verbose_name="目标类型")),
                (
                    "target_dept",
                    models.ManyToManyField(blank=True, db_constraint=False, to="account.dept", verbose_name="目标部门"),
                ),
            ],
            options={
                "verbose_name": "消息中心",
                "verbose_name_plural": "消息中心",
            },
        ),
        migrations.CreateModel(
            name="OperationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("request_modular", models.CharField(blank=True, max_length=64, null=True, verbose_name="请求模块")),
                ("request_path", models.CharField(blank=True, max_length=1000, null=True, verbose_name="请求地址")),
                ("request_body", models.TextField(blank=True, null=True, verbose_name="请求参数")),
                ("request_method", models.CharField(blank=True, max_length=32, null=True, verbose_name="请求方式")),
                ("request_msg", models.TextField(blank=True, null=True, verbose_name="操作说明")),
                ("request_ip", models.CharField(blank=True, max_length=32, null=True, verbose_name="请求ip地址")),
                ("request_browser", models.CharField(blank=True, max_length=64, null=True, verbose_name="请求浏览器")),
                ("request_os", models.CharField(blank=True, max_length=64, null=True, verbose_name="操作系统")),
                ("response_code", models.CharField(blank=True, max_length=32, null=True, verbose_name="响应状态码")),
                ("response_content", models.TextField(blank=True, null=True, verbose_name="返回信息")),
                ("request_id", models.CharField(max_length=64, null=True, verbose_name="请求唯一 ID")),
            ],
            options={
                "verbose_name": "操作日志",
                "verbose_name_plural": "操作日志",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("name", models.CharField(max_length=64, verbose_name="岗位名称")),
                ("code", models.CharField(max_length=32, verbose_name="岗位编码")),
                ("sort", models.IntegerField(default=1, verbose_name="岗位顺序")),
                (
                    "status",
                    models.CharField(
                        choices=[("QUIT", "离职"), ("IN_SERVICE", "在职")],
                        default="IN_SERVICE",
                        max_length=32,
                        verbose_name="岗位状态",
                    ),
                ),
            ],
            options={
                "verbose_name": "岗位表",
                "verbose_name_plural": "岗位表",
            },
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("name", models.CharField(max_length=64, verbose_name="角色名称")),
                ("key", models.CharField(max_length=64, unique=True, verbose_name="权限字符")),
                ("sort", models.IntegerField(default=1, verbose_name="角色顺序")),
                ("status", models.BooleanField(default=True, verbose_name="角色状态")),
            ],
            options={
                "verbose_name": "角色表",
                "verbose_name_plural": "角色表",
            },
        ),
        migrations.CreateModel(
            name="RoleMenuPermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                (
                    "menu",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_menu",
                        to="account.menu",
                        verbose_name="关联菜单",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_menu",
                        to="account.role",
                        verbose_name="关联角色",
                    ),
                ),
            ],
            options={
                "verbose_name": "角色菜单权限表",
                "verbose_name_plural": "角色菜单权限表",
            },
        ),
        migrations.CreateModel(
            name="RoleMenuButtonPermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                (
                    "data_range",
                    models.CharField(
                        choices=[
                            ("USER", "仅本人数据权限"),
                            ("GROUP", "本部门及以下数据权限"),
                            ("DEPT", "本部门数据权限"),
                            ("ALL", "全部数据权限"),
                            ("CUSTOM", "自定数据权限"),
                        ],
                        default="USER",
                        max_length=32,
                        verbose_name="数据权限范围",
                    ),
                ),
                (
                    "dept",
                    models.ManyToManyField(
                        blank=True, db_constraint=False, to="account.dept", verbose_name="数据权限-关联部门"
                    ),
                ),
                (
                    "menu_button",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="menu_button_permission",
                        to="account.menubutton",
                        verbose_name="关联菜单按钮",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_menu_button",
                        to="account.role",
                        verbose_name="关联角色",
                    ),
                ),
            ],
            options={
                "verbose_name": "角色按钮权限表",
                "verbose_name_plural": "角色按钮权限表",
            },
        ),
        migrations.CreateModel(
            name="MessageCenterTargetUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("is_read", models.BooleanField(blank=True, default=False, null=True, verbose_name="是否已读")),
                (
                    "message_center",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.messagecenter",
                        verbose_name="关联消息中心表",
                    ),
                ),
                (
                    "users",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="target_user",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="关联用户表",
                    ),
                ),
            ],
            options={
                "verbose_name": "消息中心目标用户表",
                "verbose_name_plural": "消息中心目标用户表",
            },
        ),
        migrations.AddField(
            model_name="messagecenter",
            name="target_role",
            field=models.ManyToManyField(blank=True, db_constraint=False, to="account.role", verbose_name="目标角色"),
        ),
        migrations.AddField(
            model_name="messagecenter",
            name="target_user",
            field=models.ManyToManyField(
                blank=True,
                related_name="user",
                through="account.MessageCenterTargetUser",
                to=settings.AUTH_USER_MODEL,
                verbose_name="目标用户",
            ),
        ),
        migrations.CreateModel(
            name="MenuField",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("model", models.CharField(max_length=64, verbose_name="表名")),
                ("field_name", models.CharField(max_length=64, verbose_name="模型表字段名")),
                ("title", models.CharField(max_length=64, verbose_name="字段显示名")),
                (
                    "menu",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.menu",
                        verbose_name="菜单",
                    ),
                ),
            ],
            options={
                "verbose_name": "菜单字段表",
                "verbose_name_plural": "菜单字段表",
            },
        ),
        migrations.CreateModel(
            name="FieldPermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("is_query", models.BooleanField(default=1, verbose_name="是否可查询")),
                ("is_create", models.BooleanField(default=1, verbose_name="是否可创建")),
                ("is_update", models.BooleanField(default=1, verbose_name="是否可更新")),
                (
                    "field",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="menu_field",
                        to="account.menufield",
                        verbose_name="字段",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.role",
                        verbose_name="角色",
                    ),
                ),
            ],
            options={
                "verbose_name": "字段权限表",
                "verbose_name_plural": "字段权限表",
            },
        ),
        migrations.CreateModel(
            name="Area",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="创建时间"),
                ),
                (
                    "created_by",
                    models.CharField(db_index=True, default="", max_length=32, null=True, verbose_name="创建者"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=32, null=True, verbose_name="修改者"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                ("name", models.CharField(max_length=128, verbose_name="名称")),
                ("code", models.CharField(db_index=True, max_length=32, unique=True, verbose_name="地区编码")),
                ("level", models.BigIntegerField(verbose_name="地区层级(1省份 2城市 3区县 4乡级)")),
                ("pinyin", models.CharField(max_length=255, verbose_name="拼音")),
                ("initials", models.CharField(max_length=32, verbose_name="首字母")),
                ("enable", models.BooleanField(default=True, verbose_name="是否启用")),
                (
                    "parent_code",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.area",
                        to_field="code",
                        verbose_name="父地区编码",
                    ),
                ),
            ],
            options={
                "verbose_name": "地区表",
                "verbose_name_plural": "地区表",
            },
        ),
        migrations.AddField(
            model_name="users",
            name="dept",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="account.dept",
                verbose_name="所属部门",
            ),
        ),
        migrations.AddField(
            model_name="users",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="users",
            name="post",
            field=models.ManyToManyField(blank=True, db_constraint=False, to="account.post", verbose_name="关联岗位"),
        ),
        migrations.AddField(
            model_name="users",
            name="role",
            field=models.ManyToManyField(blank=True, db_constraint=False, to="account.role", verbose_name="关联角色"),
        ),
        migrations.AddField(
            model_name="users",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
    ]
