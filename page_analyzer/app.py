from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

from page_analyzer.models import Url, UrlCheck, UrlId

app = Flask(__name__)

with app.app_context():
    from page_analyzer.config import SETTINGS_CONFIG, load_settings

    load_settings(app, SETTINGS_CONFIG)

    from page_analyzer.containers import (url_check_db_service,
                                          url_check_http_service,
                                          url_db_service)
    from page_analyzer.exceptions import (InvalidUrlCheckException,
                                          InvalidUrlException,
                                          InvalidUrlInsertionException,
                                          UrlCheckHttpFailedException)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/urls", methods=["POST"])
def create_url():
    url: Url = url_db_service.get_url_by_name(name=request.form["url"])
    if url is None:
        try:
            url_id: UrlId = url_db_service.create_url(url=request.form["url"])
        except (InvalidUrlException, InvalidUrlInsertionException) as exc:
            flash(str(exc), "danger")
            return render_template("index.html", url_name=request.form["url"]), 422
        else:
            flash("Страница успешно добавлена", "success")
            return redirect(url_for("get_url", ind=url_id))
    else:
        flash("Страница уже существует", "info")
        return redirect(url_for("get_url", ind=url["id"]))


@app.route("/urls", methods=["GET"])
def get_list_urls():
    return render_template(
        "urls/index.html",
        data=url_db_service.list_urls_with_checks(),
    )


@app.route("/urls/<int:ind>")
def get_url(ind: int):
    url: Url = url_db_service.get_url_by_id(ind=ind)
    url_checks: list[UrlCheck] = url_check_db_service.get_url_checks(url_id=ind)
    if url is None:
        abort(404)

    return render_template("urls/urls.html", url=url, checks=url_checks)


@app.route("/urls/<int:ind>/checks", methods=["POST"])
def create_url_check(ind: int):
    url: Url = url_db_service.get_url_by_id(ind=ind)
    try:
        url_check: UrlCheck = url_check_http_service.get_page_data(url["name"])
        url_check_db_service.create_url_check(url_id=ind, url_check=url_check)
    except (UrlCheckHttpFailedException, InvalidUrlCheckException) as exc:
        flash(str(exc), "danger")
    else:
        flash("Страница успешно проверена", "success")

    return redirect(url_for("get_url", ind=url["id"]))


@app.errorhandler(404)
def page_not_found():
    return render_template("errors/404.html"), 404
