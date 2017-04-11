# SQLALCHEMY_MIGRATE_REPO = "./modules/migrate"

# 数据库连接
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = ''
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'linux_study'

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8" % \
                          (MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
