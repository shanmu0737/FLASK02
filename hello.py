from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/contact/')
def contact():
	return "联系我们"

if __name__ == '__main__':
	app.run(debug=True)