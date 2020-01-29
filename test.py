from os import path

import yaml
import sys

from kubernetes import client, config

sys.path.append ("./libraries")

def main():
    config.load_kube_config(config_file='./libraries/kubeconfig')
    k8s_beta = client.ExtensionsV1beta1Api()
    project = {"apiVersion": "config.openshift.io/v1","kind": "Project","metadata":{"name": "project-test"}}
    resp = k8s_beta.create_namespaced_deployment(body=project,namespace="")
    print("Deployment created. status='%s'" % str(resp.status))


if __name__ == '__main__':
    main()