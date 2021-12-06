from datetime import datetime, timedelta
from login.models import DB
from apscheduler.schedulers.background import BackgroundScheduler


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedulerJob, 'interval', days=1)
    scheduler.start()

def schedulerJob():
    reqTime = datetime.today() - timedelta(days=30)
    updateQuerySilver = "update client set type='silver' where id IN (select distinct clientId from transaction where 100000>=(select sum(totalAmount) from transaction group by clientId having date<(%s) and status='success'))"
    db = DB()
    db.beginTransaction()
    param = (reqTime,)
    errorMsg = "cannot find"
    retval1 = db.selectPrepared(updateQuerySilver, param, errorMsg)

    updateQueryGold = "update client set type='gold' where id IN (select distinct clientId from transaction where 100000<(select sum(totalAmount) from transaction group by clientId having date<(%s) and status='success'))"
    param = (now,)
    errorMsg = "cannot find"
    retval2 = db.selectPrepared(updateQueryGold, param, errorMsg)

    if retval1 and retval2:
        db.commit()
    else:
        db.rollback()