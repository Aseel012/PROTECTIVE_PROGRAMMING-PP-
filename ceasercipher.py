# LETS BEGIN 

# 1. NAMES WILL NOT BE PREDEFINES LIKE WE GIVE IN NORMAL CODE 
# 2. CREATING FUNCTIONS EACH TIME 
# 3. SANITZE THE INPUT WHILE TAKING SHIFT VALUE 
# 4. lets try to force it to wrap in dictionary (API SAFETY)
# 5. OUTPUT FU**KED UP LETS BRING IN , THE PROCESS

def gather_input():
    #  INPUT FOR THE STRING 
    # EACH TIME WILL REMOVE ALL THE NULL SPACES
    while True:
        inp = input("Enter the string : ").strip()
        if(len(inp)==0):
            print("Error : TEXT CANNOT BE EMPTY !")
        else :
            break

    while True:
        shift_str = input("Enter the shift number : ").strip()
        try :
            shift = int(shift_str)
            if abs(shift)>10000:
                print("ERROR : SHIFT NUMBER IS TOO LARGE !")
                continue
            break
        except ValueError:
            print("Error : must be an INTEGER ")

    return {"text" : inp , "shift" : shift}



def secret_payload(payload):

    # we are going to take only dictionary !!
    if not isinstance(payload , dict):
        raise TypeError("Security Error : Payload must be dictionary !")

    # check the required keys exist indside the dictioanry 
    if "text" not in payload or "shift" not in payload:
        raise KeyError("Security error : Missing 'text' or 'keys'! ")
    
    inp = payload["text"]
    shift = payload["shift"]

    # sanitize the data types cause the user inputs cannot be predicatbale (#PP)

    if not isinstance (inp,str):
        raise TypeError("Error : MUST BE A STRING")


    if not isinstance(shift,int) or isinstance(shift,bool):
        raise TypeError("Error : MUST BE A INTEGER , not boolean or float")  



    # CEASER CIPHER (ENCRYP , DECRYP )
    # a list to store the values which are going to conver into INT 
    lsit = []

    for char in inp:
        if char.islower():
            lsit.append((ord(char) - 97 + shift) % 26 + 97)

        elif char.isupper(): #upper 'A' = 65 
            lsit.append((ord(char) - 65 + shift ) % 26 + 65)

        else:
            lsit.append(ord(char))

    print(lsit)
    
    decoded_chars= []

    for val in lsit:

        char_to_check = chr(val)

        if char_to_check.islower():
            decoded_chars.append(chr((val - 97 - shift )% 26 + 97))

        elif char_to_check.isupper():

            #wrap around 

            decoded_chars.append(chr((val - 65 - shift )% 26 + 65))

        else:
            #decoding space

            decoded_chars.append(chr(val))
    
    print("String : "," ".join(decoded_chars))


sanitized_payload = gather_input()

# dict payload

try :
    secret_payload(sanitized_payload)

except Exception as e:
    print(e)


