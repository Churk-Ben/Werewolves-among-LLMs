import pkg_resources
import subprocess
import re

def get_latest_version(package_name):
    try:
        output = subprocess.check_output(['pip', 'index', 'versions', package_name], text=True)
        versions = re.findall(r'Available versions: (.*)', output)
        if versions:
            latest_version = versions[0].split(',')[0].strip()
            return latest_version
        return None
    except Exception as e:
        print(f"Error checking {package_name}: {e}")
        return None

def main():
    with open('requirements.txt', 'r') as f:
        requirements = f.readlines()
    
    updated_requirements = []
    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            updated_requirements.append(req)
            continue
        
        # Extract package name and version
        if '==' in req:
            package_name, current_version = req.split('==')
            latest_version = get_latest_version(package_name)
            if latest_version and latest_version != current_version:
                print(f"{package_name}: {current_version} -> {latest_version}")
                updated_requirements.append(f"{package_name}=={latest_version}")
            else:
                updated_requirements.append(req)
        else:
            # For packages without version constraints
            package_name = req
            latest_version = get_latest_version(package_name)
            if latest_version:
                print(f"{package_name}: latest -> {latest_version}")
                updated_requirements.append(f"{package_name}=={latest_version}")
            else:
                updated_requirements.append(req)
    
    with open('requirements_updated.txt', 'w') as f:
        for req in updated_requirements:
            f.write(f"{req}\n")
    
    print("\nUpdated requirements written to requirements_updated.txt")

if __name__ == "__main__":
    main()