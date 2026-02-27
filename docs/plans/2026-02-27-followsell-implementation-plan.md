# 亚马逊跟卖自动上新功能实现计划

## 计划信息
- **创建日期**: 2026-02-27
- **关联设计文档**: docs/plans/2026-02-27-followsell-design.md
- **预计工期**: 2-3 小时
- **优先级**: 高

## 实现概述

本计划基于已批准的设计文档，实现亚马逊跟卖自动上新功能。该功能将集成到现有的 BU2Ama 系统中，作为第三个主要功能模块。

## 实现任务分解

### 阶段 1：后端核心逻辑实现（60 分钟）

#### 任务 1.1：创建跟卖处理器核心类
**文件**: `backend/app/core/followsell_processor.py`

**实现内容**:
```python
class FollowSellProcessor:
    """跟卖上新处理器"""

    def __init__(self):
        self.field_columns = self._init_field_columns()

    def _init_field_columns(self) -> dict:
        """初始化字段列映射"""
        # 返回字段名到列号的映射

    def extract_product_code(self, sku: str) -> str:
        """从 SKU 中提取产品代码（前7位）"""

    def calculate_launch_date(self) -> datetime:
        """计算上新日期（3PM 规则）"""

    def process(self, old_file_path: str, new_product_code: str) -> dict:
        """主处理函数"""
        # 1. 读取老版本 Excel
        # 2. 识别老产品代码
        # 3. 遍历所有行，更新字段
        # 4. 生成新 Excel
        # 5. 返回处理结果
```

**关键点**:
- 使用 openpyxl 读取和写入 Excel
- 实现 3PM 日期规则（北京时间 15:00 为界）
- 处理 11 个必须修改的字段
- 错误处理和日志记录

**验收标准**:
- 能正确识别老产品代码
- 能正确替换 SKU 中的产品代码
- 价格计算正确（-0.1）
- 日期计算符合 3PM 规则
- 所有 72 个 SKU 都正确处理

---

#### 任务 1.2：创建数据模型
**文件**: `backend/app/models/followsell.py`

**实现内容**:
```python
from pydantic import BaseModel, Field

class FollowSellRequest(BaseModel):
    """跟卖处理请求"""
    new_product_code: str = Field(..., min_length=7, max_length=8)

class FollowSellResponse(BaseModel):
    """跟卖处理响应"""
    success: bool
    message: str
    data: dict | None
```

**验收标准**:
- 数据验证正确
- 类型提示完整

---

#### 任务 1.3：创建 API 路由
**文件**: `backend/app/api/followsell.py`

**实现内容**:
```python
from fastapi import APIRouter, UploadFile, File, Form
from app.core.followsell_processor import FollowSellProcessor
from app.models.followsell import FollowSellRequest, FollowSellResponse

router = APIRouter(prefix="/api/followsell", tags=["followsell"])

@router.post("/process", response_model=FollowSellResponse)
async def process_followsell(
    file: UploadFile = File(...),
    new_product_code: str = Form(...)
):
    """处理跟卖上新"""
    # 1. 保存上传的文件
    # 2. 调用处理器
    # 3. 返回结果
```

**验收标准**:
- API 端点正常工作
- 文件上传处理正确
- 错误处理完善
- 返回数据格式正确

---

#### 任务 1.4：注册路由到主应用
**文件**: `backend/app/main.py`

**实现内容**:
```python
from app.api import followsell

app.include_router(followsell.router)
```

**验收标准**:
- 路由注册成功
- API 文档中显示新端点

---

### 阶段 2：前端 UI 实现（45 分钟）

#### 任务 2.1：创建跟卖上新组件
**文件**: `frontend/src/components/FollowSell/FollowSellUpload.tsx`

**实现内容**:
```typescript
import React, { useState } from 'react';
import { useFollowSellStore } from '@/store/useFollowSellStore';

export const FollowSellUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [newProductCode, setNewProductCode] = useState('');

  const handleUpload = async () => {
    // 调用 API
  };

  return (
    <div>
      {/* 文件上传 */}
      {/* 产品代码输入 */}
      {/* 处理按钮 */}
      {/* 结果显示 */}
    </div>
  );
};
```

**验收标准**:
- UI 布局清晰
- 文件上传功能正常
- 输入验证正确
- 加载状态显示

---

#### 任务 2.2：创建状态管理
**文件**: `frontend/src/store/useFollowSellStore.ts`

**实现内容**:
```typescript
import { create } from 'zustand';

interface FollowSellState {
  uploadedFile: File | null;
  newProductCode: string;
  processing: boolean;
  result: {
    totalSkus: number;
    outputFilename: string;
  } | null;
  setUploadedFile: (file: File | null) => void;
  setNewProductCode: (code: string) => void;
  setProcessing: (processing: boolean) => void;
  setResult: (result: any) => void;
}

export const useFollowSellStore = create<FollowSellState>((set) => ({
  // 实现状态管理
}));
```

**验收标准**:
- 状态管理正确
- 类型定义完整

---

#### 任务 2.3：创建 API 服务
**文件**: `frontend/src/services/followsellApi.ts`

**实现内容**:
```typescript
import axios from '@/lib/axios';

export const followsellApi = {
  process: async (file: File, newProductCode: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('new_product_code', newProductCode);

    const response = await axios.post('/api/followsell/process', formData);
    return response.data;
  },
};
```

**验收标准**:
- API 调用正确
- 错误处理完善

---

#### 任务 2.4：集成到主应用
**文件**: `frontend/src/App.tsx`

**实现内容**:
```typescript
import { FollowSellUpload } from '@/components/FollowSell/FollowSellUpload';

// 添加新的标签页
<Tabs>
  <TabsList>
    <TabsTrigger value="mapping">颜色映射</TabsTrigger>
    <TabsTrigger value="excel">Excel 处理</TabsTrigger>
    <TabsTrigger value="followsell">跟卖上新</TabsTrigger>
  </TabsList>
  <TabsContent value="followsell">
    <FollowSellUpload />
  </TabsContent>
</Tabs>
```

**验收标准**:
- 标签页显示正常
- 组件集成成功

---

### 阶段 3：测试和验证（30 分钟）

#### 任务 3.1：单元测试
**文件**: `backend/tests/test_followsell_processor.py`

**测试用例**:
1. 测试产品代码提取
2. 测试 SKU 替换
3. 测试价格计算
4. 测试日期计算（3PM 规则）
5. 测试完整处理流程

**验收标准**:
- 所有测试通过
- 代码覆盖率 > 80%

---

#### 任务 3.2：集成测试
**测试内容**:
1. 上传示例文件 `EP-ES01846-PH-rarity-老版本表.xlsm`
2. 输入新产品代码 `ES01846`
3. 验证生成的文件与 `EP-ES01846-PH跟卖-rarity-新版本.xlsm` 一致

**验证点**:
- SKU 替换正确
- 价格 -0.1
- ASIN 保持不变
- 日期更新正确
- 其他字段不变

**验收标准**:
- 生成的文件与预期一致
- 所有 72 个 SKU 都正确处理

---

#### 任务 3.3：手动测试
**测试清单**:
- [ ] 上传正确的 Excel 文件
- [ ] 输入正确的产品代码
- [ ] 验证生成的文件字段正确
- [ ] 测试错误文件格式
- [ ] 测试无效产品代码
- [ ] 测试不同时间的日期计算
- [ ] 验证所有 72 个 SKU 都正确处理

**验收标准**:
- 所有测试项通过
- 无明显 bug

---

### 阶段 4：文档和部署（15 分钟）

#### 任务 4.1：更新 README
**文件**: `README.md`

**更新内容**:
- 添加跟卖上新功能说明
- 更新 API 端点列表
- 添加使用示例

---

#### 任务 4.2：提交代码
**提交信息**: "实现跟卖上新功能"

**提交内容**:
- 后端代码
- 前端代码
- 测试代码
- 文档更新

---

## 实现顺序

1. **后端优先**: 先实现后端核心逻辑，确保数据处理正确
2. **前端集成**: 实现前端 UI 和 API 调用
3. **测试验证**: 进行全面测试
4. **文档完善**: 更新文档和提交代码

## 风险和注意事项

### 技术风险
1. **Excel 文件格式兼容性**: 确保支持 .xlsm 和 .xlsx 格式
2. **大文件处理**: 考虑文件大小限制和处理时间
3. **日期时区处理**: 确保 3PM 规则使用北京时间

### 解决方案
1. 使用 openpyxl 库，支持多种格式
2. 设置合理的文件大小限制（50MB）
3. 使用 `timezone(timedelta(hours=8))` 明确指定北京时区

## 验收标准

### 功能验收
- [ ] 能正确上传老版本 Excel 文件
- [ ] 能正确输入新产品代码
- [ ] 能正确生成新版本 Excel 文件
- [ ] 所有 11 个字段都正确修改
- [ ] 3PM 日期规则正确实现
- [ ] 错误处理完善

### 性能验收
- [ ] 72 个 SKU 处理时间 < 2 秒
- [ ] 文件上传和下载流畅

### 代码质量验收
- [ ] 代码符合项目规范
- [ ] 类型提示完整
- [ ] 错误处理完善
- [ ] 日志记录清晰
- [ ] 测试覆盖率 > 80%

## 后续优化

1. **BI 接口集成**: 接入 BI 系统自动匹配老版本 SKU
2. **批量处理**: 支持一次处理多个产品
3. **历史记录**: 记录每次处理的历史
4. **模板管理**: 支持不同的 Excel 模板

## 参考资料

- 设计文档: `docs/plans/2026-02-27-followsell-design.md`
- SOP 文档: `亚马逊跟卖自动上新SOP.md`
- 示例文件: `EP-ES01846-PH-rarity-老版本表.xlsm`, `EP-ES01846-PH跟卖-rarity-新版本.xlsm`
