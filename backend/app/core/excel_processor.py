"""
Excel 处理模块
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.config import UPLOADS_DIR, TEMPLATES
from app.core.color_mapper import color_mapper
from app.models.excel import SKUInfo, ColorDistribution, AnalysisResult


class ExcelProcessor:
    """Excel 处理器"""

    def parse_sku(self, sku: str) -> Optional[SKUInfo]:
        """解析 SKU 格式

        格式：前7位(Style) + 2位(颜色) + 2位(尺码) + 后缀
        例如：ES0128BDG02-PH
        - ES0128B: Style (7位)
        - DG: 颜色代码 (2位)
        - 02: 尺码 (2位)
        - -PH: 后缀
        """
        sku = sku.strip().upper()

        # 最小长度：7(style) + 2(color) + 2(size) = 11
        if len(sku) < 11:
            return None

        # 按位置提取
        product_code = sku[:7]  # 前7位
        color_code = sku[7:9]   # 8-9位
        size = sku[9:11]        # 10-11位
        suffix = sku[11:] if len(sku) > 11 else ""  # 剩余部分

        # 验证格式
        if not color_code.isalpha() or not color_code.isupper():
            return None
        if not size.isdigit():
            return None

        return SKUInfo(
            sku=sku,
            product_code=product_code,
            color_code=color_code,
            size=size,
            suffix=suffix
        )

    def extract_color_from_sku(self, sku: str) -> Optional[str]:
        """从 SKU 中提取颜色代码"""
        info = self.parse_sku(sku)
        return info.color_code if info else None

    def analyze_excel_file(self, filename: str) -> AnalysisResult:
        """分析 Excel 文件"""
        filepath = UPLOADS_DIR / filename

        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filename}")

        # 读取 Excel 文件
        wb = openpyxl.load_workbook(filepath, data_only=True)

        # 尝试使用 Template 工作表，如果不存在则使用活动工作表
        if 'Template' in wb.sheetnames:
            ws = wb['Template']
        else:
            ws = wb.active

        # 统计数据
        color_counts: Dict[str, int] = {}
        unknown_colors: set = set()
        prefixes: set = set()
        suffixes: set = set()
        total_skus = 0

        # 检测文件格式
        # EP-0/1/2.xlsm: SKU 在列 2（索引 2），从第 7 行开始
        # 其他模板: SKU 在列 1（索引 1），从第 4 行开始

        # 检查第 4 行的字段名
        row4 = list(ws[4])
        if len(row4) > 2 and row4[2].value and 'SKU' in str(row4[2].value):
            # EP-0/1/2.xlsm 格式
            sku_col = 2
            start_row = 7
        else:
            # 其他模板格式
            sku_col = 1
            start_row = 4

        # 遍历所有行
        for row in ws.iter_rows(min_row=start_row, values_only=True):
            if not row or len(row) <= sku_col or not row[sku_col]:
                continue

            sku = str(row[sku_col]).strip()
            info = self.parse_sku(sku)

            if info:
                total_skus += 1

                # 统计颜色
                color_code = info.color_code
                color_counts[color_code] = color_counts.get(color_code, 0) + 1

                # 检查是否为未知颜色
                if not color_mapper.get_color_name(color_code):
                    unknown_colors.add(color_code)

                # 收集前缀和后缀
                prefixes.add(info.product_code)
                if info.suffix:
                    suffixes.add(info.suffix)

        wb.close()

        # 构建颜色分布列表
        color_distribution = [
            ColorDistribution(
                color_code=code,
                color_name=color_mapper.get_color_name(code),
                count=count
            )
            for code, count in sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return AnalysisResult(
            success=True,
            filename=filename,
            total_skus=total_skus,
            unique_colors=len(color_counts),
            color_distribution=color_distribution,
            unknown_colors=sorted(unknown_colors),
            prefixes=sorted(prefixes),
            suffixes=sorted(suffixes)
        )

    def get_color_map_value(self, color_name: str) -> str:
        """获取颜色分类"""
        color_lower = color_name.lower()

        color_categories = {
            'Purple': ['purple', 'violet', 'lavender', 'plum'],
            'Blue': ['blue', 'navy', 'azure', 'cyan', 'teal'],
            'Green': ['green', 'olive', 'lime', 'mint'],
            'Red': ['red', 'crimson', 'burgundy', 'wine'],
            'Pink': ['pink', 'rose', 'coral', 'fuchsia'],
            'Orange': ['orange', 'peach', 'apricot'],
            'Yellow': ['yellow', 'gold', 'cream', 'beige'],
            'Brown': ['brown', 'tan', 'khaki', 'coffee', 'chocolate'],
            'Black': ['black'],
            'White': ['white', 'ivory'],
            'Grey': ['grey', 'gray', 'silver'],
            'Multicolor': ['multicolor', 'multi', 'print', 'pattern']
        }

        for category, keywords in color_categories.items():
            if any(keyword in color_lower for keyword in keywords):
                return category

        return 'Multicolor'

    def calculate_launch_date(self) -> str:
        """计算上线日期（北京时间逻辑）"""
        # 获取当前 UTC 时间
        utc_now = datetime.utcnow()

        # 转换为北京时间（UTC+8）
        beijing_time = utc_now + timedelta(hours=8)

        # 如果北京时间在下午 3 点之前，使用前一天
        if beijing_time.hour < 15:
            launch_date = beijing_time - timedelta(days=1)
        else:
            launch_date = beijing_time

        return launch_date.strftime('%Y-%m-%d')

    def process_excel_new(
        self,
        template_filename: str,
        source_filenames: List[str],
        price_report_filename: Optional[str] = None
    ) -> Tuple[str, int]:
        """新的处理逻辑：从源文件中查找 SKU 数据并更新模板

        Args:
            template_filename: 输入模板文件（包含需要处理的 SKU）
            source_filenames: 数据源文件列表（EP-0/1/2.xlsm）
            price_report_filename: 价格报告文件（All Listings Report）

        Returns:
            (输出文件名, 处理的行数)
        """

        # 1. 读取价格报告
        price_map = {}
        if price_report_filename:
            price_file = UPLOADS_DIR / price_report_filename
            if price_file.exists():
                # 尝试不同的编码
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(price_file, 'r', encoding=encoding) as f:
                            lines = f.readlines()
                            if len(lines) > 1:
                                # 第一行是表头
                                headers = lines[0].strip().split('\t')
                                sku_idx = headers.index('seller-sku') if 'seller-sku' in headers else -1
                                price_idx = headers.index('price') if 'price' in headers else -1

                                if sku_idx >= 0 and price_idx >= 0:
                                    for line in lines[1:]:
                                        fields = line.strip().split('\t')
                                        if len(fields) > max(sku_idx, price_idx):
                                            sku = fields[sku_idx]
                                            try:
                                                price = float(fields[price_idx])
                                                price_map[sku] = price
                                            except (ValueError, IndexError):
                                                pass
                        break  # 成功读取，跳出循环
                    except UnicodeDecodeError:
                        continue  # 尝试下一个编码

        print(f"从价格报告加载了 {len(price_map)} 个价格")

        # 2. 读取源文件数据（EP-0/1/2.xlsm）
        source_data = {}  # sku -> row_data

        for source_filename in source_filenames:
            print(f"正在读取源文件: {source_filename}")
            source_path = UPLOADS_DIR / source_filename
            if not source_path.exists():
                print(f"  文件不存在，跳过")
                continue

            wb = openpyxl.load_workbook(source_path, data_only=True, read_only=True)
            ws = wb['Template']

            # 从第 7 行开始读取数据
            row_count = 0
            for row_idx in range(7, ws.max_row + 1):
                row = list(ws[row_idx])
                if len(row) > 2 and row[2].value:
                    sku = str(row[2].value).strip().upper()
                    # 保存整行数据（只保存有值的单元格）
                    source_data[sku] = [(cell.value if cell.value is not None else '') for cell in row]
                    row_count += 1

                    if row_count % 1000 == 0:
                        print(f"  已读取 {row_count} 行")

            wb.close()
            print(f"  完成，共读取 {row_count} 行")

        print(f"从源文件加载了 {len(source_data)} 个 SKU 数据")

        # 3. 读取模板文件
        template_path = UPLOADS_DIR / template_filename
        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_filename}")

        wb_template = openpyxl.load_workbook(template_path)
        ws_template = wb_template['Template']

        # 4. 处理模板中的 SKU
        print(f"正在处理模板文件...")
        processed_count = 0

        # 从第 7 行开始处理（假设模板也是相同格式）
        for row_idx in range(7, ws_template.max_row + 1):
            row = list(ws_template[row_idx])
            if len(row) > 2 and row[2].value:
                sku = str(row[2].value).strip().upper()

                # 在源数据中查找
                if sku in source_data:
                    source_row = source_data[sku]

                    # 复制源数据到模板
                    for col_idx, value in enumerate(source_row):
                        if value:  # 只复制非空值
                            ws_template.cell(row=row_idx, column=col_idx + 1, value=value)

                    # 更新价格（如果有）
                    if sku in price_map:
                        # 假设价格在列 15（Your Price）
                        ws_template.cell(row=row_idx, column=16, value=price_map[sku])

                    processed_count += 1

                    if processed_count % 100 == 0:
                        print(f"  已处理 {processed_count} 行")

        print(f"处理完成，共处理 {processed_count} 行")

        # 5. 保存输出文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"processed_{timestamp}.xlsx"
        output_path = UPLOADS_DIR / output_filename

        wb_template.save(output_path)
        wb_template.close()

        return output_filename, processed_count

    def process_excel(
        self,
        template_type: str,
        filenames: List[str],
        selected_prefixes: List[str],
        target_color: Optional[str] = None,
        target_size: Optional[str] = None
    ) -> Tuple[str, int]:
        """处理 Excel 文件并生成新文件 - 直接复制输入文件格式

        Args:
            template_type: 模板类型（DaMaUS 或 EPUS，决定图片 URL 格式）
            filenames: 输入文件列表
            selected_prefixes: 选中的产品前缀
            target_color: 目标颜色代码（加色模式：替换颜色）
            target_size: 目标尺码（加码模式：替换尺码）
        """

        print(f"[DEBUG] template_type = {template_type}")
        print(f"[DEBUG] image_variant = {TEMPLATES[template_type]['image_variant']}")

        if not filenames:
            raise ValueError("没有输入文件")

        # 如果指定了目标颜色，验证颜色是否存在
        if target_color:
            target_color = target_color.upper()
            target_color_name = color_mapper.get_color_name(target_color)
            if not target_color_name:
                raise ValueError(f"未知的目标颜色代码: {target_color}")

        # 使用第一个文件作为基础
        source_filename = filenames[0]
        source_filepath = UPLOADS_DIR / source_filename

        if not source_filepath.exists():
            raise FileNotFoundError(f"文件不存在: {source_filename}")

        print(f"正在加载源文件: {source_filename}")

        # 加载源文件（不使用 read_only，因为需要复制格式）
        source_wb = openpyxl.load_workbook(source_filepath)

        # 获取 Template 工作表
        if 'Template' in source_wb.sheetnames:
            source_ws = source_wb['Template']
        else:
            source_ws = source_wb.active

        print(f"使用工作表: {source_ws.title}, 最大行数: {source_ws.max_row}")

        # 创建输出工作簿
        output_wb = openpyxl.Workbook()
        output_wb.remove(output_wb.active)  # 删除默认 sheet
        output_ws = output_wb.create_sheet(title="Template")

        # 复制前 3 行（表头）
        print("正在复制表头...")
        for row_idx in range(1, 4):
            for col_idx, source_cell in enumerate(source_ws[row_idx], start=1):
                target_cell = output_ws.cell(row=row_idx, column=col_idx)
                target_cell.value = source_cell.value

                # 复制格式
                if source_cell.has_style:
                    target_cell.font = source_cell.font.copy()
                    target_cell.border = source_cell.border.copy()
                    target_cell.fill = source_cell.fill.copy()
                    target_cell.number_format = source_cell.number_format
                    target_cell.protection = source_cell.protection.copy()
                    target_cell.alignment = source_cell.alignment.copy()

        # 复制列宽
        for col_letter in source_ws.column_dimensions:
            if col_letter in source_ws.column_dimensions:
                output_ws.column_dimensions[col_letter].width = source_ws.column_dimensions[col_letter].width

        # 复制行高（前 3 行）
        for row_num in range(1, 4):
            if row_num in source_ws.row_dimensions:
                output_ws.row_dimensions[row_num].height = source_ws.row_dimensions[row_num].height

        print("表头复制完成")

        # 处理数据行（从第 4 行开始）
        processed_count = 0
        output_row_idx = 4  # 输出文件的行索引

        print("正在处理数据行...")
        for source_row_idx in range(4, source_ws.max_row + 1):
            # SKU 在第 2 列（B列）
            sku_cell = source_ws.cell(row=source_row_idx, column=2)

            if not sku_cell.value:
                continue

            sku = str(sku_cell.value).strip()
            info = self.parse_sku(sku)

            # 只处理选中的产品前缀
            if not info or info.product_code not in selected_prefixes:
                continue

            # 复制整行
            for col_idx in range(1, source_ws.max_column + 1):
                source_cell = source_ws.cell(row=source_row_idx, column=col_idx)
                target_cell = output_ws.cell(row=output_row_idx, column=col_idx)

                # 复制值
                target_cell.value = source_cell.value

                # 复制格式
                if source_cell.has_style:
                    target_cell.font = source_cell.font.copy()
                    target_cell.border = source_cell.border.copy()
                    target_cell.fill = source_cell.fill.copy()
                    target_cell.number_format = source_cell.number_format
                    target_cell.protection = source_cell.protection.copy()
                    target_cell.alignment = source_cell.alignment.copy()

            # 复制行高
            if source_row_idx in source_ws.row_dimensions:
                output_ws.row_dimensions[output_row_idx].height = source_ws.row_dimensions[source_row_idx].height

            # 应用计算逻辑和特殊处理
            # 1. Quantity (col 17) - 默认值 5
            output_ws.cell(row=output_row_idx, column=17).value = 5

            # 2. Parentage (col 83) - 固定值 "Child"
            output_ws.cell(row=output_row_idx, column=83).value = "Child"

            # 3. 价格计算
            your_price_cell = output_ws.cell(row=output_row_idx, column=16)
            if your_price_cell.value:
                try:
                    your_price = float(your_price_cell.value)

                    # List Price (col 513) - 不填写，留空
                    # output_ws.cell(row=output_row_idx, column=513).value = your_price + 10

                    # Business Price (col 537) = Your Price - 1
                    business_price = your_price - 1
                    output_ws.cell(row=output_row_idx, column=537).value = business_price

                    # Quantity Price 1 (col 540) = Business Price * 0.95
                    output_ws.cell(row=output_row_idx, column=540).value = business_price * 0.95

                    # Quantity Price 2 (col 542) = Business Price * 0.92
                    output_ws.cell(row=output_row_idx, column=542).value = business_price * 0.92

                    # Quantity Price 3 (col 544) = Business Price * 0.90
                    output_ws.cell(row=output_row_idx, column=544).value = business_price * 0.90
                except (ValueError, TypeError):
                    pass

            # 4. Launch Date (col 532) - 北京时间逻辑
            launch_date = self.calculate_launch_date()
            output_ws.cell(row=output_row_idx, column=532).value = launch_date

            # 5. 处理图片 URL
            # 加码模式：所有图片都从输入文件复制，不生成新的
            # 加色模式：Main Image + Other Image 1-4 生成新的，Other Image 5（尺码图）从输入复制

            # 确定使用的颜色代码（加色模式用目标颜色，加码模式用原始颜色）
            color_code = target_color if target_color else info.color_code

            # 只有在加色模式下才生成图片 URL
            if target_color:

                # 判断店铺类型和后缀
                suffix = info.suffix
                is_ph_suffix = (suffix == "-PH")

                # 根据模板类型选择图片 URL 格式
                image_variant = TEMPLATES[template_type]["image_variant"]

                # 生成图片 URL
                if is_ph_suffix:
                    # PH 后缀：L101-105
                    main_image_url = f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}101.jpg"
                    other_image_urls = [
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}102.jpg",
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}103.jpg",
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}104.jpg",
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}105.jpg",
                    ]
                else:
                    # 非 PH 后缀：L1-5
                    main_image_url = f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}1.jpg"
                    other_image_urls = [
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}2.jpg",
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}3.jpg",
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}4.jpg",
                        f"https://eppic.s3.amazonaws.com/{info.product_code}{color_code}-{image_variant}5.jpg",
                    ]

                # 设置图片 URL
                output_ws.cell(row=output_row_idx, column=73).value = main_image_url  # Main Image
                output_ws.cell(row=output_row_idx, column=74).value = other_image_urls[0]  # Other Image 1
                output_ws.cell(row=output_row_idx, column=75).value = other_image_urls[1]  # Other Image 2
                output_ws.cell(row=output_row_idx, column=76).value = other_image_urls[2]  # Other Image 3
                output_ws.cell(row=output_row_idx, column=77).value = other_image_urls[3]  # Other Image 4
                # Other Image 5 (col 78, 尺码图) - 从输入文件复制，已经在复制整行时处理

                # Swatch Image (col 82) - 使用 Main Image
                output_ws.cell(row=output_row_idx, column=82).value = main_image_url

            # 加码模式：所有图片已经在复制整行时复制了，不需要额外处理
            # Swatch Image 在加码模式下也使用输入文件的 Main Image
            if target_size and not target_color:
                main_image_value = output_ws.cell(row=output_row_idx, column=73).value
                output_ws.cell(row=output_row_idx, column=82).value = main_image_value

            # 7. Colour Map (col 112) - 颜色分类
            color_name = color_mapper.get_color_name(color_code)
            if color_name:
                colour_map = self.get_color_map_value(color_name)
                output_ws.cell(row=output_row_idx, column=112).value = colour_map

            # 8. Generic Keyword (col 95) - 剔除颜色相关部分
            generic_keyword_cell = output_ws.cell(row=output_row_idx, column=95)
            if generic_keyword_cell.value:
                generic_keyword = str(generic_keyword_cell.value)

                # 如果替换颜色，需要替换关键词中的颜色名称
                if target_color and target_color != info.color_code:
                    original_color_name = color_mapper.get_color_name(info.color_code)
                    target_color_name_lower = target_color_name.lower() if target_color_name else ""

                    if original_color_name:
                        # 替换颜色名称（小写）
                        original_color_lower = original_color_name.lower()
                        generic_keyword = generic_keyword.replace(original_color_lower, target_color_name_lower)

                        # 也替换可能的颜色变体（如 "mint green" -> "dark green"）
                        # 移除旧颜色的修饰词
                        color_variants = [
                            f"mint {original_color_lower}",
                            f"light {original_color_lower}",
                            f"dark {original_color_lower}",
                            f"bright {original_color_lower}",
                        ]
                        for variant in color_variants:
                            if variant in generic_keyword:
                                generic_keyword = generic_keyword.replace(variant, target_color_name_lower)

                output_ws.cell(row=output_row_idx, column=95).value = generic_keyword

            # 9. 如果需要替换颜色（加色模式）
            if target_color:
                original_color = info.color_code
                original_color_name = color_mapper.get_color_name(original_color)

                if original_color != target_color and original_color_name:
                    # 替换 SKU 中的颜色代码（第 2 列）
                    new_sku = sku.replace(f"{info.product_code}{original_color}",
                                        f"{info.product_code}{target_color}")
                    output_ws.cell(row=output_row_idx, column=2).value = new_sku

                    # 同步更新 Style Number（第 10 列）和 Manufacturer Part Number（第 13 列）
                    output_ws.cell(row=output_row_idx, column=10).value = new_sku
                    output_ws.cell(row=output_row_idx, column=13).value = new_sku

                    # 替换产品名称中的颜色名称（第 5 列）
                    name_cell = output_ws.cell(row=output_row_idx, column=5)
                    if name_cell.value:
                        product_name = str(name_cell.value)

                        # 使用正则表达式匹配所有颜色变体
                        import re

                        # 提取颜色的基础词（如 "Dark Green" -> "Green"）
                        color_base = original_color_name.split()[-1]  # 取最后一个词作为基础颜色

                        # 匹配模式：可选修饰词 + 颜色基础词
                        # 例如：Dark Green, Light Green, Mint Green, Dreen Green, Green
                        color_pattern = r'\b(?:Dark|Light|Mint|Bright|Deep|Pale|Dreen)?\s*' + re.escape(color_base) + r'\b'
                        product_name = re.sub(color_pattern, target_color_name, product_name, flags=re.IGNORECASE)

                        name_cell.value = product_name

                    # 替换颜色列（第 136 列）
                    output_ws.cell(row=output_row_idx, column=136).value = target_color_name

            # 10. 如果需要替换尺码（加码模式）
            if target_size:
                original_size = info.size

                if original_size != target_size:
                    # 替换 SKU 中的尺码（10-11位）
                    new_sku = sku.replace(f"{info.product_code}{info.color_code}{original_size}",
                                        f"{info.product_code}{info.color_code}{target_size}")
                    output_ws.cell(row=output_row_idx, column=2).value = new_sku

                    # 同步更新 Style Number（第 10 列）和 Manufacturer Part Number（第 13 列）
                    output_ws.cell(row=output_row_idx, column=10).value = new_sku
                    output_ws.cell(row=output_row_idx, column=13).value = new_sku

                    # 替换产品名称中的尺码（第 5 列）
                    name_cell = output_ws.cell(row=output_row_idx, column=5)
                    if name_cell.value:
                        # 替换 US02 -> US{target_size}
                        name_cell.value = str(name_cell.value).replace(f"US{original_size}", f"US{target_size}")

                    # 替换 Apparel Size Value（第 30 列）- 去掉前导零
                    size_without_leading_zero = str(int(target_size))  # "05" -> "5"
                    output_ws.cell(row=output_row_idx, column=30).value = size_without_leading_zero

                    # 替换 size_map 列（第 299 列，KM 列）- 去掉前导零
                    output_ws.cell(row=output_row_idx, column=299).value = size_without_leading_zero

                    # 替换 SIZE 列（第 153 列，EW 列）- 去掉前导零
                    output_ws.cell(row=output_row_idx, column=153).value = size_without_leading_zero

            processed_count += 1
            output_row_idx += 1

            if processed_count % 100 == 0:
                print(f"  已处理 {processed_count} 行")

        print(f"数据处理完成，共处理 {processed_count} 行")

        # 保存输出文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"processed_{timestamp}.xlsx"
        output_path = UPLOADS_DIR / output_filename

        output_wb.save(output_path)
        output_wb.close()
        source_wb.close()

        return output_filename, processed_count


# 全局单例
excel_processor = ExcelProcessor()
