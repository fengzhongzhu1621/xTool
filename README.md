# xTool

Python Study Notes

# 环境依赖

## PIP源

vim ~/.pip/pip.conf

```
[global]
index-url = http://mirrors.cloud.tencent.com/pypi/simple/
trusted-host = mirrors.cloud.tencent.com
```

使用命令设置

```
pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple/
pip config set global.extra-index-url "<url1> <url2>..."
```

## 安装依赖

``` bash
cargo install --git https://github.com/mitsuhiko/rye rye

# ZSH
echo 'source "$HOME/.rye/env"' >> ~/.zshrc
# BASH
echo 'source "$HOME/.rye/env"' >> ~/.bashrc
# UNIX Shells
echo 'source "$HOME/.rye/env"' >> ~/.profile
# Windows
$USERPROFILE%\.rye\shims 加入到系统的 PATH 环境变量中

# 升级 rye
rye self update
# rye pin命令并不立即改变Python的版本，只是修改配置文件.python-version，在rye sync 执行时才进行实际的修改。
rye pin 3.10
# 第一次执行这个命令的时候，rye会下载一个单独的Python解释器，放置到$HOME/.rye/py目录下，
# 链接到项目的.venv 目录下，因此同一个Python版本在磁盘上只有一份.
# 安装依赖，刷新.lock 结尾的文件
rye sync --verbose

# 可以使用rye toolchain 来查看、拉取和删除Python版本。
# 用来显示所有已经安装的Python版本：
rye toolchain list
# 列出所有可下载的 Python 版本
# 注意已经下载的Python版本不在这个输出中
rye toolchain list --include-downloadable
```

## 安装配置pre-commit

pre-commit 是一款本地的代码规范检查工具，配置pre-commit，有助于代码质量的提升，
详细配置可在此文件中查看：.pre-commit-config.yaml

```bash
rye install pre-commit
pre-commit install --allow-missing-config
pre-commit install --hook-type commit-msg --allow-missing-config
```

## 安装 black
```sh
rye install black
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
