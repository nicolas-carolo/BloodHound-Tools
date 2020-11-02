# Requirements - pip install neo4j-driver
# This script is used to create randomized sample databases.
# Commands
# 	dbconfig - Set the credentials and URL for the database you're connecting too
#	connect - Connects to the database using supplied credentials
# 	setnodes - Set the number of nodes to generate (defaults to 500, this is a safe number!)
# 	setdomain - Set the domain name
# 	cleardb - Clears the database and sets the schema properly
#	generate - Generates random data in the database
#	clear_and_generate - Connects to the database, clears the DB, sets the schema, and generates random data

from neo4j import GraphDatabase
import cmd
import os
import sys
import random
import pickle
import math
import itertools
from collections import defaultdict
import uuid
import time

from entities.acls import get_standard_group_aces_list, get_standard_user_aces_list, get_standard_all_extended_rights,\
    get_standard_generic_write, get_standard_owns, get_standard_write_dacl, get_standard_write_owner,\
    get_standard_generic_all
from utils.principals import get_name, get_sid_from_rid
from generators.groups import generate_default_groups
from generators.domains import generate_domain
from generators.gpos import generate_default_gpos, link_default_gpos
from generators.ous import generate_domain_controllers_ou
from generators.acls import generate_enterprise_admins_acls, generate_administrators_acls, generate_domain_admins_acls,\
    generate_default_groups_acls
from generators.computers import generate_computers, generate_dcs, generate_default_admin_to
from generators.users import generate_guest_user, generate_default_account, generate_administrator, generate_krbtgt_user,\
    generate_users, link_default_users_to_domain
from generators.groups import generate_groups, generate_domain_administrators, generate_default_member_of, nest_groups

from templates.groups import WEIGHTED_PARTS


class Messages():
    def title(self):
        print("================================================================")
        print("BloodHound Sample Database Creator")
        print("================================================================")


    def input_default(self, prompt, default):
        return input("%s [%s] " % (prompt, default)) or default


    def input_yesno(self, prompt, default):
        temp = input(prompt + " " + ("Y" if default else "y") + "/" + ("n" if default else "N") + " ")
        if temp == "y" or temp == "Y":
            return True
        elif temp == "n" or temp == "N":
            return False
        return default



class MainMenu(cmd.Cmd):

    def __init__(self):
        self.m = Messages()
        self.url = "bolt://localhost:7687"
        self.username = "neo4j"
        self.password = "password"
        self.use_encryption = False
        self.driver = None
        self.connected = False
        self.num_nodes = 50
        self.domain = "TESTLAB.LOCAL"
        self.current_time = int(time.time())
        self.base_sid = "S-1-5-21-883232822-274137685-4173207997"
        with open('first.pkl', 'rb') as f:
            self.first_names = pickle.load(f)

        with open('last.pkl', 'rb') as f:
            self.last_names = pickle.load(f)

        cmd.Cmd.__init__(self)


    def cmdloop(self):
        while True:
            self.m.title()
            self.do_help("")
            try:
                cmd.Cmd.cmdloop(self)
            except KeyboardInterrupt:
                if self.driver is not None:
                    self.driver.close()
                raise KeyboardInterrupt


    def help_dbconfig(self):
        print("Configure database connection parameters")


    def help_connect(self):
        print("Test connection to the database and verify credentials")

 
    def help_setnodes(self):
        print("Set base number of nodes to generate (default 500)")

 
    def help_setdomain(self):
        print("Set domain name (default 'TESTLAB.LOCAL')")

 
    def help_cleardb(self):
        print("Clear the database and set constraints")

 
    def help_generate(self):
        print("Generate random data")

 
    def help_clear_and_generate(self):
        print("Connect to the database, clear the db, set the schema, and generate random data")

 
    def help_exit(self):
        print("Exits the database creator")

 
    def do_dbconfig(self, args):
        print("Current Settings:")
        print("DB Url: {}".format(self.url))
        print("DB Username: {}".format(self.username))
        print("DB Password: {}".format(self.password))
        print("Use encryption: {}".format(self.use_encryption))
        print("")
        self.url = self.m.input_default("Enter DB URL", self.url)
        self.username = self.m.input_default(
            "Enter DB Username", self.username)
        self.password = self.m.input_default(
            "Enter DB Password", self.password)

        self.use_encryption = self.m.input_yesno(
            "Use encryption?", self.use_encryption)
        print("")
        print("New Settings:")
        print("DB Url: {}".format(self.url))
        print("DB Username: {}".format(self.username))
        print("DB Password: {}".format(self.password))
        print("Use encryption: {}".format(self.use_encryption))
        print("")
        print("Testing DB Connection")
        self.test_db_conn()

 
    def do_setnodes(self, args):
        passed = args
        if passed != "":
            try:
                self.num_nodes = int(passed)
                """
                if self.num_nodes < 282:
                    self.num_nodes = 500
                    self.do_setnodes("")
                else:
                    return
                """
            except ValueError:
                pass
        else:
            self.num_nodes = int(self.m.input_default(
                "Number of nodes of each type to generate", self.num_nodes))
            """
            if self.num_nodes < 282:
                self.num_nodes = 500
                self.do_setnodes("")
            else:
                return
            """

 
    def do_setdomain(self, args):
        passed = args
        if passed != "":
            try:
                self.domain = passed.upper()
                return
            except ValueError:
                pass

        self.domain = self.m.input_default("Domain", self.domain).upper()
        print("")
        print("New Settings:")
        print("Domain: {}".format(self.domain))


    def do_exit(self, args):
        raise KeyboardInterrupt

 
    def do_connect(self, args):
        self.test_db_conn()


    def do_cleardb(self, args):
        if not self.connected:
            print("Not connected to database. Use connect first")
            return

        print("Clearing Database")
        d = self.driver
        session = d.session()

        session.run("match (a) -[r] -> () delete a, r")
        session.run("match (a) delete a")

        session.close()

        print("DB Cleared and Schema Set")


    def test_db_conn(self):
        self.connected = False
        if self.driver is not None:
            self.driver.close()
        try:
            self.driver = GraphDatabase.driver(
                self.url, auth=(self.username, self.password), encrypted=self.use_encryption)
            self.connected = True
            print("Database Connection Successful!")
        except:
            self.connected = False
            print("Database Connection Failed. Check your settings.")


    def do_generate(self, args):
        self.generate_data()


    def do_clear_and_generate(self, args):
        self.test_db_conn()
        self.do_cleardb("a")
        self.generate_data()

 
    def split_seq(self, iterable, size):
        it = iter(iterable)
        item = list(itertools.islice(it, size))
        while item:
            yield item
            item = list(itertools.islice(it, size))

 
    """
    def generate_timestamp(self):
        choice = random.randint(-1, 1)
        if choice == 1:
            variation = random.randint(0, 31536000)
            return self.current_time - variation
        else:
            return choice
    """

 
    def generate_data(self):
        if not self.connected:
            print("Not connected to database. Use connect first")
            return

        computers = []
        computer_properties_list = []
        dc_properties_list = []
        groups = []
        users = []
        user_properties_list = []
        gpos = []
        gpos_properties_list = []
        ou_guid_map = {}
        ou_properties_list = []

        # used_states = []

        states = ["WA", "MD", "AL", "IN", "NV", "VA", "CA", "NY", "TX", "FL"]
        partitions = ["IT", "HR", "MARKETING", "OPERATIONS", "BIDNESS"]
        
        session = self.driver.session()


        print("Starting data generation with nodes={}".format(self.num_nodes))

        print("Generating the Domain")
        generate_domain(session, self.domain, self.base_sid)
        
        print("Generating the default domain Groups")
        generate_default_groups(session, self.domain, self.base_sid)
                

        # TODO upper case for all the GPOs
        ddp = str(uuid.uuid4()).upper()
        ddcp = str(uuid.uuid4()).upper()
        dcou = str(uuid.uuid4()).upper()
    

        print("Generating default GPOs")
        generate_default_gpos(session, self.domain, ddp, ddcp)

        print("Generating Domain Controllers OU")
        generate_domain_controllers_ou(session, self.domain, dcou)

        print("Adding Standard Edges")

        print("Linking Default GPOs")
        link_default_gpos(session, self.domain, ddp, ddcp, dcou)

        print("Generating Enterprise Admins ACLs")
        generate_enterprise_admins_acls(session, self.domain)

        print("Generating Administrators ACLs")
        generate_administrators_acls(session, self.domain)

        print("Generating Domain Admins ACLs")
        generate_domain_admins_acls(session, self.domain)

        print("Generating DC Groups ACLs")
        generate_default_groups_acls(session, self.domain)

        print("Generating Computer Nodes")
        computer_properties_list, computers, ridcount = generate_computers(session, self.domain, self.base_sid, self.num_nodes, computers)

        print("Generating Domain Controllers")
        dc_properties_list, ridcount = generate_dcs(session, self.domain, self.base_sid, dcou, ridcount)
        # print(dc_properties_list)


        # used_states = list(set(used_states))
        # print(used_states)

        print("Generating default User Nodes")
        generate_guest_user(session, self.domain, self.base_sid)
        generate_default_account(session, self.domain, self.base_sid)
        generate_administrator(session, self.domain, self.base_sid)
        generate_krbtgt_user(session, self.domain, self.base_sid)

        print("Adding default User nodes to the domain")
        link_default_users_to_domain(session, self.domain, self.base_sid)

        print("Generating User Nodes")
        user_properties_list, users, ridcount = generate_users(session, self.domain, self.base_sid, self.num_nodes, self.current_time, self.first_names, self.last_names, users, ridcount)

        print("Generating Group Nodes")
        groups, ridcount = generate_groups(session, self.domain, self.base_sid, self.num_nodes, groups, ridcount)

        print("Adding Domain Admins to Local Admins of Computers")
        generate_default_admin_to(session, self.base_sid)

        das = generate_domain_administrators(session, self.domain, self.num_nodes, users)

        print("Adding members to default groups")
        generate_default_member_of(session, self.domain, self.base_sid)

        print("Applying random group nesting")
        nest_groups(session, self.num_nodes, groups)

        print("Adding users to groups")
        props = []
        a = math.log10(self.num_nodes)
        a = math.pow(a, 2)
        a = math.floor(a)
        a = int(a)
        num_groups_base = a
        variance = int(math.ceil(math.log10(self.num_nodes)))
        it_users = []

        # print("\n\nNUM GROUPS BASE:", num_groups_base)

        print("Calculated {} groups per user with a variance of - {}".format(num_groups_base, variance*2))

        for user in users:
            dept = random.choice(WEIGHTED_PARTS)
            if dept == "IT":
                it_users.append(user)
            possible_groups = [x for x in groups if dept in x]

            sample = num_groups_base + random.randrange(-(variance*2), 0)
            if (sample > len(possible_groups)):
                sample = int(math.floor(float(len(possible_groups)) / 4))

            if (sample <= 1):
                continue

            # print("\n\nPOSSIBLE GROUPS:\n", possible_groups)
            # print("\n\nSAMPLE:\n", sample)
            to_add = random.sample(possible_groups, sample)

            for group in to_add:
                props.append({'a': user, 'b': group})

            if len(props) > 500:
                session.run(
                    'UNWIND $props AS prop MERGE (n:User {name:prop.a}) WITH n,prop MERGE (m:Group {name:prop.b}) WITH n,m MERGE (n)-[:MemberOf]->(m)', props=props)
                props = []

        session.run(
            'UNWIND $props AS prop MERGE (n:User {name:prop.a}) WITH n,prop MERGE (m:Group {name:prop.b}) WITH n,m MERGE (n)-[:MemberOf]->(m)', props=props)

        it_users = it_users + das
        it_users = list(set(it_users))

        print("Adding local admin rights")
        it_groups = [x for x in groups if "IT" in x]
        random.shuffle(it_groups)
        # print("LEN IT_GROUPS:", len(it_groups))
        if len(it_groups) <= 4:
            max_lim = random.randint(1, len(it_groups) - 1)
        else:
            max_lim = 4
        super_groups = random.sample(it_groups, max_lim)
        super_group_num = int(math.floor(len(computers) * .85))

        it_groups = [x for x in it_groups if not x in super_groups]

        total_it_groups = len(it_groups)

        dista = int(math.ceil(total_it_groups * .6))
        distb = int(math.ceil(total_it_groups * .3))
        distc = int(math.ceil(total_it_groups * .07))
        distd = int(math.ceil(total_it_groups * .03))

        distribution_list = [1] * dista + [2] * \
            distb + [10] * distc + [50] * distd

        props = []
        for x in range(0, total_it_groups):
            g = it_groups[x]
            dist = distribution_list[x]

            to_add = random.sample(computers, dist)
            for a in to_add:
                props.append({'a': g, 'b': a})

            if len(props) > 500:
                session.run(
                    'UNWIND $props AS prop MERGE (n:Group {name:prop.a}) WITH n,prop MERGE (m:Computer {name:prop.b}) WITH n,m MERGE (n)-[:AdminTo]->(m)', props=props)
                props = []

        for x in super_groups:
            for a in random.sample(computers, super_group_num):
                props.append({'a': x, 'b': a})

            if len(props) > 500:
                session.run(
                    'UNWIND $props AS prop MERGE (n:Group {name:prop.a}) WITH n,prop MERGE (m:Computer {name:prop.b}) WITH n,m MERGE (n)-[:AdminTo]->(m)', props=props)
                props = []

        session.run(
            'UNWIND $props AS prop MERGE (n:Group {name:prop.a}) WITH n,prop MERGE (m:Computer {name:prop.b}) WITH n,m MERGE (n)-[:AdminTo]->(m)', props=props)

        print("Adding ACLs for standard nodes")
        standard_group_aces_list = get_standard_group_aces_list(self.domain, self.base_sid)
        for ace in standard_group_aces_list:
            query = "MATCH (identityReferenceItem:" + ace["IdentityReferenceType"] + " {objectid: '" + ace["IdentityReferenceId"] + "'}), (objectItem:" + ace["ObjectType"] + " {objectid: '" + ace["ObjectId"] + "'})"
            query = query + "\nMERGE (identityReferenceItem)-[:" + ace["Right"] + " {isinherited: " + str(ace["IsInherited"]) + "}]->(objectItem)"
            session.run(query)
        
        standard_user_aces_list = get_standard_user_aces_list(self.domain, self.base_sid)
        for ace in standard_user_aces_list:
            query = "MATCH (identityReferenceItem:" + ace["IdentityReferenceType"] + " {objectid: '" + ace["IdentityReferenceId"] + "'}), (objectItem:" + ace["ObjectType"] + " {objectid: '" + ace["ObjectId"] + "'})"
            query = query + "\nMERGE (identityReferenceItem)-[:" + ace["Right"] + " {isinherited: " + str(ace["IsInherited"]) + "}]->(objectItem)"
            session.run(query)
        

        print("Adding AllExtendedRights")
        all_extended_rights_aces_list = get_standard_all_extended_rights(user_properties_list, das, self.domain, self.base_sid)
        for ace in all_extended_rights_aces_list:
            self.add_right_relationship(session, ace)
        

        print("Adding RDP/ExecuteDCOM/AllowedToDelegateTo")
        count = int(math.floor(len(computers) * .1))
        props = []
        for i in range(0, count):
            comp = random.choice(computers)
            user = random.choice(it_users)
            props.append({'a': user, 'b': comp})

        session.run(
            'UNWIND $props AS prop MERGE (n:User {name: prop.a}) MERGE (m:Computer {name: prop.b}) MERGE (n)-[r:CanRDP]->(m)', props=props)

        props = []
        for i in range(0, count):
            comp = random.choice(computers)
            user = random.choice(it_users)
            props.append({'a': user, 'b': comp})

        session.run(
            'UNWIND $props AS prop MERGE (n:User {name: prop.a}) MERGE (m:Computer {name: prop.b}) MERGE (n)-[r:ExecuteDCOM]->(m)', props=props)

        props = []
        for i in range(0, count):
            comp = random.choice(computers)
            user = random.choice(it_groups)
            props.append({'a': user, 'b': comp})

        session.run(
            'UNWIND $props AS prop MERGE (n:Group {name: prop.a}) MERGE (m:Computer {name: prop.b}) MERGE (n)-[r:CanRDP]->(m)', props=props)

        props = []
        for i in range(0, count):
            comp = random.choice(computers)
            user = random.choice(it_groups)
            props.append({'a': user, 'b': comp})

        session.run(
            'UNWIND $props AS prop MERGE (n:Group {name: prop.a}) MERGE (m:Computer {name: prop.b}) MERGE (n)-[r:ExecuteDCOM]->(m)', props=props)

        props = []
        for i in range(0, count):
            comp = random.choice(computers)
            user = random.choice(it_users)
            props.append({'a': user, 'b': comp})

        session.run(
            'UNWIND $props AS prop MERGE (n:User {name: prop.a}) MERGE (m:Computer {name: prop.b}) MERGE (n)-[r:AllowedToDelegate]->(m)', props=props)

        props = []
        for i in range(0, count):
            comp = random.choice(computers)
            user = random.choice(computers)
            if (comp == user):
                continue
            props.append({'a': user, 'b': comp})

        session.run(
            'UNWIND $props AS prop MERGE (n:Computer {name: prop.a}) MERGE (m:Computer {name: prop.b}) MERGE (n)-[r:AllowedToDelegate]->(m)', props=props)

        print("Adding sessions")
        max_sessions_per_user = int(math.ceil(math.log10(self.num_nodes)))

        props = []
        for user in users:
            num_sessions = random.randrange(0, max_sessions_per_user)
            if (user in das):
                num_sessions = max(num_sessions, 1)

            if num_sessions == 0:
                continue

            for c in random.sample(computers, num_sessions):
                props.append({'a': user, 'b': c})

            if (len(props) > 500):
                session.run(
                    'UNWIND $props AS prop MERGE (n:User {name:prop.a}) WITH n,prop MERGE (m:Computer {name:prop.b}) WITH n,m MERGE (m)-[:HasSession]->(n)', props=props)
                props = []

        session.run(
            'UNWIND $props AS prop MERGE (n:User {name:prop.a}) WITH n,prop MERGE (m:Computer {name:prop.b}) WITH n,m MERGE (m)-[:HasSession]->(n)', props=props)

        print("Adding Domain Admin ACEs")
        group_name = "DOMAIN ADMINS@{}".format(self.domain)
        props = []
        """
        for x in computers:
            props.append({'name': x})

            if len(props) > 500:
                session.run(
                    'UNWIND $props as prop MATCH (n:Computer {name:prop.name}) WITH n MATCH (m:Group {name:$gname}) WITH m,n MERGE (m)-[r:GenericAll {isacl:true}]->(n)', props=props, gname=group_name)
                props = []

        session.run(
            'UNWIND $props as prop MATCH (n:Computer {name:prop.name}) WITH n MATCH (m:Group {name:$gname}) WITH m,n MERGE (m)-[r:GenericAll {isacl:true}]->(n)', props=props, gname=group_name)

        for x in users:
            props.append({'name': x})

            if len(props) > 500:
                session.run(
                    'UNWIND $props as prop MATCH (n:User {name:prop.name}) WITH n MATCH (m:Group {name:$gname}) WITH m,n MERGE (m)-[r:GenericAll {isacl:true}]->(n)', props=props, gname=group_name)
                props = []

        session.run(
            'UNWIND $props as prop MATCH (n:User {name:prop.name}) WITH n MATCH (m:Group {name:$gname}) WITH m,n MERGE (m)-[r:GenericAll {isacl:true}]->(n)', props=props, gname=group_name)
        """
        for x in groups:
            props.append({'name': x})

            if len(props) > 500:
                session.run(
                    'UNWIND $props as prop MATCH (n:Group {name:prop.name}) WITH n MATCH (m:Group {name:$gname}) WITH m,n MERGE (m)-[r:GenericAll {isacl:true}]->(n)', props=props, gname=group_name)
                props = []

        session.run(
            'UNWIND $props as prop MATCH (n:Group {name:prop.name}) WITH n MATCH (m:Group {name:$gname}) WITH m,n MERGE (m)-[r:GenericAll {isacl:true}]->(n)', props=props, gname=group_name)

        print("Creating OUs")
        temp_comps = computers
        random.shuffle(temp_comps)
        split_num = int(math.ceil(self.num_nodes / 10))
        split_comps = list(self.split_seq(temp_comps, split_num))
        props = []
        for i in range(0, 10):
            state = states[i]
            ou_comps = split_comps[i]
            ouname = "{}_COMPUTERS@{}".format(state, self.domain)
            guid = str(uuid.uuid4())
            ou_guid_map[ouname] = guid
            for c in ou_comps:
                ou_properties = {
                    'compname': c,
                    'ouguid': guid,
                    'ouname': ouname
                }
                props.append(ou_properties)
                ou_properties_list.append(ou_properties)
                if len(props) > 500:
                    session.run(
                        'UNWIND $props as prop MERGE (n:Computer {name:prop.compname}) WITH n,prop MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false}) SET m:OU WITH n,m,prop MERGE (m)-[:Contains]->(n)', props=props)
                    props = []

        session.run(
            'UNWIND $props as prop MERGE (n:Computer {name:prop.compname}) WITH n,prop MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false}) SET m:OU WITH n,m,prop MERGE (m)-[:Contains]->(n)', props=props)

        temp_users = users
        random.shuffle(temp_users)
        split_users = list(self.split_seq(temp_users, split_num))
        props = []

        for i in range(0, 10):
            state = states[i]
            ou_users = split_users[i]
            ouname = "{}_USERS@{}".format(state, self.domain)
            guid = str(uuid.uuid4())
            ou_guid_map[ouname] = guid
            for c in ou_users:
                props.append({'username': c, 'ouguid': guid, 'ouname': ouname})
                if len(props) > 500:
                    session.run(
                        'UNWIND $props as prop MERGE (n:User {name:prop.username}) WITH n,prop MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false}) SET m:OU WITH n,m,prop MERGE (m)-[:Contains]->(n)', props=props)
                    props = []

        session.run(
            'UNWIND $props as prop MERGE (n:User {name:prop.username}) WITH n,prop MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false}) SET m:OU WITH n,m,prop MERGE (m)-[:Contains]->(n)', props=props)

        props = []
        for x in list(ou_guid_map.keys()):
            guid = ou_guid_map[x]
            props.append({'b': guid})

        session.run(
            'UNWIND $props as prop MERGE (n:OU {objectid:prop.b}) WITH n MERGE (m:Domain {name:$domain}) WITH n,m MERGE (m)-[:Contains]->(n)', props=props, domain=self.domain)

        print("Creating GPOs")

        for i in range(1, 20):
            gpo_name = "GPO_{}@{}".format(i, self.domain)
            guid = str(uuid.uuid4())
            gpo_properties = {
                'id': guid,
                'name': gpo_name
            }
            session.run(
                "MERGE (n:Base {name:$gponame}) SET n:GPO, n.objectid=$guid", gponame=gpo_name, guid=guid)
            gpos.append(gpo_name)
            gpos_properties_list.append(gpo_properties)

        ou_names = list(ou_guid_map.keys())
        for g in gpos:
            num_links = random.randint(1, 3)
            linked_ous = random.sample(ou_names, num_links)
            for l in linked_ous:
                guid = ou_guid_map[l]
                session.run(
                    "MERGE (n:GPO {name:$gponame}) WITH n MERGE (m:OU {objectid:$guid}) WITH n,m MERGE (n)-[r:GpLink]->(m)", gponame=g, guid=guid)

        num_links = random.randint(1, 3)
        linked_ous = random.sample(ou_names, num_links)
        for l in linked_ous:
            guid = ou_guid_map[l]
            session.run(
                "MERGE (n:Domain {name:$gponame}) WITH n MERGE (m:OU {objectid:$guid}) WITH n,m MERGE (n)-[r:GpLink]->(m)", gponame=self.domain, guid=guid)

        gpos.append("DEFAULT DOMAIN POLICY@{}".format(self.domain))
        gpos.append("DEFAULT DOMAIN CONTROLLER POLICY@{}".format(self.domain))

        acl_list = ["GenericAll"] * 10 + ["GenericWrite"] * 15 + ["WriteOwner"] * 15 + ["WriteDacl"] * \
            15 + ["AddMember"] * 30 + ["ForceChangePassword"] * \
            15 + ["ReadLAPSPassword"] * 10

        num_acl_principals = int(round(len(it_groups) * .1))
        

        print("Adding GenericWrite")
        generic_write_aces_list = get_standard_generic_write(computer_properties_list, user_properties_list, gpos_properties_list, das, self.domain, self.base_sid)
        for ace in generic_write_aces_list:
            self.add_right_relationship(session, ace)
        

        print("Adding Owns")
        owns_aces_list = get_standard_owns(computer_properties_list, user_properties_list, ou_properties_list, gpos_properties_list, self.domain, self.base_sid)
        for ace in owns_aces_list:
            self.add_right_relationship(session, ace)
        

        print("Adding WriteDacl")
        write_dacl_aces_list = get_standard_write_dacl(dcou, computer_properties_list, user_properties_list, ou_properties_list, gpos_properties_list, das, self.domain, self.base_sid)
        for ace in write_dacl_aces_list:
            self.add_right_relationship(session, ace)
        

        print("Adding WriteOwner")
        write_owner_aces_list = get_standard_write_owner(dcou, computer_properties_list, user_properties_list, ou_properties_list, gpos_properties_list, das, self.domain, self.base_sid)
        for ace in write_owner_aces_list:
            self.add_right_relationship(session, ace)
        

        print("Adding GenericAll")
        generic_all_aces_list = get_standard_generic_all(dcou, dc_properties_list, computer_properties_list, user_properties_list, ou_properties_list, gpos_properties_list, das, self.domain, self.base_sid)
        for ace in generic_all_aces_list:
            self.add_right_relationship(session, ace)


        print("Adding outbound ACLs to {} objects".format(num_acl_principals))
        acl_groups = random.sample(it_groups, num_acl_principals)
        all_principals = it_users + it_groups
        props = []
        for i in acl_groups:
            ace = random.choice(acl_list)
            ace_string = '[r:' + ace + '{isacl:true}]'
            if ace == "GenericAll" or ace == 'GenericWrite' or ace == 'WriteOwner' or ace == 'WriteDacl':
                p = random.choice(all_principals)
                p2 = random.choice(gpos)
                session.run(
                    'MERGE (n:Group {name:$group}) MERGE (m {name:$principal}) MERGE (n)-' + ace_string + '->(m)', group=i, principal=p)
                session.run('MERGE (n:Group {name:$group}) MERGE (m:GPO {name:$principal}) MERGE (n)-' +
                            ace_string + '->(m)', group=i, principal=p2)
            elif ace == 'AddMember':
                p = random.choice(it_groups)
                session.run(
                    'MERGE (n:Group {name:$group}) MERGE (m:Group {name:$principal}) MERGE (n)-' + ace_string + '->(m)', group=i, principal=p)
            elif ace == 'ReadLAPSPassword':
                p = random.choice(all_principals)
                targ = random.choice(computers)
                session.run(
                    'MERGE (n {name:$principal}) MERGE (m:Computer {name:$target}) MERGE (n)-[r:ReadLAPSPassword]->(m)', target=targ, principal=p)
            else:
                p = random.choice(it_users)
                session.run(
                    'MERGE (n:Group {name:$group}) MERGE (m:User {name:$principal}) MERGE (n)-' + ace_string + '->(m)', group=i, principal=p)

        print("Marking some users as Kerberoastable")
        i = random.randint(10, 20)
        i = min(i, len(it_users))
        for user in random.sample(it_users, i):
            session.run(
                'MATCH (n:User {name:$user}) SET n.hasspn=true', user=user)

        print("Adding unconstrained delegation to a few computers")
        i = random.randint(10, 20)
        i = min(i, len(computers))
        session.run(
            'MATCH (n:Computer {name:$user}) SET n.unconstrainteddelegation=true', user=user)

        session.run('MATCH (n:User) SET n.owned=false')
        session.run('MATCH (n:Computer) SET n.owned=false')
        session.run('MATCH (n) SET n.domain=$domain', domain=self.domain)

        session.close()

        print("Database Generation Finished!")


    def add_right_relationship(self, session, ad_object):
        query = "MATCH (identityReferenceItem:" + ad_object["IdentityReferenceType"] + " {objectid: '" + ad_object["IdentityReferenceId"] + "'}), (objectItem:" + ad_object["ObjectType"] + " {objectid: '" + ad_object["ObjectId"] + "'})"
        query = query + "\nMERGE (identityReferenceItem)-[:" + ad_object["Right"] + " {isinherited: " + str(ad_object["IsInherited"]) + "}]->(objectItem)"
        session.run(query)



if __name__ == '__main__':
    try:
        MainMenu().cmdloop()
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit()

