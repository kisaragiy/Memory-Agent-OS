class LearningPolicy:
    def __init__(self):
        self.reward_weight = 0.5
        self.exploration_rate = 0.2
        self.reflection_weight = 0.3

class LearningLoopState:
    def __init__(self):
        self.policy = LearningPolicy()
        self.stability_score = 1.0
        self.modification_history = []

def should_modify(self, meta_score):
    return (
        meta_score < 0.4 or
        self.stability_score < 0.5
    )

def propose_modification(self, policy, meta_feedback):
    new_policy = LearningPolicy()

    if meta_feedback["instability"] > 0.5:
        new_policy.reward_weight = policy.reward_weight * 0.8

    if meta_feedback["reflection_quality"] > 0.7:
        new_policy.reflection_weight = policy.reflection_weight + 0.1

    if meta_feedback["overfitting"]:
        new_policy.exploration_rate += 0.1

    return new_policy

def validate_policy(self, old_policy, new_policy):
    diff = abs(old_policy.reward_weight - new_policy.reward_weight)
    if diff > 0.3:
        return False
    return True

class SelfModifyingLearningLoop:
    def __init__(self):
        self.state = LearningLoopState()

    def step(self, experience, meta_feedback):
        policy = self.state.policy

        if self.should_modify(meta_feedback):
            candidate = self.propose_modification(policy, meta_feedback)
            if self.validate_policy(policy, candidate):
                self.state.policy = candidate
                self.state.modification_history.append({
                    "old": policy,
                    "new": candidate,
                    "reason": meta_feedback
                })

        reward = experience["reward"]
        adjusted_reward = (
            reward * self.state.policy.reward_weight +
            meta_feedback.get("reflection_quality", 0.5) *
            self.state.policy.reflection_weight
        )

        return adjusted_reward
