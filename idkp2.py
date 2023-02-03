import boto3
import json

client = boto3.client('iam')
response = client.list_users()
with open("ListEverything.json","a") as file:
    for user in response['Users']:
        attached_policies = client.list_attached_user_policies(UserName=user['UserName'])
        user_policies = []
        for policy in attached_policies['AttachedPolicies']:
            policy_versions = client.list_policy_versions(PolicyArn=policy['PolicyArn'])
            for policy_version in policy_versions['Versions']:
                if policy_version['IsDefaultVersion']:
                    policy_info = client.get_policy_version(
                        PolicyArn=policy['PolicyArn'],
                        VersionId=policy_version['VersionId']
                    )
                    policy_document = json.dumps(policy_info['PolicyVersion']['Document'])
                    policy_json = json.loads(policy_document)
                    policy_actions = []
                    for statement in policy_json['Statement']:
                        actions = statement.get('Action', [])
                        effect = statement.get('Effect', [])
                        resources = statement.get('Resource', [])
                        if type(actions) is str:
                            policy_actions.append({
                                "Permission": actions,
                                "Effect": effect,
                                "Resources": resources
                            })
                        else:
                            for action in actions:
                                policy_actions.append({
                                    "Permission": action,
                                    "Effect": effect,
                                    "Resources": resources
                                })
                    user_policies.append({
                        "Policy": policy["PolicyName"],
                        "Actions": policy_actions
                    })
        file.write(json.dumps({
            "Username": user['UserName'],
            "Policies": user_policies
        }) + '\n')
