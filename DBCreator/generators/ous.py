from utils.principals import get_name


def generate_domain_controllers_ou(session, domain_name, dcou):
    session.run(
        "MERGE (n:Base {name:$ou, objectid:$guid, blocksInheritance: false}) SET n:OU",
        ou=get_name("DOMAIN CONTROLLERS", domain_name),
        guid=dcou
    )