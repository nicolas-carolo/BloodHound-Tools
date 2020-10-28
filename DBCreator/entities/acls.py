from templates.groups import STANDARD_GROUPS
# from entities.groups import set_group_attributes


def get_forest_group_aces_list(domain_name, domain_sid):
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