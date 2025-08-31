# config.py - Configuration file for labeling system

# Thresholds for high/low confidence - 进一步调整为产生10-15%不可信评论
TAU_HIGH = 0.30  # 从0.40降低到0.30 - 更容易标记为不可信
TAU_LOW = 0.70   # 从0.60提高到0.70 - 让更多评论进入忽略区域，减少可信标签

# Sampling parameters
PER_BIZ_MAX = 80
TOTAL_CAP = 50000

# Entity detection thresholds - 进一步放宽
MIN_ENTITIES_FOR_TRUST = 0  # 从1降低到0 - 更容易被认为是可信的
MAX_EMOJIS = 7              # 从6增加到7 - 更多表情符号允许
MAX_CAPS_RATIO = 0.90       # 从0.85增加到0.90 - 更多大写字母允许
MAX_WORD_REPETITION_RATIO = 0.7  # 从0.6增加到0.7 - 更多重复允许
MAX_BRAND_MENTIONS = 5      # 从4增加到5 - 更多品牌提及允许

# User behavior thresholds - 进一步放宽
MAX_DAILY_REVIEWS = 12             # 从10增加到12 - 更多每日评论允许
MAX_EXTREME_RATING_RATIO = 0.995   # 从0.99增加到0.995 - 更多极端评分允许

# Sentiment conflict threshold - 进一步放宽
SENTIMENT_CONFLICT_THRESHOLD = 0.99  # 从0.98增加到0.99 - 更宽松的情感冲突检测

# Format noise thresholds - 进一步放宽
MAX_NON_ALNUM_RATIO = 0.7        # 从0.6增加到0.7 - 更多非字母数字允许
MAX_REPEATED_CHARS = 6            # 从5增加到6 - 更多重复字符允许
MAX_REPEATED_PUNCTUATION = 5      # 从4增加到5 - 更多重复标点允许

# Business categories for offtopic detection
FOOD_CATEGORIES = [
    "restaurant", "cafe", "food", "bar", "bakery", "pizzeria", 
    "diner", "bistro", "grill", "steakhouse", "seafood", "bbq",
    "fast food", "casual dining", "fine dining", "ethnic food",
    "food truck", "food court", "delicatessen", "grocery store"
]

# File paths
DEFAULT_INPUT_PATH = r"D:\MyPersonalFiles\NTU\TechJam2025\review-Alaska_10.filtered.redacted.strict.dedup.preprocessed.targeted.json"
DEFAULT_OUTPUT_PATH = "train_highconf.parquet"
