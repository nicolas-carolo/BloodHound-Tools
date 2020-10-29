from templates.groups import STANDARD_GROUPS
from entities.users import get_standard_users_list


def get_standard_group_aces_list(domain_name, domain_sid):
    groups_aces_list = []
    groups_list = STANDARD_GROUPS
    for group in groups_list:
        filtered_aces_list = get_filtered_aces_list(group["Aces"])
        for ace in filtered_aces_list:
            object_id = get_object_id(group["ObjectIdentifier"], domain_name, domain_sid)
            identity_reference_id = get_object_id(ace["PrincipalSID"], domain_name, domain_sid)
            if str(object_id).upper() != str(identity_reference_id).upper():
                item = {
                    "ObjectId": object_id,
                    "ObjectType": "Group",
                    "IdentityReferenceId": identity_reference_id,
                    "IdentityReferenceType": ace["PrincipalType"],
                    "Right": ace["RightName"],
                    "IsInherited": ace["IsInherited"]
                }
                groups_aces_list.append(item)
    return groups_aces_list


def get_standard_user_aces_list(domain_name, domain_sid):
    users_list = get_standard_users_list()
    users_aces_list = []
    for user in users_list:
        filtered_aces_list = get_filtered_aces_list(user["Aces"])
        for ace in filtered_aces_list:
            object_id = get_object_id(user["ObjectIdentifier"], domain_name, domain_sid)
            identity_reference_id = get_object_id(ace["PrincipalSID"], domain_name, domain_sid)
            if str(object_id).upper() != str(identity_reference_id).upper():
                item = {
                    "ObjectId": object_id,
                    "ObjectType": "User",
                    "IdentityReferenceId": identity_reference_id,
                    "IdentityReferenceType": ace["PrincipalType"],
                    "Right": ace["RightName"],
                    "IsInherited": ace["IsInherited"]
                }
                users_aces_list.append(item)
    return users_aces_list


def get_standard_all_extended_rights(users_list, domain_admins_list, domain_name, domain_sid):
    aces_list = []
    administrators_sid = str(domain_name).upper() + "-" + "S-1-5-32-544"
    enterprise_admins_sid = domain_sid + "-519"
    domain_admins_sid = domain_sid + "-512"
    print("da:", domain_admins_sid)
    print("ea:", enterprise_admins_sid)
    print(domain_admins_list)
    for group_sid in [administrators_sid, domain_admins_sid]:
        ace = {
            "ObjectId": domain_sid,
            "ObjectType": "Domain",
            "IdentityReferenceId": group_sid,
            "IdentityReferenceType": "Group",
            "Right": "AllExtendedRights",
            "IsInherited": False
        }
        aces_list.append(ace)
    for user in users_list:
        if user["props"]["name"] in domain_admins_list:
            print(user["props"]["name"])
            is_inherited = False
            ace = {
                "ObjectId": user["id"],
                "ObjectType": "User",
                "IdentityReferenceId": enterprise_admins_sid,
                "IdentityReferenceType": "Group",
                "Right": "AllExtendedRights",
                "IsInherited": False
            }
            aces_list.append(ace)
            ace = {
                "ObjectId": user["id"],
                "ObjectType": "User",
                "IdentityReferenceId": domain_admins_sid,
                "IdentityReferenceType": "Group",
                "Right": "AllExtendedRights",
                "IsInherited": False
            }
            aces_list.append(ace)
        else:
            is_inherited = True
        ace = {
            "ObjectId": user["id"],
            "ObjectType": "User",
            "IdentityReferenceId": administrators_sid,
            "IdentityReferenceType": "Group",
            "Right": "AllExtendedRights",
            "IsInherited": is_inherited
        }
        aces_list.append(ace)
    return aces_list


def get_filtered_aces_list(aces_list):
    filtered_aces_list = []
    for ace in aces_list:
        if ace["RightName"] == "GenericAll":
            ace["RightName"] = "GenericAll"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "WriteDacl":
            ace["RightName"] = "WriteDacl"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "WriteOwner":
            ace["RightName"] = "WriteOwner"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "GenericWrite":
            ace["RightName"] = "GenericWrite"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "Owner":
            ace["RightName"] = "Owns"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "ReadLAPSPassword":
            ace["RightName"] = "ReadLAPSPassword"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "ReadGMSAPassword":
            ace["RightName"] = "ReadGMSAPassword"
            filtered_aces_list.append(ace)
        elif ace["AceType"] == "All":
            ace["RightName"] = "AllExtendedRights"
            filtered_aces_list.append(ace)
        elif ace["AceType"] == "GetChanges":
            ace["RightName"] = "GetChanges"
            filtered_aces_list.append(ace)
        elif ace["AceType"] == "GetChangesAll":
            ace["RightName"] = "GetChangesAll"
            filtered_aces_list.append(ace)
        elif ace["AceType"] == "User-Force-Change-Password":
            ace["RightName"] = "ForceChangePassword"
            filtered_aces_list.append(ace)
        elif ace["AceType"] == "AllowedToAct":
            ace["RightName"] = "AddAllowedToAct"
            filtered_aces_list.append(ace)
        elif ace["RightName"] == "ExtendedRight" and ace["AceType"] != "":
            ace["RightName"] = ace["AceType"]
            filtered_aces_list.append(ace)
    return filtered_aces_list


def get_object_id(object_id, domain_name, domain_sid):
    object_id = str(object_id).replace("DOMAIN_SID", domain_sid)
    object_id = str(object_id).replace("DOMAIN_NAME.DOMAIN_SUFFIX", str(domain_name).upper())
    return object_id