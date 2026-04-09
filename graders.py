def reward_based(prediction, target):
    score = 0
    total = len(target)

    for key in target:
        pred_val = str(prediction.get(key, "")).strip().lower()
        target_val = str(target.get(key, "")).strip().lower()

        if pred_val == target_val:
            score += 1

    return score / total if total > 0 else 0
