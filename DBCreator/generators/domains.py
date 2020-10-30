def generate_domain(session, domain_name, domain_sid):
    session.run(
        "MERGE (n:Base {name:$domain}) SET n:Domain, n.highvalue=true, n.objectid=$objectid",
        domain=domain_name,
        objectid=domain_sid
    )