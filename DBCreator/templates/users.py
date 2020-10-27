GUEST_USER = {
      "Properties": {
        "highvalue": False,
        "name": "GUEST@DOMAIN_NAME.DOMAIN_SUFFIX",
        "domain": "DOMAIN_NAME.DOMAIN_SUFFIX",
        "objectid": "DOMAIN_SID-501",
        "distinguishedname": "CN=Guest,CN=Users,DC=DOMAIN_NAME,DC=DOMAIN_SUFFIX",
        "description": "Built-in account for guest access to the computer/domain",
        "dontreqpreauth": False,
        "passwordnotreqd": True,
        "unconstraineddelegation": False,
        "sensitive": False,
        "enabled": False,
        "pwdneverexpires": True,
        "lastlogon": -1,
        "lastlogontimestamp": -1,
        "pwdlastset": -1,
        "serviceprincipalnames": [],
        "hasspn": False,
        "displayname": "null",
        "email": "null",
        "title": "null",
        "homedirectory": "null",
        "userpassword": "null",
        "admincount": False,
        "sidhistory": []
      },
      "AllowedToDelegate": [],
      "SPNTargets": [],
      "PrimaryGroupSid": "DOMAIN_SID-514",
      "HasSIDHistory": [],
      "ObjectIdentifier": "DOMAIN_SID-501",
      "Aces": [
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "Owner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-548",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": True
        }
      ]
    }