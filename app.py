from flask import Flask, render_template, request, flash, redirect, url_for
import os
import zipfile
import shutil
from datetime import datetime
from model import scan_for_plagiarism
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Needed for flash messages
app.config['UPLOAD_FOLDER'] = os.getcwd()
app.config['ALLOWED_EXTENSIONS'] = {'zip', 'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple authentication logic (replace with real user validation)
        if username == 'admin' and password == 'password':
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    result_filename = None
    uploaded_file_name = None
    error = None
    success = ''

    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file uploaded. Please upload a file.', 'error')
            return redirect(request.url)

        file = request.files['file']
        if not file or not file.filename:
            flash('No file selected. Please upload a file.', 'error')
            return redirect(request.url)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_base, file_extension = os.path.splitext(filename)
            uploaded_file_name = filename
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)

            # Create folder for extracted files or single file
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], file_base)
            os.makedirs(folder_path, exist_ok=True)

            # Handle file extraction or movement
            if file_extension.lower() == '.zip':
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall(folder_path)
            else:
                target_path = os.path.join(folder_path, filename)
                if not os.path.exists(target_path):
                    shutil.move(temp_path, target_path)
                else:
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        flash(f'Could not delete temporary file: {str(e)}', 'warning')

            # Run plagiarism detection
            use_level_4 = 'use_level_4' in request.form  # Checkbox for Level 4
            try:
                result = scan_for_plagiarism(folder_path, use_level_4)
            except Exception as e:
                flash(f'Error during plagiarism detection: {str(e)}', 'error')
                result = None

            if result:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    result_filename = f"result_{timestamp}.txt"
                    result_path = os.path.join(folder_path, result_filename)
                    with open(result_path, "w") as f:
                        f.write(result)
                    success = f"Results saved to: {result_filename} in {file_base} folder."
                except Exception as e:
                    flash(f'Failed to save result: {str(e)}', 'error')
            else:
                flash('Plagiarism detection failed or returned no result. Please try again.', 'error')

    return render_template('index.html', 
                         result=result, 
                         result_filename=result_filename, 
                         uploaded_file_name=uploaded_file_name, 
                         success=success)

if __name__ == '__main__':
    app.run(debug=True)