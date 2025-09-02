#!/usr/bin/env python3
"""
FortiGate Policy Fetcher
Connects to FortiGate and retrieves firewall policies for NetBox integration
"""

import requests
import json
import argparse
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

# Suppress SSL warnings for FortiGate connections
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class FortiGatePolicyFetcher:
    def __init__(self, host, api_token=None, username=None, password=None, port=443, verify_ssl=False):
        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}:{port}/api/v2"
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # Use API token if provided, otherwise use username/password
        if api_token:
            self.authenticate_token(api_token)
        else:
            self.login(username, password)
    
    def authenticate_token(self, api_token):
        """Authenticate with API token"""
        print(f"Connecting to FortiGate at {self.host}...")
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })
        
        # Test authentication with a simple API call
        test_url = f"{self.base_url}/cmdb/system/global"
        response = self.session.get(test_url)
        
        if response.status_code == 200:
            print("SUCCESS: Successfully connected to FortiGate with API token")
        else:
            raise Exception(f"Failed to authenticate with API token: {response.status_code} - {response.text}")
    
    def login(self, username, password):
        """Authenticate with FortiGate using username/password"""
        login_url = f"{self.base_url}/logincheck"
        login_data = {
            'username': username,
            'secretkey': password
        }
        
        print(f"Connecting to FortiGate at {self.host}...")
        response = self.session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            print("SUCCESS: Successfully connected to FortiGate")
        else:
            raise Exception(f"Failed to login to FortiGate: {response.status_code}")
    
    def get_firewall_policies(self, vdom="root"):
        """Fetch all firewall policies"""
        url = f"{self.base_url}/cmdb/firewall/policy"
        params = {'vdom': vdom}
        
        print(f"Fetching firewall policies from VDOM: {vdom}")
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            policies = data.get('results', [])
            print(f"SUCCESS: Retrieved {len(policies)} firewall policies")
            return policies
        else:
            raise Exception(f"Failed to fetch policies: {response.status_code} - {response.text}")
    
    def get_firewall_addresses(self, vdom="root"):
        """Fetch address objects for reference"""
        url = f"{self.base_url}/cmdb/firewall/address"
        params = {'vdom': vdom}
        
        print(f"Fetching address objects from VDOM: {vdom}")
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            addresses = data.get('results', [])
            print(f"✅ Retrieved {len(addresses)} address objects")
            return addresses
        else:
            print(f"⚠️ Failed to fetch addresses: {response.status_code}")
            return []
    
    def get_firewall_services(self, vdom="root"):
        """Fetch service objects for reference"""
        url = f"{self.base_url}/cmdb/firewall.service/custom"
        params = {'vdom': vdom}
        
        print(f"Fetching service objects from VDOM: {vdom}")
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            services = data.get('results', [])
            print(f"✅ Retrieved {len(services)} service objects")
            return services
        else:
            print(f"⚠️ Failed to fetch services: {response.status_code}")
            return []
    
    def analyze_policy_structure(self, policies):
        """Analyze policy structure to understand what fields we need to model"""
        if not policies:
            return {}
        
        print("\n📊 Analyzing FortiGate Policy Structure:")
        print("=" * 50)
        
        # Sample policy for analysis
        sample_policy = policies[0]
        
        print(f"Sample Policy ID: {sample_policy.get('policyid')}")
        print(f"Policy Name: {sample_policy.get('name', 'Unnamed')}")
        print("\nKey Fields Found:")
        
        key_fields = {}
        for key, value in sample_policy.items():
            if isinstance(value, list) and value:
                print(f"  📋 {key}: {len(value)} items - {[item.get('name', item) for item in value[:3]]}")
                key_fields[key] = 'list'
            elif isinstance(value, dict):
                print(f"  📖 {key}: {value}")
                key_fields[key] = 'dict' 
            else:
                print(f"  📝 {key}: {value}")
                key_fields[key] = type(value).__name__
        
        # Analyze common patterns across all policies
        print(f"\n🔍 Analyzing {len(policies)} policies for common patterns...")
        
        field_stats = {}
        for policy in policies[:10]:  # Analyze first 10 policies
            for key, value in policy.items():
                if key not in field_stats:
                    field_stats[key] = {'count': 0, 'types': set(), 'samples': []}
                
                field_stats[key]['count'] += 1
                field_stats[key]['types'].add(type(value).__name__)
                
                if len(field_stats[key]['samples']) < 3:
                    if isinstance(value, (list, dict)):
                        field_stats[key]['samples'].append(str(value)[:100])
                    else:
                        field_stats[key]['samples'].append(str(value))
        
        print("\n📈 Field Statistics (top 10 policies):")
        for field, stats in sorted(field_stats.items()):
            if stats['count'] >= 5:  # Fields present in most policies
                print(f"  🎯 {field}: appears in {stats['count']}/10 policies")
                print(f"     Types: {', '.join(stats['types'])}")
                if stats['samples']:
                    print(f"     Samples: {stats['samples'][:2]}")
        
        return field_stats
    
    def generate_policy_descriptions(self, policies, max_policies=5):
        """Generate AI descriptions for policies (placeholder - would call Claude API)"""
        print(f"\n🤖 Generating AI descriptions for {min(len(policies), max_policies)} policies...")
        
        for i, policy in enumerate(policies[:max_policies]):
            policy_id = policy.get('policyid', i)
            name = policy.get('name', 'Unnamed Policy')
            
            # Extract key info for description
            action = policy.get('action', 'unknown')
            srcintf = [intf.get('name', str(intf)) for intf in policy.get('srcintf', [])]
            dstintf = [intf.get('name', str(intf)) for intf in policy.get('dstintf', [])]
            srcaddr = [addr.get('name', str(addr)) for addr in policy.get('srcaddr', [])]
            dstaddr = [addr.get('name', str(addr)) for addr in policy.get('dstaddr', [])]
            service = [svc.get('name', str(svc)) for svc in policy.get('service', [])]
            
            # Generate human-readable description
            description = self._create_policy_description(
                action=action,
                srcintf=srcintf,
                dstintf=dstintf, 
                srcaddr=srcaddr,
                dstaddr=dstaddr,
                service=service
            )
            
            print(f"\n📋 Policy {policy_id}: {name}")
            print(f"   🤖 AI Description: {description}")
            
            # Add to policy data
            policy['ai_description'] = description
    
    def _create_policy_description(self, action, srcintf, dstintf, srcaddr, dstaddr, service):
        """Create a human-readable description of what the policy does"""
        action_text = "allows" if action == "accept" else "blocks" if action == "deny" else f"performs {action} on"
        
        src_text = f"traffic from {', '.join(srcintf) if srcintf else 'any interface'}"
        dst_text = f"to {', '.join(dstintf) if dstintf else 'any interface'}"
        
        addr_text = ""
        if srcaddr and dstaddr:
            addr_text = f", from {', '.join(srcaddr)} to {', '.join(dstaddr)}"
        elif srcaddr:
            addr_text = f", from {', '.join(srcaddr)}"
        elif dstaddr:
            addr_text = f", to {', '.join(dstaddr)}"
        
        service_text = f" using {', '.join(service)}" if service else ""
        
        return f"This policy {action_text} {src_text} {dst_text}{addr_text}{service_text}."
    
    def save_to_file(self, data, filename):
        """Save policy data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.json"
        
        with open(full_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"💾 Data saved to {full_filename}")
        return full_filename
    
    def logout(self):
        """Logout from FortiGate"""
        logout_url = f"{self.base_url}/logout"
        self.session.post(logout_url)
        print("👋 Logged out from FortiGate")


def main():
    parser = argparse.ArgumentParser(description="Fetch FortiGate policies for NetBox integration")
    parser.add_argument("--host", required=True, help="FortiGate hostname or IP")
    parser.add_argument("--username", required=True, help="FortiGate username")  
    parser.add_argument("--password", required=True, help="FortiGate password")
    parser.add_argument("--port", type=int, default=443, help="FortiGate HTTPS port")
    parser.add_argument("--vdom", default="root", help="FortiGate VDOM")
    parser.add_argument("--output", default="fortigate_policies", help="Output filename prefix")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze structure, don't save")
    
    args = parser.parse_args()
    
    try:
        # Connect to FortiGate
        fetcher = FortiGatePolicyFetcher(
            host=args.host,
            username=args.username, 
            password=args.password,
            port=args.port
        )
        
        # Fetch data
        policies = fetcher.get_firewall_policies(args.vdom)
        addresses = fetcher.get_firewall_addresses(args.vdom)
        services = fetcher.get_firewall_services(args.vdom)
        
        # Analyze structure
        structure = fetcher.analyze_policy_structure(policies)
        
        # Generate AI descriptions
        fetcher.generate_policy_descriptions(policies)
        
        # Save data unless analyze-only
        if not args.analyze_only:
            data = {
                'timestamp': datetime.now().isoformat(),
                'fortigate_host': args.host,
                'vdom': args.vdom,
                'policies': policies,
                'addresses': addresses,
                'services': services,
                'structure_analysis': structure
            }
            
            fetcher.save_to_file(data, args.output)
        
        # Logout
        fetcher.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())