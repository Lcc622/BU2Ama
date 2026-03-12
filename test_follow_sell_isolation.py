#!/usr/bin/env python3
"""
测试跟卖功能的分店铺索引隔离
"""
import sys
sys.path.insert(0, 'backend')

from app.core.follow_sell_processor import follow_sell_processor

# 测试 SKC
TEST_SKC = "ES01819NT"

# 三个店铺
STORES = [
    {'name': 'EP', 'template_type': 'EPUS'},
    {'name': 'DM', 'template_type': 'DaMaUS'},
    {'name': 'PZ', 'template_type': 'PZUS'},
]

def test_follow_sell_store(store_config):
    """测试单个店铺的跟卖功能"""
    print(f"\n{'='*80}")
    print(f"测试店铺: {store_config['name']} ({store_config['template_type']})")
    print(f"{'='*80}")

    try:
        result = follow_sell_processor.find_sizes_for_skc(
            skc=TEST_SKC,
            template_type=store_config['template_type']
        )

        success = result.get('success', False)
        message = result.get('message', '')
        sizes = result.get('sizes', [])
        new_style = result.get('new_style', '')
        old_style = result.get('old_style', '')
        color_code = result.get('color_code', '')

        print(f"成功: {success}")
        print(f"消息: {message}")
        print(f"新款号: {new_style}")
        print(f"老款号: {old_style}")
        print(f"颜色码: {color_code}")
        print(f"尺码数量: {len(sizes)}")
        if sizes:
            print(f"尺码列表: {', '.join(sizes[:10])}{' ...' if len(sizes) > 10 else ''}")

        # 检查使用的索引库
        store_prefix = follow_sell_processor.get_store_prefix(store_config['template_type'])
        index_db = follow_sell_processor.get_index_db_path(store_prefix)
        print(f"使用索引库: {index_db.name}")
        print(f"索引库存在: {index_db.exists()}")

        return {
            'store': store_config['name'],
            'success': success,
            'sizes_count': len(sizes),
            'index_db': index_db.name,
            'old_style': old_style,
            'message': message
        }

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'store': store_config['name'],
            'success': False,
            'sizes_count': 0,
            'index_db': 'N/A',
            'old_style': '',
            'message': str(e)
        }

def main():
    print(f"开始测试跟卖功能的分店铺索引隔离...")
    print(f"测试 SKC: {TEST_SKC}")

    results = []
    for store in STORES:
        result = test_follow_sell_store(store)
        results.append(result)

    # 输出对比表格
    print(f"\n\n{'='*80}")
    print("对比结果")
    print(f"{'='*80}")
    print(f"{'店铺':<8} {'成功':<8} {'尺码数':<10} {'索引库':<25} {'老款号':<15}")
    print('-' * 80)
    for r in results:
        print(f"{r['store']:<8} {str(r['success']):<8} {r['sizes_count']:<10} {r['index_db']:<25} {r['old_style']:<15}")

    # 检查是否有跨店铺串值
    print(f"\n分析:")
    index_dbs = [r['index_db'] for r in results if r['success']]
    if len(set(index_dbs)) == len(index_dbs):
        print("✓ 各店铺使用不同的索引库，索引隔离正常")
    else:
        print("⚠️  警告: 多个店铺使用了相同的索引库")

    old_styles = [r['old_style'] for r in results if r['success'] and r['old_style']]
    if len(set(old_styles)) > 1:
        print("⚠️  警告: 不同店铺返回了不同的老款号，可能存在数据不一致")
    elif len(old_styles) > 0:
        print(f"✓ 所有店铺返回相同的老款号: {old_styles[0]}")

if __name__ == '__main__':
    main()
