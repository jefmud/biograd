# admin.py
# This is intented to extend Flask admin with student/faculty models
from flask import abort, g, render_template, redirect, session

# adding flask_admin
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.pymongo import ModelView

import os

import forms


def initialize(app, db):
    admin = Admin(app, name='GraduateProgress', template_mode='bootstrap3')