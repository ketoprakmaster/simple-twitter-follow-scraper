from configparser import ConfigParser
from pathlib import Path as path
import os


class config(ConfigParser):
    # default configuration for filenames and director
    config_name = "config.ini"
    config_path = path.cwd() / config_name
    default_section = "last_State".upper()
    
    def __init__(self):
        # check if config file exist or not
        if not config.config_path.exists:
            print(f"config is not detected: {self.config_path}..\nproceed to make a new clean slate config..")
            print("creating new config file with a default settings..\n")
            self.createBlankConfig()
            return
    
    def validate_config(self):
        # if it does exist but if config is broken
        try:
            self.read(self.config_name) 
        except Exception as e:
            print(f"ERROR: {e}\nproceed to delete a broken config and make a new one instead")
            print("creating new config file with an default settings..\n")
            self.createBlankConfig()
    
    
    def writeDown(self):
        with open(config.config_name,"w") as conf:
            self.write(conf)
  

    def createBlankConfig(self):
        self["LAST_STATE"] = {
        "lastUsername" : "",
        "lastOperation" : "",
        "headless" : ""
        }
        self.writeDown()    
                       
                    
    def set_config(self,key:str, value:str,sections:str = default_section):
        if not key or not value:
            raise KeyError("no key/value is inputed")
        self.set(section=sections.upper(),option=key,value=value)

        self.writeDown()
    
    
    def return_value(self,section=default_section,key:str = None):
        try:value = self[section][key].lower()
        except KeyError: return False
        if value in ('true',"yes"):
            return True
        elif value in ("no","false") or not value :
            return False
        else: return value
    
    
    # def return_default_user_path(self) -> path:
    #     if self.return_value(key="lastusername") is not False and self.return_value(key="lastoperation") is not False:
    #         return path.cwd() / self.return_value(key="lastusername") / self.return_value(key="lastoperation")
    #     else:
    #         raise KeyError("current config is not complete!\ncannot return path")
    
    
if __name__ == "__main__":
    conf = config()
    conf.validate_config()