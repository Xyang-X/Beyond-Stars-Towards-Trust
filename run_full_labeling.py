# run_full_labeling.py - 对整个数据集进行标签
import sys
import os
import json
import pandas as pd
import time
from tqdm import tqdm

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_and_process_data(input_path, batch_size=1000):
    """分批加载和处理数据"""
    print(f"📁 开始处理文件: {input_path}")
    print(f"📊 批处理大小: {batch_size}")
    
    # 统计总行数
    print("🔍 统计文件总行数...")
    total_lines = 0
    with open(input_path, 'r', encoding='utf-8') as f:
        for _ in f:
            total_lines += 1
    
    print(f"📈 文件总行数: {total_lines:,}")
    
    # 分批处理
    all_results = []
    processed_lines = 0
    
    with open(input_path, 'r', encoding='utf-8') as f:
        batch = []
        
        for line_num, line in enumerate(tqdm(f, total=total_lines, desc="处理进度")):
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                batch.append(data)
                processed_lines += 1
                
                # 当批次满了或到达文件末尾时处理
                if len(batch) >= batch_size or line_num == total_lines - 1:
                    batch_results = process_batch(batch, processed_lines - len(batch) + 1)
                    all_results.extend(batch_results)
                    
                    # 显示进度
                    progress = (processed_lines / total_lines) * 100
                    print(f"📊 进度: {processed_lines:,}/{total_lines:,} ({progress:.1f}%) - 已处理 {len(all_results):,} 条评论")
                    
                    # 清空批次
                    batch = []
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ 第{line_num+1}行JSON解析失败: {e}")
                continue
            except Exception as e:
                print(f"❌ 第{line_num+1}行处理失败: {e}")
                continue
    
    return all_results

def process_batch(batch, start_index):
    """处理一批数据"""
    try:
        from lf_rules import (
            lf_promo_has_link, lf_too_short, lf_template_low_entities,
            lf_entity_sparse, lf_offtopic, lf_format_noise, lf_trust_signal,
            lf_rating_sentiment_conflict, lf_suspicious_patterns,
            lf_brand_mentioning, lf_time_sensitive_content, rough_entity_count
        )
        from lf_aggregate import aggregate_lfs
        from config import TAU_HIGH, TAU_LOW
    except ImportError as e:
        print(f"❌ 导入标签函数失败: {e}")
        return []
    
    results = []
    
    for i, row in enumerate(batch):
        try:
            # 获取文本信息
            text = row.get('text', row.get('original_text', ''))
            if not text:
                text = row.get('processed_text', '')
            
            # 计算文本特征
            len_tok = len(text.split()) if text else 0
            len_char = len(text) if text else 0
            ent_count = rough_entity_count(text) if 'rough_entity_count' in globals() else 0
            
            # 运行所有标签函数
            lf_outputs = {}
            
            # 1. 促销检测
            has_url = False  # 简化处理
            has_phone = False  # 简化处理
            lf_outputs['promo'] = lf_promo_has_link(text, has_url, has_phone)
            
            # 2. 长度检测
            lf_outputs['too_short'] = lf_too_short(len_tok, len_char)
            
            # 3. 模板检测
            lf_outputs['template'] = lf_template_low_entities(text, ent_count)
            
            # 4. 实体稀疏检测
            lf_outputs['entity_sparse'] = lf_entity_sparse(len_char, ent_count)
            
            # 5. 离题检测
            lf_outputs['offtopic'] = lf_offtopic(row.get('category'), text)
            
            # 6. 格式噪音检测
            lf_outputs['format_noise'] = lf_format_noise(text)
            
            # 7. 可信信号检测
            has_promo_hit = lf_outputs['promo'][0] == 1
            lf_outputs['trust_signal'] = lf_trust_signal(ent_count, has_promo_hit)
            
            # 8. 评分情感冲突检测
            rating = row.get('rating', 3)
            sent_pos = 0.5  # 简化处理
            sent_neg = 0.3  # 简化处理
            lf_outputs['sent_conflict'] = lf_rating_sentiment_conflict(rating, sent_pos, sent_neg)
            
            # 9. 可疑模式检测
            lf_outputs['suspicious_patterns'] = lf_suspicious_patterns(text)
            
            # 10. 品牌提及检测
            lf_outputs['brand_mentioning'] = lf_brand_mentioning(text)
            
            # 11. 时间敏感内容检测
            lf_outputs['time_sensitive_content'] = lf_time_sensitive_content(text)
            
            # 聚合标签函数输出
            p_untrust, score, hits = aggregate_lfs(lf_outputs)
            
            # 根据阈值确定最终标签
            if p_untrust >= TAU_HIGH:
                final_label = 1  # 不可信
                label_str = "untrustworthy"
            elif p_untrust <= TAU_LOW:
                final_label = 0  # 可信
                label_str = "trustworthy"
            else:
                final_label = -1  # 忽略
                label_str = "ignore"
            
            # 记录结果
            result = {
                'comment_id': start_index + i,
                'user_id': row.get('user_id', ''),
                'name': row.get('name', ''),
                'rating': row.get('rating', ''),
                'time': row.get('time', ''),
                'category': row.get('category', ''),
                'robot_review': row.get('robot_review', False),
                'text': text[:200] + "..." if len(text) > 200 else text,
                'processed_text': row.get('processed_text', ''),
                'entity_count': ent_count,
                'len_char': len_char,
                'len_tok': len_tok,
                'p_untrust': p_untrust,
                'score': score,
                'final_label': final_label,
                'label_str': label_str,
                'lf_outputs': lf_outputs
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ 处理第{start_index + i}条评论失败: {e}")
            # 添加错误记录
            text_content = row.get('text', row.get('original_text', ''))
            if isinstance(text_content, str) and len(text_content) > 200:
                text_display = text_content[:200] + "..."
            else:
                text_display = str(text_content)
                
            result = {
                'comment_id': start_index + i,
                'user_id': row.get('user_id', ''),
                'name': row.get('name', ''),
                'rating': row.get('rating', ''),
                'time': row.get('time', ''),
                'category': row.get('category', ''),
                'robot_review': row.get('robot_review', False),
                'text': text_display,
                'processed_text': row.get('processed_text', ''),
                'entity_count': 'ERROR',
                'len_char': 'ERROR',
                'len_tok': 'ERROR',
                'p_untrust': 'ERROR',
                'score': 'ERROR',
                'final_label': 'ERROR',
                'label_str': 'ERROR',
                'lf_outputs': {}
            }
            results.append(result)
    
    return results

def save_results(results, output_path):
    """保存结果到文件"""
    print(f"\n💾 保存结果到: {output_path}")
    
    # 转换为DataFrame
    df = pd.DataFrame(results)
    
    # 保存为CSV格式（便于查看）
    csv_path = output_path.replace('.parquet', '.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ 已保存 {len(df)} 条评论到 {csv_path}")
    
    return df

def generate_summary_report(df):
    """生成摘要报告"""
    print(f"\n📊 标签结果摘要报告")
    print("=" * 60)
    
    # 基本统计
    total = len(df)
    untrustworthy = len(df[df['final_label'] == 1])
    trustworthy = len(df[df['final_label'] == 0])
    ignore = len(df[df['final_label'] == -1])
    errors = len(df[df['final_label'] == 'ERROR'])
    
    print(f"📈 总体统计:")
    print(f"   总评论数: {total:,}")
    print(f"   可信评论: {trustworthy:,} ({trustworthy/total*100:.1f}%)")
    print(f"   不可信评论: {untrustworthy:,} ({untrustworthy/total*100:.1f}%)")
    print(f"   忽略评论: {ignore:,} ({ignore/total*100:.1f}%)")
    print(f"   处理失败: {errors:,} ({errors/total*100:.1f}%)")
    
    # 按评分统计
    print(f"\n⭐ 按评分统计:")
    rating_stats = df[df['final_label'] != 'ERROR'].groupby('rating').agg({
        'final_label': ['count', lambda x: (x == 1).sum(), lambda x: (x == 0).sum()]
    }).round(2)
    
    for rating in sorted(rating_stats.index):
        total_count = rating_stats.loc[rating, ('final_label', 'count')]
        untrust_count = rating_stats.loc[rating, ('final_label', '<lambda_0>')]
        trust_count = rating_stats.loc[rating, ('final_label', '<lambda_1>')]
        
        if total_count > 0:
            untrust_rate = untrust_count / total_count * 100
            trust_rate = trust_count / total_count * 100
            print(f"   评分 {rating}: {untrust_count}/{total_count} 不可信 ({untrust_rate:.1f}%), {trust_count}/{total_count} 可信 ({trust_rate:.1f}%)")
    
    # 按业务类型统计
    print(f"\n🏪 按业务类型统计:")
    # 处理category字段（可能是列表）
    df['category_str'] = df['category'].apply(lambda x: str(x[0]) if isinstance(x, list) and x else str(x))
    
    category_stats = df[df['final_label'] != 'ERROR'].groupby('category_str').agg({
        'final_label': ['count', lambda x: (x == 1).sum(), lambda x: (x == 0).sum()]
    }).round(2)
    
    # 显示前10个最常见的业务类型
    top_categories = category_stats.sort_values(('final_label', 'count'), ascending=False).head(10)
    
    for category in top_categories.index:
        total_count = top_categories.loc[category, ('final_label', 'count')]
        untrust_count = top_categories.loc[category, ('final_label', '<lambda_0>')]
        trust_count = top_categories.loc[category, ('final_label', '<lambda_1>')]
        
        if total_count > 0:
            untrust_rate = untrust_count / total_count * 100
            trust_rate = trust_count / total_count * 100
            print(f"   {category}: {untrust_count}/{total_count} 不可信 ({untrust_rate:.1f}%), {trust_count}/{total_count} 可信 ({trust_rate:.1f}%)")
    
    # 机器人评论分析
    print(f"\n🤖 机器人评论分析:")
    robot_stats = df[df['robot_review'] == True]
    if len(robot_stats) > 0:
        robot_total = len(robot_stats)
        robot_untrust = len(robot_stats[robot_stats['final_label'] == 1])
        robot_trust = len(robot_stats[robot_stats['final_label'] == 0])
        
        print(f"   机器人评论总数: {robot_total:,}")
        print(f"   机器人不可信评论: {robot_untrust:,} ({robot_untrust/robot_total*100:.1f}%)")
        print(f"   机器人可信评论: {robot_trust:,} ({robot_trust/robot_total*100:.1f}%)")
    else:
        print("   未发现机器人评论")
    
    print(f"\n🎯 标签质量评估:")
    print(f"   可信评论比例: {trustworthy/total*100:.1f}% (目标: 30-50%)")
    print(f"   不可信评论比例: {untrustworthy/total*100:.1f}% (目标: 20-40%)")
    print(f"   忽略评论比例: {ignore/total*100:.1f}% (目标: 最小化)")
    
    if trustworthy/total*100 >= 30 and trustworthy/total*100 <= 50:
        print("   ✅ 可信评论比例在目标范围内")
    else:
        print("   ⚠️ 可信评论比例超出目标范围")
    
    if untrustworthy/total*100 >= 20 and untrustworthy/total*100 <= 40:
        print("   ✅ 不可信评论比例在目标范围内")
    else:
        print("   ⚠️ 不可信评论比例超出目标范围")
    
    if ignore/total*100 < 10:
        print("   ✅ 忽略评论比例较低")
    else:
        print("   ⚠️ 忽略评论比例较高")

def main():
    """主函数"""
    print("🚀 开始对整个数据集进行标签")
    print("=" * 80)
    
    # 文件路径
    input_path = r"D:\MyPersonalFiles\NTU\TechJam2025\review-Alaska_10.filtered.redacted.strict.dedup.preprocessed.targeted.json"
    output_path = "full_dataset_labeled.csv"
    
    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"❌ 输入文件不存在: {input_path}")
        return
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 1. 加载和处理数据
        results = load_and_process_data(input_path, batch_size=1000)
        
        # 2. 保存结果
        df = save_results(results, output_path)
        
        # 3. 生成摘要报告
        generate_summary_report(df)
        
        # 4. 计算总耗时
        total_time = time.time() - start_time
        print(f"\n⏱️ 总耗时: {total_time:.2f} 秒")
        print(f"🚀 处理速度: {len(results)/total_time:.0f} 条/秒")
        
        print(f"\n🎉 标签完成!")
        print(f"📁 结果文件: {output_path}")
        print(f"📊 总处理评论数: {len(results):,}")
        
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
