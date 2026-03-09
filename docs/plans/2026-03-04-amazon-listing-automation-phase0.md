# 亚马逊上新跟卖系统 - P0 阶段开发计划

## 分支信息
- **分支名称**: `feature/amazon-listing-automation`
- **基于**: `main` 分支
- **创建日期**: 2026-03-04
- **开发阶段**: P0 - 风险预检与质检

## 开发策略

### 核心原则
1. **不影响现有功能**: 所有新功能在独立模块中开发
2. **复用现有逻辑**: 将现有加色加码逻辑作为基础引擎
3. **渐进式集成**: 先独立开发，测试通过后再集成
4. **向后兼容**: 保留现有 API 接口不变

### 代码组织
```
backend/app/
├── core/                      # 现有核心模块（保持不变）
│   ├── color_mapper.py        # 颜色映射（复用）
│   ├── excel_processor.py     # Excel 处理（复用）
│   ├── follow_sell_processor.py  # 跟卖处理（复用）
│   └── export_history.py      # 导出历史（复用）
│
├── services/                  # 新增：领域服务层
│   ├── __init__.py
│   ├── compliance_service.py  # 风险预检服务
│   ├── listing_qa_service.py  # 上架质检服务
│   └── workflow_service.py    # 工作流编排服务
│
├── models/                    # 数据模型
│   ├── compliance.py          # 新增：合规模型
│   ├── listing_qa.py          # 新增：质检模型
│   └── workflow.py            # 新增：工作流模型
│
└── api/                       # API 路由
    ├── compliance.py          # 新增：合规 API
    ├── listing_qa.py          # 新增：质检 API
    └── workflow.py            # 新增：工作流 API
```

## P0 阶段任务分解

### 第 1 周：基础设施搭建

#### 任务 1.1：数据库表结构设计
**文件**: `backend/migrations/001_compliance_tables.sql`

```sql
-- 合规规则表
CREATE TABLE compliance_rules (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR(50) NOT NULL,  -- trademark | ip | forbidden_word | category
    rule_name VARCHAR(100) NOT NULL,
    pattern TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,   -- critical | high | medium | low
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 禁用词库
CREATE TABLE blacklist_keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    reason TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword)
);

-- 质检点配置
CREATE TABLE qa_checkpoints (
    id SERIAL PRIMARY KEY,
    checkpoint_name VARCHAR(100) NOT NULL,
    checkpoint_type VARCHAR(50) NOT NULL,  -- field | image | variant | category
    validation_rule TEXT NOT NULL,
    error_message TEXT,
    severity VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审批记录
CREATE TABLE approval_records (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    approver VARCHAR(50),
    action VARCHAR(20),  -- approved | rejected | pending
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_id (job_id),
    INDEX idx_approver (approver)
);

-- 合规检查历史
CREATE TABLE compliance_check_history (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    check_result JSONB NOT NULL,
    risk_score DECIMAL(5,2),
    flags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_id (job_id)
);
```

#### 任务 1.2：配置管理升级
**文件**: `backend/app/config.py`

```python
# 新增配置项
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/bu2ama"
)

# 合规检查配置
COMPLIANCE_CONFIG = {
    "enable_trademark_check": True,
    "enable_ip_check": True,
    "enable_forbidden_word_check": True,
    "risk_threshold": 0.7,  # 风险分数阈值
}

# 质检配置
QA_CONFIG = {
    "min_title_length": 50,
    "max_title_length": 200,
    "required_images": 5,
    "enable_variant_check": True,
}
```

### 第 2 周：合规服务开发

#### 任务 2.1：合规服务核心类
**文件**: `backend/app/services/compliance_service.py`

```python
"""
合规检查服务
"""
from typing import Dict, List, Any
import re
from app.models.compliance import ComplianceCheckRequest, ComplianceCheckResult

class ComplianceService:
    """合规检查服务"""

    def __init__(self):
        self.trademark_patterns = self._load_trademark_patterns()
        self.ip_patterns = self._load_ip_patterns()
        self.forbidden_words = self._load_forbidden_words()

    def check(self, request: ComplianceCheckRequest) -> ComplianceCheckResult:
        """执行合规检查"""
        flags = []
        risk_score = 0.0

        # 1. 商标词检查
        trademark_result = self._check_trademark(request.title, request.description)
        if trademark_result['violations']:
            flags.extend(trademark_result['violations'])
            risk_score += 0.4

        # 2. IP 词检查
        ip_result = self._check_ip(request.title, request.description)
        if ip_result['violations']:
            flags.extend(ip_result['violations'])
            risk_score += 0.3

        # 3. 禁用词检查
        forbidden_result = self._check_forbidden_words(
            request.title,
            request.description,
            request.bullet_points
        )
        if forbidden_result['violations']:
            flags.extend(forbidden_result['violations'])
            risk_score += 0.2

        # 4. 敏感品类检查
        category_result = self._check_category(request.category)
        if category_result['is_sensitive']:
            flags.append(f"敏感品类: {request.category}")
            risk_score += 0.1

        return ComplianceCheckResult(
            passed=risk_score < 0.7,
            risk_score=min(risk_score, 1.0),
            flags=flags,
            details={
                'trademark': trademark_result,
                'ip': ip_result,
                'forbidden_words': forbidden_result,
                'category': category_result
            }
        )

    def _check_trademark(self, title: str, description: str) -> Dict[str, Any]:
        """检查商标词"""
        violations = []
        text = f"{title} {description}".lower()

        for pattern in self.trademark_patterns:
            if re.search(pattern['pattern'], text, re.IGNORECASE):
                violations.append({
                    'type': 'trademark',
                    'keyword': pattern['name'],
                    'severity': 'critical'
                })

        return {
            'violations': violations,
            'checked': True
        }

    def _check_ip(self, title: str, description: str) -> Dict[str, Any]:
        """检查 IP 词"""
        violations = []
        text = f"{title} {description}".lower()

        for pattern in self.ip_patterns:
            if re.search(pattern['pattern'], text, re.IGNORECASE):
                violations.append({
                    'type': 'ip',
                    'keyword': pattern['name'],
                    'severity': 'high'
                })

        return {
            'violations': violations,
            'checked': True
        }

    def _check_forbidden_words(
        self,
        title: str,
        description: str,
        bullet_points: List[str]
    ) -> Dict[str, Any]:
        """检查禁用词"""
        violations = []
        text = f"{title} {description} {' '.join(bullet_points)}".lower()

        for word in self.forbidden_words:
            if word.lower() in text:
                violations.append({
                    'type': 'forbidden_word',
                    'keyword': word,
                    'severity': 'medium'
                })

        return {
            'violations': violations,
            'checked': True
        }

    def _check_category(self, category: str) -> Dict[str, Any]:
        """检查敏感品类"""
        sensitive_categories = [
            'health', 'medical', 'baby', 'food',
            'cosmetics', 'electronics'
        ]

        is_sensitive = any(
            cat in category.lower()
            for cat in sensitive_categories
        )

        return {
            'is_sensitive': is_sensitive,
            'category': category
        }

    def _load_trademark_patterns(self) -> List[Dict[str, str]]:
        """加载商标词库"""
        # TODO: 从数据库加载
        return [
            {'name': 'Nike', 'pattern': r'\bnike\b'},
            {'name': 'Adidas', 'pattern': r'\badidas\b'},
            {'name': 'Apple', 'pattern': r'\bapple\b'},
        ]

    def _load_ip_patterns(self) -> List[Dict[str, str]]:
        """加载 IP 词库"""
        # TODO: 从数据库加载
        return [
            {'name': 'Disney', 'pattern': r'\bdisney\b'},
            {'name': 'Marvel', 'pattern': r'\bmarvel\b'},
            {'name': 'Pokemon', 'pattern': r'\bpokemon\b'},
        ]

    def _load_forbidden_words(self) -> List[str]:
        """加载禁用词库"""
        # TODO: 从数据库加载
        return [
            'best', 'guarantee', 'cure', 'medical grade',
            'FDA approved', 'clinical', 'therapeutic'
        ]


# 全局实例
compliance_service = ComplianceService()
```

#### 任务 2.2：合规 API 路由
**文件**: `backend/app/api/compliance.py`

```python
"""
合规检查 API 路由
"""
from fastapi import APIRouter, HTTPException
from app.services.compliance_service import compliance_service
from app.models.compliance import (
    ComplianceCheckRequest,
    ComplianceCheckResult
)

router = APIRouter(prefix="/api/compliance", tags=["合规检查"])


@router.post("/check", response_model=ComplianceCheckResult)
async def check_compliance(request: ComplianceCheckRequest):
    """执行合规检查"""
    try:
        result = compliance_service.check(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_compliance_rules():
    """获取合规规则列表"""
    # TODO: 从数据库查询
    return {
        "success": True,
        "data": {
            "trademark_count": 100,
            "ip_count": 50,
            "forbidden_word_count": 200
        }
    }
```

### 第 3 周：质检服务开发

#### 任务 3.1：质检服务核心类
**文件**: `backend/app/services/listing_qa_service.py`

```python
"""
Listing 质检服务
"""
from typing import Dict, List, Any
from app.models.listing_qa import ListingQARequest, ListingQAResult

class ListingQAService:
    """Listing 质检服务"""

    def check(self, request: ListingQARequest) -> ListingQAResult:
        """执行质检"""
        errors = []
        warnings = []
        score = 100.0

        # 1. 字段完整性检查
        field_result = self._check_fields(request)
        errors.extend(field_result['errors'])
        warnings.extend(field_result['warnings'])
        score -= field_result['penalty']

        # 2. 图片规范检查
        image_result = self._check_images(request)
        errors.extend(image_result['errors'])
        warnings.extend(image_result['warnings'])
        score -= image_result['penalty']

        # 3. 变体逻辑检查
        variant_result = self._check_variants(request)
        errors.extend(variant_result['errors'])
        warnings.extend(variant_result['warnings'])
        score -= variant_result['penalty']

        # 4. 类目映射检查
        category_result = self._check_category_mapping(request)
        errors.extend(category_result['errors'])
        warnings.extend(category_result['warnings'])
        score -= category_result['penalty']

        return ListingQAResult(
            passed=len(errors) == 0,
            score=max(score, 0.0),
            errors=errors,
            warnings=warnings,
            details={
                'fields': field_result,
                'images': image_result,
                'variants': variant_result,
                'category': category_result
            }
        )

    def _check_fields(self, request: ListingQARequest) -> Dict[str, Any]:
        """检查字段完整性"""
        errors = []
        warnings = []
        penalty = 0.0

        # 标题检查
        if not request.title:
            errors.append("标题不能为空")
            penalty += 20
        elif len(request.title) < 50:
            warnings.append("标题长度过短，建议至少 50 字符")
            penalty += 5
        elif len(request.title) > 200:
            errors.append("标题长度超过 200 字符")
            penalty += 10

        # 五点描述检查
        if not request.bullet_points or len(request.bullet_points) < 5:
            warnings.append("建议提供至少 5 个要点描述")
            penalty += 5

        # SKU 检查
        if not request.sku:
            errors.append("SKU 不能为空")
            penalty += 20

        return {
            'errors': errors,
            'warnings': warnings,
            'penalty': penalty
        }

    def _check_images(self, request: ListingQARequest) -> Dict[str, Any]:
        """检查图片规范"""
        errors = []
        warnings = []
        penalty = 0.0

        if not request.images or len(request.images) < 5:
            warnings.append("建议提供至少 5 张产品图片")
            penalty += 10

        return {
            'errors': errors,
            'warnings': warnings,
            'penalty': penalty
        }

    def _check_variants(self, request: ListingQARequest) -> Dict[str, Any]:
        """检查变体逻辑"""
        errors = []
        warnings = []
        penalty = 0.0

        # TODO: 实现变体逻辑检查

        return {
            'errors': errors,
            'warnings': warnings,
            'penalty': penalty
        }

    def _check_category_mapping(self, request: ListingQARequest) -> Dict[str, Any]:
        """检查类目映射"""
        errors = []
        warnings = []
        penalty = 0.0

        if not request.category:
            warnings.append("未指定产品类目")
            penalty += 5

        return {
            'errors': errors,
            'warnings': warnings,
            'penalty': penalty
        }


# 全局实例
listing_qa_service = ListingQAService()
```

### 第 4 周：工作流集成

#### 任务 4.1：工作流服务
**文件**: `backend/app/services/workflow_service.py`

```python
"""
工作流编排服务
"""
from typing import Dict, Any
from app.services.compliance_service import compliance_service
from app.services.listing_qa_service import listing_qa_service
from app.core.excel_processor import excel_processor
from app.models.workflow import WorkflowRequest, WorkflowResult

class WorkflowService:
    """工作流编排服务"""

    async def run(self, request: WorkflowRequest) -> WorkflowResult:
        """执行工作流"""
        job_id = self._generate_job_id()

        # 1. 合规检查
        compliance_result = compliance_service.check(request.compliance_data)
        if not compliance_result.passed:
            return WorkflowResult(
                success=False,
                job_id=job_id,
                stage='compliance',
                message='合规检查未通过',
                compliance_result=compliance_result
            )

        # 2. 质检
        qa_result = listing_qa_service.check(request.qa_data)
        if not qa_result.passed:
            return WorkflowResult(
                success=False,
                job_id=job_id,
                stage='qa',
                message='质检未通过',
                qa_result=qa_result
            )

        # 3. 生成 Excel（复用现有引擎）
        output_file = await self._generate_excel(request)

        # 4. 记录历史
        self._save_history(job_id, request, compliance_result, qa_result, output_file)

        return WorkflowResult(
            success=True,
            job_id=job_id,
            stage='completed',
            message='处理成功',
            output_file=output_file,
            compliance_result=compliance_result,
            qa_result=qa_result
        )

    async def _generate_excel(self, request: WorkflowRequest) -> str:
        """生成 Excel（复用现有引擎）"""
        # 调用现有的 excel_processor
        # TODO: 根据 job_type 路由到不同的处理器
        return "output.xlsx"

    def _generate_job_id(self) -> str:
        """生成任务 ID"""
        import uuid
        return uuid.uuid4().hex

    def _save_history(self, job_id: str, request: WorkflowRequest, *args):
        """保存历史记录"""
        # TODO: 保存到数据库
        pass


# 全局实例
workflow_service = WorkflowService()
```

## 复用现有代码的策略

### 1. Excel 处理引擎（完全复用）
```python
# 现有代码保持不变
from app.core.excel_processor import excel_processor

# 在工作流中调用
result = excel_processor.process(...)
```

### 2. 跟卖处理器（完全复用）
```python
# 现有代码保持不变
from app.core.follow_sell_processor import FollowSellProcessor

# 在工作流中调用
processor = FollowSellProcessor()
result = processor.process_skc(...)
```

### 3. 颜色映射（完全复用）
```python
# 现有代码保持不变
from app.core.color_mapper import color_mapper

# 在合规检查中使用
color_name = color_mapper.get(color_code)
```

### 4. 导出历史（扩展）
```python
# 现有代码保持不变，新增字段
from app.core.export_history import export_history

# 添加合规和质检结果
export_history.add_record(
    module='workflow',
    template=template_type,
    params=params,
    result=result,
    compliance_result=compliance_result,  # 新增
    qa_result=qa_result  # 新增
)
```

## 测试策略

### 单元测试
```python
# tests/services/test_compliance_service.py
def test_trademark_check():
    service = ComplianceService()
    request = ComplianceCheckRequest(
        title="Nike Shoes",
        description="Best Nike shoes"
    )
    result = service.check(request)
    assert not result.passed
    assert result.risk_score > 0.7
```

### 集成测试
```python
# tests/api/test_workflow.py
async def test_workflow_with_compliance_failure():
    response = await client.post("/api/workflow/run", json={
        "job_type": "add-color",
        "compliance_data": {
            "title": "Nike Shoes"
        }
    })
    assert response.status_code == 200
    assert response.json()["success"] == False
    assert response.json()["stage"] == "compliance"
```

## 部署计划

### 开发环境
```bash
# 在新分支上开发
git checkout feature/amazon-listing-automation

# 启动服务
docker-compose up
```

### 测试环境
```bash
# 合并到 develop 分支
git checkout develop
git merge feature/amazon-listing-automation

# 部署测试环境
docker-compose -f docker-compose.test.yml up
```

### 生产环境
```bash
# 测试通过后合并到 main
git checkout main
git merge develop

# 部署生产环境
docker-compose -f docker-compose.prod.yml up
```

## 下一步行动

### 本周（第 1 周）
- [ ] 设计数据库表结构
- [ ] 创建 migrations 文件
- [ ] 升级 config.py 配置
- [ ] 搭建基础目录结构

### 下周（第 2 周）
- [ ] 实现 ComplianceService
- [ ] 实现 Compliance API
- [ ] 编写单元测试
- [ ] 准备测试数据

### 第 3 周
- [ ] 实现 ListingQAService
- [ ] 实现 Listing QA API
- [ ] 编写集成测试
- [ ] 前端界面开发

### 第 4 周
- [ ] 实现 WorkflowService
- [ ] 集成现有引擎
- [ ] 端到端测试
- [ ] 文档完善

---

**注意事项**:
1. 所有新代码在 `feature/amazon-listing-automation` 分支开发
2. 不修改现有 `core/` 目录下的代码
3. 通过依赖注入的方式复用现有功能
4. 保持向后兼容，现有 API 不受影响
5. 充分测试后再合并到主分支
