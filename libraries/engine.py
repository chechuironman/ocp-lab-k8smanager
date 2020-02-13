from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
import sys
from pymongo import MongoClient
sys.path.append ("/project/userapp/libraries")
import helpers

def namespaces():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config(config_file='/project/userapp/libraries/kubeconfig')

    v1 = client.CoreV1Api()
    try:
        namespaces = v1.list_namespace()
        namespace_ = []
        i = 0
        for namespace in namespaces.items:
            namespace_.append({'id': str(i), 'namespace' : namespace.metadata.name})
            i +=1
            # print(namespace.metadata.name)
        
        # print(response)
        return(json.dumps(namespace_))
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

def create_namespace(namespace):
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config(config_file='/project/userapp/libraries/kubeconfig')

    v1 = client.CoreV1Api()
    body = client.V1Namespace() # V1Namespace | 
    body.metadata = client.V1ObjectMeta(name=namespace)
    print(body.metadata)
    pretty = 'pretty_example' # str | If 'true', then the output is pretty printed. (optional)
    # dry_run = 'dry_run_example' # str | When present, indicates that modifications should not be persisted. An invalid or unrecognized dryRun directive will result in an error response and no further processing of the request. Valid values are: - All: all dry run stages will be processed (optional)
    # field_manager = 'field_manager_example' # str | fieldManager is a name associated with the actor or entity that is making these changes. The value must be less than or 128 characters long, and only contain printable characters, as defined by https://golang.org/pkg/unicode/#IsPrint. (optional)

    try:
        api_response = v1.create_namespace(body, pretty=pretty)
        print(api_response)
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)
        

def user_create(user,course):
    helper = helpers.helper()
    check_exist = helper.user_course_exist(user,course)
    print(check_exist)
    if check_exist==False:
        # pivot = helper.check_pivot()
        create_registry = helper.create_user_registry(user,course)
        print(create_registry)
        create_ssh_user = helper.create_ssh_user(user,course)
        create_oc_user = helper.create_user_oc()
        create_project = helper.create_project_oc()
        workspace = helper.workspace(user,course)
        helper.update_pivot()
        return json.dumps({"workspace": workspace}), 200
    else:
        workspace = helper.workspace(user,course)
        return json.dumps(workspace)

def course_info(user,course):
    try:
        helper = helpers.helper()
        course_result = helper.course_info(user,course)
        # print(json.dumps(course_result))
        # print(json.dumps(course_result))
        return(json.dumps(course_result))
    except:
        e = sys.exc_info()[0]
        print( "<p>Errorpid: %s</p>" % e )
        return str(0) 
    # return check_exist

    # print(x)                  
    # collection = db['user-course']
    # collection = db.find({})
    # cursor = collection.find({})
    # for document in cursor:
    #       print(document)
    # print(collection)

    