import sqlite3
from flask import Flask , render_template ,request,url_for,redirect,g,flash,send_from_directory
from datetime import datetime
import os

app=Flask(__name__)
app.debug=True
app.secret_key = "jkljksk8843(*##*"

DATEBASE_URL = r'F:\VIP\Flask02\db\feedback.db'
UPLOAD_FOLDER = r'F:\VIP\Flask02\uploads'
ALLOWED_EXTENSIONS = ['.jpg','.png','.gif']

#呈现特定目录下的资源
@app.route('/profile/<filename>')    #视图函数
def render_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

#检查文件是否允许上传
def allowed_file(filename):
	# filename = 'sdd.png'
	_,ext = os.path.splitext(filename) #必须要传两个值，name没有用_替代，splitext是截取文件名
	return ext.lower() in ALLOWED_EXTENSIONS  #lower 还不明白

#将游标获取的Tuple根据数据库列表转换为dict
def make_dicts(cursor,row):
	return dict((cursor.description[i][0],value)for i,value in enumerate(row))

#获取（建立数据库连接），把连接缓存起来
#全局变量 global  ,优点：全局都能访问到
#调用def_db的时候，先到全局变量global找有没有这个变量，如果有-->返回
#如果没有-->执行一个返回
def get_db():
	db = getattr(g ,'_database',None)
	if db is None:
		# db = g._database = sqlite3.connect(DATEBASE_URL) #多目标赋值
		db = sqlite3.connect(DATEBASE_URL)
		g._database = db
		db.row_factory = make_dicts #
	return db

#执行sql语句不返回结果
def execute_sql(sql , prms=()):
	c = get_db().cursor()
	c.execute(sql,prms)
	c.connection.commit()

#执行用于查询数据的sql语句，返回结果
def query_sql(sql,prms=(),one = False):  #one 默认为False,显示所有
	c = get_db().cursor()
	result = c.execute(sql,prms).fetchall()  #fetchall获取多行数据
	c.close()
	return result[0] if one else result  #（默认情况下刚才返回的 0，如果result不等于空，否则返回None）如果成立显示一条，否则显示所有

#关闭连接(在当前app上下文销毁时关闭连接)
@app.teardown_appcontext
def close_connnection(exeption):
	db = getattr(g , '_database',None)
	if db is not None:
		db.close()


#模板页
@app.route('/')
def hello_world():
	return render_template('base.html')

#登录页
@app.route('/login/',methods=['GET',"POST"])
def login():
	if request.method == 'POST':
		username = request.form.get('username',2001)
		pwd = request.form.get('pwd',2002)
		sql = 'select count(*) as [count] from UserInfo where Username =? and Password = ?'
		result = query_sql(sql,(username,pwd), one = True)
		# return str(result)
		if  int(result.get('count')) > 0:
			return redirect(url_for('feedback_list'))
		flash('账号或密码错误') #闪现错误提示信息
	return render_template('login.html')

#查寻出分类表内容
@app.route('/feedback/')
def feedback():
	# conn = sqlite3.connect(r'.\db\feedback.db') #相对地址出了问题
	conn = sqlite3.connect(DATEBASE_URL) #启用绝对地址
	c = conn.cursor()	# 游标
	sql = "select ROWID,CategoryName from category"
	categories = c.execute(sql).fetchall()  #执行sql,fetchall()查找全部的值
	c.close()
	conn.close()
	# categories = [(1,'产品质量'),(2,'客户服务'),(3,'购买支付')]
	return render_template('post.html',categories=categories)  #跳转到HTML页面

# # 接收提交表单数据
@app.route('/post_feedbock/',methods=['POST'])
def post_feedbock():
	#如果当前请求数据为POST
	if request.method == 'POST':
		#获取表单数据
		subject = request.form.get('subject',2222) #主题
		categoryid = request.form.get('categoryid',3333)  # 用get可以使用默认值
		username = request.form.get('username')
		email = request.form.get('email')
		body = request.form.get('body')
		release_time = datetime.now()
		state = 0
		img_path = None
        # if 'screenshot' in request.files:
		if request.files.get('screenshot',None):
			#获取图片上传，并且获取文件名，以便和其它字段一并插入数据库
			img = request.files['screenshot']  #screetshow是表单里name的值
			if allowed_file(img.filename): #如果允许的话就上传
				img_path = datetime.now().strftime('%Y%m%d%H%M%f') + os.path.splitext(img.filename)[1] #截取后缀名
				img.save(os.path.join(UPLOAD_FOLDER, img_path))  #同一目录不能有相同文件名，文件名统一
		# return str(img_path)
		# return render_template('post.html')

		conn = sqlite3.connect(DATEBASE_URL)  #连接数据库
		c = conn.cursor()    #游标
		sql = "insert into feedback(Subject, CategoryID, UserName, Email, Body ,State, RealeseTime,Image) VALUES (?,?,?,?,?,?,?,?)"
		c.execute(sql,(subject,categoryid,username,email,body,state,release_time,img_path)) #元组形式  #通过游标 执行sql
		conn.commit()
		conn.close()
		return redirect(url_for('feedback'))  #redirect  重定向



#查看提交数据列表
@app.route('/admin/list/')
def feedback_list():
	# conn = sqlite3.connect(DATEBASE_URL)
	# c = conn.cursor()
	# sql = "select f.ROWID,f.* ,c.CategoryName from feedback f INNER JOIN category c ON c.ROWID=f.CategoryID"
	# feedbacks = c.execute(sql).fetchall()
	# conn.close()
    key = request.args.get('key', '')    #搜索功能  key值
    sql = "select f.ROWID,f.* ,c.CategoryName from feedback f INNER JOIN category c ON c.ROWID=f.CategoryID where f.Subject like ? ORDER BY f.rowid DESC "
    feedbacks = query_sql(sql,('%{}%'.format(key),))
    return render_template('feedback-list.html',items=feedbacks)

#在编辑页显示提交的反馈信息 （查询操作）
@app.route('/admin/edit/<id>')
def edit_feedback(id=None):
	# conn = sqlite3.connect(DATEBASE_URL) #启用绝对地址
	# c = conn.cursor()	# 游标
	# sql = "select ROWID,CategoryName from category"
	# categories = c.execute(sql).fetchall()
    #
	# #获取当前id的信息并绑定到Form表单，以备修改
	# sql = "select ROWID,* from feedback WHERE rowid=?"
	# current_feedback = c.execute(sql,(id,)).fetchone()
	# c.close()
	# conn.close()
    sql = "select ROWID,CategoryName from category"
    categories = query_sql(sql)

    sql = "select ROWID,* from feedback WHERE rowid=?"
    current_feedback = query_sql(sql,(id), one = True)  #查一条数据，加 one = True
    # return render_template('edit.html', categories=categories, item=current_feedback)  #跳转到edit.html页面
	# return str(current_feedback)
    return render_template('edit.html')

#保存编辑后的反馈信息  更新操作
@app.route('/admin/save_edit/',methods=['POST'])
def save_feedback():
	if request.method == 'POST':
		# 获取表单数据
		rowid = request.form.get('rowid',2002)
		reply = request.form.get('reply',2)
		state =  1 if request.form.get('state',0) == 'on' else 0
		sql = 'update feedback set Reply = ?,State = ? WHERE rowid = ?'

		conn = sqlite3.connect(DATEBASE_URL)
		c = conn.cursor()
		c.execute(sql, (reply,state,rowid))
		conn.commit()  #提交操作
		conn.close()
		return redirect(url_for('feedback_list'))
		# return str(rowid)

#删除数据
@app.route('/admin/feedback/del/<id>/')
def delete_feedaback(id=0):
	# conn = sqlite3.connect(DATEBASE_URL)
	# c = conn.cursor()
	# sql = "delete from feedback WHERE ROWID = ?"
	# c.execute(sql,(id,))
	# conn.commit()  #提交操作
	# conn.close()
	sql = "delete from feedback WHERE ROWID = ?"
	execute_sql(sql,(id,))
	return redirect(url_for('feedback_list')) #跳转

if __name__ == '__main__':
	app.run()