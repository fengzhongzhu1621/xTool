# 1. 安装
```shell
pip install poetry
brew install poetry
choco install poetry
```

# 2. 初始化项目
```shell
poetry new my_project
poetry new my_project
```

# 3. 依赖项管理
## 3.1 添加依赖项
```shell
poetry add requests
poetry add --dev pytest
```

## 3.2 移除依赖项
```shell
poetry remove requests
```

## 3.3 更新依赖项
```shell
poetry update
```

## 3.4 安装依赖
```shell
poetry install
```

# 4. 虚拟环境
Poetry 自动为每个项目创建独立的虚拟环境，无需手动配置。默认情况下，虚拟环境会被存储在 $HOME/.cache/pypoetry/virtualenvs 目录下。

## 4.1 激活虚拟环境
```shell
poetry shell
```

## 4.2 重新创建虚拟环境
```shell
poetry env remove . && poetry install
```

# 5. 构建和发布
```shell
# 会生成 .whl 和 .tar.gz 文件，默认存储在 dist/ 目录中
poetry build
# 将包上传到 PyPI。如果需要指定其他仓库，可以通过 --repository 参数指定
poetry publish
```

# 6. pyproject.toml
```toml
[tool.poetry.scripts]
start = "python my_script.py"
test = "pytest"
```

```shell
poetry run start
poetry run test
```

指定python版本
```shell
[tool.poetry.dependencies]
python = "^3.9"
python = "~3.10.0"
```

# 私有仓库支持
```shell
poetry config repositories.my-repo https://example.com/simple
poetry config http-basic.my-repo username password
```
```shell
[[tool.poetry.source]]
name = "tencent"
url = "https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple"
priority = "supplemental"
```
