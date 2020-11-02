def get_name(name, domain_name):
    return f"{name}@{domain_name}"


def get_cn(name):
    return str(name).upper().split("@")[0]


def get_sid_from_rid(rid, domain_sid):
    return f"{domain_sid}-{str(rid)}"

# TODO remove?
"""
def cws(security_id):
    return f"{self.domain}-{str(security_id)}"
"""