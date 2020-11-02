from utils.principals import get_name


def generate_default_gpos(session, domain_name, ddp, ddcp):
    base_statement = "MERGE (n:Base {name:$gpo, objectid:$guid}) SET n:GPO"
    session.run(base_statement, gpo=get_name("DEFAULT DOMAIN POLICY", domain_name), guid=ddp)
    session.run(base_statement, gpo=get_name("DEFAULT DOMAIN CONTROLLERS POLICY", domain_name), guid=ddcp)


def link_default_gpos(session, domain_name, ddp, ddcp, dcou):
    gpo_name = "DEFAULT DOMAIN POLICY@{}".format(domain_name)
    session.run('MERGE (n:GPO {name:$gpo}) MERGE (m:Domain {name:$domain}) MERGE (n)-[:GpLink {isacl:false, enforced:toBoolean(false)}]->(m)', gpo=gpo_name, domain=domain_name)
    session.run('MERGE (n:Domain {name:$domain}) MERGE (m:OU {objectid:$guid}) MERGE (n)-[:Contains {isacl:false}]->(m)', domain=domain_name, guid=dcou)
    gpo_name = "DEFAULT DOMAIN CONTROLLERS POLICY@{}".format(domain_name)
    session.run('MERGE (n:GPO {objectid:$gpoguid}) MERGE (m:OU {objectid:$ouguid}) MERGE (n)-[:GpLink {isacl:false, enforced:toBoolean(false)}]->(m)', gpoguid=ddcp, ouguid=dcou)