import random
from utils.principals import get_sid_from_rid, get_name
from templates.ous import STATES
from templates.computers import OS_LIST


def generate_computers(session, domain_name, domain_sid, num_nodes, computers):
    computer_properties_list = []
    group_name = "DOMAIN COMPUTERS@{}".format(domain_name)
    props = []
    ridcount = 1000
    for i in range(1, num_nodes + 1):
        comp_name = "COMP{:05d}.{}".format(i, domain_name)
        computers.append(comp_name)
        os = random.choice(OS_LIST)
        enabled = True
        computer_property = {
            'id': get_sid_from_rid(ridcount, domain_sid),
            'props': {
                'name': comp_name,
                'operatingsystem': os,
                'enabled': enabled,
            }
        }
        props.append(computer_property)
        computer_properties_list.append(computer_property)
        ridcount += 1

        if (len(props) > 500):
            session.run('UNWIND $props as prop MERGE (n:Base {objectid: prop.id}) SET n:Computer, n += prop.props WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (n)-[:MemberOf]->(m)', props=props, gname=group_name)
            props = []
    session.run('UNWIND $props as prop MERGE (n:Base {objectid:prop.id}) SET n:Computer, n += prop.props WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (n)-[:MemberOf]->(m)', props=props, gname=group_name)
    return computer_properties_list, ridcount


def generate_dcs(session, domain_name, domain_sid, dcou, ridcount):
    dc_properties_list = []
    for state in STATES:
        comp_name = get_name(f"{state}LABDC", domain_name)
        group_name = get_name("DOMAIN CONTROLLERS", domain_name)
        sid = get_sid_from_rid(ridcount, domain_sid)
        dc_properties = {
            'name': comp_name,
            'id': sid
        }
        ridcount += 1
        dc_properties_list.append(dc_properties)
        session.run('MERGE (n:Base {objectid:$sid}) SET n:Computer,n.name=$name WITH n MATCH (m:Group {name:$gname}) WITH n,m MERGE (n)-[:MemberOf]->(m)', sid=sid, name=comp_name, gname=group_name)
        # print("MERGE (n:Base {objectid:" + sid + "}) SET n:Computer,n.name=" + comp_name + " WITH n MATCH (m:Group {name:" + group_name + "}) WITH n,m MERGE (n)-[:MemberOf]->(m)")
        session.run('MATCH (n:Computer {objectid:$sid}) WITH n MATCH (m:OU {objectid:$dcou}) WITH n,m MERGE (m)-[:Contains]->(n)', sid=sid, dcou=dcou)
        session.run('MATCH (n:Computer {objectid:$sid}) WITH n MATCH (m:Group {name:$gname}) WITH n,m MERGE (n)-[:MemberOf]->(m)', sid=sid, gname=get_name("ENTERPRISE DOMAIN CONTROLLERS", domain_name))
        session.run('MERGE (n:Computer {objectid:$sid}) WITH n MERGE (m:Group {name:$gname}) WITH n,m MERGE (m)-[:AdminTo]->(n)', sid=sid, gname=get_name("DOMAIN ADMINS", domain_name))
    return dc_properties_list, ridcount