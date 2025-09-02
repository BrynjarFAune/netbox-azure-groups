#!/usr/bin/env python3
"""
FortiGate Policy Import Script
Parses FortiGate policy JSON and converts to NetBox-compatible format
"""

import json
import requests
from datetime import datetime

class FortiGatePolicyParser:
    def __init__(self, fortigate_host='10.0.101.1', vdom='root'):
        self.fortigate_host = fortigate_host
        self.vdom = vdom
    
    def load_policies_from_file(self, filename='fortigate_policies_raw.json'):
        """Load policies from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        return data.get('results', [])
    
    def parse_policy(self, policy_data):
        """Parse a single FortiGate policy into NetBox format"""
        
        # Extract basic info
        policy_id = policy_data.get('policyid')
        name = policy_data.get('name', '').strip() or f"Policy-{policy_id}"
        uuid = policy_data.get('uuid', '')
        status = policy_data.get('status', 'enable')
        action = policy_data.get('action', 'accept')
        
        # Extract interfaces
        source_interfaces = [intf.get('name') for intf in policy_data.get('srcintf', [])]
        destination_interfaces = [intf.get('name') for intf in policy_data.get('dstintf', [])]
        
        # Extract addresses
        source_addresses = [addr.get('name') for addr in policy_data.get('srcaddr', [])]
        destination_addresses = [addr.get('name') for addr in policy_data.get('dstaddr', [])]
        
        # Extract services
        services = [svc.get('name') for svc in policy_data.get('service', [])]
        
        # Check for NAT
        nat_enabled = policy_data.get('nat', 'disable') == 'enable'
        nat_type = None
        nat_outbound = None
        
        if nat_enabled:
            # Determine NAT type based on FortiGate policy settings
            if policy_data.get('natip', '0.0.0.0 0.0.0.0') != '0.0.0.0 0.0.0.0':
                nat_type = 'snat'
            if policy_data.get('dnatip'):
                nat_type = 'dnat' if nat_type != 'snat' else 'both'
            
            nat_outbound = destination_interfaces[0] if destination_interfaces else ''
        
        # Security profiles
        utm_status = policy_data.get('utm-status', 'disable')
        profile_group = policy_data.get('profile-group', '')
        
        # Logging
        log_traffic = policy_data.get('logtraffic', 'utm')
        
        # Schedule and groups
        schedule = policy_data.get('schedule', 'always')
        groups = [grp.get('name') for grp in policy_data.get('groups', [])]
        
        # Comments
        comments = policy_data.get('comments', '')
        
        return {
            'policy_id': policy_id,
            'name': name,
            'uuid': uuid,
            'status': status,
            'action': action,
            'source_interfaces': source_interfaces,
            'destination_interfaces': destination_interfaces,
            'source_addresses': source_addresses,
            'destination_addresses': destination_addresses,
            'services': services,
            'nat_enabled': nat_enabled,
            'nat_type': nat_type,
            'nat_outbound_interface': nat_outbound,
            'utm_status': utm_status,
            'profile_group': profile_group,
            'log_traffic': log_traffic,
            'schedule': schedule,
            'groups': groups,
            'comments': comments,
            'fortigate_host': self.fortigate_host,
            'vdom': self.vdom,
        }
    
    def generate_ai_description(self, parsed_policy):
        """Generate AI description for the policy"""
        action_text = "allows" if parsed_policy['action'] == "accept" else "blocks" if parsed_policy['action'] == "deny" else f"applies {parsed_policy['action']} to"
        
        # Source description
        src_intf = ', '.join(parsed_policy['source_interfaces']) if parsed_policy['source_interfaces'] else 'any interface'
        src_addr = ', '.join(parsed_policy['source_addresses']) if parsed_policy['source_addresses'] and 'all' not in parsed_policy['source_addresses'] else ''
        
        src_text = f"traffic from {src_intf}"
        if src_addr:
            src_text += f" ({src_addr})"
        
        # Destination description  
        dst_intf = ', '.join(parsed_policy['destination_interfaces']) if parsed_policy['destination_interfaces'] else 'any interface'
        dst_addr = ', '.join(parsed_policy['destination_addresses']) if parsed_policy['destination_addresses'] and 'all' not in parsed_policy['destination_addresses'] else ''
        
        dst_text = f"to {dst_intf}"
        if dst_addr:
            dst_text += f" ({dst_addr})"
        
        # Services description
        svc_text = ""
        if parsed_policy['services'] and 'ALL' not in parsed_policy['services']:
            svc_text = f" using {', '.join(parsed_policy['services'])}"
        
        # NAT description
        nat_text = ""
        if parsed_policy['nat_enabled']:
            nat_type = parsed_policy['nat_type'].upper() if parsed_policy['nat_type'] else 'NAT'
            nat_text = f" with {nat_type} applied"
        
        description = f"This policy {action_text} {src_text} {dst_text}{svc_text}{nat_text}."
        
        # Add status info
        if parsed_policy['status'] == 'disable':
            description += " (Currently disabled)"
        
        # Add security info
        if parsed_policy['utm_status'] == 'enable':
            description += " Security profiles are enabled."
        
        return description
    
    def analyze_policies(self, policies_data):
        """Analyze policies and show statistics"""
        parsed_policies = []
        
        print(f"Analyzing {len(policies_data)} FortiGate policies...")
        print("=" * 50)
        
        # Statistics
        actions = {}
        statuses = {}
        nat_policies = 0
        utm_policies = 0
        
        for policy in policies_data:  # Process all policies
            parsed = self.parse_policy(policy)
            parsed['ai_description'] = self.generate_ai_description(parsed)
            parsed_policies.append(parsed)
            
            # Track stats
            actions[parsed['action']] = actions.get(parsed['action'], 0) + 1
            statuses[parsed['status']] = statuses.get(parsed['status'], 0) + 1
            
            if parsed['nat_enabled']:
                nat_policies += 1
            if parsed['utm_status'] == 'enable':
                utm_policies += 1
        
        print(f"Policy Actions: {actions}")
        print(f"Policy Status: {statuses}")
        print(f"NAT Policies: {nat_policies}/{len(parsed_policies)}")
        print(f"UTM Policies: {utm_policies}/{len(parsed_policies)}")
        print()
        
        # Show sample policies
        print("Sample Parsed Policies:")
        print("-" * 30)
        
        for i, policy in enumerate(parsed_policies[:3]):
            print(f"\nPolicy {policy['policy_id']}: {policy['name']}")
            print(f"  Action: {policy['action']} | Status: {policy['status']}")
            print(f"  Source: {policy['source_interfaces_display'] if 'source_interfaces_display' in policy else ', '.join(policy['source_interfaces']) or 'any'}")
            print(f"  Destination: {policy['destination_interfaces_display'] if 'destination_interfaces_display' in policy else ', '.join(policy['destination_interfaces']) or 'any'}")
            print(f"  Services: {', '.join(policy['services']) or 'any'}")
            print(f"  NAT: {'Yes' if policy['nat_enabled'] else 'No'}")
            print(f"  AI Description: {policy['ai_description']}")
        
        return parsed_policies
    
    def create_netbox_payload(self, parsed_policy):
        """Create NetBox API payload for FortiGate policy"""
        return {
            'policy_id': parsed_policy['policy_id'],
            'name': parsed_policy['name'],
            'uuid': parsed_policy['uuid'],
            'status': parsed_policy['status'],
            'action': parsed_policy['action'],
            'source_interfaces': parsed_policy['source_interfaces'],
            'destination_interfaces': parsed_policy['destination_interfaces'], 
            'source_addresses': parsed_policy['source_addresses'],
            'destination_addresses': parsed_policy['destination_addresses'],
            'services': parsed_policy['services'],
            'nat_enabled': parsed_policy['nat_enabled'],
            'nat_type': parsed_policy['nat_type'] or '',
            'nat_outbound_interface': parsed_policy['nat_outbound_interface'] or '',
            'utm_status': parsed_policy['utm_status'],
            'profile_group': parsed_policy['profile_group'],
            'log_traffic': parsed_policy['log_traffic'],
            'schedule': parsed_policy['schedule'],
            'groups': parsed_policy['groups'],
            'comments': parsed_policy['comments'],
            'ai_description': parsed_policy['ai_description'],
            'fortigate_host': parsed_policy['fortigate_host'],
            'vdom': parsed_policy['vdom'],
        }


def main():
    parser = FortiGatePolicyParser()
    
    # Load policies from file
    try:
        policies = parser.load_policies_from_file()
        print(f"Loaded {len(policies)} policies from FortiGate JSON file")
    except FileNotFoundError:
        print("Error: fortigate_policies_raw.json not found. Run the curl command first to fetch policies.")
        return 1
    
    # Analyze and parse policies
    parsed_policies = parser.analyze_policies(policies)
    
    # Save parsed policies for NetBox import
    output_file = f"fortigate_policies_parsed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    netbox_payloads = [parser.create_netbox_payload(p) for p in parsed_policies]
    
    with open(output_file, 'w') as f:
        json.dump(netbox_payloads, f, indent=2, default=str)
    
    print(f"\nParsed policies saved to: {output_file}")
    print(f"Ready for NetBox import via API!")
    
    return 0


if __name__ == "__main__":
    exit(main())