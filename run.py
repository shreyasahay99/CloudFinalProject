from flaskapp import app
import os
print("Static folder path:", os.path.join(app.root_path, 'static'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
