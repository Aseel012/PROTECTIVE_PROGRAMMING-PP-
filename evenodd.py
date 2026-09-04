# TO GET EVEN ODD WE BASIICALLY USE NUMBER % 2 
# ITS GOOD ITS TIME COMPLEXITY IS 0(1) BUT STILL WE CAN DO BETTER 
# THE TECHNIC I AM GOING TO SHOW IS IN BITS LETS DO THEN AT FIRST UDNERSTAND THE BASICS LATER WE WILL SECURE IT 
# SORRY FOR WASTING TIME IN ARRANGEMENTS NO OTHER CHOICE FOR BEGIN CONVINENT :>

# SANITIZE THE INPUT 
# U CAN USE NON IDENTIFIABLE NAMES TO VARAIBLES , FUNCTIONS LIKE USING _ , - 
#   EX - __GATH_ARG()

# UNABLE to UDNERSTAND the VAL_X cause its dreclared and value is alrady 
# justifted in payload but isinstance is not acessing it in dictionary ??

# lets again check out 


# lets ask GPT WHY conversion is not working 

def gather_input():

    while True:
        user_input = input("Enter the Integer : ")

        # lets check if its empty and return error

        if len(user_input) == 0:
            print("ERROR ! INPUT CANNOT BE EMPTY ")
            continue
        

        # lets check for decimal values 
        if "." in user_input:
            print("DECIMALS ARE NOT ALLOWED !")
            continue

        # safety conversion to Integer not primary important but better to use 

        try : 
            # lets strip the negative sign to check the rest are integers or not 
            str_check = user_input.lstrip('-')
            if not str_check.isdigit():
                raise ValueError

            num = int(user_input)
            break

        except ValueError:
            print("Not a Integer !")    
    return {"val_x" : num}

        
# performance checker

def check_bits(payload):

    # ANTI AI 

    if not isinstance(payload,dict):
        raise TypeError("MUST BE DICT !")


    if "val_x" not in payload:
        raise KeyError("Payload Missing , val_x !")


    num = payload["val_x"]


# boolean check true = 1 , false = 0
# explicitly check the block booleans to protect our math 

    if not isinstance(num,bool) or not isinstance(num,int):
        raise TypeError("Strict Integer Required ! ")

    # Resource Protection ! 
    # PY cannot handle Infinite Numbers 
    
    if abs(num) > 10*100000:
        raise OverflowError("Integer Size limit ! ")

# lets check the best one !
# bitwise handle directly at hardware CPU level O(1) TC.

    if(num & 1) == 0:
        return "Even"
    else :
        return "Odd"


secure_payload = gather_input()


try:
    result = check_bits(secure_payload)
    print(result)
except Exception as e:
    print(e) 


# 1 . Boolean Hack 
# Attempting to pass true Value
try :
    check_bits({"val_x":True})

except Exception as e :
    print(e)
 
# 2. Ai Raw String Hack 
try:
    check_bits(42)

except Exception as e :
    pass