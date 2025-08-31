import math
from config import STRICTNESS_LEVEL

# 根据严格程度动态调整权重
def get_adjusted_weights():
    """根据严格程度动态调整权重"""
    base_weights = {
        "promo": 2.0,              # 促销内容基础权重
        "near_dupe": 1.8,          # 重复内容
        "sent_conflict": 1.8,      # 情感冲突基础权重
        "offtopic": 0.6,           # 离题内容基础权重
        "user_burst": 1.2,         # 用户爆发
        "biz_burst": 1.2,          # 业务爆发
        "too_short": 0.6,          # 过短文本
        "template": 0.8,           # 模板化内容
        "entity_sparse": 0.6,      # 实体稀疏
        "format_noise": 0.6,       # 格式噪音
        "trust_signal": 2.5,       # 可信信号 (正向)
        "suspicious_patterns": 1.2, # 可疑模式
        "brand_mentioning": 1.0,   # 品牌提及
        "time_sensitive_content": 1.5, # 时效性内容
        "political_content": 3.0,  # 政治内容 - 最高权重
    }
    
    # 严格程度越高，权重越高
    adjusted_weights = {}
    for key, base_weight in base_weights.items():
        if key in ["promo", "sent_conflict", "political_content"]:
            # 促销内容、情感冲突、政治内容权重随严格程度线性增加
            adjusted_weights[key] = base_weight + STRICTNESS_LEVEL * 1.0
        elif key in ["offtopic", "near_dupe"]:
            # 离题内容和重复内容权重适度增加
            adjusted_weights[key] = base_weight + STRICTNESS_LEVEL * 0.5
        else:
            # 其他权重保持不变
            adjusted_weights[key] = base_weight
    
    return adjusted_weights

# 动态权重
W = get_adjusted_weights()

def sigmoid(x): return 1.0 / (1.0 + math.exp(-x))

def aggregate_lfs(lf_outputs):
    """
    lf_outputs: dict {lf_name: (label, conf)}
    label: 1 不可信, 0 可信, -1 忽略
    """
    score = 0.0
    hits = []
    
    # 重新计算权重（支持运行时调整）
    current_weights = get_adjusted_weights()
    
    for name, (lab, conf) in lf_outputs.items():
        if lab == -1: 
            continue
        w = current_weights.get(name, 1.0)
        contrib = (1 if lab == 1 else -1) * w * conf
        score += contrib
        hits.append((name, lab, conf, w, contrib))
    
    p_untrust = sigmoid(score)
    return p_untrust, score, hits

def print_weight_status():
    """打印当前权重状态"""
    current_weights = get_adjusted_weights()
    print(f"🔧 当前严格程度: {STRICTNESS_LEVEL:.1f}")
    print("📊 当前权重配置:")
    for key, weight in sorted(current_weights.items()):
        print(f"   {key:20}: {weight:5.2f}")
