# lf_rules.py - Labeling functions for review trustworthiness detection
import re
from config import *

PROMO_EN = r"(deal|discount|whatsapp|contact me|official|promo code|coupon|click (the )?link|buy now|limited time|referral|wholesale|reseller|unlock|free gift|dm me|cashback|use code|dm|pm|text me|message me|call me|reach out|get in touch|inbox me|slide into dm|hit me up|drop a line|shoot me a text|ping me|buzz me|ring me|drop me a line|give me a shout|drop me a message|send me a message|contact me directly|reach me at|get me on|find me on|look me up|search for me|my number is|my contact is|my details are|my info is|my contact info|my contact details|my phone number|my whatsapp|my telegram|my signal|my line|my wechat|my kik|my snapchat|my instagram|my facebook|my twitter|my linkedin|my email|my gmail|my yahoo|my outlook|my hotmail|my protonmail|my tutanota|my zoho|my aol|my icloud|my yandex|my mail|my inbox|my dm|my pm|my message|my text|my call|my voice|my video|my facetime|my skype|my zoom|my teams|my slack|my discord|my telegram|my signal|my line|my wechat|my kik|my snapchat|my instagram|my facebook|my twitter|my linkedin|my email|my gmail|my yahoo|my outlook|my hotmail|my protonmail|my tutanota|my zoho|my aol|my icloud|my yandex|my mail|my inbox|my dm|my pm|my message|my text|my call|my voice|my video|my facetime|my skype|my zoom|my teams|my slack|my discord)"
# 高度模板化的评论模式 - 只在明显模板化时触发
# 这些是非常具体的模板化短语，通常出现在批量生成的评论中
TEMPLATE_EN = r"(highly recommend to everyone|must buy this product|100% recommend|definitely recommend this|strongly recommend this|absolutely recommend|would definitely recommend|will definitely buy again|worth every single penny|five star rating|top notch quality|best product ever|excellent quality and service|amazing quality and fast delivery|perfect in every way|couldn't be happier|exceeded my expectations completely|outstanding product and service|phenomenal experience overall|spectacular quality and value)"

# Off-topic patterns for food-related businesses (restaurants, cafes, etc.)
# Excludes delivery-related terms as they are normal for food businesses
FOOD_OFFTOPIC_EN = r"(political|election|vote|government|tax|insurance|investment|stock|crypto|bitcoin|ethereum|forex|trading|gambling|casino|lottery|betting|dating|marriage|divorce|legal|law|court|attorney|lawyer|medical|health|pharmacy|prescription|medication|surgery|hospital|clinic|doctor|nurse|dentist|orthodontist|veterinarian|pet|animal|car|automotive|vehicle|motorcycle|bike|bicycle|real estate|property|house|apartment|condo|mortgage|loan|credit|debt|banking|finance|accounting|tax|audit|consulting|marketing|advertising|seo|web design|graphic design|software|programming|coding|development|maintenance|repair|installation|construction|renovation|plumbing|electrical|hvac|landscaping|gardening|cleaning|janitorial|security|pest control|exterminator)"

# General off-topic patterns for non-food businesses
# Includes delivery-related terms as they might be off-topic for non-food businesses
GENERAL_OFFTOPIC_EN = r"(shipping|delivery|logistics|courier|warehouse|parcel|invoice|refund|return|chargeback|tracking number|lost package|resend|political|election|vote|government|tax|insurance|investment|stock|crypto|bitcoin|ethereum|forex|trading|gambling|casino|lottery|betting|dating|marriage|divorce|legal|law|court|attorney|lawyer|medical|health|pharmacy|prescription|medication|surgery|hospital|clinic|doctor|nurse|dentist|orthodontist|veterinarian|pet|animal|car|automotive|vehicle|motorcycle|bike|bicycle|real estate|property|house|apartment|condo|mortgage|loan|credit|debt|banking|finance|accounting|tax|audit|consulting|marketing|advertising|seo|web design|graphic design|software|programming|coding|development|maintenance|repair|installation|construction|renovation|plumbing|electrical|hvac|landscaping|gardening|cleaning|janitorial|security|pest control|exterminator)"

# Enhanced entity detection patterns
MONEY_RE = re.compile(r"\$ ?\d+(?:\.\d+)?|\d+ ?(?:dollars?|bucks?|quid|pounds?|euros?|yen|yuan|won|rupees?|pesos?|francs?|marks?|liras?|rubles?|kronor?|kroner?|zloty|forints?|korunas?|leis?|levs?|dinars?|dirhams?|rials?|taka|ringgit|baht|dong|rupiah|tugrik|som|tenge|manat|somoni|afghani|ariary|dalasi|cedi|dalasi|gourde|kina|kwacha|maloti|metical|naira|pula|shilling|tala|vatu|zloty)\b", re.I)
TIME_RE  = re.compile(r"\b(\d{1,2}:\d{2} ?(?:am|pm)?|[A-Z][a-z]{2,8} \d{1,2}, \d{4}|yesterday|today|tomorrow|morning|afternoon|evening|night|tonight|this morning|this afternoon|this evening|this week|next week|last week|this month|next month|last month|this year|next year|last year)\b")
QTY_RE   = re.compile(r"\b\d+ (?:mins?|hours?|days?|weeks?|months?|years?|km|miles?|meters?|feet|inches|cm|mm|kg|pounds?|ounces?|grams?|liters?|gallons?|cups?|tablespoons?|teaspoons?|pieces?|items?|units?|sets?|pairs?|dozens?|hundreds?|thousands?|millions?|billions?)\b")
FOOD_RE  = re.compile(r"\b(noodles|burger|sushi|espresso|latte|pasta|ramen|taco|steak|salad|pizza|sandwich|hot dog|chicken|beef|pork|lamb|fish|shrimp|salmon|tuna|cod|halibut|mahi mahi|swordfish|mackerel|sardines|anchovies|herring|trout|bass|perch|walleye|catfish|tilapia|snapper|grouper|redfish|blackfish|bluefish|striped bass|white bass|yellow bass|rock bass|smallmouth bass|largemouth bass|spotted bass|guadalupe bass|redeye bass|choctaw bass|tallapoosa bass|alabama bass|florida bass|georgia bass|kentucky bass|mississippi bass|missouri bass|north carolina bass|south carolina bass|tennessee bass|virginia bass|west virginia bass|arkansas bass|louisiana bass|oklahoma bass|texas bass|new mexico bass|arizona bass|california bass|nevada bass|utah bass|colorado bass|wyoming bass|montana bass|idaho bass|washington bass|oregon bass|alaska bass|hawaii bass|puerto rico bass|guam bass|virgin islands bass|northern mariana islands bass|american samoa bass|marshall islands bass|micronesia bass|palau bass|nauru bass|kiribati bass|tuvalu bass|tokelau bass|niue bass|cook islands bass|samoa bass|tonga bass|fiji bass|vanuatu bass|new caledonia bass|solomon islands bass|papua new guinea bass|timor leste bass|indonesia bass|malaysia bass|singapore bass|brunei bass|philippines bass|vietnam bass|laos bass|cambodia bass|thailand bass|myanmar bass|bangladesh bass|india bass|pakistan bass|afghanistan bass|iran bass|iraq bass|syria bass|lebanon bass|jordan bass|israel bass|palestine bass|egypt bass|libya bass|tunisia bass|algeria bass|morocco bass|western sahara bass|mauritania bass|senegal bass|gambia bass|guinea bass|guinea bissau bass|sierra leone bass|liberia bass|ivory coast bass|ghana bass|togo bass|benin bass|nigeria bass|niger bass|chad bass|cameroon bass|central african republic bass|equatorial guinea bass|gabon bass|congo bass|democratic republic of congo bass|angola bass|zambia bass|zimbabwe bass|botswana bass|namibia bass|south africa bass|lesotho bass|eswatini bass|mozambique bass|malawi bass|tanzania bass|kenya bass|uganda bass|rwanda bass|burundi bass|ethiopia bass|eritrea bass|djibouti bass|somalia bass|somaliland bass|comoros bass|mayotte bass|reunion bass|madagascar bass|mauritius bass|seychelles bass|maldives bass|sri lanka bass)\b", re.I)

def rough_entity_count(text: str) -> int:
    """Count entities in text using regex patterns"""
    if not text: return 0
    cnt = 0
    cnt += len(MONEY_RE.findall(text))
    cnt += len(TIME_RE.findall(text))
    cnt += len(QTY_RE.findall(text))
    cnt += len(FOOD_RE.findall(text))
    return cnt

def lf_promo_has_link(text, has_url, has_phone):
    """Detect promotional content with links or phone numbers"""
    if re.search(PROMO_EN, text, re.I):
        return (1, 0.95) if (has_url or has_phone) else (1, 0.80)
    return (-1, 0.0)

def lf_too_short(len_tok, len_char):
    """Detect reviews that are too short"""
    return (1, 0.70) if (len_tok <= 5 or len_char <= 12) else (-1, 0.0)

def lf_template_low_entities(text, ent_count):
    """Detect template reviews with low entity count - 更严格的模板检测"""
    if not text: return (-1, 0.0)
    
    # 检查是否包含模板化短语
    template_matches = len(re.findall(TEMPLATE_EN, text, re.I))
    
    # 只有在以下条件下才触发：
    # 1. 包含模板化短语
    # 2. 实体数量为0（缺乏具体信息）
    # 3. 文本长度较短（<100字符）或包含多个模板短语
    if template_matches > 0 and ent_count == 0:
        if len(text) < 100 or template_matches >= 2:
            return (1, 0.80)
    
    return (-1, 0.0)

def lf_entity_sparse(len_char, ent_count):
    """Detect reviews with sparse entity information"""
    return (1, 0.60) if (len_char > 12 and ent_count == 0) else (-1, 0.0)

def lf_offtopic(category, text):
    """Detect off-topic content for business category"""
    if not text:
        return (-1, 0.0)
    
    # Use the new keyword-based detector (more reliable and faster)
    try:
        from keyword_offtopic_detector import lf_offtopic_keyword
        return lf_offtopic_keyword(category, text)
    except ImportError:
        # Fallback to original keyword-based detection
        return _lf_offtopic_keyword_fallback(category, text)

def _lf_offtopic_keyword_fallback(category, text):
    """Fallback keyword-based offtopic detection (original implementation)"""
    # Handle different category formats
    if category is not None:
        if isinstance(category, list):
            # Handle list of categories (e.g., ["RV park", "Cabin rental agency", "Campground"])
            categories = [str(cat).lower() for cat in category]
        elif isinstance(category, (int, float)):
            # For numeric categories, assume it's a business ID
            categories = ["restaurant"]  # Default to restaurant for testing
        else:
            # Handle single string category
            categories = [str(cat).lower() for cat in [category]]
    else:
        categories = ["restaurant"]  # Default
    
    # Define business-specific off-topic patterns
    # For restaurants: delivery, takeout, etc. are ON-topic
    # For non-food businesses: these might be off-topic
    
    # Check if any category is food-related
    is_food_related = any(cat in FOOD_CATEGORIES for cat in categories)
    
    if is_food_related:
        # For food-related businesses, use FOOD_OFFTOPIC_EN (excludes delivery-related terms)
        if re.search(FOOD_OFFTOPIC_EN, text, re.I):
            return (1, 0.75)
    else:
        # For non-food businesses, use GENERAL_OFFTOPIC_EN (includes delivery-related terms)
        if re.search(GENERAL_OFFTOPIC_EN, text, re.I):
            return (1, 0.75)
    
    return (-1, 0.0)

def lf_format_noise(text):
    """Detect format noise like excessive punctuation"""
    if not text: return (-1, 0.0)
    non_alnum = sum(1 for c in text if not c.isalnum() and not c.isspace())
    ratio = non_alnum / max(1, len(text))
    # also catch stretched characters / repeated punctuation
    if ratio > MAX_NON_ALNUM_RATIO or re.search(r"(.)\1{" + str(MAX_REPEATED_CHARS + 1) + r",}", text) or re.search(r"([!?])\1{" + str(MAX_REPEATED_PUNCTUATION + 1) + r",}", text):
        return (1, 0.60)
    return (-1, 0.0)

def lf_trust_signal(ent_count, has_promo_hit):
    """Detect trust signals (high entity count without promotional content)"""
    if ent_count >= MIN_ENTITIES_FOR_TRUST and not has_promo_hit:
        return (0, 0.70)
    return (-1, 0.0)

def lf_rating_sentiment_conflict(rating, sent_pos, sent_neg, hi=0.9):
    """Detect conflicts between rating and sentiment"""
    if rating in (1,2) and sent_pos >= hi: return (1, 0.85)
    if rating in (4,5) and sent_neg >= hi: return (1, 0.85)
    return (-1, 0.0)

def lf_user_burst(user_daily_cnt, thr=5):
    """Detect user review bursts"""
    return (1, 0.80) if user_daily_cnt >= thr else (-1, 0.0)

def lf_user_extreme_hist(user_ratio_all5_or_all1, thr=0.95):
    """Detect users with extreme rating history"""
    return (1, 0.60) if user_ratio_all5_or_all1 >= thr else (-1, 0.0)

def lf_biz_burst(is_biz_burst):
    """Detect business review bursts"""
    return (1, 0.70) if is_biz_burst else (-1, 0.0)

def lf_user_near_dupe(is_near_dupe):
    """Detect near-duplicate user reviews"""
    return (1, 0.95) if is_near_dupe else (-1, 0.0)

def lf_suspicious_patterns(text):
    """Detect suspicious patterns like excessive emojis, caps, or repetitive text"""
    if not text: return (-1, 0.0)
    
    # Excessive emojis
    emoji_count = len(re.findall(r'[😀-🙿🌀-🗿🚀-🛿🦀-🧿]', text))
    if emoji_count > MAX_EMOJIS:
        return (1, 0.75)
    
    # Excessive caps
    caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
    if caps_ratio > MAX_CAPS_RATIO:
        return (1, 0.70)
    
    # Repetitive words
    words = text.lower().split()
    if len(words) > 3:
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        max_freq = max(word_freq.values())
        if max_freq > len(words) * MAX_WORD_REPETITION_RATIO:
            return (1, 0.65)
    
    return (-1, 0.0)

def lf_brand_mentioning(text):
    """Detect excessive brand/product mentioning"""
    if not text: return (-1, 0.0)
    
    # Common brand indicators
    brand_indicators = r'\b(brand|product|item|goods|merchandise|stock|inventory|supply|supplier|manufacturer|distributor|retailer|wholesaler|reseller|dealer|vendor|seller|buyer|customer|client|consumer|user|end user|target audience|market|marketplace|platform|website|app|application|software|tool|service|solution|package|bundle|offer|deal|promotion|campaign|marketing|advertising|publicity|exposure|visibility|reach|engagement|conversion|sales|revenue|profit|margin|commission|fee|charge|cost|price|value|worth|quality|standard|specification|requirement|feature|function|benefit|advantage|pro|con|pros|cons|positive|negative|good|bad|better|worse|best|worst|improve|enhance|upgrade|optimize|maximize|minimize|increase|decrease|reduce|boost)\b'
    
    matches = len(re.findall(brand_indicators, text, re.I))
    if matches > MAX_BRAND_MENTIONS:
        return (1, 0.60)
    
    return (-1, 0.0)

def lf_time_sensitive_content(text):
    """Detect time-sensitive promotional content"""
    time_indicators = r'\b(limited time|flash sale|24 hours|48 hours|72 hours|weekend|today only|tonight only|this week|this month|this year|seasonal|holiday|christmas|black friday|cyber monday|boxing day|new year|valentine|easter|halloween|thanksgiving|independence day|memorial day|labor day|veterans day|presidents day|columbus day|martin luther king day|juneteenth|kwanzaa|ramadan|eid|diwali|hanukkah|passover|rosh hashanah|yom kippur|chinese new year|lunar new year|vietnamese new year|korean new year|japanese new year|thai new year|lao new year|cambodian new year|burmese new year|mongolian new year|tibetan new year|nepali new year|bangladeshi new year|sri lankan new year|pakistani new year|indian new year|afghan new year|iranian new year|iraqi new year|syrian new year|lebanese new year|jordanian new year|palestinian new year|israeli new year|egyptian new year|libyan new year|tunisian new year|algerian new year|moroccan new year|sudanese new year|ethiopian new year|somali new year|kenyan new year|ugandan new year|tanzanian new year|rwandan new year|burundian new year|central african new year|chadian new year|cameroonian new year|gabonese new year|congolese new year|equatorial guinean new year|sao tomean new year|angolan new year|zambian new year|zimbabwean new year|botswanan new year|namibian new year|south african new year|lesotho new year|swazi new year|mozambican new year|malawian new year)\b'
    
    if re.search(time_indicators, text, re.I):
        return (1, 0.80)
    
    return (-1, 0.0)
