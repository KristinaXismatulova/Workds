import configparser

def cheks():
    """
    param::      
    out:: 
    
    """

    conf = configparser.ConfigParser()
    conf.read('setting.ini')

    if conf['SETT']['token'] == "ur token":
        raise Exception("Sorry, token is None")
    
    if conf['SETT']['group'] == "your group id":
        raise Exception("Sorry, your number of group is None")

    return conf['SETT']['token'], conf['SETT']['group']

answer= cheks()

token = ""
group = ""

if len(answer)>1:
    token = answer[0]
    group = answer[1]
 
