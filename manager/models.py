from django.db import models, connection
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your models here.
class DB:

    def __init__(self):
        self.cursor = connection.cursor()

    # def __del__(self):
    #     self.cursor.close()
    #     connection.close()

    def beginTransaction(self):

        try:
            self.cursor.execute("set autocommit = off;")
        except:
            print("Error in setting autocommit off")
            return False

        try:
            self.cursor.execute("begin;")
        except:
            print("Error in beginning transaction")
            return False

        return True

    def rollback(self):

        try:
            self.cursor.execute("rollback;")
        except:
            print("Error in rolling back")
            return False

        try:
            self.cursor.execute("set autocommit = on;")
        except:
            print("Error in setting autocommit on")
            return False

        return True

    def commit(self):

        try:
            self.cursor.execute("commit;")
        except:
            print("Error in commiting")
            return False

        try:
            self.cursor.execute("set autocommit = on;")
        except:
            print("Error in setting autocommit on")
            return False

        return True

    def select(self, query, errorMsg):
        try:
            self.cursor.execute(query)

        except:
            print(errorMsg)
            return False

        row = self.cursor.fetchall()
        return row

    def insertOrUpdateOrDelete(self, query, errorMsg):
        try:
            self.cursor.execute(query)
        except:
            print(errorMsg)
            return False

        return True

class Transaction(models.Model):
    tid = models.IntegerField(primary_key=True)
    clientid = models.IntegerField('Users',db_column='clientId')  # Field name made lowercase.
    traderid = models.IntegerField('Users', db_column='traderId')  # Field name made lowercase.
    commissiontype = models.CharField(db_column='commissionType', max_length=255)  # Field name made lowercase.
    totalamount = models.FloatField(db_column='totalAmount')  # Field name made lowercase.
    commissionamount = models.FloatField(db_column='commissionAmount')  # Field name made lowercase.
    ordertype = models.CharField(db_column='orderType', max_length=255)  # Field name made lowercase.
    status = models.CharField(max_length=255)
    date = models.DateTimeField()
    btcamount = models.FloatField(db_column='btcAmount')  # Field name made lowercase.
    btcrate = models.FloatField(db_column='btcRate')  # Field name made lowercase.
    walletid = models.IntegerField('Wallet', db_column='walletId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'transaction'