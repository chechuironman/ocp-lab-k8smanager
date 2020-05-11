from pymongo import MongoClient
import sys
import configparser
import paramiko
import string
import random
import time
import os
sys.path.append ("/project/userapp/libraries")

class helper:
    def __init__(self):
        self.connection = MongoClient(os.environ['MONGODB_HOST'],
                            username=os.environ['MONGODB_USER'],
                            password=os.environ['MONGODB_PASSWORD'],
                            authSource=os.environ['MONGODB_DATABASE'])
        config = configparser.ConfigParser(allow_no_value=True)
        config.read("/project/userapp/libraries/host/host")
        sections = config.sections()
        for section in sections:
            for option in config.options(section):
                self.server = option
        self.github = ''        
        self.ssh_user = ''
        self.ssh_passwd = ''
        self.oc_user = ''
        self.oc_passwd = ''
        self.user = ''
        self.course = ''
        self.pivot = ''
        self.oc_project = ''
        self.oc_instance = ''
        self.ssh_host = ''


    def ssh(self,command):
        key = paramiko.RSAKey.from_private_key_file("/project/userapp/libraries/ssh-key/ssh-privatekey")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = self.server,  username = "root", pkey = key )
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        # print(ssh_stdin)
        # print(ssh_stdout)
        if  ssh_stderr.readlines():
            print(ssh_stderr.readlines())
        print(ssh_stdout.readlines())   

    def randomString(self,stringLength=6):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def user_course_exist(self, user,course):
        try:
            db = self.connection["management"]
            collection = db["usercourse"]
            x = collection.find_one({"user":user,"courseName":course})
            print(x)
            if x:
                if((x['user'] == user) and (x['courseName'] == course)):
                    self.user = user
                    self.course = course
                    print('resgistry found')
                    return True
                else:
                    print('resgistry NOT found')
                    return False
            else:
                return False
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def check_pivot(self):
        try:
            db = self.connection["management"]
            collection = db["pivot"]
            x = collection.find_one({'name':'base'})
            self.pivot = x
            print(x)
            return int(x['base'])
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def check_ssh_host(self):
        try:
            print("SSH host check")
            db = self.connection["management"]
            collection = db["sshhost"]
            x = collection.find_one({'host':'cloud-lab'})
            self.ssh_host = x['ip']
            print(x)
            return str(x['ip'])
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def update_pivot(self):
        try:
            db = self.connection["management"]
            collection = db["pivot"]
            search = collection.find_one({'name':'base'})
            print("pivot")
            x = int(search['base'])
            x += 1
            myquery = { "name": "base" }
            newvalues = { "$set": { "base": x } }
            collection.update_one(myquery, newvalues)
            return True
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def create_user_registry(self,user,course):
        try:
            print("Create course: {} for user {}".format(course,user))
            ssh_host = self.check_ssh_host()
            print(ssh_host)
            db = self.connection["management"]
            collection = db["courses"]
            self.user = user
            self.course = course
            document = collection.find_one({'courseName':course})
            collection = db["usercourse"]
            x = collection.insert_one({'user':user,'courseName':course,'github':document['github'], 'oc_instance': document['clusterUrl'], 'ssh_host' : self.ssh_host})
            return True
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def workspace(self,user,course):
        try:
            print("Workspace: {} for user {}".format(course,user))
            db = self.connection["management"]
            collection = db["usercourse"]
            document = collection.find_one({'user':user,'courseName':course})
            response = []
            document['_id'] = str(document['_id'])
            print("chechu {}".format(document))
            response.append(document)
            return response
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def update_user_registry(self,user,course,parameters):
        try:
            print("Update course: {} for user {}".format(course,user))
            db = self.connection["management"]
            collection = db["usercourse"]
            myquery = { "user": user,"courseName":course }
            # print(myquery)
            newvalues = { "$set":  parameters  }
            # print('hola')
            # print(newvalues)
            result = collection.update_one(myquery, newvalues)
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def create_user_oc(self):
        try:
            print("Create oc user: {} ".format(self.user))
            passwd =  self.randomString()
            self.oc_passwd = passwd
            self.oc_user = self.ssh_user
            if os.path.exists("guru99.txt"):
                command = 'htpasswd -b /mnt/lab/users.htpasswd {} {}'.format(self.oc_user,self.oc_passwd)
            else:
                command = 'htpasswd -c -B -b /mnt/lab/users.htpasswd {} {}'.format(self.oc_user,self.oc_passwd)

            print(command)
            os.system(command)
            # create_oc_user = self.ssh(command)
            command = 'oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig config use-context admin && oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig delete secret htpass-secret -n openshift-config'
            print(command)
            os.system(command)
            # create_oc_user = self.ssh(command)
            command = 'oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig config use-context admin && oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig create secret generic htpass-secret --from-file=htpasswd=/mnt/lab/users.htpasswd -n openshift-config'
            print(command)
            os.system(command)
            # create_oc_user = self.ssh(command)
            parameters = {"oc_user":self.oc_user,"oc_passwd":self.oc_passwd}
            print(parameters)
            # print(parameters)
            update_registry = self.update_user_registry(self.user,self.course,parameters)
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def create_project_oc(self):
        try:
            self.oc_project = self.ssh_user
            command = 'oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig config use-context admin && oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig new-project {}'.format(self.oc_project)
            # create_oc_user = self.ssh(command)
            os.system(command)
            command = 'oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig config use-context admin && oc --kubeconfig=/project/userapp/libraries/kubeconfig/kubeconfig adm policy add-role-to-user edit {} -n {}'.format(self.oc_user,self.oc_project)
            os.system(command)
            # create_oc_user = self.ssh(command)
            parameters = {"oc_project":self.oc_project}
            # print(parameters)
            update_registry = self.update_user_registry(self.user,self.course,parameters)
        except: 
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def create_ssh_user(self,user,course):
        try:
            print("Create ssh user: {} ".format(user))
            # print("user {}".format(self.user))
            passwd =  self.randomString()
            pivot = self.check_pivot()
            ssh_user = 'user{}'.format(pivot)
            self.ssh_user = ssh_user
            # self.ssh('ls')
            command = 'useradd    {}'.format(ssh_user)
            create_user = self.ssh(command) 
            # print(create_user)
            command = 'echo "{}" | passwd {} --stdin '.format(passwd,ssh_user)
            print(command)
            assign_passwd = self.ssh(command)  
            self.ssh_passwd = assign_passwd
            parameters = {"ssh_user":ssh_user,"ssh_passwd":passwd}
            # print(parameters)
            update_registry = self.update_user_registry(user,course,parameters)    
        except:
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False

    def course_info(self,user,course):
        try:
            course_exist = self.user_course_exist(user,course)
            i = 0
            while (i < 5 and not course_exist):
                time.sleep( 30 )
                i += 1
            result = self.workspace(user,course)
            return self.workspace(user,course)
        except:
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            return False
               



    