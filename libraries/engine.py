from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
import sys
from pymongo import MongoClient
sys.path.append ("/project/userapp/libraries")
import helpers
from pino import pino

logger = pino(
    bindings={"service": "k8smanager"}
)
    

def user_create(user,course,req_id):
    logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Check user workspace for user {} and course {}".format(user,course))
    helper = helpers.helper()
    check_exist = helper.user_course_exist(user,course)
    if check_exist==False:
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Creating user {} and course {} MongoDB registry".format(user,course))
        create_registry = helper.create_user_registry(user,course,req_id)
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Creating user {} and course {} SSH user".format(user,course))
        create_ssh_user = helper.create_ssh_user(user,course,req_id)
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Creating user {} and course {} OpenShift User".format(user,course))
        create_oc_user = helper.create_user_oc(req_id)
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Creating user {} and course {} OpenShift Project".format(user,course))
        create_project = helper.create_project_oc(req_id)
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Creating user {} and course {} READING Workspace".format(user,course))
        workspace = helper.workspace(user,course,req_id)
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "Creating user {} and course {} Increase the pivot".format(user,course))
        helper.update_pivot(req_id)
        return json.dumps({"workspace": workspace}), 200
    else:
        logger.info({'reqID': req_id,'user':user,'status': 'progressing'}, "User {} and course {} READING".format(user,course))
        workspace = helper.workspace(user,course,req_id)
        return json.dumps({"workspace": workspace}), 200

