class TenantManager:
    def __init__(self):
        self.tenants = {}

    def register_tenant(self, tenant):
        self.tenants[tenant.id] = tenant

    def isolate(self, tenant_id):
        return self.tenants[tenant_id].isolated_runtime()
