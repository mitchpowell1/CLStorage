from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/test/')
def test():
    return 'test successful'

@app.route('/test2/')
def test2():
	return ['a','b','c']

if __name__ == '__main__':
    app.run()
