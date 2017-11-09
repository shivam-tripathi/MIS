from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


class Check:
    def __init__(self, one, two, three):
        self.one = one
        self.two = two
        self.three = three

    def get_alpha(self):
        return self.one

@app.route('/check')
def check():
    obj = Check(1, "Two", [i for i in range(10)])
    print (obj.three, obj.two)
    return render_template('check.html', obj=obj, lis=obj.three, str=obj.two, user=obj.two)

if __name__ == '__main__':
    app.run(debug=True)
