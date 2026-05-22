class BillingEngine:
    def __init__(self, rate):
        self.rate = rate

    def charge(self, tenant, usage):
        cost = usage.tokens * self.rate
        tenant.balance -= cost
