from pymongo import MongoClient
import sys
import configparser
import paramiko
import string
import random
import time
sys.path.append ("/project/userapp/libraries")

class helper:
    def __init__(self):
        self.connection = MongoClient('host.docker.internal:27017',
                            username='batman',
                            password='BatMan_2020',
                            authSource='management')
        config = configparser.ConfigParser(allow_no_value=True)
        config.read("/project/userapp/libraries/host")
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


    def ssh(self,command):
        key = paramiko.RSAKey.from_private_key_file("/project/userapp/libraries/ssh_key")
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
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
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
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False
    def update_pivot(self):
        try:
            db = self.connection["management"]
            collection = db["pivot"]
            x = int(collection.find_one({'name':'base'}))
            print(x)
            x += 1
            myquery = { "name": "base" }
            newvalues = { "$set": { "base": x } }
            collection.update_one(myquery, newvalues)
            return True
        except: 
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False

    def create_user_registry(self,user,course):
        try:
            db = self.connection["management"]
            collection = db["courses"]
            self.user = user
            self.course = course
            document = collection.find_one({'courseName':course})
            collection = db["usercourse"]
            x = collection.insert_one({'user':user,'courseName':course,'github':document['github']})
            return True
        except: 
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False

    def workspace(self,user,course):
        try:
            db = self.connection["management"]
            collection = db["usercourse"]
            document = collection.find_one({'user':user,'courseName':course})
            response = []
            document['_id'] = str(document['_id'])
            response.append(document)
            return response
        except: 
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False
    def update_user_registry(self,user,course,parameters):
        try:
            db = self.connection["management"]
            collection = db["usercourse"]
            myquery = { "user": user,"courseName":course }
            print(myquery)
            newvalues = { "$set":  parameters  }
            print('hola')
            print(newvalues)
            result = collection.update_one(myquery, newvalues)
        except: 
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False
    def create_user_oc(self):
        try:
            passwd =  self.randomString()
            self.oc_passwd = passwd
            self.oc_user = self.ssh_user
            command = 'htpasswd -b /root/lab/users.htpasswd {} {}'.format(self.oc_user,self.oc_passwd)
            create_oc_user = self.ssh(command)
            command = 'oc --kubeconfig=/root/lab/kubeconfig delete secret htpass-secret -n openshift-config'
            create_oc_user = self.ssh(command)
            command = 'oc --kubeconfig=/root/lab/kubeconfig create secret generic htpass-secret --from-file=htpasswd=/root/lab/users.htpasswd -n openshift-config'
            create_oc_user = self.ssh(command)
            parameters = {"oc_user":self.oc_user,"oc_passwd":self.oc_passwd}
            print(parameters)
            update_registry = self.update_user_registry(self.user,self.course,parameters)
        except: 
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False
    def create_project_oc(self):
        try:
            self.oc_project = self.ssh_user
            command = 'oc --kubeconfig=/root/lab/kubeconfig new-project {}'.format(self.oc_project)
            create_oc_user = self.ssh(command)
            command = 'oc --kubeconfig=/root/lab/kubeconfig adm policy add-role-to-user edit {} -n {}'.format(self.oc_user,self.oc_project)
            create_oc_user = self.ssh(command)
            parameters = {"oc_project":self.oc_project}
            print(parameters)
            update_registry = self.update_user_registry(self.user,self.course,parameters)
        except: 
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False
    def create_ssh_user(self,user,course):
        try:
            print("user {}".format(self.user))
            passwd =  self.randomString()
            pivot = self.check_pivot()
            ssh_user = 'user{}'.format(pivot)
            self.ssh_user = ssh_user
            # self.ssh('ls')
            command = 'useradd    {}'.format(ssh_user)
            create_user = self.ssh(command) 
            print(create_user)
            command = 'echo "{}" | passwd {} --stdin '.format(passwd,ssh_user)
            print(command)
            assign_passwd = self.ssh(command)  
            self.ssh_passwd = assign_passwd
            parameters = {"ssh_user":ssh_user,"ssh_passwd":passwd}
            print(parameters)
            update_registry = self.update_user_registry(user,course,parameters)    
        except:
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False

    def course_info(self,user,course):
        try:
            course_exist = self.user_course_exist(user,course)
            # print(course_exist)
            i = 0
            while (i < 5 and not course_exist):
                time.sleep( 30 )
                i += 1
            result = self.workspace(user,course)
            # print("cehchu {}".format(result))
            return self.workspace(user,course)
        except:
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            return False
               



    