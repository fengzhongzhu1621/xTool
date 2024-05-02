# xTool

Python Study Notes

# 环境依赖

## PIP源

    ```
    [global]
    index-url=https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple
    extra-index-url=http://mirrors.cloud.tencent.com/pypi/simple/
    trusted-host = mirrors.tencent.com, mirrors.cloud.tencent.com
    ```

## 安装依赖

``` bash
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

## 安装配置pre-commit

pre-commit 是一款本地的代码规范检查工具，配置pre-commit，有助于代码质量的提升，
详细配置可在此文件中查看：.pre-commit-config.yaml

```bash
pip install pre-commit
pre-commit install --allow-missing-config
pre-commit install --hook-type commit-msg --allow-missing-config
```

## 配置DB

创建本地数据库

```
CREATE DATABASE IF NOT EXISTS `db_test_xtool` DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
```

## 启动服务

使用IDE或者在项目根目录执行(命令行启动需要提前配置好环境变量，export DJANGO_SETTINGS_MODULE=settings):

```bash
python manage.py migrate
python manage.py runserver
```

## 配置文件覆盖顺序

```
config.default -> config.{env}
    默认配置    ->    环境配置

INSTALLED_APPS 应在模块的配置中进行覆盖式声明
所有需要对用户开放的配置都建议使用 os.getenv 或 get_env_or_raise 获取
```
