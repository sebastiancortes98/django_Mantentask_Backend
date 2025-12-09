"""Project package initialization.

If `PyMySQL` is installed, expose it as `MySQLdb` so Django can use it
as the MySQL DB backend on environments where `mysqlclient` is not available.
"""

try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL isn't installed, leave it to the runtime to report an ImportError
	pass

