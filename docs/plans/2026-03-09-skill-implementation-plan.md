# BU2Ama Skill 实施计划

## 概述

基于设计方案（`2026-03-09-bu2ama-skill-design.md`），本文档提供具体的实施步骤和代码示例。

## 实施路线图

```
阶段 1: 配置统一 (0.5 天)
  └─ 统一文件命名和路径

阶段 2: CLI 封装 (2 天)
  ├─ 创建 CLI 目录结构
  ├─ 实现环境检查脚本
  ├─ 封装加色加码入口
  ├─ 封装跟卖入口
  └─ 封装文件上传入口

阶段 3: Skill 创建 (1.5 天)
  ├─ 创建 skill 目录
  ├─ 编写 SKILL.md
  ├─ 编写参考文档
  └─ 创建示例

阶段 4: 集成测试 (1 天)
  ├─ 本地测试
  ├─ OpenClaw 集成
  └─ Telegram 端到端测试

总计: 约 5 天
```

## 阶段 1: 配置统一

### 任务 1.1: 检查当前配置

需要确认的配置项：
- [ ] 颜色映射文件：`backend/data/colorMapping.json` 是否存在
- [ ] 跟卖映射文件：当前硬编码为 `新老款映射信息(1).xlsx`
- [ ] 店铺配置：`STORE_CONFIGS` 中的文件名规则
- [ ] 模板配置：`TEMPLATES` 中的模板定义

### 任务 1.2: 统一配置（如需要）

如果发现不一致，需要：
1. 统一文件命名规范
2. 更新 `config.py` 中的路径
3. 更新相关代码引用

## 阶段 2: CLI 封装

### 目录结构

```
backend/app/cli/
├── __init__.py
├── check_env.py          # 环境检查
├── add_color_size.py     # 加色加码 CLI
├── follow_sell.py        # 跟卖 CLI
├── upload_source.py      # 文件上传 CLI
└── utils.py              # 共享工具函数
```

### 2.1 check_env.py

```python
#!/usr/bin/env python3
"""
环境检查脚本
检查 BU2Ama 项目环境是否就绪
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def check_environment() -> Dict[str, Any]:
    """检查环境配置"""
    result = {
        "valid": True,
        "project_root": None,
        "python_version": None,
        "dependencies": {},
        "files": {},
        "indexes": {},
        "warnings": [],
        "errors": []
    }

    # 1. 检查项目根目录
    current = Path.cwd()
    if (current / "backend" / "app" / "config.py").exists():
        result["project_root"] = str(current)
    elif (current.parent / "backend" / "app" / "config.py").exists():
        result["project_root"] = str(current.parent)
    else:
        result["valid"] = False
        result["errors"].append("未找到 BU2Ama 项目根目录")
        return result

    project_root = Path(result["project_root"])

    # 2. 检查 Python 版本
    import platform
    result["python_version"] = platform.python_version()

    # 3. 检查依赖
    dependencies = ["openpyxl", "fastapi", "pydantic"]
    for dep in dependencies:
        try:
            __import__(dep)
            result["dependencies"][dep] = "installed"
        except ImportError:
            result["dependencies"][dep] = "missing"
            result["errors"].append(f"缺少依赖: {dep}")
            result["valid"] = False

    # 4. 检查必需文件
    files_to_check = {
        "color_mapping": project_root / "backend" / "data" / "colorMapping.json",
        "follow_sell_mapping": project_root / "backend" / "data" / "新老款映射信息(1).xlsx",
        "uploads_dir": project_root / "backend" / "uploads",
        "results_dir": project_root / "backend" / "results"
    }

    for name, path in files_to_check.items():
        if path.exists():
            result["files"][name] = "exists"
        else:
            result["files"][name] = "missing"
            if name in ["color_mapping", "follow_sell_mapping"]:
                result["errors"].append(f"缺少文件: {path}")
                result["valid"] = False
            else:
                result["warnings"].append(f"目录不存在: {path}")

    # 5. 检查店铺索引
    uploads_dir = project_root / "backend" / "uploads"
    for store in ["EP", "DM", "PZ"]:
        index_path = uploads_dir / f"excel_index_{store}.db"
        follow_index_path = uploads_dir / f"ep_index_{store}.db"

        if index_path.exists() and follow_index_path.exists():
            result["indexes"][store] = "exists"
        elif index_path.exists() or follow_index_path.exists():
            result["indexes"][store] = "partial"
            result["warnings"].append(f"{store} 店铺索引不完整")
        else:
            result["indexes"][store] = "missing"
            result["warnings"].append(f"{store} 店铺索引缺失（首次使用时会自动创建）")

    return result

def main():
    """主函数"""
    result = check_environment()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()
```

### 2.2 add_color_size.py

```python
#!/usr/bin/env python3
"""
加色加码 CLI 入口
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.excel_processor import ExcelProcessor
from app.config import UPLOADS_DIR, RESULTS_DIR

def main():
    parser = argparse.ArgumentParser(description="加色加码处理")
    parser.add_argument("--template", required=True, help="模板文件名")
    parser.add_argument("--store", required=True, choices=["EP", "DM", "PZ"], help="店铺类型")
    parser.add_argument("--sources", nargs="+", help="源文件列表")
    parser.add_argument("--price-report", help="价格报告文件")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    try:
        processor = ExcelProcessor()

        # 确定源文件
        if args.sources:
            source_files = args.sources
        else:
            # 自动查找店铺源文件
            source_files = []
            for i in range(3):
                filename = f"{args.store}-{i}.xlsm"
                if (UPLOADS_DIR / filename).exists():
                    source_files.append(filename)

        if not source_files:
            raise ValueError(f"未找到 {args.store} 店铺的源文件")

        # 执行处理
        output_file, processed_count = processor.process_excel_new(
            template_filename=args.template,
            source_filenames=source_files,
            price_report_filename=args.price_report
        )

        result = {
            "success": True,
            "output_file": str(output_file),
            "processed_count": processed_count,
            "skipped_count": 0,  # TODO: 从处理器获取
            "errors": [],
            "warnings": []
        }

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"✅ 处理完成")
            print(f"输出文件: {output_file}")
            print(f"处理数量: {processed_count}")

        sys.exit(0)

    except Exception as e:
        result = {
            "success": False,
            "output_file": None,
            "processed_count": 0,
            "skipped_count": 0,
            "errors": [str(e)],
            "warnings": []
        }

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 处理失败: {e}", file=sys.stderr)

        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2.3 follow_sell.py

```python
#!/usr/bin/env python3
"""
跟卖 CLI 入口
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.follow_sell_processor import FollowSellProcessor

def main():
    parser = argparse.ArgumentParser(description="跟卖查询")
    parser.add_argument("--skc", nargs="+", help="SKC 列表")
    parser.add_argument("--skc-file", help="SKC 列表文件（每行一个）")
    parser.add_argument("--store", required=True, choices=["EP", "DM", "PZ"], help="店铺类型")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    try:
        # 获取 SKC 列表
        skc_list = []
        if args.skc:
            skc_list = args.skc
        elif args.skc_file:
            with open(args.skc_file, "r", encoding="utf-8") as f:
                skc_list = [line.strip() for line in f if line.strip()]
        else:
            raise ValueError("必须提供 --skc 或 --skc-file")

        processor = FollowSellProcessor()

        results = []
        not_found = []

        for skc in skc_list:
            try:
                # 调用跟卖处理器
                size_info = processor.process_skc(skc, template_type=f"{args.store}US")

                results.append({
                    "skc": skc,
                    "old_style": size_info.get("old_style"),
                    "sizes": size_info.get("sizes", []),
                    "source_files": size_info.get("source_files", [])
                })
            except Exception as e:
                not_found.append(skc)

        result = {
            "success": True,
            "results": results,
            "not_found": not_found,
            "errors": []
        }

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"✅ 查询完成")
            print(f"找到: {len(results)} 个")
            print(f"未找到: {len(not_found)} 个")
            for item in results:
                print(f"\n{item['skc']} → {item['old_style']}")
                print(f"  尺码: {', '.join(item['sizes'])}")

        sys.exit(0)

    except Exception as e:
        result = {
            "success": False,
            "results": [],
            "not_found": [],
            "errors": [str(e)]
        }

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 查询失败: {e}", file=sys.stderr)

        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2.4 upload_source.py

```python
#!/usr/bin/env python3
"""
源文件上传处理 CLI
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.config import UPLOADS_DIR
from app.core.excel_processor import ExcelProcessor

def main():
    parser = argparse.ArgumentParser(description="源文件上传")
    parser.add_argument("--file", required=True, help="上传的文件路径")
    parser.add_argument("--store", choices=["EP", "DM", "PZ"], help="店铺类型（可自动识别）")
    parser.add_argument("--rebuild-index", action="store_true", help="重建索引")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    try:
        source_file = Path(args.file)
        if not source_file.exists():
            raise FileNotFoundError(f"文件不存在: {args.file}")

        # 识别店铺类型
        processor = ExcelProcessor()
        if args.store:
            store = args.store
        else:
            store = processor.get_store_prefix(source_file.name)

        # 复制文件到 uploads 目录
        dest_file = UPLOADS_DIR / source_file.name
        shutil.copy2(source_file, dest_file)

        # 重建索引（如果需要）
        sku_count = 0
        if args.rebuild_index:
            # TODO: 调用索引重建逻辑
            pass

        result = {
            "success": True,
            "file_saved": str(dest_file),
            "store": store,
            "index_rebuilt": args.rebuild_index,
            "sku_count": sku_count,
            "errors": []
        }

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"✅ 文件上传成功")
            print(f"保存位置: {dest_file}")
            print(f"店铺类型: {store}")
            if args.rebuild_index:
                print(f"索引已重建，SKU 数量: {sku_count}")

        sys.exit(0)

    except Exception as e:
        result = {
            "success": False,
            "file_saved": None,
            "store": None,
            "index_rebuilt": False,
            "sku_count": 0,
            "errors": [str(e)]
        }

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 上传失败: {e}", file=sys.stderr)

        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 阶段 3: Skill 创建

### 3.1 创建 Skill 目录

```bash
mkdir -p ~/.claude/skills/bu2ama-listing-ops/{scripts,references,examples}
```

### 3.2 SKILL.md 内容

见下一个文件...

## 阶段 4: 测试计划

### 4.1 本地测试

```bash
# 测试环境检查
cd /path/to/BU2Ama
python backend/app/cli/check_env.py

# 测试加色加码
python backend/app/cli/add_color_size.py \
  --template EPUS模板.xlsx \
  --store EP \
  --json

# 测试跟卖
python backend/app/cli/follow_sell.py \
  --skc ES01819NT \
  --store EP \
  --json

# 测试文件上传
python backend/app/cli/upload_source.py \
  --file /path/to/EP-3.xlsm \
  --rebuild-index \
  --json
```

### 4.2 Skill 测试

```bash
# 在 Claude Code 中测试
# 触发词："帮我加色加码"
# 预期：skill 被触发，执行环境检查，调用 CLI
```

### 4.3 Telegram 集成测试

```
1. 上传文件测试
   - 用户上传 EP-3.xlsm
   - 验证文件保存到 backend/uploads/
   - 验证索引重建

2. 加色加码测试
   - 用户："帮我生成 EPUS 加色表"
   - 验证 CLI 调用
   - 验证结果文件返回

3. 跟卖查询测试
   - 用户："查询 ES01819NT 的尺码"
   - 验证查询结果
   - 验证格式化输出
```

## 下一步行动

1. **立即执行**：
   - [ ] 检查配置文件一致性
   - [ ] 创建 `backend/app/cli/` 目录
   - [ ] 实现 `check_env.py`

2. **本周完成**：
   - [ ] 实现三个 CLI 脚本
   - [ ] 创建 skill 目录和文档
   - [ ] 本地测试验证

3. **下周完成**：
   - [ ] OpenClaw 集成
   - [ ] Telegram 端到端测试
   - [ ] 文档完善和优化
