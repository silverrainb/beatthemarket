from beatthemarket.app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ('beatthemarket.blueprints.user.tasks',
                                       'beatthemarket.blueprints.portfolio.tasks')
