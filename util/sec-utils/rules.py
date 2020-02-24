
import sys, argparse, re, json
from config import get_config, get_config_section, update_config_section


ZINGBOX_DATA_RULE_START = 1200000
ZINGBOX_DATA_RULE_END = 1200000 + 1000

def is_rule_id_in_valid_range (sig_id):
    if sig_id == 0:
        return False
    if sig_id >= ZINGBOX_DATA_RULE_START and sig_id <= ZINGBOX_DATA_RULE_END:
        return False
    return True

def dump_rules(rules, comment):
    print("#{}".format(comment))
    for rule in rules:
        print("{}".format(rule))

rule_pattern_ignore = re.compile("(^\#.*$|^\s*$)")
def ignore_rule_line(line):
    if rule_pattern_ignore.match(line):
        return True
    return False

rule_pattern_alert  = re.compile("^\s*alert\s+.*\(.*sid:\s*[0-9]+.*\)\s*$")
def is_alert_rule(line):
    if rule_pattern_alert.match(line):
        return True
    return False

def get_rule_id(line):
    m = re.search("sid:\s*([0-9]+)", line)
    if not m:
         return (0,0)
    try:
        sig_id = int(m.groups()[0])
    except:
        return (0,0)
    m = re.search("rev:\s*[0-9]+", line)
    if not m or not m.groups():
        sig_rev = 0
    else:
        try:
            sig_rev = int(m.groups()[0])
        except:
            sig_rev = 0
    return (sig_id, sig_rev)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api_server", help="API server to point to")
    parser.add_argument("-j", "--jwt", help="JWT token to access api server")
    parser.add_argument("-t", "--tenant", help="external tenant id")
    parser.add_argument("-i", "--inspector", help="inspector specific rules")
    parser.add_argument("action", nargs='*', help='get | set <file>')
    args = parser.parse_args()

    api_server = args.api_server
    if not api_server:
        print("Missing API Server")
        sys.exit(1)

    jwt = args.jwt
    if not jwt:
        print("Missing jwt Token")
        sys.exit(1)

    tenant = args.tenant
    if not tenant:
        print("Missing Tenant")
        sys.exit(1)

    inspector = args.inspector

    if not args.action:
        sys.exit(1)
    action = args.action[0]
    if action == 'get':
        pass
    elif action == 'set':
        if len(args.action) < 2:
            print("Missing input file")
            sys.exit(1)
        file_name = args.action[1]
    else:
        print("Unknown Action: {}".format(action))
        sys.exit(1)

    config = get_config(api_server, jwt, tenant)
    if config:
        pass
    else:
        print("Error retrieving tenant configuration for: {}".format(tenant))
        sys.exit(1)

    rules = get_config_section (config, 'rules')

    if action == 'get':
        dump_rules(rules[0], "common rules for all inspectors of this tenant")
        if inspector is None:
            for ins,ins_rules in rules[1].iteritems():
                dump_rules(ins_rules, "rules for inspector %s only" % ins)
            sys.exit(0)

        print("#At inspector level, inspectors with rules(empty if none): ")
        rules = get_config_section (config, 'rules', inspector=inspector)
        if inspector in rules[1]:
            dump_rules(rules[1][inspector], "rules for inspector %s only" % inspector)
        sys.exit(0)

    # set
    new_rules = []
    with open(file_name, 'r') as f:
        lines = f.readlines()
        lines = [ l.strip() for l in lines ]
        line_num = 1
        for line in lines:
            if is_alert_rule(line):
                (sig_id, sig_rev) = get_rule_id(line)
                if not is_rule_id_in_valid_range(sig_id):
                    print("Error: rule at line {} is not in valid sid range: {}, {}".format(line_num, sig_id, line))
                    sys.exit(1)
                new_rules.append(line)
            elif ignore_rule_line(line):
                continue
            else:
                print("ignore line {}: {}".format(line_num,line))
            line_num += 1

    if inspector:
        print("About to write to tenant {}'s common rules section".format(tenant))
    else:
        print("About to write to tenant {}'s inspector rules section for {}".format(tenant, inspector))
    dump_rules(new_rules, "rules to write")  
    res = update_config_section(api_server, jwt, tenant, 'rules', new_rules, inspector=inspector)
    if 'error' in res:
        print("!!!!Error!!!:\n     {}".format(res['error']))
    else:
        print("Updated configuration at version: {}".format(res['newVersion']))
