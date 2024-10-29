from pathlib import Path
from datetime import datetime

import os
#twitter users class functions for easier storing and manipulation of user list data
class UserClass():
    def __init__(self,users: list = []) -> None:
        if not isinstance(users, list):
            raise ValueError("(list) must an object of class userList")
        self.users          =   users
        self.userpath       =   Path()
        self.missing_users  =   []
        self.added_users    =   []
        
        
    def add(self,user: str):
        self.users.append(user)
    
    
    def saved(self, filename:str = None,withMissingsUsers:bool = False):
        # uses default filename of datetime strings if the name isn't specified
        if not filename:
            filename = datetime.today().strftime("%Y.%m.%d") + ".txt"
        # if for some reason userpath isn't defined then it will just default to CWD
        path: Path = self.userpath.resolve() / filename 
        
    
        # checking if dir or destination folder exist
        path.parent.mkdir(exist_ok=True,parents=True)
        
        # Saving the User handles
        with open(path,"w") as file:
            
            file.write(f"\ntotal numbers of users: {len(self.users)}")
            file.write('\n'.join())
            
            if withMissingsUsers:
                self.missing_users.sort()
                file.write(f"\n\ntotal missings: {len(self.missing_users)}\n\n")
                file.write(''.join(f"{user.ljust(30,' ')} :missing\n" for user in self.missing_users))
                file.close
            
            print(f"\nUser handles saved to: {path}\n")

            
    
    
    def read(self,path: Path = None, return_mode: bool = False):
        #read the users file specified by the paramaters "path"
        users = path.read_text()
        users = [line.lower() for line in users.split("\n") if "@" in line]
        
        #return a users from the the file instead of saving it in the class "users"
        #if the "return_mode" is True
        if return_mode:
            return users
        else:
            self.users = users     
        
        
    def read_allFiles(self,pathList: list[Path]):
        for file in pathList:
            users = self.read(file,True)
            for user in users:
                if user not in self.users:
                    self.add(user=user)
    
    
    def compared_to(self,users: list,outputs: bool = False):
        #return missing users when compared to external user list
        for user in users:
            if user not in self.users:
                #if the compared users does not exist in the users class then..
                self.missing_users.append(user) 
        for user in self.users:
            if user not in users:
                #if the users class contain user that does not exist in the compared users then..
                self.added_users.append(user) 
                
        #return an output on terminal if True
        if outputs:
            self.output_any_changes()
            
    # def compared_to_recent(self,path:Path = None): 
    #     # if no path were inputted then it will default to self.userpath regardless whether or not the path is pointing the correct dir
    #     if not path:
    #         path = self.userpath.resolve()
    #     if recent_records(path) is False:
    #         return
    #     else:
    #         usersFromRecent = self.read(
    #             path=recent_records(path),
    #             return_mode=True
    #             )
    #         self.compared_to(users=usersFromRecent,outputs=True)
    
    def notices_any_changes(self) -> bool:
        if self.added_users == [] and self.missing_users == []:
            return False
        else:
            return True 
        
    def output_any_changes(self) -> None:
        print("\nMissings Users:\n")
        for user in self.missing_users:
            print(f"{user} is missing!")
        if self.missing_users == []:
            print("No compared users that are missings...")
        else:print(f"\ntotal missings users:{len(self.missing_users)}")
            
        print("\nAdded Users:\n")
        for user in self.added_users:
            print(f"{user} is added!")
        if self.added_users == []:
            print("No compared users that are added...")
        else:print(f"\ntotal added users: {len(self.added_users)}")
        
        os.system('pause')

    # def saved_if_theres_changes(self,userPath:path = None) -> None:
    #     if userPath is None:
    #         raise ValueError(f"no inputted argument for the path to comparison!\ncheck {self.__module__}")
    #     if self.notices_any_changes():
    #         self.saved(userPath)
    #     else:
    #         pass





    
