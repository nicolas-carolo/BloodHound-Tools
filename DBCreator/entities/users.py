from templates.users import GUEST_USER


def get_guest_user(domain_name, domain_sid):
    guest_user = GUEST_USER
    return set_guest_user_attributes(guest_user, domain_name, domain_sid)


def set_guest_user_attributes(user, domain_name, domain_sid):
    domain_name_splitted = str(domain_name).split(".")
    user["Properties"]["name"] = str(user["Properties"]["name"]).replace("DOMAIN_NAME.DOMAIN_SUFFIX", str(domain_name).upper())
    user["Properties"]["domain"] = str(domain_name).upper()
    user["ObjectIdentifier"] = str(user["ObjectIdentifier"]).replace("DOMAIN_SID", domain_sid)
    user["Properties"]["distinguishedname"] = str(user["Properties"]["distinguishedname"]).replace("DOMAIN_SUFFIX", str(domain_name_splitted[1]).upper())
    user["Properties"]["distinguishedname"] = str(user["Properties"]["distinguishedname"]).replace("DOMAIN_NAME", str(domain_name_splitted[0]).upper())
    return user