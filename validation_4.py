
#  VALIDATION IN PRODUCTION STYLE 
# CREATING A SIMPLE USER MANAGEMNT SYSMTEM TO STORE VALIDATION , SANTIZE , WHITE , BLACK LIST , REGEX AND APPLYING BOUNDARY CASES TO IT 
# STORING IT IN JAVASCRIPT OBJECT NOTATION(JSON)


# LETS BEGIN 

import logging
import re 
import json 
import os 
from datetime import datetime
from typing import Tuple,Optional,Dict,Any,List
from dataclasses import dataclass,field,asdict


def print_header(title:str):
    print("\n" + "="*50)
    print(f"{title}".center(50))
    print("="*50)

# lets at frsit create the loggin to write to a file instead of clusstering in terminal UI

logging.basicConfig(
    filename = 'app.log',
    level = logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# lets store in the directory same as this file where this file is located 
# it will take current location and store ait where the script is located


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class ValidationResult:
    is_valid:bool
    data:Optional[Dict[str,Any]]=None
    errors: Dict[str,str] = field(default_factory=dict)
    sanitized_data : Optional[Dict[str, Any]] = None

    def add_error(self,field_name : str, message:str):
        self.errors[field_name] = message
        self.is_valid = False

    def to_dict(self) -> Dict[str,any]:
        return{
            'valid' : self.is_valid,
            'data' : self.sanitized_data or self.data,
            'errors' : self.errors
        
        }


class UserRecord:
    # to store the recods names , email , age 
    username = str
    email = str
    age = int
    validated_at : str
    validation_status : str

    def to_dict(self) -> Dict[str,Any]:
        return asdict(self)


class UserDataStorage:
    # handle the storage of validate user data in json

    def __init__(self,storage_filename:str = "validate_users.json"):
        self.storage_file = os.path.join(BASE_DIR, storage_filename)
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        # create storage file if it is not exisiting 
        # adding this due to github push for new users to valadate the user input as of it own 

        if not os.path.exists(self.storage_file):
            try:
                with open(self.storage_file,'w') as f :
                    json.dump([],f , indent =2)

                logger.info(f"Created new file at storage file at : {self.storage_file}")

            except Exception as e:
                logger.error(f"Failed to create storage file : {e}")

        else:
            logger.info(f"Storage File found at : {self.storage_file}")

# the fetch is working but not pushing i think changed the global mail need to of the screen to put email and pass will od later 
    def save_user(self,user_data:Dict[str, Any])->bool:
        "save the data in json "
        try:
            users = self.get_all_users()
            record = UserRecord(
            username=user_data['username'],
            email=user_data['email'],
            age=user_data['age'],
            validated_at=datetime.now().isoformat(),
            validation_status='PASSED'
            )
            users.append(record.to_dict())
            with open(self.storage_file,'w') as f:
                json.dump(users,f,indent=2)
            logger.info(f"user {user_data['username']} saved to storage")
            return True
        except Exception as e:
            logger.error(f"Failed to save user data : {e}")
            return False

    def get_all_users(self) -> List[Dict[str , Any]]:
        # RETRIVING THE STORED USER
        try:
            with open(self.storage_file,'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users : {e}")
            return[]

    def get_user_by_username_fetch(self,username:str) -> Optional[Dict[str,Any]]:

        users = self.get_all_users()
        for user in users:
            if user['username'].lower() == username.lower():
                return user
            return None


     # "DELTE THE USER BY NAME"
    def delete_user_nm(self,username:str)-> bool:
        try:
            users = self.get_all_users()
            initial_count = len(users)
            users = [u for u in users if u['username'].lower()!= username.lower()]
            if len(users) == initial_count:
                return False
            with open(self.storage_file, 'w') as f:
                json.dump(users,f,indent=2)
            logger.info(f"User {username} deleted from storage")
            return True
        except Exception as e :
            logger.error(f"Failed to delte : {e}")

    def get_statistics(self)-> Dict[str,Any]:
        users = self.get_all_users()
        return
        {
            'total_users' : len(users),
            'latest_validation' : users[-1]['Validated_at'] if users else None,
            'usernames' : [u['username'] for u in users]
        }


# WHITE LISTING , BLACK LISTING , REGRESSION , BOUNDARY CHECKS
class UserInputValidate:

    USERNAME_WHITELIST = re.compile(r'^[a-zA-Z0-9._]{3,30}$')
    USERNAME_BLACKLIST = {'admin','root','superuser','moderator','administrator','support','helpdesk','test','guest'}
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    EMAIL_BLACKLIST_DOMAINS = {'tempmail.com','guerrillamail.com','throwaway.com'}
    AGE_MIN = 10
    AGE_MAX = 99

    def __init__(self,storage : UserDataStorage):
        self.validation_stats = {'total_validations': 0 , 'passed' : 0, 'failed' : 0}
        self.storage = storage

    def validate_username(self,username:str) -> Tuple[bool,str]:
        if not username:
            return False,"Username cannot be empty"
        username = username.strip()

        if len(username) < 3:
            return False , "Username must be at least > 3 char "


        if len(username) > 30:
            return False , "Username must be at least < 30 char "


        if not self.USERNAME_WHITELIST.match(username):
        
            return False , "Username can only cotain letters , numbers , dots  and underscores "

            
        if username.lower() in self.USERNAME_BLACKLIST:
            return False, f"username '{username}' is not available "

        if '..' in username or '__' in  username:
            return False, "username cannot contain dots or underscors"

        if username.endswith(('.','_')):
            return False, "Username cannot end with dot or underscore"

        if username.startswith(('.','_')):
            return False, "Username cannot start with dot or underscore"


        if self.storage.get_user_by_username_fetch(username):
            return False , f"Username '{username} is already taken "

        return True,""

    def validate_email(self,email:str)->Tuple[bool,str]:
        if not email:
            return False, "Email Cannot be empty"

        email = email.strip().lower()
        if not self.EMAIL_PATTERN.match(email):
            return False,"Please enter a valid email address"
        try:
             _, domain = email.split('@', 1)

        # for the value imporper using in buuilt method of VALUE ERROR


        except ValueError:
            return False,"Invalid Email Format"

        if domain in self.EMAIL_BLACKLIST_DOMAINS:
            return False,"EMAIL PROVIDER IS NOT ALLOWED , enter a PERMANENT EMAIL ADDR"

            
        if len(email)>254:
            return False, "Email Address is too long"

        if '..' in email:
            return False, "Email Cannot contain consecutive dots"
        local_part = email.split('@')[0]
        if len(local_part)>64:
            return False, "Email local part is too long"

        return True,""

    def validate_age(self,age_input:Any) -> Tuple[bool,str]:
        if age_input is none or age_input == '':
            return False , "Age is requried"
        try:
            age = int(age_input)

        except(ValueError,TypeError):
            return False, "Age must be a Valid Number "

        if age<0:
            return False , "Age must Positive"
        
        if age< self.AGE_MAX:
            return False , f"Age Cannot exceed {self.AGE_MAX} years"
        
        return True, " "


    # lets validate all the thigsn 
    # callin the calass its self while passing values in refrence 

    def validate_all(self,data:Dict[str,any])->ValidationResult:

        self.validation_stats['total_validations'] +=1

        result = ValidationResult(is_valid=True,data=data.copy())
        
        #initializing a empty trap to store the reulst after coptign and comaprning the old name the same set is alreadypresent or not 
        
        sanitized={}

        username = data.get('username')
        is_valid , error = self.validate_username(username)
        if not is_valid:
            result.add_error('username',error)
        else:
            sanitized['username'] = username.strip()

        email = data.get('email')

        is_valid,error = self.validate_email(email)
        if not is_valid:
            result.add_error('email',error)
        else:
            sanitized['emails']=email.strip().lower()

        age=data.get('age')

        is_valid , error = self.validate_age(age)

        if not is_valid:
            result.add_error('age',error)

        else:
            sanitized['age'] = int(age)

        if result.is_valid:
            self._validation_stats['passed']+=1
            result.sanitized_data = sanitized
            logger.info(f"Validation passed for user : {sanitized_get('username')}")
            if self.storage.save_user(sanitized):
                logger.info("user data saved ! ")
        else :
            self._validation_stats['failed'] +=1
            # lets give warning at first then reutnr 

            logger.warning(f"validation failed : {result.errors}")
        return result

        def get_stats(self)-> Dict[str,int]:
            return self.validation_stats.copy()


# lets take user input ! 

def get_user_input(prompt:str) -> str:
    while True:
        user_input = input(f"{prompt} > ")
        if user_input.strip():
            return user_input
        print("INPUT CANNOT BE EMPTY , PLEASE TRY AGAIN ")


def view_stored_users(storage: UserDataStorage):

    users = storage.get_all_users()
    print_header("STORED USERS")
    if not users:
        print("\n No users found in storage .\n")
        return
# printng the data with enumertae cause for in loop but i am good with enumerate 
    print(f"total users : {len(users)}")
    for idx, user in enumureate(users,1):
        print(f,"[{idx}] {user['username']}")
        print(f"  Email {user['email']}")
        print(f"  Age   {user['Age']}")
        print(f"  Status {user['Validation_status']}")


# lets do write the the main application for performing 


def main():
    storage = UserDataStorage()
    validator = UserInputValidate(storage=storage)

    while True:
        print_header("User validation system")
        print("1. Register new user")
        print("2. View Stored User")
        print("3. Search for a user")
        print("4. Delete a user")
        print("5. View Statistics user")
        print("6. EXIT")

        # lets take input and allow operatios

        choice = input("Enter your choice (1-6) > ").strip()

        if choice == '1':
            attempts = 0
            max_attempts = 3

            while attempts < max_attempts:
                print_header("REGISTER A NEW USER")
                print(f"Attempt {attempts+1} of {max_attempts} (Type 'q' for cancel)")

                print()

                username = get_user_input("Enter the user name (3-30 chars)")
                if username.lower() == 'q' : break

                email = get_user_input("Enter email addrr")
                if email.lower() == 'q' : break

                age_input = get_user_input("Enter age (10-99)")
                if age_input.lower() == 'q' : break

                user_data = {'username' : username , 'email' : email , 'age':age_input}
                result = validator.validate_all(user_data)


                if result.is_valid:
                    print_header("REGISRATION SUCCED ! ")
                    print(f"un : {result.sanitized_data['username']}")
                    print(f"email : {result.sanitized_data['Email']}")
                    print(f"age : {result.sanitized_data['Age']}")
                    input("\n Enter to return menu ")
                    break
                else:
                    print_header("REGISTRATION FAILED")
                    for field_name , error in result.error.items():
                        print(f"{field_name.capitalize()}:{error}")

                    attempts +=1
                    if attempts < max_attempts:
                        input("Press enter to try again !")

        elif choice == '2':
            view_stored_users(storage)
            input("\n Press enter to return to menu ")

        elif choice == '3':
            print_header("Search user")
            if username:
                username = input("Enter un to search > ").strip()

                if user:
                    print(f"User found : {user['username']}")
                    print(f"Email   :   {user['email']}")
                    print(f"age   :   {user['age']}")
                    print(f"status   :   {user['validation_status']}")

                else:
                    print("NO USER FOUND ")

            input("\n Enter to return menu")


        elif choice == '4' :
            print_header("DELETE USER")
            username = input("Enter User name to delete > ").strip()
            if username:
                confirm = input(f"Are u sure u to want delete ' {username}'")

                if confirm.lower() == 'y':
                    if storage.delete_user_nm(username):
                        print(f"USER '{username}' deleted successfuly. ")

                    else:
                        print(f"Failed to delte user '{username}' (or user dont exist).")

                else:
                        print("DELETION CANCELLED")

                input("\n Press enter to return to Menu... ")


        elif choice == '5':

            stats = storage.get_statistics()
            val_stas = validator.get_stats()
            print_header("STATSITICS")

            print("storage stats : ")
            print(f" Total Registered user : {stats['latest_validation']}")
            

            if stats['latest_validation']:
                print(f"Latest Registration : {stats['latest_validation']}")
            
            print(f" usernaemes    : {', '.join(stats['usernames'])if stats ['usernames'] else 'None'}")

            print("\n validation stats : ")

            print(f" Total Validations : {val_stas['total_validations']}")
            print(f" Successful        : {val_stas['passes']}")
            print(f" Failed            : {val_stas['failed']}")


            if val_stas['total_validations']>0:
                pass_rate = (val_stas['passed'] / val_stas['total_validations']) * 100
                print(f" Pass Rate   : {pass_rate:.1f}%")

            input("\nPress enter to return menu...")

        elif choice =='6':
            break

        else:
            print("INVALID CHOICE. PLEASE TRY AGAIN ")
            input("Press Enter to Continue....")


if __name__== "__main__":
    main()


# we alaredy csotred error till stats now lets move beyond 

            

            













