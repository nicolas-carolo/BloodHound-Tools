import random
from utils.principals import get_cn, get_sid_from_rid
from utils.time import generate_timestamp
from entities.users import get_guest_user, get_default_account, get_administrator_user, get_krbtgt_user,\
    get_forest_user_sid_list


def generate_guest_user(session, domain_name, domain_sid):
    guest_user = get_guest_user(domain_name, domain_sid)
    generate_user(session, guest_user)


def generate_default_account(session, domain_name, domain_sid):
    default_account = get_default_account(domain_name, domain_sid) 
    generate_user(session, default_account)


def generate_administrator(session, domain_name, domain_sid):
    administrator_user = get_administrator_user(domain_name, domain_sid)
    generate_user(session, administrator_user)


def generate_krbtgt_user(session, domain_name, domain_sid):
    krbtgt_user = get_krbtgt_user(domain_name, domain_sid)
    generate_user(session, krbtgt_user)


def generate_user(session, user):
    if get_cn(user["Properties"]["name"]) == "GUEST":
        enabled_property = random.choice([True, False])
        pwdneverexpires_property = random.choice([True, False])
    else:
        enabled_property = user["Properties"]["enabled"]
        pwdneverexpires_property = user["Properties"]["pwdneverexpires"]
    session.run(
        """
        MERGE (n:Base {name: $name}) SET n:User, n.objectid=$sid,
        n.highvalue=$highvalue, n.domain=$domain,
        n.distinguishedname=$distinguishedname,
        n.description=$description, n.admincount=$admincount,
        n.dontreqpreauth=$dontreqpreauth, n.passwordnotreqd=$passwordnotreqd,
        n.unconstraineddelegation=$unconstraineddelegation,
        n.sensitive=$sensitive, n.enabled=$enabled,
        n.pwdneverexpires=$pwdneverexpires, n.lastlogon=$lastlogon,
        n.lastlogontimestamp=$lastlogontimestamp, n.pwdlastset=$pwdlastset,
        n.serviceprincipalnames=$serviceprincipalnames, n.hasspn=$hasspn,
        n.displayname=$displayname, n.email=$email, n.title=$title,
        n.homedirectory=$homedirectory, n.userpassword=$userpassword,
        n.sidhistory=$sidhistory
        """,
        name=user["Properties"]["name"],
        sid=user["ObjectIdentifier"],
        highvalue=user["Properties"]["highvalue"],
        domain=user["Properties"]["domain"],
        distinguishedname=user["Properties"]["distinguishedname"],
        description=user["Properties"]["description"],
        admincount=user["Properties"]["admincount"],
        dontreqpreauth=user["Properties"]["dontreqpreauth"],
        passwordnotreqd=user["Properties"]["passwordnotreqd"],
        unconstraineddelegation=user["Properties"]["unconstraineddelegation"],
        sensitive=user["Properties"]["sensitive"],
        enabled=enabled_property,
        pwdneverexpires=pwdneverexpires_property,
        lastlogon=user["Properties"]["lastlogon"],
        lastlogontimestamp=user["Properties"]["lastlogontimestamp"],
        pwdlastset=user["Properties"]["pwdlastset"],
        serviceprincipalnames=user["Properties"]["serviceprincipalnames"],
        hasspn=user["Properties"]["hasspn"],
        displayname=user["Properties"]["displayname"],
        email=user["Properties"]["email"],
        title=user["Properties"]["title"],
        homedirectory=user["Properties"]["homedirectory"],
        userpassword=user["Properties"]["userpassword"],
        sidhistory=user["Properties"]["sidhistory"]
    )


def link_default_users_to_domain(session, domain_name, domain_sid):
    standard_users_list = get_forest_user_sid_list(domain_name, domain_sid)
    for user in standard_users_list:
        add_contains_object_on_domain_relationship(session, user)


def add_contains_object_on_domain_relationship(session, ad_object):
        query = "MATCH (objectItem:" + ad_object["ObjectType"] + " {objectid: '" + ad_object["ObjectId"] + "'}), (domainItem:Domain {objectid: '" + ad_object["DomainId"] + "'})"
        query = query + "\nMERGE (domainItem)-[:Contains]->(objectItem)"
        session.run(query)


def generate_users(session, domain_name, domain_sid, num_nodes, current_time, first_names, last_names, users, ridcount):
    user_properties_list = []
    group_name = "DOMAIN USERS@{}".format(domain_name)
    props = []
    for i in range(1, num_nodes + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)
        user_name = "{}{}{:05d}@{}".format(first[0], last, i, domain_name).upper()
        user_name = user_name.format(first[0], last, i).upper()
        users.append(user_name)
        dispname = "{} {}".format(first, last)
        enabled = True
        pwdlastset = generate_timestamp(current_time)
        lastlogon = generate_timestamp(current_time)
        ridcount += 1
        objectsid = get_sid_from_rid(ridcount, domain_sid)

        user_property = {
            'id': objectsid,
            'props': {
                'displayname': dispname,
                'name': user_name,
                'enabled': enabled,
                'pwdlastset': pwdlastset,
                'lastlogon': lastlogon
            }
        }
        props.append(user_property)
        user_properties_list.append(user_property)
        if (len(props) > 500):
            session.run('UNWIND $props as prop MERGE (n:Base {objectid:prop.id}) SET n:User, n += prop.props WITH n MATCH (m:Group {name:$gname}) WITH n,m MERGE (n)-[:MemberOf]->(m)', props=props, gname=group_name)
            props = []

    session.run('UNWIND $props as prop MERGE (n:Base {objectid:prop.id}) SET n:User, n += prop.props WITH n MATCH (m:Group {name:$gname}) WITH n,m MERGE (n)-[:MemberOf]->(m)', props=props, gname=group_name)
    return user_properties_list, users, ridcount
