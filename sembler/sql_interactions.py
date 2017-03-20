
sqlOn = False

import logging
logger = logging.getLogger('root')

try:
    import MySQLdb
    sqlOn = True
except:
    logger.critical("Failed to load SQL library!")
    pass

## Set up db things
user="root"
password="root"
dbName = "mambo"
db = None
cursor = None

## There's no good way to pipe this variable around, need to discuss with Mark
projectID = None

if sqlOn:
    try:
        db = MySQLdb.connect(user=user, passwd=password, db =dbName)
        cursor = db.cursor()
    except:
        logger.critical("Failed to establish a database connection.")
    pass


def setProjectID(pid):
    if not sqlOn:
        return
    try:
        pid = int(pid)
        logger.debug("Setting projectID to %i" % pid)
        projectID = pid
    except:
        logger.critical("Failed to cast pid %s to int. DB interactions will fail." % pid)
        pass


def getName(projectID=projectID, cursor=cursor):
    """
    Fetches the name of the project (user submitted dxf file name) from the database.
    If no name is fetched, none returns.
    """
    if not sqlOn:
        return None
    if (projectID == None):
        return None
    ## set up everything we need
    query = """select display_name from projects where project_id=%i""" % projectID
    logger.debug(query)
    names = []
    name = None
    res = True
    try:
        cursor.execute(query)

        while res != None:
            res = cursor.fetchone()
            if res:
                names.append(res)
                if len(names) != 1:
                    ## error case
                    logger.critical("getName: Multiple projects with the same ID: %i." % projectID)
                else:
                    name = names[0][0]
    except:
        pass
    return name


def getStatus(projectID=projectID, cursor=cursor):
    ## set up everything we need
    if not sqlOn:
        return None
    if (projectID == None):
        return None
    query = """select drc_status from projects where project_id=%i""" % projectID
    logger.debug(query)
    statuses = []
    status = None
    res = True
    sawOne = False
    try:
        cursor.execute(query)
        while res != None:
            sawOne = True
            res = cursor.fetchone()
            if res:
                statuses.append(res)
                if sawOne:
                    if statuses:
                        if len(statuses) > 1:
                            ## error case
                            logger.critical("getName: Multiple projects with the same ID: %i." % projectID)
                        else:
                            status = statuses[0][0]
    except:
        pass
    return status


def setStatus(status, projectID=projectID, cursor=cursor, db=db):
    if not sqlOn:
        return None
    if (projectID == None):
        return None
    ## set up everything we need
    query = """update projects set drc_status=%i where project_id=%i""" % (status, projectID)
    logger.debug(query)
    try:
        cursor.execute(query)
        db.commit()
    except:
        logger.critical("setStatus: failed to set satus of %i to %i!" % (projectID, status))
        pass
