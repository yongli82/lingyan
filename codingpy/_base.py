#!usr/bin/env python
# -*- coding: utf-8 -*-

# import os
# import sys

from flask import Flask, send_from_directory, flash, render_template
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import logout_user, current_user
from flask_admin import Admin

# from .models import User, AnonymousUser
from .ext import (bootstrap, db, moment, cache, mail,
                  login_manager, bcrypt)
from .config import config


__all__ = ['create_app']

csrf = CsrfProtect()
admin = Admin()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    # babel.init_app(app)
    cache.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)

    register_managers(app)
    register_routes(app)
    # register_uploadsets(app)
    register_error_handle(app)

    # before every request
    @app.before_request
    def before_request():
        if not current_user.is_anonymous:
            if not current_user.confirmed:
                flash('请登录邮箱激活账户。')
                logout_user()
            if current_user.is_banned:
                flash('账户已被禁用，请联系管理员。')
                logout_user()

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder, 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')

    @app.route('/robots.txt')
    def robotstxt():
        return send_from_directory(app.static_folder, 'robots.txt')

    return app


def register_routes(app):
    from .controllers import site, user

    app.register_blueprint(site.bp, url_prefix='')
    app.register_blueprint(user.bp, url_prefix='/user')
    # app.register_blueprint(admin.bp, url_prefix='/admin')


def register_managers(app):

    login_manager.session_protection = 'strong'
    # flask-login will keep track of ip and broswer agent,
    # will log user out if it detects a change
    login_manager.login_view = 'user.login'
    login_manager.login_message = '请先登陆'
    # login_manager.anonymous_user = AnonymousUser
    login_manager.init_app(app)


def register_error_handle(app):
    @app.errorhandler(403)
    def page_403(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_404(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def page_500(error):
        return render_template('errors/500.html'), 500