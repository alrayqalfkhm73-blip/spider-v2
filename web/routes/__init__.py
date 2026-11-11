"""Routes registration"""
def register_routes(app):
    from web.routes import (
        auth, me, health, scrape, pump, chat,
        scrape_more, sessions, store, economy, misc, proxies,
        telegram_webhook,
    )
    app.register_blueprint(auth.bp)
    app.register_blueprint(me.bp)
    app.register_blueprint(health.bp)
    app.register_blueprint(scrape.bp)
    app.register_blueprint(pump.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(scrape_more.bp)
    app.register_blueprint(sessions.bp)
    app.register_blueprint(store.bp)
    app.register_blueprint(economy.bp)
    app.register_blueprint(misc.bp)
    app.register_blueprint(proxies.bp)
    app.register_blueprint(telegram_webhook.bp)
