def generate_enterprise_admins_acls(session, domain_name):
    # Ent Admins -> Domain Node
    group_name = "ENTERPRISE ADMINS@{}".format(domain_name)
    session.run('MERGE (n:Domain {name:$domain}) MERGE (m:Group {name:$gname}) MERGE (m)-[:GenericAll {isacl:true, isinherited: false}]->(n)', domain=domain_name, gname=group_name)


def generate_administrators_acls(session, domain_name):
    # Administrators -> Domain Node
    group_name = "ADMINISTRATORS@{}".format(domain_name)
    session.run('MERGE (n:Domain {name:$domain}) MERGE (m:Group {name:$gname}) MERGE (m)-[:Owns {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:WriteOwner {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:WriteDacl {isacl:true, isinherited: false}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:DCSync {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChanges {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChangesAll {isacl:true}]->(n)', domain=domain_name, gname=group_name)


def generate_domain_admins_acls(session, domain_name):
    # Domain Admins -> Domain Node
    group_name = "DOMAIN ADMINS@{}".format(domain_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:WriteOwner {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:WriteDacl {isacl:true, isinherited: false}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:DCSync {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChanges {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChangesAll {isacl:true}]->(n)', domain=domain_name, gname=group_name)


def generate_default_groups_acls(session, domain_name):
    # DC Groups -> Domain Node
    group_name = "ENTERPRISE DOMAIN CONTROLLERS@{}".format(domain_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChanges {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    group_name = "ENTERPRISE READ-ONLY DOMAIN CONTROLLERS@{}".format(domain_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChanges {isacl:true}]->(n)', domain=domain_name, gname=group_name)
    group_name = "DOMAIN CONTROLLERS@{}".format(domain_name)
    session.run('MERGE (n:Domain {name:$domain}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:GetChangesAll {isacl:true}]->(n)', domain=domain_name, gname=group_name)