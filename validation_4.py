
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

                logger.json(f"Created new file at storage file at : {self.storage_file}")

            except Exception as e:
                logger.error(f"Failed to create storage file : {e}")

        else:
            logger.info(f"Storage File found at : {self.storage_file}")


    def save_user(self,user_data:Dict[str, Any])->bool:
        "save the data in json "
        try:
            users = self.get_all_users()
            record = UserRecord(

                
            )






