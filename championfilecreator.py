import json,shelve,os
from urllib.request import urlopen

def delete_db():
    try:
        os.remove("champions.bak")
        os.remove("champions.dat")
        os.remove("champions.dir")
    except FileNotFoundError:
        pass
    else:
        pass


def recreate_dynamic():
    delete_db()
    try:
        urldata = urlopen("http://www.dashadower-1.appspot.com/championdata")
    except:
        input("Data could not be loaded from remote server. Press any key to exit.")
    else:
        data = str(urldata.read().decode("utf-8")).rstrip()
        print(len(data))
        datafile = shelve.open("champions")
        data = json.loads(data)



        for objects in data["data"]:

            championinfo = data["data"][str(objects)]
            kr = championinfo["name"]
            id = championinfo["id"]
            name = championinfo["key"]
            datafile[name] = {"id":id,"kr":kr}

        datafile.close()


if __name__ == "__main__":
    if input("Are you sure? This will delete all user added champion info(Y/N)") == "Y":
        delete_db()
        recreate_dynamic()
        input("Recreated database. Press any key to continue")