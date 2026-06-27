import re
POS_WORDS = {"good","great","excellent","wonderful","love","best","amazing","brilliant","perfect"}
NEG_WORDS = {"bad","worst","awful","terrible","hate","boring","waste","poor","horrible"}

def sentiment_score(text: str) -> int:
    words = re.findall(r"\w+", text.lower())
    return sum(1 for w in words if w in POS_WORDS) - sum(1 for w in words if w in NEG_WORDS)