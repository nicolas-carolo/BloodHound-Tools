from entities.groups import get_forest_default_groups_list, get_forest_standard_group_members_list



def generate_default_groups(session, domain_name, domain_sid):
    default_groups_list = get_forest_default_groups_list(domain_name, domain_sid)
    for default_group in default_groups_list:
        try:
            session.run(
                """
                MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid,
                n.highvalue=$highvalue, n.domain=$domain,
                n.distinguishedname=$distinguishedname,
                n.description=$description, n.admincount=$admincount
                """,
                gname=default_group["Properties"]["name"],
                sid=default_group["ObjectIdentifier"],
                highvalue=default_group["Properties"]["highvalue"],
                domain=default_group["Properties"]["domain"],
                distinguishedname=default_group["Properties"]["distinguishedname"],
                description=default_group["Properties"]["description"],
                admincount=default_group["Properties"]["admincount"]
            )
        except KeyError:
            default_group_properties = default_group["Properties"]
            if not "highvalue" in default_group_properties:
                highvalue = "null"
            else:
                highvalue = default_group["Properties"]["highvalue"]
            if not "distinguishedname" in default_group_properties:
                dn = "null"
            else:
                dn = default_group["Properties"]["distinguishedname"]
            if not "description" in default_group_properties:
                description = "null"
            else:
                description = default_group["Properties"]["description"]
            if not "admincount" in default_group_properties:
                admincount = "null"
            else:
                admincount = default_group["Properties"]["admincount"]
            if not "domain" in default_group_properties:
                domain = "null"
            else:
                domain = default_group["Properties"]["domain"]
            
            session.run(
                """
                MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid,
                n.highvalue=$highvalue, n.domain=$domain,
                n.distinguishedname=$distinguishedname,
                n.description=$description, n.admincount=$admincount
                """,
                gname=default_group["Properties"]["name"],
                sid=default_group["ObjectIdentifier"],
                highvalue=highvalue,
                domain=domain,
                distinguishedname=dn,
                description=description,
                admincount=admincount
            )