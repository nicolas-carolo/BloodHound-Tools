from utils.principals import get_cn


def generate_default_gpos(session, domain_name, ddp, ddcp):
    base_statement = "MERGE (n:Base {name:$gpo, objectid:$guid}) SET n:GPO"
    session.run(base_statement, gpo=get_cn("DEFAULT DOMAIN POLICY", domain_name), guid=ddp)
    session.run(base_statement, gpo=get_cn("DEFAULT DOMAIN CONTROLLERS POLICY", domain_name), guid=ddcp)