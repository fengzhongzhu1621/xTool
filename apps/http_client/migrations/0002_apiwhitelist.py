# Generated by Django 4.2.13 on 2024-05-30 14:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("http_client", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApiWhiteList",
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
                ("url", models.CharField(max_length=32, verbose_name="url地址")),
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
                        default="GET",
                        max_length=32,
                        null=True,
                        verbose_name="接口请求方法",
                    ),
                ),
                ("enable_datasource", models.BooleanField(blank=True, default=True, verbose_name="激活数据权限")),
            ],
            options={
                "verbose_name": "接口白名单",
                "verbose_name_plural": "接口白名单",
            },
        ),
    ]
