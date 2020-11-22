from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm
import os
import pandas as pd
from wtforms.fields import SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import configure_uploads, IMAGES, UploadSet, DOCUMENTS
from werkzeug.utils import secure_filename, redirect
from src.sentiment import get_sentiment
from flask import send_file

app = Flask(__name__, static_folder="../static/")

app.config['SECRET_KEY'] = 'thisisasecret'
app.config['UPLOADED_DATAFILES_DEST'] = 'uploads/documents'

upset_xlsx = UploadSet('datafiles', DOCUMENTS)
configure_uploads(app, upset_xlsx)


class MyForm(FlaskForm):
    xls = FileField("choose xls", [FileRequired(),
                                   FileAllowed(['xls', 'xlsx', 'csv'], 'excel,csv')])


class PostUploadForm(FlaskForm):
    choose_col = SelectField(
        u'Column available in uploaded file'
    )


@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    form = MyForm()

    if form.validate_on_submit():
        filename = upset_xlsx.save(form.xls.data)
        print(filename)
        return redirect(url_for('transform', fname=filename))

    return render_template('sentiment_upload.html', form=form, title="Upload xlsx")


@app.route('/transform/<fname>', methods=['GET', 'POST'])
def transform(fname):
    form = PostUploadForm()
    filepath = os.path.join(app.config['UPLOADED_DATAFILES_DEST'], fname)
    df = pd.read_excel(filepath)
    print(df.shape)
    ch = [(col, col) for col in list(df.columns)]
    form.choose_col.choices = ch
    if form.validate_on_submit():
        selected_col = request.form.get('choose_col')
        # xl_file = request.files['file']
        print(selected_col)

        if selected_col in list(df.columns):
            df_processed = get_sentiment(df, selected_col)
            df_processed.to_excel(os.path.join(app.config['UPLOADED_DATAFILES_DEST'], "_proc.xlsx"))

        return send_file(os.path.join(app.config['UPLOADED_DATAFILES_DEST'], "_proc.xlsx"), as_attachment=True)

    return render_template('sentiment_transformed.html', form=form, title="Choose col")


@app.route('/')
@app.route('/home')
def home():
    form = MyForm()
    return render_template('home.html', form=form, title="Home")


@app.route('/about')
def about():
    form = MyForm()
    return render_template('about.html', form=form, title="About")


@app.route('/models')
def models():
    form = MyForm()
    return render_template('models.html', form=form, title="Models")


if __name__ == '__main__':
    app.run(debug=True)
