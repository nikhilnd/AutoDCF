from flask import Flask
from flask import request, render_template
from flask import current_app, abort
from flask import send_file

import os 
import uuid
import io 

from generate import generate_dcf

app = Flask(__name__)

@app.route('/')
def main(): 
    ticker = request.args.get('ticker')
    path = current_app.root_path 

    if ticker != None: 
        unique = uuid.uuid4() 

        # Generate excel file
        try: 
            new_file = generate_dcf(ticker, path, unique)
        except Exception as error: 
            print(error)
            abort(500, description="Unable to get data")
        
        # Copy file into memory
        return_data = io.BytesIO()
        with open(new_file, 'rb') as fo: 
            return_data.write(fo.read())
        return_data.seek(0)

        # Remove local file
        os.remove(new_file)
        files = os.path.join(path, "files")
        # os.rmdir(files + "/" + str(unique))
        os.rmdir(os.path.join(files, str(unique)))

        # Send file
        file_name = "DCF_" + ticker + ".xlsx"
        return send_file(return_data, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name=file_name, as_attachment=True)
        
    return render_template('index.html', error=False)